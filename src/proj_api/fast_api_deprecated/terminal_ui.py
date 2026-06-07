"""
terminal_ui.py
═══════════════════════════════════════════════════════════════════════════════
HTML template for the in-browser terminal.

Renders a full-screen xterm.js terminal that connects to the FastAPI
WebSocket endpoint at  /ws/game  and streams the Tintin Bagels game.

Libraries loaded from CDN (no build step required)
───────────────────────────────────────────────────
  xterm.js 5.3.0        — VT100/xterm terminal emulator for the browser
  xterm-addon-fit 0.8.0 — auto-resizes the terminal to fill its container

WebSocket protocol (client → server)
──────────────────────────────────────
  Text frame, plain string  — raw keystroke(s) forwarded to the game's stdin
  Text frame, JSON object   — control message; currently only resize:
        { "type": "resize", "cols": <int>, "rows": <int> }

WebSocket protocol (server → client)
──────────────────────────────────────
  Binary frame — raw bytes from the game's stdout/stderr (PTY output).
  xterm.js renders them directly, including all ANSI colour / control codes.

Usage
─────
  from terminal_ui import TERMINAL_HTML
  ...
  return HTMLResponse(content=TERMINAL_HTML)
"""


TERMINAL_HTML: str = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>TINTIN — Secret Coordinates Game</title>

  <!-- xterm.js stylesheet -->
  <link
    rel="stylesheet"
    href="https://cdn.jsdelivr.net/npm/xterm@5.3.0/css/xterm.css"
  />

  <style>
    /* ── Reset & base ─────────────────────────────────────────── */
    *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

    :root {
      --bg:        #0a0a14;
      --card:      #16213e;
      --accent:    #e94560;
      --text:      #e0e0e0;
      --muted:     #8892a4;
      --green:     #2ecc71;
    }

    html, body {
      height: 100%;
      background: var(--bg);
      color: var(--text);
      font-family: 'Segoe UI', system-ui, sans-serif;
    }

    /* ── Layout ───────────────────────────────────────────────── */
    body {
      display: flex;
      flex-direction: column;
      align-items: center;
      padding: 10px 8px 8px;
      gap: 6px;
    }

    /* ── Top header bar ───────────────────────────────────────── */
    #header {
      width: 100%;
      max-width: 1200px;
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding: 6px 12px;
      background: var(--card);
      border: 1px solid var(--accent);
      border-radius: 8px;
    }

    #header .title {
      color: var(--accent);
      font-weight: 700;
      font-size: 0.95rem;
      letter-spacing: 2px;
    }

    #header .subtitle {
      color: var(--muted);
      font-size: 0.75rem;
    }

    /* ── Status pill ──────────────────────────────────────────── */
    #status {
      font-size: 0.75rem;
      padding: 3px 10px;
      border-radius: 12px;
      background: #1e1e2e;
      border: 1px solid var(--muted);
      color: var(--muted);
      transition: color 0.3s, border-color 0.3s;
    }

    #status.connected    { color: var(--green);  border-color: var(--green);  }
    #status.disconnected { color: var(--accent); border-color: var(--accent); }

    /* ── Terminal container ───────────────────────────────────── */
    #terminal-wrap {
      width: 100%;
      max-width: 1200px;
      flex: 1;
      border: 1px solid var(--accent);
      border-radius: 8px;
      overflow: hidden;
      padding: 4px;
      background: #0a0a0a;
    }

    /* xterm.js fills its container */
    #terminal {
      width: 100%;
      height: 100%;
    }

    /* ── Footer hint ──────────────────────────────────────────── */
    #hint {
      color: var(--muted);
      font-size: 0.7rem;
    }

    /* ── Tintin cover image — fixed overlay, top-right corner ─── */
    #tintin-cover {
      position      : fixed;
      top           : 58px;          /* sit just below the header bar  */
      bottom        : 20vh;          /* bottom edge 20 % up from foot  */
      right         : 10px;
      width         : 20vw;          /* 20 % of viewport width         */
      border        : 3px solid #ff1a3c;
      border-radius : 10px;
      overflow      : hidden;
      z-index       : 200;
      box-shadow    : 0 0 12px 3px rgba(255, 26, 60, 0.85),
                      0 6px 32px rgba(255, 26, 60, 0.45),
                      0 2px 10px rgba(0, 0, 0, 0.7);
      background    : #0a0a14;       /* fallback while image loads     */
      cursor        : default;
    }

    #tintin-cover img {
      width      : 100%;
      height     : 100%;
      object-fit : cover;            /* fill box, no distortion        */
      object-position : top center;  /* show the book's top (cover art)*/
      display    : block;
    }

    /* Subtle title badge along the bottom of the image */
    #tintin-cover .img-label {
      position    : absolute;
      bottom      : 0;
      left        : 0;
      right       : 0;
      background  : linear-gradient(transparent, rgba(10,10,20,0.88));
      color       : #e0e0e0;
      font-size   : 0.62rem;
      font-weight : 600;
      letter-spacing : 0.6px;
      text-align  : center;
      padding     : 12px 4px 5px;
    }
  </style>
</head>

<body>

  <!-- ── Header ────────────────────────────────────────────── -->
  <div id="header">
    <span class="title">&#x1F3F4; OVERLANDER TECH &mdash; TINTIN BAGELS GAME</span>
    <span class="subtitle">Pirate Edition &mdash; The Secret of the Unicorn</span>
    <span id="status">Connecting&hellip;</span>
  </div>

  <!-- ── Tintin cover image (top-right fixed overlay) ─────────── -->
  <div id="tintin-cover">
    <img src="/static/tintin-red-rackhams-treasure-cover.jpg"
         alt="Tintin — Red Rackham's Treasure" />
    <div class="img-label">Red Rackham's Treasure</div>
  </div>

  <!-- ── xterm.js terminal ─────────────────────────────────── -->
  <div id="terminal-wrap">
    <div id="terminal"></div>
  </div>

  <!-- ── Footer ────────────────────────────────────────────── -->
  <div id="hint">
    Type your 3-digit guess and press Enter &mdash; use keyboard only
  </div>

  <!-- ── Scripts ───────────────────────────────────────────── -->
  <script src="https://cdn.jsdelivr.net/npm/xterm@5.3.0/lib/xterm.js"></script>
  <script src="https://cdn.jsdelivr.net/npm/xterm-addon-fit@0.8.0/lib/xterm-addon-fit.js"></script>

  <script>
    // ── Terminal setup ─────────────────────────────────────────────────
    const term = new Terminal({
      cursorBlink   : true,
      fontSize      : 14,
      fontFamily    : '"Courier New", "Lucida Console", "DejaVu Sans Mono", monospace',
      scrollback    : 2000,
      convertEol    : false,   // let the game control line endings via PTY

      // Match Overlander Tech site colour palette
      theme: {
        background      : '#0a0a0a',
        foreground      : '#e0e0e0',
        cursor          : '#e94560',
        cursorAccent    : '#ffffff',
        selectionBackground: 'rgba(233,69,96,0.25)',

        // Standard 16 ANSI colours
        black           : '#000000',
        red             : '#e94560',
        green           : '#2ecc71',
        yellow          : '#f1c40f',
        blue            : '#3498db',
        magenta         : '#9b59b6',
        cyan            : '#1abc9c',
        white           : '#ecf0f1',

        // Bright variants
        brightBlack     : '#555555',
        brightRed       : '#ff6b6b',
        brightGreen     : '#51cf66',
        brightYellow    : '#ffd43b',
        brightBlue      : '#74c0fc',
        brightMagenta   : '#cc5de8',
        brightCyan      : '#63e6be',
        brightWhite     : '#ffffff',
      },
    });

    const fitAddon = new FitAddon.FitAddon();
    term.loadAddon(fitAddon);
    term.open(document.getElementById('terminal'));
    fitAddon.fit();

    // ── WebSocket URL (auto-detects local vs ngrok / http vs https) ────
    const wsProto = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const wsUrl   = `${wsProto}//${window.location.host}/ws/game`;

    const statusEl = document.getElementById('status');

    let ws = null;

    // ── Connect ────────────────────────────────────────────────────────
    function connect() {
      statusEl.textContent  = 'Connecting…';
      statusEl.className    = '';

      ws = new WebSocket(wsUrl);
      ws.binaryType = 'arraybuffer';   // receive PTY output as ArrayBuffer

      ws.onopen = () => {
        statusEl.textContent = 'Connected — game running';
        statusEl.className   = 'connected';

        // Tell the server the current terminal dimensions immediately
        sendResize(term.cols, term.rows);

        term.focus();
      };

      // ── Server → browser: raw PTY bytes → xterm ───────────────────
      ws.onmessage = (event) => {
        term.write(new Uint8Array(event.data));
      };

      ws.onclose = () => {
        statusEl.textContent = 'Disconnected — refresh to play again';
        statusEl.className   = 'disconnected';
      };

      ws.onerror = () => {
        statusEl.textContent = 'Connection error — check ngrok is running';
        statusEl.className   = 'disconnected';
      };
    }

    // ── Browser → server: keystrokes as plain text ─────────────────────
    term.onData((data) => {
      if (ws && ws.readyState === WebSocket.OPEN) {
        ws.send(data);           // xterm.js encodes special keys as escape sequences
      }
    });

    // ── Browser → server: resize notification as JSON ──────────────────
    function sendResize(cols, rows) {
      if (ws && ws.readyState === WebSocket.OPEN) {
        ws.send(JSON.stringify({ type: 'resize', cols: cols, rows: rows }));
      }
    }

    term.onResize(({ cols, rows }) => sendResize(cols, rows));

    // Re-fit terminal when the browser window is resized
    window.addEventListener('resize', () => {
      fitAddon.fit();           // recalculate cols/rows → triggers term.onResize
    });

    // ── Start ──────────────────────────────────────────────────────────
    connect();
  </script>

</body>
</html>
"""
