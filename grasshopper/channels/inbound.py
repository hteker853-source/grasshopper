"""One normalizer so web, Telegram, WhatsApp, Alexa, and the CLI agree."""

from __future__ import annotations

from grasshopper.schemas import Task


def task_from_channel(text: str, channel: str) -> Task:
    cleaned = " ".join((text or "").split())
    return Task.create(cleaned, channel=channel)
