"""Run a command on this machine."""

from __future__ import annotations

import subprocess

from grasshopper.sandbox_runner.audit import AuditLog
from grasshopper.sandbox_runner.base import RunnerResult


class LocalRunner:
    name = "local"

    def __init__(self, audit: AuditLog):
        self.audit = audit

    def run(self, action: str, command: list[str], *, timeout: int = 30) -> RunnerResult:
        try:
            completed = subprocess.run(command, capture_output=True, text=True, timeout=timeout, check=False)
        except subprocess.TimeoutExpired:
            self.audit.write(action, self.name, "timeout")
            return RunnerResult(False, self.name, "timeout", False)
        detail = (completed.stdout or completed.stderr or "").strip()
        ok = completed.returncode == 0
        self.audit.write(action, self.name, detail or f"exit {completed.returncode}")
        return RunnerResult(ok, self.name, detail or f"exit {completed.returncode}", False)
