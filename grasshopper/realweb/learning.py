"""First-run call count and the replay that should spend zero model calls."""

from __future__ import annotations

import json
from pathlib import Path


class LearningStore:
    def __init__(self, path: Path):
        self.path = Path(path)
        self.data = {"scenarios": {}}
        if self.path.is_file():
            try:
                loaded = json.loads(self.path.read_text(encoding="utf-8"))
            except json.JSONDecodeError:
                loaded = {}
            if isinstance(loaded, dict) and isinstance(loaded.get("scenarios"), dict):
                self.data = loaded

    def row(self, scenario_id: str) -> dict | None:
        return self.data["scenarios"].get(scenario_id)

    def save_first(self, scenario_id: str, actions: list[dict], calls: int) -> None:
        row = self.data["scenarios"].setdefault(scenario_id, {})
        if "first_calls" not in row:
            row["first_calls"] = calls
        row["actions"] = actions
        self._write()

    def save_replay(self, scenario_id: str, calls: int) -> None:
        row = self.data["scenarios"].setdefault(scenario_id, {})
        if "second_calls" not in row:
            row["second_calls"] = calls
        self._write()

    def panel(self) -> dict:
        scenarios = self.data.get("scenarios") or {}
        picked = None
        for key, row in scenarios.items():
            if "first_calls" in row and "second_calls" in row:
                picked = (key, row)
                break
        if picked is None:
            return {"scenario": "", "first_calls": None, "second_calls": None, "label": "ölçülmedi"}
        key, row = picked
        return {
            "scenario": key,
            "first_calls": row.get("first_calls"),
            "second_calls": row.get("second_calls"),
            "label": "ölçüldü",
        }

    def _write(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(json.dumps(self.data, indent=2), encoding="utf-8")
