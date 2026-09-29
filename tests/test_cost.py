"""Router call counts and the estimated tokens kept off the strong model."""

from __future__ import annotations

import asyncio
from pathlib import Path

from grasshopper.main import _cost_panel


def test_savings_counts_fast_strong_and_vision_and_estimates_tokens(ctx):
    before = ctx.router.savings()
    asyncio.run(ctx.router.complete("fast", "cost-fast-prompt"))
    asyncio.run(ctx.router.complete("strong", "cost-strong-prompt"))
    asyncio.run(ctx.router.complete("vision", "cost-vision-prompt"))
    now = ctx.router.savings()
    assert now["by_tier"]["fast"] == before["by_tier"].get("fast", 0) + 1
    assert now["by_tier"]["strong"] == before["by_tier"].get("strong", 0) + 1
    assert now["by_tier"]["vision"] == before["by_tier"].get("vision", 0) + 1
    assert now["saved_tokens"] > before.get("saved_tokens", 0)
    panel = _cost_panel(now)
    assert panel["fast"] >= 1 and panel["strong"] >= 1 and panel["vision"] >= 1
    assert panel["saved_tokens"] == now["saved_tokens"]
    assert panel["saved_usd"] > 0
    html = Path("grasshopper/ui/templates/dashboard.html").read_text(encoding="utf-8")
    assert 'id="cost"' in html
    assert "Fast calls" in html and "Strong calls" in html and "Vision calls" in html
    assert "saved_tokens" in html
    assert 'id="learning"' in html and 'id="learn-first"' in html and 'id="learn-second"' in html
    assert 'id="savings"' in html and "Cost savings" in html
