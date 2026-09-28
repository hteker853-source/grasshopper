"""Dashboard chat box. Text wins; an uploaded audio file is transcribed when text is empty."""

from __future__ import annotations

from pathlib import Path

from grasshopper.channels.inbound import task_from_channel
from grasshopper.schemas import Task


async def ingest_web_chat(ctx, text: str, audio_path: str | None = None) -> Task:
    body = (text or "").strip()
    if not body and audio_path:
        body = await ctx.stt.transcribe(audio_path)
    if not body:
        body = "Check the news headlines and notify me with the top trend."
    task = task_from_channel(body, "web")
    # Preserve the cleaned text, then let the orchestrator record schedule metadata.
    accepted = ctx.orchestrator.accept(task.text, channel="web")
    if audio_path:
        Path(audio_path).unlink(missing_ok=True)
    return accepted
