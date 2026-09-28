"""Start the fake provider app on 127.0.0.1 and wait until it answers."""

from __future__ import annotations

import socket
import threading
import time

import httpx
import uvicorn

from tests.fakes.app import Capture, create_app


def _free_port() -> int:
    sock = socket.socket()
    sock.bind(("127.0.0.1", 0))
    port = sock.getsockname()[1]
    sock.close()
    return port


def start_fakes() -> tuple[str, Capture]:
    capture = Capture()
    port = _free_port()
    config = uvicorn.Config(create_app(capture), host="127.0.0.1", port=port, log_level="warning")
    server = uvicorn.Server(config)
    thread = threading.Thread(target=server.run, daemon=True)
    thread.start()
    deadline = time.time() + 15
    url = f"http://127.0.0.1:{port}"
    while time.time() < deadline:
        try:
            httpx.post(url + "/search", json={"query": "ping"}, timeout=0.3)
            return url, capture
        except Exception:
            time.sleep(0.05)
    raise RuntimeError("fake provider server did not start")
