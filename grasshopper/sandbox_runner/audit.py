"""One JSON line per runner action: what ran, in which container, and the result."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path


class AuditLog:
    def __init__(self, path: Path):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def write(self, action: str, container: str, result: str) -> None:
        row = {
            "ts": datetime.now(timezone.utc).isoformat(),
            "action": action,
            "container": container,
            "result": result[:500],
        }
        with self.path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(row) + "\n")

    def read(self) -> list[dict]:
        if not self.path.exists():
            return []
        rows = []
        for line in self.path.read_text(encoding="utf-8").splitlines():
            if line.strip():
                rows.append(json.loads(line))
        return rows
