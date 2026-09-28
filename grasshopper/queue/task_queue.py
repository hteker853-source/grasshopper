"""SQLite task queue. claim_next is the only way a worker takes a job."""

from __future__ import annotations

import json
from datetime import datetime, timezone

from grasshopper.db import Database
from grasshopper.schemas import Task, TaskStatus


def _iso(value: datetime | None) -> str | None:
    if value is None:
        return None
    if value.tzinfo is None:
        value = value.replace(tzinfo=timezone.utc)
    return value.isoformat()


def _parse(value: str | None) -> datetime | None:
    if not value:
        return None
    return datetime.fromisoformat(value)


class TaskQueue:
    def __init__(self, db: Database):
        self.db = db

    def enqueue(self, task: Task) -> Task:
        now = datetime.now(timezone.utc).isoformat()
        self.db.conn.execute(
            "INSERT INTO tasks (id, text, status, priority, scheduled_at, cron, created_at, updated_at, channel, result_json, run_id) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (
                task.id,
                task.text,
                task.status.value,
                task.priority,
                _iso(task.scheduled_at),
                task.cron,
                _iso(task.created_at) or now,
                now,
                task.channel,
                json.dumps(task.result) if task.result else None,
                task.run_id,
            ),
        )
        return task

    def get(self, task_id: str) -> Task | None:
        row = self.db.conn.execute("SELECT * FROM tasks WHERE id=?", (task_id,)).fetchone()
        if row is None:
            return None
        return self._row(row)

    def list_recent(self, limit: int = 30) -> list[Task]:
        rows = self.db.conn.execute("SELECT * FROM tasks ORDER BY created_at DESC LIMIT ?", (limit,)).fetchall()
        return [self._row(row) for row in rows]

    def all(self) -> list[Task]:
        rows = self.db.conn.execute("SELECT * FROM tasks ORDER BY created_at ASC").fetchall()
        return [self._row(row) for row in rows]

    def update_status(self, task_id: str, status: TaskStatus, *, result: dict | None = None, run_id: str | None = None) -> None:
        now = datetime.now(timezone.utc).isoformat()
        if result is None and run_id is None:
            self.db.conn.execute(
                "UPDATE tasks SET status=?, updated_at=? WHERE id=?",
                (status.value, now, task_id),
            )
            return
        current = self.get(task_id)
        merged = current.result if current and current.result else {}
        if result:
            merged.update(result)
        self.db.conn.execute(
            "UPDATE tasks SET status=?, updated_at=?, result_json=?, run_id=COALESCE(?, run_id) WHERE id=?",
            (status.value, now, json.dumps(merged), run_id, task_id),
        )

    def claim_next(self, now: datetime | None = None) -> Task | None:
        moment = (now or datetime.now(timezone.utc)).isoformat()
        row = self.db.conn.execute(
            "SELECT id FROM tasks WHERE status='queued' AND (scheduled_at IS NULL OR scheduled_at<=?) "
            "ORDER BY priority DESC, created_at ASC LIMIT 1",
            (moment,),
        ).fetchone()
        if row is None:
            return None
        cur = self.db.conn.execute(
            "UPDATE tasks SET status='planning', updated_at=? WHERE id=? AND status='queued'",
            (moment, row["id"]),
        )
        if cur.rowcount != 1:
            return None
        return self.get(row["id"])

    def queued_count(self) -> int:
        row = self.db.conn.execute(
            "SELECT COUNT(*) AS n FROM tasks WHERE status IN ('queued', 'planning', 'running', 'waiting_approval')"
        ).fetchone()
        return int(row["n"])

    def running_count(self) -> int:
        row = self.db.conn.execute(
            "SELECT COUNT(*) AS n FROM tasks WHERE status IN ('planning', 'running')"
        ).fetchone()
        return int(row["n"])

    def _row(self, row) -> Task:
        result = json.loads(row["result_json"]) if row["result_json"] else None
        return Task(
            id=row["id"],
            text=row["text"],
            status=TaskStatus(row["status"]),
            priority=row["priority"],
            scheduled_at=_parse(row["scheduled_at"]),
            cron=row["cron"],
            created_at=_parse(row["created_at"]) or datetime.now(timezone.utc),
            channel=row["channel"] or "api",
            result=result,
            run_id=row["run_id"],
        )
