"""Live frame on the run page, /canli, and approval photos."""

from __future__ import annotations

import asyncio
import os
from pathlib import Path

import pytest
from fastapi import HTTPException
from jinja2 import Environment, FileSystemLoader

from grasshopper.channels.telegram_bot import build_telegram_application, deliver_canli
from grasshopper.providers.notify_telegram import TelegramNotifier
from grasshopper.publish.live import latest_screenshot, running_screenshot
from grasshopper.schemas import TaskStatus


def test_live_png_is_the_newest_frame(ctx):
    from grasshopper.main import live_png

    run_id = "run_live_frame"
    folder = ctx.settings.runs_dir / run_id
    folder.mkdir(parents=True)
    older = folder / "a.png"
    newer = folder / "b.png"
    older.write_bytes(b"old")
    newer.write_bytes(b"new")
    os.utime(older, (1_700_000_000, 1_700_000_000))
    os.utime(newer, (1_700_000_100, 1_700_000_100))
    response = live_png(run_id)
    assert Path(response.path) == newer
    assert response.headers["cache-control"] == "no-store"
    assert latest_screenshot(ctx.settings.runs_dir, "../escape") is None
    with pytest.raises(HTTPException) as raised:
        live_png("../escape")
    assert raised.value.status_code == 404


def test_run_page_reloads_the_frame_every_second():
    env = Environment(loader=FileSystemLoader("grasshopper/ui/templates"))
    html = env.get_template("run.html").render(run_id="run_abc", events=[], summary="")
    assert 'id="live-shot"' in html
    assert "/runs/run_abc/live.png?t=" in html
    assert "setInterval(refreshLive, 700)" in html
    assert 'id="canli"' in html


def test_browser_reloads_live_frame(tmp_path):
    from playwright.sync_api import sync_playwright

    env = Environment(loader=FileSystemLoader("grasshopper/ui/templates"))
    html = env.get_template("run.html").render(run_id="run_browser", events=[], summary="")
    page_path = tmp_path / "run.html"
    page_path.write_text(html, encoding="utf-8")
    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(page_path.as_uri())
        page.wait_for_timeout(1100)
        src = page.locator("#live-shot").get_attribute("src")
        browser.close()
    assert src is not None and "live.png?t=" in src


def test_canli_sends_only_to_the_allowed_user(ctx):
    previous = ctx.settings.telegram_allowed_user_id
    ctx.settings.telegram_allowed_user_id = "4242"
    run_id = "run_canli"
    folder = ctx.settings.runs_dir / run_id
    folder.mkdir(parents=True, exist_ok=True)
    shot = folder / "frame.png"
    shot.write_bytes(b"\x89PNG\r\n")
    task = ctx.orchestrator.accept("show the live frame", channel="test")
    ctx.queue.update_status(task.id, TaskStatus.running, run_id=run_id)
    photos: list[Path] = []
    texts: list[str] = []

    async def send_photo(path: Path):
        photos.append(path)

    async def send_text(text: str):
        texts.append(text)

    try:
        assert running_screenshot(ctx) == shot
        assert asyncio.run(deliver_canli(ctx, "4242", send_photo=send_photo, send_text=send_text)) == "photo"
        assert photos == [shot]
        assert asyncio.run(deliver_canli(ctx, "9999", send_photo=send_photo, send_text=send_text)) == "ignored"
        assert photos == [shot]
        assert texts == []
    finally:
        ctx.settings.telegram_allowed_user_id = previous
        ctx.queue.update_status(task.id, TaskStatus.cancelled)


def test_canli_command_is_registered():
    class Settings:
        telegram_bot_token = "100000:TESTTOKEN"
        telegram_allowed_user_id = "7"

    class Ctx:
        settings = Settings()

    application = build_telegram_application(Ctx())
    commands = set()
    for handlers in application.handlers.values():
        for handler in handlers:
            commands.update(getattr(handler, "commands", ()) or ())
    assert "canli" in commands


def test_approval_photo_goes_only_to_the_allowed_chat(tmp_path, monkeypatch):
    image = tmp_path / "now.png"
    image.write_bytes(b"\x89PNG\r\n")
    calls = []

    class Dummy:
        def __init__(self, *args, **kwargs):
            pass

        async def __aenter__(self):
            return self

        async def __aexit__(self, *args):
            return None

        async def post(self, url, json=None, data=None, files=None):
            calls.append({"url": str(url), "json": json, "data": data, "files": files})

            class Response:
                status_code = 200

            return Response()

    monkeypatch.setattr("grasshopper.providers.notify_telegram.httpx.AsyncClient", Dummy)
    notifier = TelegramNotifier("100000:TESTTOKEN", "6588")
    asyncio.run(notifier.notify(
        "Approval needed: pay",
        kind="approval",
        payload={"approval_id": "ap_1", "screenshot": str(image), "task_id": "task_1"},
    ))
    assert len(calls) == 1
    assert calls[0]["url"].endswith("/sendPhoto")
    assert calls[0]["data"]["chat_id"] == "6588"
    assert "approve:ap_1" in calls[0]["data"]["reply_markup"]
    assert "reject:ap_1" in calls[0]["data"]["reply_markup"]
    assert calls[0]["files"]["photo"][0] == "now.png"
    calls.clear()
    asyncio.run(notifier.notify("done", kind="done", payload={"task_id": "task_1"}))
    assert calls[0]["url"].endswith("/sendMessage")
    assert calls[0]["json"]["chat_id"] == "6588"
    assert calls[0]["files"] is None
