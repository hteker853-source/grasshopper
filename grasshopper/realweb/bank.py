"""Mock bank gate for the ING template. Topics arrive 9 October; the three gates stay."""

from __future__ import annotations

from datetime import datetime, timezone


class BankLimit(RuntimeError):
    pass


class BankSandbox:
    """Approval, a per-transfer limit, and an append-only audit trail."""

    def __init__(self, *, balance: float = 1000.0, per_tx: float = 100.0, daily: float = 500.0):
        self.balance = balance
        self.per_tx = per_tx
        self.daily = daily
        self.spent_today = 0.0
        self.pending: dict | None = None
        self.audit: list[dict] = []

    def _note(self, event: str, amount: float, detail: str) -> None:
        self.audit.append({
            "ts": datetime.now(timezone.utc).isoformat(),
            "event": event,
            "amount": amount,
            "detail": detail,
        })

    def request_transfer(self, amount: float, memo: str) -> str:
        self._note("request", amount, memo)
        if amount <= 0:
            self._note("refused", amount, "amount must be positive")
            raise BankLimit("amount must be positive")
        if amount > self.per_tx:
            self._note("refused", amount, f"per-transfer limit {self.per_tx}")
            raise BankLimit(f"per-transfer limit is {self.per_tx}")
        if self.spent_today + amount > self.daily:
            self._note("refused", amount, f"daily limit {self.daily}")
            raise BankLimit(f"daily limit is {self.daily}")
        self.pending = {"amount": amount, "memo": memo}
        self._note("approval_required", amount, memo)
        return "approval_required"

    def decide(self, decision: str) -> str:
        pending = self.pending
        if pending is None:
            self._note("rejected", 0, "nothing pending")
            return "rejected"
        amount = float(pending["amount"])
        if decision != "approved":
            self.pending = None
            self._note("rejected", amount, decision)
            return "rejected"
        self.balance = round(self.balance - amount, 2)
        self.spent_today = round(self.spent_today + amount, 2)
        self.pending = None
        self._note("approved", amount, pending["memo"])
        return "approved"
