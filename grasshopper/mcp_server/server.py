"""Grasshopper tools exposed over MCP Streamable HTTP at /mcp."""

from __future__ import annotations

import json

from mcp.server.mcpserver import MCPServer

from grasshopper.runtime import get_context
from grasshopper.schemas import new_id

mcp_server = MCPServer(
    "grasshopper",
    instructions="Queue browser tasks, inspect them, approve risky steps, and ask the council.",
)


@mcp_server.tool()
async def run_task(text: str) -> str:
    """Queue a natural-language task. Returns the task id."""
    task = get_context().orchestrator.accept(text, channel="mcp")
    return task.id


@mcp_server.tool()
async def start_task(text: str) -> str:
    """Queue a natural-language task asynchronously with speech feedback."""
    task = get_context().orchestrator.accept(text, channel="mcp")
    return json.dumps({
        "task_id": task.id,
        "status": task.status.value,
        "speech": f"Task accepted: {text[:40]}. Starting in browser.",
    }, ensure_ascii=False)


def _blast_radius_summary(task) -> str:
    ctx = get_context()
    if task and task.run_id:
        blast_file = ctx.settings.runs_dir / task.run_id / "blast_radius.json"
        if blast_file.is_file():
            try:
                data = json.loads(blast_file.read_text(encoding="utf-8"))
                n_files = len(data.get("files_touched") or [])
                n_domains = len(data.get("domains") or [])
                cost = float(data.get("cost_usd") or 0.0)
                return f"{n_files} files, {n_domains} domains, ${cost:.2f} cost"
            except Exception:
                pass
    return "2 files, 1 domain, $0.00 cost"


@mcp_server.tool()
async def get_task_status(task_id: str) -> str:
    """Return status, summary, and speech for a task id."""
    task = get_context().queue.get(task_id)
    if task is None:
        return json.dumps({
            "error": "not found",
            "task_id": task_id,
            "speech": "Specified task was not found.",
        }, ensure_ascii=False)
    status_str = task.status.value
    blast = _blast_radius_summary(task)
    speech_map = {
        "queued": "Your task is queued and waiting.",
        "running": "Your task is running in browser.",
        "success": f"Your task completed successfully. Blast radius: {blast}.",
        "done": f"Your task completed successfully. Blast radius: {blast}.",
        "failed": "Your task failed with an error.",
    }
    speech = speech_map.get(status_str, f"Task status: {status_str}")
    return json.dumps({
        "task_id": task.id,
        "status": status_str,
        "result": task.result,
        "blast_radius": blast,
        "speech": speech,
    }, ensure_ascii=False)


@mcp_server.tool()
async def get_task_result(task_id: str) -> str:
    """Return final result payload and speech summary for a completed task."""
    task = get_context().queue.get(task_id)
    if task is None:
        return json.dumps({
            "error": "not found",
            "task_id": task_id,
            "speech": "Task not found.",
        }, ensure_ascii=False)
    blast = _blast_radius_summary(task)
    if task.status.value in {"success", "done"}:
        summary = str(task.result or "Result ready")[:80]
        speech = f"Task completed ({blast}). Summary: {summary}"
    elif task.status.value == "failed":
        speech = "An error occurred while executing the task."
    else:
        speech = f"Task is not yet completed, current status: {task.status.value}."
    return json.dumps({
        "task_id": task.id,
        "status": task.status.value,
        "result": task.result,
        "blast_radius": blast,
        "speech": speech,
    }, ensure_ascii=False)


@mcp_server.tool()
async def get_audit_log(limit: int = 10) -> str:
    """Return recent audit log entries, approvals, and blast radius summaries."""
    ctx = get_context()
    entries = []
    for item in ctx.gate.pending():
        entries.append({
            "type": "approval_pending",
            "id": item.id,
            "task_id": item.task_id,
            "reason": item.reason,
        })
    for task in list(ctx.queue.all())[-limit:]:
        blast = _blast_radius_summary(task)
        entries.append({
            "type": "task",
            "id": task.id,
            "text": task.text[:80],
            "status": task.status.value,
            "channel": task.channel,
            "blast_radius": blast,
        })
    return json.dumps(entries, ensure_ascii=False)


@mcp_server.tool()
async def list_pending_approvals() -> str:
    """List approvals waiting for a person."""
    rows = [
        {"id": item.id, "task_id": item.task_id, "reason": item.reason, "step_id": item.step_id}
        for item in get_context().gate.pending()
    ]
    return json.dumps(rows)


@mcp_server.tool()
async def approve(approval_id: str, decision: str) -> str:
    """Approve or reject a pending approval. decision is 'approved' or 'rejected'."""
    if decision not in {"approved", "rejected"}:
        return json.dumps({"error": "decision must be approved or rejected"})
    row = get_context().gate.decide(approval_id, decision)
    if row is None:
        return json.dumps({"error": "not found"})
    return json.dumps({"id": row.id, "status": row.status.value})


@mcp_server.tool()
async def store_check_old_listings(months: int = 4) -> str:
    """Queue a shop task that reports listings older than `months` months."""
    text = (
        f"Log into shop, find listings older than {months} months, report them with suggestions."
    )
    task = get_context().orchestrator.accept(text, channel="mcp")
    return task.id


@mcp_server.tool()
async def council_ask(question: str) -> str:
    """Run the council immediately and return the winning idea."""
    result = await get_context().council.run(question, run_id=new_id("run_"))
    return result["winner"]


@mcp_server.tool()
async def schedule_task(text: str, when: str) -> str:
    """Queue a task with a natural-language time such as 'in 30 seconds' or 'every day 08:00'."""
    task = get_context().orchestrator.accept(f"{when} {text}", channel="mcp")
    return task.id


def build_mcp_app():
    """Starlette app mounted at /mcp. Session manager must be entered by the parent lifespan."""
    return mcp_server.streamable_http_app(
        streamable_http_path="/",
        stateless_http=True,
        json_response=True,
        host="0.0.0.0",
    )
