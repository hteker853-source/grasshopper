"""Memories with a hashing embedder (512-d) and cosine retrieval."""

from __future__ import annotations

import hashlib
import re
from datetime import datetime, timezone

import numpy as np

from grasshopper.db import Database
from grasshopper.schemas import new_id

DIM = 512


def embed(text: str, dim: int = DIM) -> np.ndarray:
    vector = np.zeros(dim, dtype=np.float32)
    tokens = re.findall(r"[a-z0-9]+", text.lower())
    for token in tokens:
        digest = hashlib.sha256(token.encode()).digest()
        index = int.from_bytes(digest[:4], "little") % dim
        sign = 1.0 if digest[4] % 2 == 0 else -1.0
        vector[index] += sign
    norm = float(np.linalg.norm(vector))
    if norm > 0:
        vector /= norm
    return vector


class MemoryStore:
    def __init__(self, db: Database):
        self.db = db

    def add(self, kind: str, text: str) -> str:
        memory_id = new_id("mem_")
        blob = embed(text).tobytes()
        now = datetime.now(timezone.utc).isoformat()
        self.db.conn.execute(
            "INSERT INTO memories (id, kind, text, embedding, created_at) VALUES (?, ?, ?, ?, ?)",
            (memory_id, kind, text, blob, now),
        )
        return memory_id

    def search(self, query: str, k: int = 5) -> list[dict]:
        query_vec = embed(query)
        rows = self.db.conn.execute("SELECT id, kind, text, embedding, created_at FROM memories").fetchall()
        scored = []
        for row in rows:
            vector = np.frombuffer(row["embedding"], dtype=np.float32)
            if vector.size != query_vec.size:
                continue
            score = float(np.dot(query_vec, vector))
            scored.append((score, row))
        scored.sort(key=lambda item: item[0], reverse=True)
        return [
            {"id": row["id"], "kind": row["kind"], "text": row["text"], "score": score, "created_at": row["created_at"]}
            for score, row in scored[:k]
        ]
