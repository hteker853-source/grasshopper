"""S1–S9 against the sandbox. S4 waits about 20 seconds on purpose."""

from __future__ import annotations

import json
import os
import subprocess
import sys
import time
from pathlib import Path

import httpx
import pytest

from grasshopper.demo_scenarios import S1, S2, S3, S4, S5, S6, S7, S9, run_scenario

pytestmark = pytest.mark.e2e


def test_s1_account_research_share(ctx):
    result = _run(ctx, S1)
    assert result.status.value == "done"
    assert "Missing: phone" in result.summary or "phone" in result.summary
    assert result.success_rate == 1


def test_s2_cross_site(ctx):
    result = _run(ctx, S2)
    assert result.status.value == "done"
    assert "Shortened:" in result.summary


def test_s3_old_listings(ctx):
    result = _run(ctx, S3)
    assert result.status.value == "done"
    assert "Stale listings" in result.summary


def test_s4_scheduled_news(ctx):
    started = time.time()
    result = _run(ctx, S4)
    assert time.time() - started >= 18
    assert result.status.value == "done"
    assert "Video script" in result.summary
    assert "bees" in result.summary.lower() or "bee" in result.summary.lower()


def test_s5_council(ctx):
    result = _run(ctx, S5)
    assert result.status.value == "done"
    assert "Winner:" in result.summary or "Council winner" in result.summary
    council = Path(result.artifacts[0]).parent / "council.md"
    # artifacts[0] is explain.jsonl; council.md sits beside it
    council = Path(ctx.settings.runs_dir) / result.run_id / "council.md"
    assert council.exists()
    text = council.read_text(encoding="utf-8")
    assert "Devil's advocate" in text
    assert "Winner" in text


def test_s6_payment_and_limit(ctx):
    result = _run(ctx, S6)
    assert result.status.value == "done"
    assert "Receipt:" in result.summary
    shots = _approval_shots(ctx, result.task_id)
    assert shots
    assert Path(shots[0]).is_file()
    from grasshopper.providers.wallet_mock import WalletLimitError

    with pytest.raises(WalletLimitError):
        ctx.wallet.pay(0.2, "over per-tx limit")


def test_s7_stuck_and_repair(ctx):
    result = _run(ctx, S7, approve=False)
    assert result.status.value == "waiting_approval"
    shots = _approval_shots(ctx, result.task_id)
    assert shots
    assert Path(shots[0]).is_file()
    assert result.artifacts[-1].endswith(".diff") or "patch" in (ctx.queue.get(result.task_id).result or {}).get("patch", "")
    patch = (ctx.queue.get(result.task_id).result or {}).get("patch")
    assert patch and Path(patch).exists()
    assert "export-btn-renamed" in Path(patch).read_text(encoding="utf-8")
    pending = ctx.gate.pending(result.task_id)
    assert pending


def test_s8_second_run_uses_playbook(ctx):
    first = _run(ctx, S3)
    second = _run(ctx, S3)
    assert second.plan_source == "playbook"
    assert second.llm_calls == 0
    assert second.status.value == "done"
    explain = Path(ctx.settings.runs_dir) / second.run_id / "explain.jsonl"
    assert "playbook" in explain.read_text(encoding="utf-8")
    assert first.plan_source == "playbook"


def test_s9_mcp_client(tmp_path):
    port = 18871
    sandbox_port = 18872
    env = os.environ.copy()
    env.update({
        "DASHBOARD_PORT": str(port),
        "SANDBOX_PORT": str(sandbox_port),
        "SANDBOX_BASE_URL": "",
        "GRASSHOPPER_EMBED_SANDBOX": "1",
        "BROWSER_DRIVER": "http",
        "SANDBOX_DELAY_MIN_MS": "0",
        "SANDBOX_DELAY_MAX_MS": "10",
        "GRASSHOPPER_DATA_DIR": str(tmp_path),
        "GRASSHOPPER_DB": str(tmp_path / "gh.db"),
        "GRASSHOPPER_RUNS_DIR": str(tmp_path / "runs"),
        "SANDBOX_DB": str(tmp_path / "sandbox.db"),
        "SANDBOX_MEDIA_DIR": str(tmp_path / "media"),
        "API_TOKEN": "test-token",
    })
    proc = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "grasshopper.main:app", "--host", "127.0.0.1", "--port", str(port)],
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )
    try:
        deadline = time.time() + 20
        while time.time() < deadline:
            try:
                httpx.get(f"http://127.0.0.1:{port}/health", timeout=0.4)
                break
            except Exception:
                time.sleep(0.2)
        else:
            out = proc.stdout.read().decode() if proc.stdout else ""
            raise RuntimeError(out[-2000:])
        from mcp import Client

        async def exercise():
            async with Client(f"http://127.0.0.1:{port}/mcp/") as client:
                listed = await client.list_tools()
                names = {tool.name for tool in listed.tools}
                assert "run_task" in names
                assert "get_task_status" in names
                queued = await client.call_tool("run_task", {"text": S9})
                task_id = queued.content[0].text.strip()
                status = "queued"
                for _ in range(40):
                    current = await client.call_tool("get_task_status", {"task_id": task_id})
                    body = json.loads(current.content[0].text)
                    status = body["status"]
                    if status in {"done", "failed", "waiting_approval", "cancelled"}:
                        return status
                    await _asleep()
                return status

        import asyncio
        status = asyncio.run(exercise())
        assert status == "done"
    finally:
        proc.terminate()
        try:
            proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            proc.kill()


async def _asleep():
    import asyncio
    await asyncio.sleep(0.4)


def _run(ctx, text, approve=True):
    import asyncio
    return asyncio.run(run_scenario(ctx, text, approve=approve))


def _approval_shots(ctx, task_id: str) -> list[str]:
    shots = []
    for notifier in ctx.notifier.notifiers:
        for message in getattr(notifier, "messages", []):
            payload = message.get("payload") or {}
            if message.get("kind") == "approval" and payload.get("task_id") == task_id and payload.get("screenshot"):
                shots.append(payload["screenshot"])
    return shots
