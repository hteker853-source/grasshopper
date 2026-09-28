"""Offline speech-to-text. A sibling .txt file wins; otherwise a fixed sample."""

from __future__ import annotations

from pathlib import Path

SAMPLE = "Enable research mode and research solar panels."


class MockSTT:
    name = "mock"

    def configured(self) -> bool:
        return True

    async def transcribe(self, audio_path: str) -> str:
        path = Path(audio_path)
        sibling = path.with_suffix(".txt")
        if sibling.exists():
            return sibling.read_text(encoding="utf-8").strip()
        return SAMPLE
