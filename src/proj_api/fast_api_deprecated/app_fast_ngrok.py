from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn
import json
from pathlib import Path

app = FastAPI(docs_url=None, redoc_url=None, openapi_url=None)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

SECRETS_FILE = Path(__file__).parent / "mapping_secrets.json"


def _load_secrets() -> dict:
    """Re-read mapping_secrets.json on every call — no restart needed when URLs change."""
    return json.loads(SECRETS_FILE.read_text())


def _game_link_html(url: str) -> str:
    """
    Wrap a game URL in a styled HTML button.
    The raw URL is placed only in href — it is never rendered as visible text.
    """
    return (
        '<div style="text-align:center;padding:8px 0 4px;">'

        '<a href="' + url + '" target="_blank" rel="noopener noreferrer" '
        'style="'
        'display:inline-block;'
        'background:linear-gradient(135deg,#e94560 0%,#0f3460 100%);'
        'color:#ffffff;'
        'padding:13px 32px;'
        'border-radius:10px;'
        'text-decoration:none;'
        'font-weight:700;'
        'font-size:1rem;'
        'letter-spacing:1.5px;'
        'border:2px solid rgba(233,69,96,0.55);'
        'box-shadow:0 4px 22px rgba(233,69,96,0.38);'
        '">'
        '&#x1F3F4;&nbsp;&nbsp;Thundering Typhoons &mdash; Your Game Link'
        '</a>'

        '<div style="'
        'color:#8892a4;'
        'font-size:0.72rem;'
        'margin-top:9px;'
        'letter-spacing:0.5px;'
        '">'
        'Click to open the Tintin Bagels Game'
        '</div>'

        '</div>'
    )


class ChatRequest(BaseModel):
    message: str


@app.post("/chat")
def chat(req: ChatRequest):
    # Re-read on every request — game URL can be updated in mapping_secrets.json
    # without restarting the server.
    secrets = _load_secrets()
    text    = req.message.strip()

    # ── Secret code lookup (exact match, case-sensitive) ──────────────
    if text in secrets:
        value = secrets[text]

        # If the stored value is a URL → it is a game link.
        # Wrap it in HTML so the raw URL is never shown in the chat.
        if value.startswith("http"):
            return {"reply": _game_link_html(value), "html": True}

        # Plain-text reply (all other secret codes)
        return {"reply": value, "html": False}

    # ── Default greeting ──────────────────────────────────────────────
    if text.lower() == "hello bot":
        return {"reply": "HELLO MASTER RD", "html": False}

    return {"reply": "I only understand HELLO BOT", "html": False}


if __name__ == "__main__":
    uvicorn.run("app_fast_ngrok:app", host="0.0.0.0", port=8087, reload=True)
