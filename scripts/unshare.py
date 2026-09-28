#!/usr/bin/env python3
"""Stop the cloudflared process recorded by make share."""

from __future__ import annotations

import os
import signal
from pathlib import Path

PID_FILE = Path(__file__).resolve().parents[1] / "runs" / "cloudflared.pid"


def main() -> int:
    if not PID_FILE.is_file():
        print("no tunnel pid")
        return 0
    pid = int(PID_FILE.read_text(encoding="utf-8").strip())
    try:
        os.kill(pid, signal.SIGTERM)
        print(f"stopped {pid}")
    except ProcessLookupError:
        print("tunnel already stopped")
    PID_FILE.unlink(missing_ok=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
