#!/usr/bin/env python3
"""Send one status line to the allowed Telegram chat. The token is not printed."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _env_value(key: str) -> str:
    path = ROOT / ".env"
    if not path.is_file():
        return ""
    for raw in path.read_text(encoding="utf-8").splitlines():
        if raw.startswith(key + "="):
            return raw.split("=", 1)[1].strip().strip('"').strip("'")
    return ""


def send(text: str) -> str:
    chat = _env_value("TELEGRAM_ALLOWED_USER_ID")
    bot = _env_value("TELEGRAM_BOT_TOKEN")
    if not chat or not bot:
        return "not sent"
    proc = subprocess.run(
        [
            "curl", "-sS",
            f"https://api.telegram.org/bot{bot}/sendMessage",
            "-d", f"chat_id={chat}",
            "--data-urlencode", f"text={text[:3500]}",
        ],
        capture_output=True,
        text=True,
    )
    try:
        body = json.loads(proc.stdout or "{}")
    except json.JSONDecodeError:
        return "not sent"
    if body.get("ok"):
        return "sent"
    return "not sent"


if __name__ == "__main__":
    message = " ".join(sys.argv[1:]).strip()
    if not message:
        raise SystemExit("message required")
    print(send(message))
