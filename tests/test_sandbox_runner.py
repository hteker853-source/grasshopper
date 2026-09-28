"""Local, Docker, and Vultr runners, plus the isolated badge."""

from __future__ import annotations

import logging
import shutil
import socket
import threading
import time
from pathlib import Path

import httpx
import uvicorn

from grasshopper.sandbox_runner.audit import AuditLog
from grasshopper.sandbox_runner.docker import DockerRunner, docker_argv
from grasshopper.sandbox_runner.factory import runner_status
from grasshopper.sandbox_runner.local import LocalRunner
from grasshopper.sandbox_runner.vultr import VultrRunner
from tests.fakes.vultr_app import create_vultr_app


def test_local_runner_logs_the_action_and_its_output(tmp_path):
    audit = AuditLog(tmp_path / "audit.log")
    result = LocalRunner(audit).run("echo", ["echo", "hello-runner"])
    assert result.ok
    assert result.container == "local"
    assert result.isolated is False
    assert result.detail == "hello-runner"
    rows = audit.read()
    assert rows[-1]["action"] == "echo"
    assert rows[-1]["container"] == "local"
    assert rows[-1]["result"] == "hello-runner"


def test_docker_command_is_limited_and_named_for_the_kill_switch():
    argv = docker_argv(["python", "-c", "print(1)"], name="grasshopper-job", memory="256m", cpus="0.5")
    assert argv[0:3] == ["docker", "run", "--rm"]
    assert argv[argv.index("--memory") + 1] == "256m"
    assert argv[argv.index("--cpus") + 1] == "0.5"
    assert argv[argv.index("--network") + 1] == "none"
    assert argv[argv.index("--name") + 1] == "grasshopper-job"
    allowed = docker_argv(["python"], name="job", network="sandbox-net")
    assert allowed[allowed.index("--network") + 1] == "sandbox-net"


def test_missing_docker_falls_back_to_local(tmp_path, monkeypatch, caplog):
    monkeypatch.setattr(shutil, "which", lambda name: None)
    audit = AuditLog(tmp_path / "audit.log")
    runner = DockerRunner(audit, LocalRunner(audit))
    with caplog.at_level(logging.WARNING, logger="grasshopper.sandbox"):
        result = runner.run("echo", ["echo", "still-local"])
    assert "Docker is not installed" in caplog.text
    assert result.container == "local"
    assert result.isolated is False
    assert result.detail == "still-local"
    assert any(row["result"] == "docker missing; fell back to local" for row in audit.read())


def test_docker_timeout_kills_the_named_container(tmp_path, monkeypatch):
    import subprocess

    calls = []

    def fake_run(argv, **kwargs):
        calls.append(list(argv))
        if list(argv)[:2] == ["docker", "kill"]:
            return subprocess.CompletedProcess(argv, 0, "", "")
        raise subprocess.TimeoutExpired(cmd=argv, timeout=1)

    monkeypatch.setattr("grasshopper.sandbox_runner.docker.shutil.which", lambda name: "/usr/bin/docker")
    monkeypatch.setattr("grasshopper.sandbox_runner.docker.subprocess.run", fake_run)
    audit = AuditLog(tmp_path / "audit.log")
    result = DockerRunner(audit, LocalRunner(audit), timeout=1).run("sleep", ["sleep", "9"])
    assert result.ok is False
    assert result.isolated is True
    assert result.detail == "timeout; killed"
    assert ["docker", "kill", "grasshopper-job"] in calls


def test_vultr_without_a_key_stays_mock(tmp_path, caplog):
    audit = AuditLog(tmp_path / "audit.log")
    runner = VultrRunner(audit, LocalRunner(audit), api_key="")
    with caplog.at_level(logging.WARNING, logger="grasshopper.sandbox"):
        result = runner.run("echo", ["echo", "no-cloud"])
    assert "VULTR_API_KEY is empty" in caplog.text
    assert result.container == "vultr-mock"
    assert result.isolated is False
    assert result.detail == "no-cloud"
    assert runner_status(audit.path)["isolated"] is False


def test_vultr_fake_api_creates_and_deletes_the_instance(tmp_path):
    store: dict = {}
    url = _serve(create_vultr_app(store))
    audit = AuditLog(tmp_path / "audit.log")
    runner = VultrRunner(audit, LocalRunner(audit), api_key="fake-vultr-key", api_base=url)
    result = runner.run("echo", ["echo", "on-box"])
    assert result.ok
    assert result.isolated is True
    assert result.container == "vultr:inst-1"
    assert store["deleted"] == ["inst-1"]
    assert store["alive"] == ""
    rows = audit.read()
    assert any(row["result"] == "created" and row["container"] == "vultr:inst-1" for row in rows)
    assert any(row["result"] == "deleted" for row in rows)
    badge = runner_status(audit.path)
    assert badge["isolated"] is True
    assert badge["label"] == "izole çalıştırıldı"


def test_dashboard_mentions_the_isolated_badge():
    html = Path("grasshopper/ui/templates/dashboard.html").read_text(encoding="utf-8")
    assert 'id="isolated"' in html
    assert "izole çalıştırıldı" in html


def _serve(app) -> str:
    sock = socket.socket()
    sock.bind(("127.0.0.1", 0))
    port = sock.getsockname()[1]
    sock.close()
    config = uvicorn.Config(app, host="127.0.0.1", port=port, log_level="warning")
    server = uvicorn.Server(config)
    threading.Thread(target=server.run, daemon=True).start()
    url = f"http://127.0.0.1:{port}"
    deadline = time.time() + 15
    while time.time() < deadline:
        try:
            httpx.get(url + "/v2/instances/none", timeout=0.3)
            return url
        except Exception:
            time.sleep(0.05)
    raise RuntimeError("vultr fake did not start")


