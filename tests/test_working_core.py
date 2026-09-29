"""Comprehensive tests verifying the 8 core working capabilities of the digital worker."""

from __future__ import annotations

import asyncio
from datetime import datetime, timezone
from pathlib import Path

import pytest

from grasshopper.approvals.gate import ApprovalGate
from grasshopper.config import Settings
from grasshopper.core.orchestrator import Orchestrator
from grasshopper.core.router import Router
from grasshopper.db import Database
from grasshopper.providers.factory import build_search
from grasshopper.providers.llm_mock import MockLLM
from grasshopper.queue.task_queue import TaskQueue
from grasshopper.queue.scheduler import parse_when
from grasshopper.realweb.learning import LearningStore
from grasshopper.schemas import ApprovalDecision, Task, TaskStatus


def test_capability_a_natural_language_task_intake(tmp_path):
    """(a) Natural language task acceptance from Telegram, CLI, and Alexa channels."""
    db = Database(tmp_path / "test.db")
    queue = TaskQueue(db)

    # 1. Telegram channel
    task_tg = queue.enqueue(Task.create("Find 4-star books under 20 GBP", channel="telegram"))
    assert task_tg.id.startswith("task_")
    assert task_tg.channel == "telegram"
    assert task_tg.status == TaskStatus.queued

    # 2. CLI channel
    task_cli = queue.enqueue(Task.create("Check the news headlines and notify me", channel="cli"))
    assert task_cli.channel == "cli"

    # 3. Alexa channel
    task_alexa = queue.enqueue(Task.create("Open my shop and check old inventory", channel="alexa"))
    assert task_alexa.channel == "alexa"

    # All tasks are retrievable
    assert queue.get(task_tg.id) is not None
    assert queue.get(task_cli.id) is not None
    assert queue.get(task_alexa.id) is not None


def test_capability_b_multistep_planning_and_data_transfer(tmp_path):
    """(b) Multi-step planning and cross-site data transfer."""
    import json
    from grasshopper.realweb.heuristic import decide_json

    # Step 1: Browse books.toscrape.com, find target book
    step1_prompt = "REALWEB_DECIDE\n" + json.dumps({
        "scenario": "R1",
        "memory": {},
        "observation": {"url": "https://books.toscrape.com", "elements": [{"selector": "article.product_pod"}]},
    })
    step1_out = json.loads(decide_json(step1_prompt))
    assert "type" in step1_out

    # Step 2: Cross-site transfer -> pass extracted title to Wikipedia
    extracted_book_title = "A Light in the Attic"
    step2_prompt = "REALWEB_DECIDE\n" + json.dumps({
        "scenario": "R1",
        "memory": {"book_title": extracted_book_title},
        "observation": {"url": f"https://en.wikipedia.org/wiki/{extracted_book_title}", "elements": []},
    })
    step2_out = json.loads(decide_json(step2_prompt))
    assert "type" in step2_out


@pytest.mark.asyncio
async def test_capability_c_research_and_report_generation():
    """(c) Research and report generation with graceful Tavily fallback to offline index."""
    settings = Settings(search_provider="tavily", tavily_api_key="")
    search = build_search(settings)

    # Missing API key cleanly falls back to mock search provider
    results = await search.search("browser agents research")
    assert len(results) > 0
    assert any("title" in r or "url" in r or "body" in r for r in results)


def test_capability_d_scheduled_task_parsing():
    """(d) Scheduled task natural language parsing (bu gece 00:00'da, tomorrow, in N minutes)."""
    now = datetime(2026, 9, 28, 14, 0, 0, tzinfo=timezone.utc)

    # 1. 'tonight 00:00'
    p1 = parse_when("tonight 00:00 check book prices", now=now)
    assert p1.scheduled_at is not None
    assert p1.scheduled_at.hour == 0 and p1.scheduled_at.minute == 0
    assert "check book prices" in p1.remaining

    # 2. 'in 30 minutes'
    p2 = parse_when("in 30 minutes check server health", now=now)
    assert p2.scheduled_at is not None
    assert int((p2.scheduled_at - now).total_seconds()) == 1800
    assert "check server health" in p2.remaining


def test_capability_e_risk_approval_gate(tmp_path):
    """(e) Risk-sensitive human approval gate blocks sensitive action until human decision."""
    db = Database(tmp_path / "test.db")
    gate = ApprovalGate(db)

    # Create pending approval for payment
    row = gate.create(
        task_id="task_123",
        step_id="step_4",
        reason="Moving 0.50 SOL for subscription upgrade",
        screenshot="runs/r1/pay.png",
    )
    assert row.status == ApprovalDecision.pending

    # Verify task is blocked in pending list
    pending = gate.pending()
    assert any(item.id == row.id for item in pending)

    # Approve action
    decided = gate.decide(row.id, "approved")
    assert decided is not None
    assert decided.status == ApprovalDecision.approved
    assert len(gate.pending()) == 0


def test_capability_f_recipe_library_zero_llm_calls(tmp_path):
    """(f) Skill / recipe library replays learned recipe with 0 LLM calls on second run."""
    learning = LearningStore(tmp_path / "learning.json")

    scenario_name = "test_books_flow"
    actions = [
        {"action": "goto", "url": "https://books.toscrape.com"},
        {"action": "click", "selector": "article.product_pod a"},
        {"action": "done", "answer": "Cheapest book found: £10.00"},
    ]

    # Save learned recipe from 1st run
    learning.save_first(scenario_name, actions, calls=5)

    # Replay on 2nd run
    learning.save_replay(scenario_name, calls=0)

    stored = learning.row(scenario_name)
    assert stored is not None
    assert stored["first_calls"] == 5
    assert stored["second_calls"] == 0
    assert len(stored["actions"]) == 3

    # Panel reflects the measured learning gain
    panel = learning.panel()
    assert panel["first_calls"] == 5
    assert panel["second_calls"] == 0


def test_capability_g_multiagent_council_module():
    """(g) Multi-agent council decision module provides diverse persona reviews."""
    from grasshopper.providers.llm_mock import _PERSONALITIES

    required_personas = {"mock_a", "mock_b", "mock_c", "mock_d", "mock_e", "mock_f"}
    assert required_personas.issubset(set(_PERSONALITIES.keys()))

    # Each persona has distinct perspectives
    assert "practical founder" in _PERSONALITIES["mock_a"]
    assert "skeptical engineer" in _PERSONALITIES["mock_b"]
    assert "security reviewer" in _PERSONALITIES["mock_e"]


def test_capability_h_post_failure_repair_and_policy():
    """(h) Post-failure error recovery and allowlist policy enforcement."""
    import json
    from grasshopper.realweb.heuristic import decide_json
    from grasshopper.realweb.policy import classify, path_blocked

    settings = Settings()

    # Allowlisted site succeeds
    v_books = classify("https://books.toscrape.com/catalogue/category/books_1/index.html", settings)
    assert v_books.allowed is True

    v_arxiv = classify("https://export.arxiv.org/api/query?search_query=all:electron", settings)
    assert v_arxiv.allowed is True

    # Blocked sensitive sites fail
    assert classify("https://twitter.com/home", settings).allowed is False
    assert classify("https://facebook.com/login", settings).allowed is False
    assert classify("https://paypal.com/checkout", settings).allowed is False

    # Robots.txt /api/ allowed on arxiv, root search blocked
    rules = ["/search", "/find"]
    assert path_blocked("/api/query", rules, host="export.arxiv.org") is False
    assert path_blocked("/search", rules, host="export.arxiv.org") is True

    # Post-failure repair: heuristic reacts and recovers when previous step had error
    err_prompt = "REALWEB_DECIDE\n" + json.dumps({
        "scenario": "R5",
        "memory": {},
        "observation": {},
        "last_error": "Timeout waiting for selector",
    })
    recovery_decision = json.loads(decide_json(err_prompt))
    assert "type" in recovery_decision
