"""Run a command in a resource-limited container. Missing Docker falls back to local."""

from __future__ import annotations

import logging
import shutil
import subprocess

from grasshopper.sandbox_runner.audit import AuditLog
from grasshopper.sandbox_runner.base import RunnerResult
from grasshopper.sandbox_runner.local import LocalRunner

log = logging.getLogger("grasshopper.sandbox")


def docker_argv(
    command: list[str],
    *,
    name: str,
    memory: str = "256m",
    cpus: str = "0.5",
    network: str | None = None,
) -> list[str]:
    """argv for docker run. network None means no network. The name is the kill switch."""
    return [
        "docker", "run", "--rm",
        "--name", name,
        "--memory", memory,
        "--cpus", cpus,
        "--network", network or "none",
        "python:3.12-slim",
        *command,
    ]


class DockerRunner:
    name = "docker"

    def __init__(self, audit: AuditLog, local: LocalRunner, *, timeout: int = 30, network: str | None = None):
        self.audit = audit
        self.local = local
        self.timeout = timeout
        self.network = network

    def run(self, action: str, command: list[str], *, timeout: int | None = None) -> RunnerResult:
        if shutil.which("docker") is None:
            log.warning("Docker is not installed. Falling back to the local runner.")
            local = self.local.run(action, command, timeout=timeout or self.timeout)
            self.audit.write(action, "local", "docker missing; fell back to local")
            return RunnerResult(local.ok, "local", local.detail, False)
        limit = timeout or self.timeout
        name = "grasshopper-job"
        argv = docker_argv(command, name=name, network=self.network)
        try:
            completed = subprocess.run(argv, capture_output=True, text=True, timeout=limit, check=False)
        except subprocess.TimeoutExpired:
            subprocess.run(["docker", "kill", name], capture_output=True, check=False)
            self.audit.write(action, self.name, "timeout; killed")
            return RunnerResult(False, self.name, "timeout; killed", True)
        detail = (completed.stdout or completed.stderr or "").strip() or f"exit {completed.returncode}"
        ok = completed.returncode == 0
        self.audit.write(action, self.name, detail)
        return RunnerResult(ok, self.name, detail, ok)
