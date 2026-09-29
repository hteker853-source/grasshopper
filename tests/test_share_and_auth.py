"""Dashboard token gate, live captions, and tunnel URL parsing."""

from __future__ import annotations

import asyncio
import logging
from pathlib import Path

from fastapi.testclient import TestClient

from grasshopper.browser.controller import BrowserController
from grasshopper.main import app
from grasshopper.publish.live_feed import LIVE_INTERVAL_SEC, publish_frame, read_status
from scripts.share import cloudflared_name, parse_trycloudflare


def test_pages_require_the_token_and_a_query_sets_the_cookie(caplog):
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpx2").setLevel(logging.WARNING)
    with TestClient(app) as client, caplog.at_level(logging.DEBUG):
        assert client.get("/health").status_code == 200
        assert client.get("/").status_code == 401
        assert client.get("/api/overview").status_code == 401
        denied = client.get("/?token=not-the-token")
        assert denied.status_code == 401
        assert "set-cookie" not in denied.headers
        with caplog.at_level(logging.DEBUG):
            entered = client.get("/?token=test-token", follow_redirects=False)
        assert entered.status_code == 303
        assert "token" not in entered.headers["location"]
        assert "test-token" not in caplog.text
        assert client.get("/").status_code == 200
        assert client.get("/api/overview").status_code == 200
        assert "LIVE" in client.get("/").text
        assert "waiting" in client.get("/").text


def test_live_caption_shows_the_goal_and_waits_when_idle(ctx, tmp_path):
    idle = read_status(ctx.settings.runs_dir)
    assert idle["label"] == "waiting"
    assert idle["active"] is False
    frame = tmp_path / "shot.png"
    frame.write_bytes(b"\x89PNG\r\n")
    publish_frame(ctx.settings.runs_dir, run_id="run_live", source=frame, url="http://127.0.0.1/shop", goal="Log into the shop", active=True)
    current = read_status(ctx.settings.runs_dir)
    assert current["label"] == "LIVE"
    assert current["url"] == "http://127.0.0.1/shop"
    assert current["goal"] == "Log into the shop"
    publish_frame(ctx.settings.runs_dir, run_id="run_live", source=frame, url="http://127.0.0.1/shop", goal="Log into the shop", active=False)
    assert read_status(ctx.settings.runs_dir)["label"] == "waiting"
    html = Path("grasshopper/ui/templates/dashboard.html").read_text(encoding="utf-8")
    assert 'id="canli"' in html and "canli-meta" in html


def test_chromium_capture_is_about_one_and_a_half_frames_per_second(tmp_path):
    assert abs(LIVE_INTERVAL_SEC - (1 / 1.5)) < 1e-9

    class Driver:
        def __init__(self):
            self.n = 0
            self.url = "http://127.0.0.1/shop"

        async def screenshot(self, path):
            self.n += 1
            Path(path).write_bytes(b"png")

    driver = Driver()
    stop = asyncio.Event()
    controller = BrowserController.__new__(BrowserController)
    controller.live_goal = "Open the listings"

    async def goal():
        return controller.live_goal

    from grasshopper.publish.live_feed import capture_live_frames

    async def run():
        task = asyncio.create_task(
            capture_live_frames(driver, tmp_path / "live_frame.png", tmp_path, "run_x", lambda: controller.live_goal, stop)
        )
        await asyncio.sleep(1.45)
        stop.set()
        await task

    asyncio.run(run())
    assert driver.n >= 2
    status = read_status(tmp_path)
    assert status["goal"] == "Open the listings"
    assert status["active"] is True


def test_trycloudflare_address_is_parsed_from_fake_output():
    sample = "INF +--------------------------------------------------------------------------------------------+\nINF 2026-09-28 Your quick Tunnel has been created! Visit it at:\nINF https://demo-hop-1234.trycloudflare.com\n"
    assert parse_trycloudflare(sample) == "https://demo-hop-1234.trycloudflare.com"
    assert parse_trycloudflare("no tunnel yet") is None
    assert cloudflared_name("x86_64") == "cloudflared-linux-amd64"
    assert cloudflared_name("aarch64") == "cloudflared-linux-arm64"
