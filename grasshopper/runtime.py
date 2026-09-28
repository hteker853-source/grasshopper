"""Process-wide wiring. Channels, MCP, and the CLI all enter through here."""

from __future__ import annotations

import asyncio
import logging

from grasshopper.approvals.gate import ApprovalGate
from grasshopper.config import Settings, get_settings, reset_settings
from grasshopper.core.council import Council
from grasshopper.core.executor import Executor
from grasshopper.core.orchestrator import Orchestrator
from grasshopper.core.planner import Planner
from grasshopper.core.router import Router
from grasshopper.core.self_repair import SelfRepair
from grasshopper.core.verifier import Verifier
from grasshopper.db import Database
from grasshopper.memory.skills import SkillLibrary
from grasshopper.memory.store import MemoryStore
from grasshopper.providers.factory import build_notifier, build_search, build_stt, build_wallet
from grasshopper.queue.task_queue import TaskQueue

log = logging.getLogger("grasshopper.runtime")


class AppContext:
    def __init__(self, settings: Settings):
        self.settings = settings
        self.db = Database(settings.db_path)
        self.memory = MemoryStore(self.db)
        self.skills = SkillLibrary(self.db, settings.playbook_dir)
        self.queue = TaskQueue(self.db)
        self.router = Router(settings, self.db)
        self.notifier = build_notifier(settings)
        self.router.notifier = self.notifier
        self.planner = Planner(self.skills, self.memory, self.router)
        self.council = Council(settings, settings.runs_dir)
        self.wallet = build_wallet(settings, self.db)
        self.gate = ApprovalGate(self.db, settings.approval_timeout_sec)
        self.repair = SelfRepair(settings, self.router)
        self.executor = Executor(settings, self.wallet, self.notifier, self.council, self.memory)
        self.verifier = Verifier(self.router)
        self.orchestrator = Orchestrator(
            settings,
            self.db,
            self.queue,
            self.planner,
            self.executor,
            self.verifier,
            self.skills,
            self.memory,
            self.gate,
            self.notifier,
            self.repair,
        )
        self.stt = build_stt(settings)
        self.search = build_search(settings)
        self.stop = asyncio.Event()
        self._worker: asyncio.Task | None = None
        self._inflight: set[asyncio.Task] = set()

    async def worker_loop(self) -> None:
        while not self.stop.is_set():
            self._inflight = {job for job in self._inflight if not job.done()}
            if len(self._inflight) < self.settings.max_concurrent_tasks:
                task = self.queue.claim_next()
                if task is not None:
                    self._inflight.add(asyncio.create_task(self._safe_execute(task.id)))
                    continue
            await asyncio.sleep(0.3)

    async def _safe_execute(self, task_id: str) -> None:
        try:
            await self.orchestrator.execute(task_id)
        except Exception:
            log.exception("task %s crashed", task_id)

    def start_worker(self) -> None:
        if self._worker is None or self._worker.done():
            self.stop.clear()
            self._worker = asyncio.create_task(self.worker_loop())

    async def stop_worker(self) -> None:
        self.stop.set()
        for job in list(self._inflight):
            job.cancel()
        if self._worker:
            self._worker.cancel()
            try:
                await self._worker
            except asyncio.CancelledError:
                pass
            self._worker = None

    def close(self) -> None:
        self.db.close()


_context: AppContext | None = None


def get_context() -> AppContext:
    global _context
    if _context is None:
        _context = AppContext(get_settings())
    return _context


def set_context(ctx: AppContext) -> AppContext:
    global _context
    _context = ctx
    return _context


def reset_context() -> None:
    global _context
    if _context is not None:
        _context.close()
        _context = None
    reset_settings()

