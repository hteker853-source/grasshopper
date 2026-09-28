"""Video recording arguments and the demo edit decisions."""

from __future__ import annotations

import asyncio
import shutil
import subprocess

from grasshopper.browser.controller import PlaywrightDriver
from grasshopper.publish.demo_edit import probe_duration, side_by_side_filter, speed_factor, under_telegram_limit


def test_playwright_driver_records_720p(tmp_path, monkeypatch):
    captured = {}

    class Page:
        pass

    class Context:
        pages = [Page()]

        async def close(self):
            return None

    class Chromium:
        async def launch_persistent_context(self, **kwargs):
            captured.update(kwargs)
            return Context()

    class PW:
        chromium = Chromium()

        async def stop(self):
            return None

    class Manager:
        async def start(self):
            return PW()

    monkeypatch.setattr("playwright.async_api.async_playwright", lambda: Manager())
    video_dir = tmp_path / "video"
    driver = PlaywrightDriver(tmp_path / "profile", video_dir)
    asyncio.run(driver.start())
    assert captured["record_video_dir"] == str(video_dir)
    assert captured["record_video_size"] == {"width": 1280, "height": 720}
    assert captured["viewport"] == {"width": 1280, "height": 720}
    assert video_dir.is_dir()


def test_titles_drop_without_a_font():
    graph, label = side_by_side_filter("S3 old listings", None, left_pad=1.5, right_pad=0)
    assert label == "stacked"
    assert "drawtext" not in graph
    assert "stop_duration=1.500" in graph
    titled, titled_label = side_by_side_filter("S6 approved payment", "/usr/share/fonts/DejaVuSans.ttf")
    assert titled_label == "vout"
    assert "S6 approved payment" in titled
    assert "fontfile=/usr/share/fonts/DejaVuSans.ttf" in titled


def test_long_demo_speeds_up_and_telegram_cap():
    assert speed_factor(90) is None
    assert speed_factor(180) is None
    factor = speed_factor(358)
    assert factor is not None and abs(factor - (358 / 179)) < 0.001
    assert under_telegram_limit(49 * 1024 * 1024)
    assert not under_telegram_limit(50 * 1024 * 1024)


def test_probe_duration_of_a_one_second_clip(tmp_path):
    assert shutil.which("ffmpeg") and shutil.which("ffprobe")
    target = tmp_path / "one.mp4"
    subprocess.run(
        [
            "ffmpeg", "-y", "-f", "lavfi", "-i", "color=c=black:s=320x180:d=1",
            "-c:v", "libx264", "-pix_fmt", "yuv420p", str(target),
        ],
        check=True,
        capture_output=True,
    )
    assert 0.5 < probe_duration(target) < 1.5
