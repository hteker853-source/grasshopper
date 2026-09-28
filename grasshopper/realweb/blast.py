"""Per-run blast radius: files, domains, time, and dollars."""

from __future__ import annotations

import json
import shutil
from pathlib import Path


def runner_label() -> str:
    if shutil.which("docker"):
        return "docker mevcut; bu koşu yerel (docker isteğe bağlı)"
    return "docker yok, uyarıyla yerel"


def write_blast(
    path: Path,
    *,
    files: list[str],
    domains: list[str],
    seconds: float,
    cost_usd: float,
    runner: str,
) -> None:
    payload = {
        "files_touched": list(files),
        "domains": list(domains),
        "duration_sec": round(float(seconds), 3),
        "cost_usd": float(cost_usd),
        "runner": runner,
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
