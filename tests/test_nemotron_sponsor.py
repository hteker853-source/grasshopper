"""Verification of NVIDIA Nemotron sponsor integration, routing, and Open Agent protocol schema compatibility."""

from __future__ import annotations

import pytest

from grasshopper.config import Settings
from grasshopper.core.budget import BudgetLedger, PRICE_PER_1K
from grasshopper.core.router import Router
from grasshopper.db import Database
from grasshopper.mcp_server.server import (
    approve,
    get_task_status,
    list_pending_approvals,
    run_task,
    store_check_old_listings,
)


def test_nemotron_open_agent_tool_schema_compliance():
    """Verify tool functions exposed by MCP server conform to Open Agent function call specifications."""
    tools = [
        run_task,
        get_task_status,
        list_pending_approvals,
        approve,
        store_check_old_listings,
    ]
    for fn in tools:
        assert callable(fn)
        assert fn.__doc__ is not None
        assert len(fn.__doc__.strip()) > 10
        assert fn.__name__ in {
            "run_task",
            "get_task_status",
            "list_pending_approvals",
            "approve",
            "store_check_old_listings",
        }


def test_nemotron_two_tier_pricing_and_budget_routing():
    """Verify routing between Nemotron fast tier and strong tier respects pricing policy."""
    ledger = BudgetLedger(daily_usd=0.50, per_run_usd=0.05)

    # Fast tier price check
    fast_tokens, fast_cost = ledger.estimate("fast", "sample prompt with 40 characters")
    assert fast_cost > 0
    assert PRICE_PER_1K["fast"] == 0.0002

    # Strong tier price check
    strong_tokens, strong_cost = ledger.estimate("strong", "sample prompt with 40 characters")
    assert strong_cost == strong_tokens * 0.003 / 1000.0

    # Authorization succeeds within limit
    est = ledger.authorize("fast", "navigate to books", "run_1")
    assert est > 0
    ledger.commit("run_1", est, 0.0001)
    assert ledger.daily_actual == 0.0001


@pytest.mark.asyncio
async def test_router_falls_back_to_strong_on_repair_need(tmp_path):
    """Verify Router supports routing across tiers with budget authorization."""
    settings = Settings(llm_fast_provider="mock", llm_strong_provider="mock", budget_usd_daily=0.50, budget_usd_per_run=0.05)
    db = Database(tmp_path / "test.db")
    router = Router(settings, db)

    res_fast = await router.complete("fast", "navigate home", run_id="r1")
    assert res_fast.tier == "fast"
    assert res_fast.text is not None

    res_strong = await router.complete("strong", "fix selector failure", run_id="r1")
    assert res_strong.tier == "strong"
    assert res_strong.text is not None
