"""Comprehensive unit and integration tests for Vultr sandbox execution, API completeness, and containment."""

from __future__ import annotations

import socket
import threading
import time
from pathlib import Path

import httpx
import pytest
import uvicorn
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from grasshopper.sandbox_runner.audit import AuditLog
from grasshopper.sandbox_runner.local import LocalRunner
from grasshopper.sandbox_runner.vultr import VultrAPI, VultrRunner
from tests.fakes.vultr_app import create_vultr_app


def _serve_app(app: FastAPI) -> str:
    sock = socket.socket()
    sock.bind(("127.0.0.1", 0))
    port = sock.getsockname()[1]
    sock.close()
    config = uvicorn.Config(app, host="127.0.0.1", port=port, log_level="warning")
    server = uvicorn.Server(config)
    threading.Thread(target=server.run, daemon=True).start()
    url = f"http://127.0.0.1:{port}"
    deadline = time.time() + 10
    while time.time() < deadline:
        try:
            httpx.get(url + "/v2/instances", timeout=0.2)
            return url
        except Exception:
            time.sleep(0.05)
    raise RuntimeError("Test server did not start")


def test_vultr_api_full_lifecycle():
    store: dict = {}
    base_url = _serve_app(create_vultr_app(store))
    api = VultrAPI(api_key="test-key", base_url=base_url)

    # Create instance with cloud-init payload
    inst_id = api.create_instance(label="test-runner", user_data="#!/bin/bash\necho ready")
    assert inst_id == "inst-1"

    # Get instance
    details = api.get_instance(inst_id)
    assert details["id"] == "inst-1"
    assert details["status"] == "active"

    # List instances
    instances = api.list_instances()
    assert len(instances) == 1
    assert instances[0]["id"] == "inst-1"

    # Wait until active
    status = api.wait_until_active(inst_id, attempts=3)
    assert status == "active"

    # Delete instance
    api.delete_instance(inst_id)
    assert store["deleted"] == ["inst-1"]
    assert store["alive"] == ""


def test_vultr_api_unauthorized_error():
    store: dict = {}
    base_url = _serve_app(create_vultr_app(store))
    # Missing/invalid key should raise HTTPStatusError (401)
    api = VultrAPI(api_key="", base_url=base_url)
    with pytest.raises(httpx.HTTPStatusError) as exc_info:
        api.create_instance()
    assert exc_info.value.response.status_code == 401


def test_vultr_runner_cleans_up_on_failure(tmp_path):
    store: dict = {}
    base_url = _serve_app(create_vultr_app(store))
    audit = AuditLog(tmp_path / "audit.log")

    class FailingLocalRunner:
        def run(self, action: str, command: list[str], *, timeout: int = 30):
            raise RuntimeError("Execution exploded inside sandbox")

    runner = VultrRunner(audit, FailingLocalRunner(), api_key="valid-key", api_base=base_url)

    with pytest.raises(RuntimeError, match="Execution exploded inside sandbox"):
        runner.run("faulty_job", ["do_evil"])

    # Guaranteed cleanup in finally block
    assert "inst-1" in store["deleted"]
    rows = audit.read()
    assert any(r["result"] == "deleted" for r in rows)


def test_vultr_blast_radius_report_generation(tmp_path):
    import json
    from grasshopper.realweb.blast import runner_label, write_blast

    blast_file = tmp_path / "blast_radius.json"
    label = runner_label()
    assert "yerel" in label or "docker" in label

    write_blast(
        blast_file,
        files=["/tmp/output.txt"],
        domains=["books.toscrape.com"],
        seconds=1.245,
        cost_usd=0.0002,
        runner=label,
    )
    assert blast_file.is_file()
    data = json.loads(blast_file.read_text(encoding="utf-8"))
    assert data["files_touched"] == ["/tmp/output.txt"]
    assert data["domains"] == ["books.toscrape.com"]
    assert data["duration_sec"] == 1.245
    assert data["cost_usd"] == 0.0002
    assert "runner" in data

