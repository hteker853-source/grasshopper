"""Latest browser frame for a run. Used by the dashboard and Telegram."""

from __future__ import annotations

import re
from pathlib import Path

from grasshopper.schemas import TaskStatus

_RUN_ID = re.compile(r"[A-Za-z0-9_-]+")
_ACTIVE = (TaskStatus.running, TaskStatus.planning, TaskStatus.waiting_approval)


def latest_screenshot(runs_dir: Path, run_id: str) -> Path | None:
    """Newest PNG in a run directory, or None. Rejects ids that could escape the folder."""
    if not run_id or _RUN_ID.fullmatch(run_id) is None:
        return None
    root = runs_dir.resolve()
    folder = (root / run_id).resolve()
    if folder != root and root not in folder.parents:
        return None
    if not folder.is_dir():
        return None
    shots = [path for path in folder.glob("*.png") if path.is_file()]
    if not shots:
        return None
    return max(shots, key=lambda path: path.stat().st_mtime)


def running_screenshot(ctx) -> Path | None:
    """Latest frame of the task that is planning, running, or waiting for approval."""
    tasks = ctx.queue.list_recent(40)
    for status in _ACTIVE:
        for task in tasks:
            if task.status != status or not task.run_id:
                continue
            shot = latest_screenshot(ctx.settings.runs_dir, task.run_id)
            if shot is not None:
                return shot
    return None
