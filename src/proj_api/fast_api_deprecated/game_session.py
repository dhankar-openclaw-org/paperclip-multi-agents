"""
game_session.py
═══════════════════════════════════════════════════════════════════════════════
PTY-backed game subprocess manager.

Each GameSession wraps one pseudo-terminal (PTY) pair and one child process
running TINTIN_BAGELS_GAME_V4.py.

Architecture
────────────
  Browser  ←──WebSocket──→  FastAPI  ←──PTY master fd──→  Game subprocess
                                                           (slave fd = stdin/
                                                            stdout/stderr)

Why PTY and not plain pipes?
─────────────────────────────
  • os.system('clear') in the game emits ANSI escape codes that only work
    inside a real or pseudo terminal.
  • colorama detects sys.stdout.isatty() to decide whether to emit ANSI
    colour codes.  A pipe returns False; a PTY slave returns True.
  • Arrow keys and special keys sent by xterm.js are encoded as ANSI escape
    sequences that require a PTY to pass through correctly.

Public API
──────────
  session = GameSession()
  session.start(rows=40, cols=120)   # spawn subprocess
  data = await session.read()        # async read from PTY (returns bytes)
  session.write(b"hello\n")          # write keystrokes to PTY
  session.resize(rows, cols)         # notify PTY of terminal resize
  session.stop()                     # terminate subprocess, close PTY

Thread-safety
─────────────
  start() / stop() / write() / resize() are synchronous and safe to call
  from the asyncio thread.  read() is a coroutine and must be awaited.
"""

import asyncio
import fcntl
import os
import pty
import struct
import subprocess
import termios
from pathlib import Path

# ── Path to the game script (same directory as this file) ─────────────────────
GAME_SCRIPT = Path(__file__).parent / "TINTIN_BAGELS_GAME_V4.py"

# ── Default terminal dimensions sent to the PTY before the game starts ────────
DEFAULT_ROWS = 40
DEFAULT_COLS = 130


# ═══════════════════════════════════════════════════════════════════════════════

class GameSession:
    """
    One live game session: one PTY pair + one game child process.

    Lifecycle
    ─────────
      1.  Instantiate:  session = GameSession()
      2.  Start:        session.start()      ← spawns subprocess
      3.  I/O loop:     await session.read() / session.write()
      4.  Cleanup:      session.stop()       ← always call on disconnect
    """

    def __init__(self) -> None:
        self._master_fd: int | None = None   # PTY master — parent reads/writes here
        self._proc: subprocess.Popen | None = None

    # ── Lifecycle ──────────────────────────────────────────────────────────────

    def start(self, rows: int = DEFAULT_ROWS, cols: int = DEFAULT_COLS) -> None:
        """
        Open a PTY pair and launch the game subprocess.

        Parameters
        ──────────
        rows : int  — initial terminal height in character rows
        cols : int  — initial terminal width in character columns
        """
        master_fd, slave_fd = pty.openpty()

        # Set initial window size on the SLAVE side before the game starts.
        # This is what the game process will inherit as its terminal dimensions.
        self._set_winsize(slave_fd, rows, cols)

        self._proc = subprocess.Popen(
            ["python3", "-u", str(GAME_SCRIPT)],
            stdin=slave_fd,
            stdout=slave_fd,
            stderr=slave_fd,
            close_fds=True,   # close all other open fds in the child
        )

        # Parent process no longer needs the slave side.
        # All communication happens through master_fd.
        os.close(slave_fd)
        self._master_fd = master_fd

    def stop(self) -> None:
        """
        Terminate the game subprocess and release the PTY master fd.
        Safe to call multiple times.
        """
        if self._proc is not None and self._proc.poll() is None:
            self._proc.terminate()
            try:
                self._proc.wait(timeout=3)
            except subprocess.TimeoutExpired:
                self._proc.kill()

        if self._master_fd is not None:
            try:
                os.close(self._master_fd)
            except OSError:
                pass
            self._master_fd = None

    @property
    def is_alive(self) -> bool:
        """True while the game subprocess is still running."""
        return self._proc is not None and self._proc.poll() is None

    # ── Async I/O ──────────────────────────────────────────────────────────────

    async def read(self) -> bytes | None:
        """
        Wait asynchronously for output from the game and return it.

        Uses asyncio's event-loop reader (add_reader) so the coroutine yields
        without blocking any thread while waiting for data.

        Returns
        ───────
        bytes  — data chunk from PTY (may be 1 … 4096 bytes)
        None   — PTY has been closed (game exited or error)
        """
        if self._master_fd is None:
            return None

        loop = asyncio.get_event_loop()
        future: asyncio.Future = loop.create_future()

        def _on_readable() -> None:
            loop.remove_reader(self._master_fd)
            try:
                data = os.read(self._master_fd, 4096)
                if not future.done():
                    future.set_result(data)
            except OSError:
                if not future.done():
                    future.set_result(None)   # signal EOF

        loop.add_reader(self._master_fd, _on_readable)

        try:
            return await future
        except asyncio.CancelledError:
            # Clean up the reader if the task is cancelled mid-wait
            try:
                loop.remove_reader(self._master_fd)
            except Exception:
                pass
            raise

    # ── Synchronous I/O ────────────────────────────────────────────────────────

    def write(self, data: bytes) -> None:
        """
        Send raw bytes to the game's stdin via the PTY master.

        Parameters
        ──────────
        data : bytes  — keystrokes or control sequences from the browser
        """
        if self._master_fd is not None:
            try:
                os.write(self._master_fd, data)
            except OSError:
                pass   # PTY closed — session will clean up on next read

    def resize(self, rows: int, cols: int) -> None:
        """
        Notify the PTY of a terminal window resize event.

        Called when the user resizes their browser window.  The game
        receives SIGWINCH and can re-draw if it uses curses (not used
        here, but correct behaviour for the PTY regardless).

        Parameters
        ──────────
        rows : int  — new terminal height
        cols : int  — new terminal width
        """
        if self._master_fd is not None:
            self._set_winsize(self._master_fd, rows, cols)

    # ── Private helpers ────────────────────────────────────────────────────────

    @staticmethod
    def _set_winsize(fd: int, rows: int, cols: int) -> None:
        """
        Write a TIOCSWINSZ ioctl to set the PTY window dimensions.

        struct winsize layout (from <sys/ioctl.h>):
          ws_row   uint16  — rows in characters
          ws_col   uint16  — columns in characters
          ws_xpixel uint16 — (unused, set to 0)
          ws_ypixel uint16 — (unused, set to 0)
        """
        winsize = struct.pack("HHHH", rows, cols, 0, 0)
        try:
            fcntl.ioctl(fd, termios.TIOCSWINSZ, winsize)
        except OSError:
            pass   # ignore if fd already closed
