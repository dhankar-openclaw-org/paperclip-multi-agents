"""
app_ws_tintin.py
═══════════════════════════════════════════════════════════════════════════════
FastAPI application — WebSocket game server + original chat bot endpoint.

Traffic flow
────────────
  Internet
    └─ ngrok (https://xxx.ngrok-free.app)
         └─ localhost:8088
              ├─ GET  /            → terminal HTML page (xterm.js)
              ├─ WS   /ws/game     → live game session (PTY bridge)
              └─ POST /chat        → simple chat bot (mapping_secrets.json)

WebSocket session lifecycle
────────────────────────────
  1.  Browser opens  wss://xxx.ngrok-free.app/ws/game
  2.  FastAPI accepts, creates a GameSession (opens PTY + spawns game)
  3.  Two concurrent asyncio tasks run until either side disconnects:
        pty_to_ws  — reads PTY output  → sends binary frames to browser
        ws_to_pty  — receives text frames from browser → writes to PTY
  4.  On disconnect (or game exit), both tasks are cancelled and the
      GameSession is stopped (subprocess killed, PTY closed).

Modules
───────
  game_session.py  — GameSession class (PTY + subprocess management)
  terminal_ui.py   — TERMINAL_HTML constant (xterm.js page)

Run
───
  python3 app_ws_tintin.py
  # or
  uvicorn app_ws_tintin:app --host 0.0.0.0 --port 8088 --reload

Then in a separate terminal:
  ngrok http 8088
"""

import asyncio
import json
import logging
from contextlib import asynccontextmanager
from pathlib import Path

import uvicorn
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from game_session import GameSession
from terminal_ui import TERMINAL_HTML

# ─── Logging ──────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger("app_ws_tintin")

# ─── Chat-bot secrets (reused from original app) ──────────────────────────────
_SECRETS_FILE = Path(__file__).parent / "mapping_secrets.json"

def _load_secrets() -> dict:
    """Load secret-code → response mapping from mapping_secrets.json."""
    if _SECRETS_FILE.exists():
        return json.loads(_SECRETS_FILE.read_text())
    log.warning("mapping_secrets.json not found — chat bot will only respond to HELLO BOT")
    return {}

SECRETS: dict = _load_secrets()


# ═══════════════════════════════════════════════════════════════════════════════
#  FastAPI application
# ═══════════════════════════════════════════════════════════════════════════════

app = FastAPI(
    title       = "Tintin Bagels Game Server",
    description = "WebSocket PTY bridge + chat bot endpoint",
    # Disable Swagger / ReDoc / OpenAPI schema — not needed for production
    docs_url    = None,
    redoc_url   = None,
    openapi_url = None,
)

# CORS — allow the GitHub Pages chat page to call /chat
app.add_middleware(
    CORSMiddleware,
    allow_origins  = ["*"],
    allow_methods  = ["*"],
    allow_headers  = ["*"],
)

# Static files — serves images_tintin/ directory at /static/
# e.g.  /static/tintin-red-rackhams-treasure-cover.jpg
_IMAGES_DIR = Path(__file__).parent / "images_tintin"
app.mount("/static", StaticFiles(directory=str(_IMAGES_DIR)), name="static")


# ═══════════════════════════════════════════════════════════════════════════════
#  HTTP routes
# ═══════════════════════════════════════════════════════════════════════════════

@app.get("/", response_class=HTMLResponse, include_in_schema=False)
async def serve_terminal():
    """
    Serve the xterm.js terminal page.

    The browser loads this once, then upgrades to a WebSocket connection
    at  /ws/game  to start the game.
    """
    return HTMLResponse(content=TERMINAL_HTML)


# ─── Chat bot (original endpoint — kept for backward compatibility) ────────────

class ChatRequest(BaseModel):
    message: str

@app.post("/chat")
async def chat(req: ChatRequest):
    """
    Simple chat bot.

    Checks the incoming message against:
      1. Secret codes in mapping_secrets.json (exact match, case-sensitive)
      2. The literal string 'hello bot' (case-insensitive)
      3. Everything else → default reply
    """
    text = req.message.strip()

    if text in SECRETS:
        return {"reply": SECRETS[text]}

    if text.lower() == "hello bot":
        return {"reply": "HELLO MASTER RD"}

    return {"reply": "I only understand HELLO BOT"}


# ═══════════════════════════════════════════════════════════════════════════════
#  WebSocket — game session bridge
# ═══════════════════════════════════════════════════════════════════════════════

async def _stream_pty_to_ws(session: GameSession, ws: WebSocket) -> None:
    """
    Continuously read PTY output and forward it as binary WebSocket frames.

    Runs until:
      • the game process exits  (session.read() returns None)
      • the WebSocket closes    (send raises WebSocketDisconnect / RuntimeError)
      • the task is cancelled   (on_disconnect cleanup)
    """
    while session.is_alive:
        data = await session.read()

        if data is None:
            # PTY EOF — game has exited
            log.info("PTY closed — game subprocess exited")
            try:
                await ws.send_bytes(
                    b"\r\n\r\n"
                    b"  [ Game over - refresh the page to play again ]\r\n"
                )
            except Exception:
                pass
            break

        if data:
            try:
                await ws.send_bytes(data)
            except (WebSocketDisconnect, RuntimeError):
                break


async def _stream_ws_to_pty(session: GameSession, ws: WebSocket) -> None:
    """
    Receive text frames from the browser and forward them to the game's stdin.

    Frame types handled
    ───────────────────
    • Plain text  → raw keystroke(s), written directly to the PTY.
    • JSON object → control message:
          { "type": "resize", "cols": <int>, "rows": <int> }
      Any other JSON type is silently ignored.

    Runs until the WebSocket closes (WebSocketDisconnect is raised).
    """
    while True:
        text = await ws.receive_text()

        # ── Detect JSON control messages ──────────────────────────────
        if text.startswith("{"):
            try:
                msg = json.loads(text)
                if msg.get("type") == "resize":
                    rows = int(msg["rows"])
                    cols = int(msg["cols"])
                    session.resize(rows, cols)
                    log.debug("Terminal resize → %d rows × %d cols", rows, cols)
                    continue
            except (json.JSONDecodeError, KeyError, ValueError):
                pass   # not a valid control message — fall through as plain text

        # ── Regular input → write to PTY ──────────────────────────────
        session.write(text.encode("utf-8"))


@app.websocket("/ws/game")
async def websocket_game(websocket: WebSocket):
    """
    WebSocket endpoint — one connection = one game session.

    On connect:   create PTY, spawn game subprocess
    During game:  bridge PTY ↔ WebSocket bidirectionally
    On disconnect: cancel both streaming tasks, stop the session
    """
    await websocket.accept()
    client = websocket.client
    log.info("WebSocket connected  from  %s:%s", client.host, client.port)

    session = GameSession()
    session.start()
    log.info("Game session started  (PID %d)", session._proc.pid)

    # ── Launch both streaming tasks concurrently ───────────────────────
    pty_task = asyncio.create_task(
        _stream_pty_to_ws(session, websocket),
        name="pty→ws",
    )
    ws_task = asyncio.create_task(
        _stream_ws_to_pty(session, websocket),
        name="ws→pty",
    )

    try:
        # Wait for whichever task finishes first (game exit OR disconnect)
        done, pending = await asyncio.wait(
            {pty_task, ws_task},
            return_when=asyncio.FIRST_COMPLETED,
        )

        # Cancel the surviving task — it is no longer needed
        for task in pending:
            task.cancel()
            try:
                await task
            except (asyncio.CancelledError, Exception):
                pass

        # Re-raise any unexpected exception from the completed task
        for task in done:
            if task.exception():
                log.warning("Task %s raised: %s", task.get_name(), task.exception())

    except WebSocketDisconnect:
        log.info("WebSocket disconnected by client")
        for task in (pty_task, ws_task):
            task.cancel()

    finally:
        session.stop()
        log.info("Game session stopped  (client %s:%s)", client.host, client.port)


# ═══════════════════════════════════════════════════════════════════════════════
#  Entry point
# ═══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    uvicorn.run(
        "app_ws_tintin:app",
        host    = "0.0.0.0",
        port    = 8088,
        reload  = True,       # set False in production
        log_level = "info",
    )
