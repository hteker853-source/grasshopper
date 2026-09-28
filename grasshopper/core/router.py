"""Three-tier model router. Every call is logged with a cost estimate."""

from __future__ import annotations

import logging
import time
from datetime import datetime, timezone

from grasshopper.core.budget import PRICE_PER_1K, BudgetExceeded, BudgetLedger
from grasshopper.db import Database
from grasshopper.providers.factory import build_llm
from grasshopper.providers.llm_mock import MockLLM
from grasshopper.schemas import LLMResponse

log = logging.getLogger("grasshopper.router")

_COST_PER_1K = PRICE_PER_1K


class Router:
    def __init__(self, settings, db: Database):
        self.settings = settings
        self.db = db
        self.fast = build_llm(settings.llm_fast_provider, settings, tier="fast")
        self.strong = build_llm(settings.llm_strong_provider, settings, tier="strong")
        self.vision = build_llm(settings.llm_vision_provider, settings, tier="vision")
        self.repair = build_llm(settings.llm_repair_provider, settings, tier="repair")
        self.calls: list[LLMResponse] = []
        self.budget = BudgetLedger(settings.budget_usd_daily, settings.budget_usd_per_run)
        from grasshopper.providers.factory import build_notifier

        self.notifier = build_notifier(settings)

    def _provider(self, tier: str):
        return {"fast": self.fast, "strong": self.strong, "vision": self.vision, "repair": self.repair}[tier]

    async def _tell_budget(self, exc: BudgetExceeded) -> None:
        if self.notifier is None:
            return
        await self.notifier.notify(str(exc), kind="budget")

    async def complete(self, tier: str, prompt: str, *, system: str = "", run_id: str | None = None) -> LLMResponse:
        try:
            estimate = self.budget.authorize(tier, prompt, run_id)
        except BudgetExceeded as exc:
            await self._tell_budget(exc)
            raise
        provider = self._provider(tier)
        started = time.perf_counter()
        used = provider
        try:
            text = await provider.complete(prompt, tier=tier, system=system)
        except Exception as exc:
            log.warning("Provider %s failed (%s). Falling back to mock.", getattr(provider, "name", "?"), exc)
            used = MockLLM("mock")
            text = await used.complete(prompt, tier=tier, system=system)
        duration_ms = int((time.perf_counter() - started) * 1000)
        tokens = max(1, len(prompt) // 4 + len(text) // 4)
        cost = 0.0 if isinstance(used, MockLLM) else _COST_PER_1K.get(tier, 0.001) * tokens / 1000
        self.budget.commit(run_id, estimate, cost)
        response = LLMResponse(
            text=text,
            provider=getattr(used, "name", "unknown"),
            tier=tier,
            tokens=tokens,
            cost_usd=cost,
            duration_ms=duration_ms,
        )
        self.calls.append(response)
        self.db.conn.execute(
            "INSERT INTO llm_calls (run_id, tier, provider, tokens, cost_usd, duration_ms, created_at) "
            "VALUES (?, ?, ?, ?, ?, ?, ?)",
            (
                run_id,
                tier,
                response.provider,
                tokens,
                cost,
                duration_ms,
                datetime.now(timezone.utc).isoformat(),
            ),
        )
        log.info("llm tier=%s provider=%s tokens=%s cost=%.6f ms=%s", tier, response.provider, tokens, cost, duration_ms)
        return response

    def savings(self) -> dict:
        if not self.calls:
            rows = self.db.conn.execute(
                "SELECT tier, COUNT(*) AS n, COALESCE(SUM(tokens), 0) AS tokens FROM llm_calls GROUP BY tier"
            ).fetchall()
            counts = {row["tier"]: int(row["n"]) for row in rows}
            tokens = {row["tier"]: int(row["tokens"]) for row in rows}
        else:
            counts = {}
            tokens = {}
            for call in self.calls:
                counts[call.tier] = counts.get(call.tier, 0) + 1
                tokens[call.tier] = tokens.get(call.tier, 0) + int(call.tokens)
        total = sum(counts.values())
        fast_tokens = tokens.get("fast", 0)
        # Tokens answered by the fast tier are the ones not sent to the strong model.
        gap = _COST_PER_1K["strong"] - _COST_PER_1K["fast"]
        return {
            "total": total,
            "by_tier": counts,
            "tokens_by_tier": tokens,
            "fast_ratio": (counts.get("fast", 0) / total) if total else 0.0,
            "saved_tokens": fast_tokens,
            "saved_usd": gap * fast_tokens / 1000,
        }
