"""Shared result for every runner."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class RunnerResult:
    ok: bool
    container: str
    detail: str
    isolated: bool
