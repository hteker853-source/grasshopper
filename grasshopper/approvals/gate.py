"""Pending approvals. A step with requires_approval waits here; timeout cancels it."""

from __future__ import annotations

import asyncio
from datetime import datetime, timezone

from grasshopper.db import Database
from grasshopper.schemas import Approval, ApprovalDecision, new_id


class ApprovalGate:
    def __init__(self, db: Database, timeout_sec: int = 1800):
        self.db = db
        self.timeout_sec = timeout_sec

    def create(self, *, task_id: str, step_id: str | None, reason: str, screenshot: str | None = None) -> Approval:
        approval = Approval(
            id=new_id("apr_"),
            task_id=task_id,
            step_id=step_id,
            reason=reason,
            screenshot=screenshot,
        )
        self.db.conn.execute(
            "INSERT INTO approvals (id, task_id, step_id, reason, status, screenshot, created_at, decided_at) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, NULL)",
            (
                approval.id,
                task_id,
                step_id,
                reason,
                approval.status.value,
                screenshot,
                approval.created_at.isoformat(),
            ),
        )
        return approval

    def get(self, approval_id: str) -> Approval | None:
        row = self.db.conn.execute("SELECT * FROM approvals WHERE id=?", (approval_id,)).fetchone()
        return _row(row) if row else None

    def pending(self, task_id: str | None = None) -> list[Approval]:
        if task_id:
            rows = self.db.conn.execute(
                "SELECT * FROM approvals WHERE status='pending' AND task_id=? ORDER BY created_at",
                (task_id,),
            ).fetchall()
        else:
            rows = self.db.conn.execute(
                "SELECT * FROM approvals WHERE status='pending' ORDER BY created_at"
            ).fetchall()
        return [_row(row) for row in rows]

    def decide(self, approval_id: str, decision: str) -> Approval | None:
        if decision not in {"approved", "rejected"}:
            raise ValueError("decision must be approved or rejected")
        now = datetime.now(timezone.utc).isoformat()
        self.db.conn.execute(
            "UPDATE approvals SET status=?, decided_at=? WHERE id=? AND status='pending'",
            (decision, now, approval_id),
        )
        return self.get(approval_id)

    async def wait(self, approval_id: str, timeout: int | None = None) -> str:
        deadline = asyncio.get_event_loop().time() + (timeout if timeout is not None else self.timeout_sec)
        while asyncio.get_event_loop().time() < deadline:
            current = self.get(approval_id)
            if current and current.status != ApprovalDecision.pending:
                return current.status.value
            await asyncio.sleep(0.1)
        now = datetime.now(timezone.utc).isoformat()
        self.db.conn.execute(
            "UPDATE approvals SET status='expired', decided_at=? WHERE id=? AND status='pending'",
            (now, approval_id),
        )
        return "expired"


def _row(row) -> Approval:
    return Approval(
        id=row["id"],
        task_id=row["task_id"],
        step_id=row["step_id"],
        reason=row["reason"],
        status=ApprovalDecision(row["status"]),
        screenshot=row["screenshot"],
        created_at=datetime.fromisoformat(row["created_at"]),
        decided_at=datetime.fromisoformat(row["decided_at"]) if row["decided_at"] else None,
    )
