"""Hard spend ceiling. The router asks before every model call.

Catalog prices are the same table the cost panel uses. Mock calls still
reserve the catalog estimate so a later switch to a billed provider cannot
walk past the cap. Actual dollars charged by a provider stay on the call row.
A mock call's actual is 0.
"""

from __future__ import annotations

PRICE_PER_1K = {"fast": 0.0002, "strong": 0.003, "vision": 0.004, "repair": 0.0004}
# Tokens we cannot see yet. The pre-call check reserves a short reply.
_REPLY_RESERVE = 64


class BudgetExceeded(RuntimeError):
    def __init__(self, message: str, *, scope: str, estimate_usd: float, spent_usd: float, limit_usd: float):
        super().__init__(message)
        self.scope = scope
        self.estimate_usd = estimate_usd
        self.spent_usd = spent_usd
        self.limit_usd = limit_usd


class BudgetLedger:
    def __init__(self, daily_usd: float = 0.50, per_run_usd: float = 0.05):
        self.daily_limit = float(daily_usd)
        self.per_run_limit = float(per_run_usd)
        self.daily_estimated = 0.0
        self.daily_actual = 0.0
        self.run_estimated: dict[str, float] = {}
        self.run_actual: dict[str, float] = {}

    def estimate(self, tier: str, prompt: str) -> tuple[int, float]:
        tokens = max(1, len(prompt) // 4) + _REPLY_RESERVE
        price = PRICE_PER_1K.get(tier, 0.001)
        return tokens, price * tokens / 1000.0

    def authorize(self, tier: str, prompt: str, run_id: str | None) -> float:
        _tokens, estimate = self.estimate(tier, prompt)
        key = run_id or ""
        run_spent = self.run_estimated.get(key, 0.0) if key else 0.0
        if key and run_spent + estimate > self.per_run_limit + 1e-12:
            raise BudgetExceeded(
                f"Budget stop: run {key} would reach ${run_spent + estimate:.6f} "
                f"over the ${self.per_run_limit:.2f} per-run cap",
                scope="run",
                estimate_usd=estimate,
                spent_usd=run_spent,
                limit_usd=self.per_run_limit,
            )
        if self.daily_estimated + estimate > self.daily_limit + 1e-12:
            raise BudgetExceeded(
                f"Budget stop: day would reach ${self.daily_estimated + estimate:.6f} "
                f"over the ${self.daily_limit:.2f} daily cap",
                scope="day",
                estimate_usd=estimate,
                spent_usd=self.daily_estimated,
                limit_usd=self.daily_limit,
            )
        return estimate

    def commit(self, run_id: str | None, estimate_usd: float, actual_usd: float) -> None:
        key = run_id or ""
        self.daily_estimated += estimate_usd
        self.daily_actual += actual_usd
        if key:
            self.run_estimated[key] = self.run_estimated.get(key, 0.0) + estimate_usd
            self.run_actual[key] = self.run_actual.get(key, 0.0) + actual_usd
