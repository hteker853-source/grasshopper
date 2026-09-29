"""Choose a runner from SANDBOX_RUNNER. The default is local."""

from __future__ import annotations

import os
from pathlib import Path

from grasshopper.sandbox_runner.audit import AuditLog
from grasshopper.sandbox_runner.docker import DockerRunner
from grasshopper.sandbox_runner.local import LocalRunner
from grasshopper.sandbox_runner.vultr import VultrRunner


def audit_path(settings) -> Path:
    return Path(settings.runs_dir) / "sandbox-audit.log"


def build_runner(settings):
    audit = AuditLog(audit_path(settings))
    local = LocalRunner(audit)
    kind = (os.environ.get("SANDBOX_RUNNER") or "local").strip().lower()
    if kind == "docker":
        network = (os.environ.get("GRASSHOPPER_DOCKER_NETWORK") or "").strip() or None
        return DockerRunner(audit, local, network=network)
    if kind == "vultr":
        return VultrRunner(
            audit,
            local,
            api_key=os.environ.get("VULTR_API_KEY", ""),
            api_base=os.environ.get("VULTR_API_BASE") or "https://api.vultr.com",
        )
    return local


def note_browser_action(settings, action: str, result: str) -> None:
    """Record a browser action without launching a second container."""
    import shutil

    from grasshopper.sandbox_runner.docker import DockerRunner
    from grasshopper.sandbox_runner.vultr import VultrRunner

    runner = build_runner(settings)
    container = "local"
    if isinstance(runner, DockerRunner):
        container = "docker" if shutil.which("docker") else "local"
    elif isinstance(runner, VultrRunner) and runner.api is not None:
        container = "vultr"
    elif isinstance(runner, VultrRunner):
        container = "vultr-mock"
    runner.audit.write(action, container, result)


def runner_status(path: Path) -> dict:
    rows = AuditLog(path).read()
    if not rows:
        return {"name": "local", "isolated": False, "label": ""}
    container = str(rows[-1].get("container") or "local")
    isolated = container == "docker" or container.startswith("vultr:")
    return {
        "name": container,
        "isolated": isolated,
        "label": "isolated execution" if isolated else "",
    }
