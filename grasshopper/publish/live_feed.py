"""About 1.5 frames per second while a real Chromium task is running."""

from __future__ import annotations

import asyncio
import json
import shutil
from pathlib import Path

LIVE_INTERVAL_SEC = 1 / 1.5


def status_path(runs_dir: Path) -> Path:
    return Path(runs_dir) / "live_status.json"


def frame_path(runs_dir: Path) -> Path:
    return Path(runs_dir) / "live_frame.png"


def read_status(runs_dir: Path) -> dict:
    path = status_path(runs_dir)
    if not path.is_file():
        return {"active": False, "url": "", "goal": "", "run_id": "", "label": "waiting"}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        data = {}
    active = bool(data.get("active"))
    return {
        "active": active,
        "url": str(data.get("url") or ""),
        "goal": str(data.get("goal") or ""),
        "run_id": str(data.get("run_id") or ""),
        "label": "LIVE" if active else "waiting",
    }


def publish_frame(runs_dir: Path, *, run_id: str, source: Path, url: str, goal: str, active: bool) -> None:
    """Copy the newest frame and write the caption. Never includes a token."""
    runs_dir = Path(runs_dir)
    runs_dir.mkdir(parents=True, exist_ok=True)
    target = frame_path(runs_dir)
    if source.is_file() and source.resolve() != target.resolve():
        shutil.copyfile(source, target)
    status_path(runs_dir).write_text(
        json.dumps({"run_id": run_id, "url": url, "goal": goal, "active": active}, ensure_ascii=False),
        encoding="utf-8",
    )


async def capture_live_frames(driver, dest: Path, runs_dir: Path, run_id: str, goal_for, stop: asyncio.Event) -> None:
    """Screenshot, then wait. The first frame is immediate; later ones are ~1.5 fps."""
    while not stop.is_set():
        try:
            await driver.screenshot(dest)
            publish_frame(
                runs_dir,
                run_id=run_id,
                source=dest,
                url=getattr(driver, "url", "") or "",
                goal=goal_for(),
                active=True,
            )
        except Exception:
            pass
        try:
            await asyncio.wait_for(stop.wait(), timeout=LIVE_INTERVAL_SEC)
        except asyncio.TimeoutError:
            continue
