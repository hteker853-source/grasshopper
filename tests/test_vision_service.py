"""Click targets and page change, locally and through the vision HTTP service."""

from __future__ import annotations

import os
import socket
import threading
import time
from pathlib import Path

import httpx
import uvicorn
from PIL import Image, ImageDraw

from grasshopper.browser.vision import change_percent, detect_regions


def _frames(folder: Path) -> tuple[Path, Path]:
    before = folder / "login.png"
    image = Image.new("RGB", (400, 240), (240, 240, 240))
    draw = ImageDraw.Draw(image)
    draw.rectangle((40, 80, 200, 130), outline=(10, 10, 10), width=3)
    draw.rectangle((40, 150, 200, 200), fill=(20, 80, 40))
    image.save(before)
    after = folder / "after.png"
    Image.new("RGB", (400, 240), (20, 20, 80)).save(after)
    return before, after


def _start_service() -> str:
    sock = socket.socket()
    sock.bind(("127.0.0.1", 0))
    port = sock.getsockname()[1]
    sock.close()
    config = uvicorn.Config("vision_service.app:app", host="127.0.0.1", port=port, log_level="warning")
    server = uvicorn.Server(config)
    threading.Thread(target=server.run, daemon=True).start()
    deadline = time.time() + 15
    url = f"http://127.0.0.1:{port}"
    while time.time() < deadline:
        try:
            if httpx.get(url + "/health", timeout=0.3).json().get("ok"):
                return url
        except Exception:
            time.sleep(0.05)
    raise RuntimeError("vision service did not start")


def test_service_detects_a_target_and_a_page_change(tmp_path, monkeypatch):
    before, after = _frames(tmp_path)
    url = _start_service()
    monkeypatch.setenv("VISION_SERVICE_URL", url)
    regions = detect_regions(before, tmp_path / "remote-annotated.png")
    assert regions
    assert (tmp_path / "remote-annotated.png").stat().st_size > 0
    assert change_percent(before, after) > 10
    health = httpx.get(url + "/health", timeout=2).json()
    assert health["service"] == "vision"
    monkeypatch.delenv("VISION_SERVICE_URL", raising=False)
    os.environ.pop("VISION_SERVICE_URL", None)
    local = detect_regions(before, tmp_path / "local-annotated.png")
    assert local
    assert change_percent(before, after) > 10


def test_empty_vision_url_stays_local(tmp_path, monkeypatch):
    monkeypatch.delenv("VISION_SERVICE_URL", raising=False)
    before, after = _frames(tmp_path)
    assert os.environ.get("VISION_SERVICE_URL", "") == ""
    assert detect_regions(before, tmp_path / "annotated.png")
    assert change_percent(before, after) > 10
