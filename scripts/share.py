#!/usr/bin/env python3
"""Open a temporary Cloudflare tunnel to the local dashboard and send the link.

The token is read from .env and sent only to the allowed Telegram chat.
It is not printed.
"""

from __future__ import annotations

import json
import os
import platform
import re
import stat
import subprocess
import sys
import time
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BIN_DIR = Path.home() / "bin"
PID_FILE = ROOT / "runs" / "cloudflared.pid"
URL_RE = re.compile(r"https://[a-z0-9-]+\.trycloudflare\.com")


def cloudflared_name(machine: str) -> str:
    names = {
        "x86_64": "cloudflared-linux-amd64",
        "aarch64": "cloudflared-linux-arm64",
        "armv7l": "cloudflared-linux-arm",
    }
    if machine not in names:
        raise SystemExit(f"unsupported architecture {machine}")
    return names[machine]


def parse_trycloudflare(text: str) -> str | None:
    match = URL_RE.search(text)
    return match.group(0) if match else None


def ensure_cloudflared() -> Path:
    BIN_DIR.mkdir(parents=True, exist_ok=True)
    dest = BIN_DIR / "cloudflared"
    if dest.is_file() and os.access(dest, os.X_OK):
        return dest
    asset = cloudflared_name(platform.machine())
    url = f"https://github.com/cloudflare/cloudflared/releases/latest/download/{asset}"
    urllib.request.urlretrieve(url, dest)
    dest.chmod(dest.stat().st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
    return dest


def _env_value(key: str) -> str:
    for raw in (ROOT / ".env").read_text(encoding="utf-8").splitlines():
        if raw.startswith(key + "="):
            return raw.split("=", 1)[1].strip().strip('"').strip("'")
    return ""


def _send(public: str, target: str = "dashboard") -> str:
    token = _env_value("API_TOKEN")
    chat = _env_value("TELEGRAM_ALLOWED_USER_ID")
    bot = _env_value("TELEGRAM_BOT_TOKEN")
    if not token or not chat or not bot:
        return "not sent, telegram or API token missing"
    if target == "mcp":
        link = f"{public}/mcp/"
        msg = f"Grasshopper MCP endpoint: {link}"
    else:
        link = f"{public}/?token={token}"
        msg = f"Grasshopper canlı: {link}"
    proc = subprocess.run(
        [
            "curl", "-sS",
            f"https://api.telegram.org/bot{bot}/sendMessage",
            "-d", f"chat_id={chat}",
            "--data-urlencode", f"text={msg}",
        ],
        capture_output=True,
        text=True,
    )
    try:
        body = json.loads(proc.stdout or "{}")
    except json.JSONDecodeError:
        return "send failed"
    if body.get("ok"):
        return "sent"
    return "send failed: " + str(body.get("description") or "error")


def start_tunnel(binary: Path, minutes: int, target: str = "dashboard") -> str:
    proc = subprocess.Popen(
        [str(binary), "tunnel", "--url", "http://127.0.0.1:8080"],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )
    PID_FILE.parent.mkdir(parents=True, exist_ok=True)
    PID_FILE.write_text(str(proc.pid), encoding="utf-8")
    public = ""
    deadline = time.time() + 40
    assert proc.stdout is not None
    while time.time() < deadline:
        line = proc.stdout.readline()
        if not line:
            if proc.poll() is not None:
                break
            time.sleep(0.1)
            continue
        found = parse_trycloudflare(line)
        if found:
            public = found
            break
    if not public:
        proc.terminate()
        raise SystemExit("cloudflared did not print a trycloudflare address")
    sent = _send(public, target=target)
    # Detach the closer so this command can return. The token is not in the command.
    subprocess.Popen(
        ["bash", "-c", f"sleep {minutes}; kill {proc.pid} >/dev/null 2>&1 || true; rm -f {PID_FILE}"],
        start_new_session=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    endpoint = f"{public}/mcp/" if target == "mcp" else public
    print(f"tunnel={endpoint} send={sent} minutes={minutes} target={target}")
    return endpoint


def main() -> int:
    minutes = int(os.environ.get("SHARE_MINUTES") or "60")
    target = "mcp" if "--mcp" in sys.argv or os.environ.get("SHARE_TARGET") == "mcp" else "dashboard"
    binary = ensure_cloudflared()
    start_tunnel(binary, minutes, target=target)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
