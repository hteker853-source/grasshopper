"""SQLite ledger with a fake 10 SOL balance and fake transaction hashes."""

from __future__ import annotations

from datetime import datetime, timezone

from grasshopper.db import Database
from grasshopper.schemas import new_id


class WalletLimitError(RuntimeError):
    pass


class MockWallet:
    name = "mock"
    OPENING_SOL = 10.0

    def __init__(self, db: Database, *, daily_limit: float, per_tx_limit: float):
        self.db = db
        self.daily_limit = daily_limit
        self.per_tx_limit = per_tx_limit
        self._ensure_opening_balance()

    def configured(self) -> bool:
        return True

    def _ensure_opening_balance(self) -> None:
        row = self.db.conn.execute("SELECT COUNT(*) AS n FROM wallet_ledger").fetchone()
        if row["n"] == 0:
            self._insert(self.OPENING_SOL, "credit", "opening balance", "mock_open", None)

    def _insert(self, amount: float, direction: str, memo: str, tx_hash: str, task_id: str | None) -> None:
        now = datetime.now(timezone.utc).isoformat()
        self.db.conn.execute(
            "INSERT INTO wallet_ledger (id, amount_sol, direction, memo, tx_hash, created_at, task_id) "
            "VALUES (?, ?, ?, ?, ?, ?, ?)",
            (new_id("tx_"), amount, direction, memo, tx_hash, now, task_id),
        )

    def balance(self) -> float:
        rows = self.db.conn.execute("SELECT amount_sol, direction FROM wallet_ledger").fetchall()
        total = 0.0
        for row in rows:
            total += row["amount_sol"] if row["direction"] == "credit" else -row["amount_sol"]
        return round(total, 6)

    def spent_today(self) -> float:
        today = datetime.now(timezone.utc).date().isoformat()
        rows = self.db.conn.execute(
            "SELECT amount_sol FROM wallet_ledger WHERE direction='debit' AND created_at LIKE ?",
            (today + "%",),
        ).fetchall()
        return round(sum(row["amount_sol"] for row in rows), 6)

    def pay(self, amount_sol: float, memo: str, task_id: str | None = None) -> str:
        if amount_sol <= 0:
            raise WalletLimitError("Amount must be positive")
        if amount_sol > self.per_tx_limit:
            raise WalletLimitError(
                f"Per-transaction limit is {self.per_tx_limit} SOL; refused {amount_sol} SOL"
            )
        if self.spent_today() + amount_sol > self.daily_limit + 1e-9:
            raise WalletLimitError(
                f"Daily limit is {self.daily_limit} SOL; spent {self.spent_today()} SOL; refused {amount_sol} SOL"
            )
        if amount_sol > self.balance() + 1e-9:
            raise WalletLimitError("Insufficient mock balance")
        tx_hash = "mock" + new_id()
        self._insert(amount_sol, "debit", memo, tx_hash, task_id)
        return tx_hash

    def ledger(self) -> list[dict]:
        rows = self.db.conn.execute(
            "SELECT id, amount_sol, direction, memo, tx_hash, created_at FROM wallet_ledger ORDER BY created_at"
        ).fetchall()
        return [dict(row) for row in rows]
