"""Regex scheduler for Turkish and English phrases. No third-party date parser."""

from __future__ import annotations

import re
from datetime import datetime, timedelta, timezone

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger

# (pattern, handler name)
_RELATIVE = re.compile(
    r"(?:in\s+)?(\d+)\s*(second|seconds|sec|saniye|sn|minute|minutes|min|dakika|dk|hour|hours|saat)\s*(?:later|sonra)?",
    re.I,
)
_DAILY = re.compile(
    r"(?:every\s+day|her\s+g[\u00fc]n|daily)\s*(?:at\s*)?(\d{1,2})[:.](\d{2})(?:['’](?:da|de|ta|te))?",
    re.I,
)
_TOMORROW = re.compile(
    r"(?:tomorrow|yar[\u0131i]n)\s*(?:at\s*)?(\d{1,2})[:.](\d{2})(?:['’](?:da|de|ta|te))?",
    re.I,
)
_TONIGHT = re.compile(
    r"(?:tonight|bu\s+gece|this\s+evening)\s*(?:at\s*)?(\d{1,2})[:.](\d{2})(?:['’](?:da|de|ta|te))?",
    re.I,
)


class ParsedWhen:
    def __init__(self, scheduled_at: datetime | None = None, cron: str | None = None, remaining: str = ""):
        self.scheduled_at = scheduled_at
        self.cron = cron
        self.remaining = remaining


def parse_when(text: str, now: datetime | None = None) -> ParsedWhen:
    moment = now or datetime.now(timezone.utc)
    if moment.tzinfo is None:
        moment = moment.replace(tzinfo=timezone.utc)
    original = text.strip()

    match = _DAILY.search(original)
    if match:
        hour, minute = int(match.group(1)), int(match.group(2))
        cron = f"{minute} {hour} * * *"
        target = moment.replace(hour=hour, minute=minute, second=0, microsecond=0)
        if target <= moment:
            target = target + timedelta(days=1)
        remaining = (original[: match.start()] + original[match.end() :]).strip(" ,.-")
        return ParsedWhen(target, cron, remaining or original)

    match = _TOMORROW.search(original)
    if match:
        hour, minute = int(match.group(1)), int(match.group(2))
        target = (moment + timedelta(days=1)).replace(hour=hour, minute=minute, second=0, microsecond=0)
        remaining = (original[: match.start()] + original[match.end() :]).strip(" ,.-")
        return ParsedWhen(target, None, remaining or original)

    match = _TONIGHT.search(original)
    if match:
        hour, minute = int(match.group(1)), int(match.group(2))
        target = moment.replace(hour=hour, minute=minute, second=0, microsecond=0)
        if target <= moment:
            target = target + timedelta(days=1)
        remaining = (original[: match.start()] + original[match.end() :]).strip(" ,.-")
        return ParsedWhen(target, None, remaining or original)

    match = _RELATIVE.search(original)
    if match:
        amount = int(match.group(1))
        unit = match.group(2).lower()
        if unit in {"second", "seconds", "sec", "saniye", "sn"}:
            delta = timedelta(seconds=amount)
        elif unit in {"minute", "minutes", "min", "dakika", "dk"}:
            delta = timedelta(minutes=amount)
        else:
            delta = timedelta(hours=amount)
        remaining = (original[: match.start()] + original[match.end() :]).strip(" ,.-")
        return ParsedWhen(moment + delta, None, remaining or original)

    return ParsedWhen(None, None, original)


class Scheduler:
    """Polls the queue. Cron tasks are re-queued by the orchestrator after a successful run."""

    def __init__(self, on_tick):
        self.on_tick = on_tick
        self.scheduler = AsyncIOScheduler()

    def start(self) -> None:
        if self.scheduler.running:
            return
        self.scheduler.add_job(self.on_tick, IntervalTrigger(seconds=1), id="grasshopper-tick", replace_existing=True)
        self.scheduler.start()

    def shutdown(self) -> None:
        if self.scheduler.running:
            self.scheduler.shutdown(wait=False)
