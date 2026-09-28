#!/usr/bin/env python3
"""Run S3 slowly on real Chromium and share the dashboard link.

LIVE_STEP_PAUSE_SEC is 1.2 so a person can watch each step. The server
stays on 127.0.0.1. The share step sends the token only to Telegram.
"""

from __future__ import annotations

import os
import subprocess
import sys
import time
from pathlib import Path

import httpx

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from grasshopper.demo_scenarios import S3


def _env_value(key: str) -> str:
    for raw in (ROOT / ".env").read_text(encoding="utf-8").splitlines():
        if raw.startswith(key + "="):
            return raw.split("=", 1)[1].strip().strip('"').strip("'")
    return ""


def main() -> int:
    token = _env_value("API_TOKEN") or "live-demo"
    env = os.environ.copy()
    env.update({
        "BROWSER_DRIVER": "playwright",
        "LIVE_STEP_PAUSE_SEC": "1.2",
        "GRASSHOPPER_EMBED_SANDBOX": "1",
        "API_TOKEN": token,
    })
    log = (ROOT / "runs" / "live-demo.log").open("w", encoding="utf-8")
    (ROOT / "runs").mkdir(parents=True, exist_ok=True)
    proc = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "grasshopper.main:app", "--host", "127.0.0.1", "--port", "8080"],
        cwd=ROOT,
        env=env,
        stdout=log,
        stderr=subprocess.STDOUT,
    )
    try:
        deadline = time.time() + 40
        while time.time() < deadline:
            try:
                httpx.get("http://127.0.0.1:8080/health", timeout=0.4)
                break
            except Exception:
                time.sleep(0.2)
        else:
            raise SystemExit("dashboard did not start")
        subprocess.run([sys.executable, str(ROOT / "scripts" / "share.py")], check=True, cwd=ROOT)
        response = httpx.post(
            "http://127.0.0.1:8080/api/tasks",
            headers={"Authorization": f"Bearer {token}"},
            json={"text": S3},
            timeout=20,
        )
        response.raise_for_status()
        task_id = response.json()["id"]
        deadline = time.time() + 240
        status = ""
        while time.time() < deadline:
            current = httpx.get(
                f"http://127.0.0.1:8080/api/tasks/{task_id}",
                headers={"Authorization": f"Bearer {token}"},
                timeout=10,
            )
            status = current.json().get("status", "")
            if status in {"done", "failed", "waiting_approval", "cancelled"}:
                break
            time.sleep(0.5)
        print(f"s3={status}")
        return 0 if status == "done" else 1
    finally:
        proc.terminate()
        try:
            proc.wait(timeout=8)
        except subprocess.TimeoutExpired:
            proc.kill()
        log.close()


if __name__ == "__main__":
    raise SystemExit(main())
