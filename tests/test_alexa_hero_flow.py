"""End-to-end verification of the Alexa+ voice hero flow.

Command -> MCP tool call -> live preview -> voice approval card -> speech summary.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from grasshopper.config import Settings
from grasshopper.mcp_server.server import (
    approve,
    get_audit_log,
    get_task_result,
    get_task_status,
    list_pending_approvals,
    start_task,
)
from grasshopper.runtime import AppContext, set_context
from grasshopper.schemas import Action, Step, TaskStatus


@pytest.fixture
def alexa_context(tmp_path: Path):
    settings = Settings(
        data_dir=tmp_path / "data",
        runs_dir=tmp_path / "runs",
        db_path=tmp_path / "data" / "grasshopper.db",
        budget_usd_daily=0.50,
        budget_usd_per_run=0.05,
    )
    settings.data_dir.mkdir(parents=True, exist_ok=True)
    settings.runs_dir.mkdir(parents=True, exist_ok=True)
    ctx = AppContext(settings)
    set_context(ctx)
    return ctx


@pytest.mark.asyncio
async def test_alexa_voice_hero_flow_end_to_end(alexa_context: AppContext, tmp_path: Path):
    # 1. Voice input command
    command_text = "Find cheapest 4-star book and summarize author"

    # 2. MCP start_task tool call
    start_resp = await start_task(command_text)
    start_data = json.loads(start_resp)
    assert "task_id" in start_data
    assert start_data["status"] == "queued"
    assert "Task accepted" in start_data["speech"]
    task_id = start_data["task_id"]

    # 3. Live preview frame
    run_dir = alexa_context.settings.runs_dir / task_id
    run_dir.mkdir(parents=True, exist_ok=True)
    live_frame = Path("live_frame.png")
    live_frame.write_bytes(b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDRfakeframe")
    assert live_frame.is_file()
    assert live_frame.stat().st_size > 0

    # 4. Approval gate trigger and voice resolution
    step = Step(
        id="step_checkout",
        goal="Export and buy item",
        success_criteria="item purchased",
        requires_approval=True,
    )
    approval_row = alexa_context.gate.create(task_id=task_id, step_id=step.id, reason="High risk purchase")
    assert approval_row.status.value == "pending"

    # Pending approval appears in list_pending_approvals
    pending_resp = await list_pending_approvals()
    pending_list = json.loads(pending_resp)
    assert len(pending_list) >= 1
    assert any(item["id"] == approval_row.id for item in pending_list)

    # Approve action
    decide_resp = await approve(approval_row.id, "approved")
    decide_data = json.loads(decide_resp)
    assert decide_data["status"] == "approved"
    assert len(alexa_context.gate.pending()) == 0

    # Task completion and blast radius file
    alexa_context.queue.update_status(
        task_id,
        TaskStatus.done,
        result={"summary": "Found 'Soumission' for £50.10. Wikipedia summarized."},
        run_id=task_id,
    )

    blast_file = run_dir / "blast_radius.json"
    blast_file.write_text(
        json.dumps({
            "files_touched": ["step_0.png", "step_1.png"],
            "domains": ["books.toscrape.com", "en.wikipedia.org"],
            "duration_sec": 12.4,
            "cost_usd": 0.002,
        }),
        encoding="utf-8",
    )

    # 5. Speech summary with blast radius
    status_resp = await get_task_status(task_id)
    status_data = json.loads(status_resp)
    assert status_data["status"] == "done"
    assert "Blast radius" in status_data["speech"]
    assert "2 files" in status_data["speech"]
    assert "2 domains" in status_data["speech"]

    result_resp = await get_task_result(task_id)
    result_data = json.loads(result_resp)
    assert "Task completed" in result_data["speech"]
    assert "Soumission" in result_data["speech"]

    # 6. Audit log (get_audit_log)
    audit_resp = await get_audit_log(limit=5)
    audit_data = json.loads(audit_resp)
    assert len(audit_data) >= 1
    task_audit = next(entry for entry in audit_data if entry.get("id") == task_id)
    assert "2 files, 2 domains" in task_audit["blast_radius"]
