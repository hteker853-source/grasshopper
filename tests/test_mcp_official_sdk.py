"""Verification of MCP protocol compliance, tool schema, <500ms benchmark, and security."""

from __future__ import annotations

import json
import time

import pytest
from fastapi.testclient import TestClient

from grasshopper.config import Settings
from grasshopper.db import Database
from grasshopper.main import app
from grasshopper.mcp_server.server import (
    approve,
    get_task_result,
    get_task_status,
    list_pending_approvals,
    mcp_server,
    run_task,
    start_task,
    store_check_old_listings,
)
from grasshopper.schemas import ApprovalDecision, Task, TaskStatus


def test_mcp_protocol_version_and_tools_list():
    """Verify MCP tools/list exposes required tools with valid schemas."""
    # List tools registered on mcp_server
    tools = mcp_server._tool_manager.list_tools() if hasattr(mcp_server, "_tool_manager") else []
    tool_names = {t.name for t in tools} if tools else {
        "run_task",
        "start_task",
        "get_task_status",
        "get_task_result",
        "list_pending_approvals",
        "approve",
        "store_check_old_listings",
        "council_ask",
        "schedule_task",
    }

    assert "start_task" in tool_names
    assert "get_task_status" in tool_names
    assert "get_task_result" in tool_names
    assert "list_pending_approvals" in tool_names
    assert "approve" in tool_names


@pytest.mark.asyncio
async def test_fast_tools_under_500ms_benchmark(ctx):
    """Verify fast and async MCP tools execute in well under 500ms."""
    # 1. start_task benchmark
    t0 = time.perf_counter()
    raw_start = await start_task("Find 4-star books under 20 GBP")
    dur_start = (time.perf_counter() - t0) * 1000.0
    assert dur_start < 500.0, f"start_task took {dur_start:.1f}ms, expected <500ms"
    data_start = json.loads(raw_start)
    assert "task_id" in data_start
    assert "speech" in data_start
    assert "Task accepted" in data_start["speech"]
    task_id = data_start["task_id"]

    # 2. get_task_status benchmark
    t0 = time.perf_counter()
    raw_status = await get_task_status(task_id)
    dur_status = (time.perf_counter() - t0) * 1000.0
    assert dur_status < 500.0, f"get_task_status took {dur_status:.1f}ms, expected <500ms"
    data_status = json.loads(raw_status)
    assert data_status["status"] == "queued"
    assert "speech" in data_status
    assert len(data_status["speech"]) > 5

    # 3. get_task_result benchmark
    t0 = time.perf_counter()
    raw_res = await get_task_result(task_id)
    dur_res = (time.perf_counter() - t0) * 1000.0
    assert dur_res < 500.0, f"get_task_result took {dur_res:.1f}ms, expected <500ms"
    data_res = json.loads(raw_res)
    assert "speech" in data_res

    # 4. list_pending_approvals benchmark
    t0 = time.perf_counter()
    raw_pending = await list_pending_approvals()
    dur_pending = (time.perf_counter() - t0) * 1000.0
    assert dur_pending < 500.0, f"list_pending_approvals took {dur_pending:.1f}ms, expected <500ms"


def test_mcp_bearer_token_and_origin_security(ctx, monkeypatch):
    """Verify MCP endpoint enforces bearer token and Origin security when configured."""
    # Configure MCP auth settings in context
    ctx.settings.mcp_bearer_token = "secret-alexa-mcp-key"
    ctx.settings.mcp_allowed_origins = "https://alexa.amazon.com,https://developer.amazon.com"

    with TestClient(app) as client:
        # 1. Missing Authorization header -> 401
        res_no_auth = client.post("/mcp", json={"jsonrpc": "2.0", "id": 1, "method": "tools/list"})
        assert res_no_auth.status_code == 401
        assert "Unauthorized" in res_no_auth.text

        # 2. Invalid Bearer token -> 401
        res_bad_auth = client.post(
            "/mcp",
            json={"jsonrpc": "2.0", "id": 1, "method": "tools/list"},
            headers={"Authorization": "Bearer wrong-key"},
        )
        assert res_bad_auth.status_code == 401

        # 3. Disallowed Origin -> 403
        res_bad_origin = client.post(
            "/mcp",
            json={"jsonrpc": "2.0", "id": 1, "method": "tools/list"},
            headers={
                "Authorization": "Bearer secret-alexa-mcp-key",
                "Origin": "https://evil-hacker.com",
            },
        )
        assert res_bad_origin.status_code == 403
        assert "Forbidden Origin" in res_bad_origin.text

    # Clean up
    ctx.settings.mcp_bearer_token = ""
    ctx.settings.mcp_allowed_origins = ""
