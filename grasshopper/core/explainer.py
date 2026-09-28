"""JSONL explain-why log for a single run."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from grasshopper.schemas import ExplainEvent


class Explainer:
    def __init__(self, run_dir: Path):
        self.path = Path(run_dir) / "explain.jsonl"
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def log(self, event: ExplainEvent) -> None:
        payload = event.model_dump()
        if not payload.get("ts"):
            payload["ts"] = datetime.now(timezone.utc).isoformat()
        with self.path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(payload) + "\n")

    def read(self) -> list[dict]:
        if not self.path.exists():
            return []
        lines = []
        for line in self.path.read_text(encoding="utf-8").splitlines():
            if line.strip():
                lines.append(json.loads(line))
        return lines
