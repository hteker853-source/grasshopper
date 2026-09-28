"""SQLite connection shared by the queue, memory, skills, approvals, and wallet."""

from __future__ import annotations

import sqlite3
from pathlib import Path

SCHEMA = """
CREATE TABLE IF NOT EXISTS tasks (
    id TEXT PRIMARY KEY,
    text TEXT NOT NULL,
    status TEXT NOT NULL,
    priority INTEGER DEFAULT 0,
    scheduled_at TEXT,
    cron TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT,
    channel TEXT,
    result_json TEXT,
    run_id TEXT
);
CREATE TABLE IF NOT EXISTS approvals (
    id TEXT PRIMARY KEY,
    task_id TEXT,
    step_id TEXT,
    reason TEXT,
    status TEXT,
    screenshot TEXT,
    created_at TEXT,
    decided_at TEXT
);
CREATE TABLE IF NOT EXISTS memories (
    id TEXT PRIMARY KEY,
    kind TEXT,
    text TEXT,
    embedding BLOB,
    created_at TEXT
);
CREATE TABLE IF NOT EXISTS skills (
    id TEXT PRIMARY KEY,
    name TEXT,
    triggers TEXT,
    site TEXT,
    body_yaml TEXT,
    status TEXT,
    success_count INTEGER DEFAULT 0,
    created_at TEXT
);
CREATE TABLE IF NOT EXISTS wallet_ledger (
    id TEXT PRIMARY KEY,
    amount_sol REAL,
    direction TEXT,
    memo TEXT,
    tx_hash TEXT,
    created_at TEXT,
    task_id TEXT
);
CREATE TABLE IF NOT EXISTS llm_calls (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    run_id TEXT,
    tier TEXT,
    provider TEXT,
    tokens INTEGER,
    cost_usd REAL,
    duration_ms INTEGER,
    created_at TEXT
);
"""


class Database:
    def __init__(self, path: Path):
        path.parent.mkdir(parents=True, exist_ok=True)
        self.path = path
        self.conn = sqlite3.connect(str(path), check_same_thread=False, isolation_level=None)
        self.conn.row_factory = sqlite3.Row
        self.conn.execute("PRAGMA journal_mode=WAL")
        self.conn.execute("PRAGMA busy_timeout=4000")
        self.conn.executescript(SCHEMA)

    def close(self) -> None:
        self.conn.close()
