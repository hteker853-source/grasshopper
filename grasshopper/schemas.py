"""Shared pydantic models. Every channel produces a Task; every run produces a RunResult."""

from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import Any
from uuid import uuid4

from pydantic import BaseModel, Field


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


def new_id(prefix: str = "") -> str:
    body = uuid4().hex[:12]
    return f"{prefix}{body}" if prefix else body


class RiskLevel(str, Enum):
    low = "low"
    high = "high"


class TaskStatus(str, Enum):
    queued = "queued"
    planning = "planning"
    running = "running"
    waiting_approval = "waiting_approval"
    done = "done"
    failed = "failed"
    cancelled = "cancelled"


class Action(BaseModel):
    type: str
    selector: str | None = None
    url: str | None = None
    text: str | None = None
    key: str | None = None
    value: str | None = None
    timeout_ms: int = 8000
    save_as: str | None = None
    amount_sol: float | None = None
    memo: str | None = None
    question: str | None = None
    file_path: str | None = None
    reason: str | None = None


class Step(BaseModel):
    id: str
    goal: str
    site: str | None = None
    action_hint: str | None = None
    success_criteria: str
    risk_level: RiskLevel = RiskLevel.low
    requires_approval: bool = False
    actions: list[Action] = Field(default_factory=list)
    reason: str = ""


class Plan(BaseModel):
    steps: list[Step]
    source: str  # playbook | llm
    playbook_id: str | None = None
    alternatives_considered: list[str] = Field(default_factory=list)


class Task(BaseModel):
    id: str
    text: str
    status: TaskStatus = TaskStatus.queued
    priority: int = 0
    scheduled_at: datetime | None = None
    cron: str | None = None
    created_at: datetime = Field(default_factory=utcnow)
    channel: str = "api"
    result: dict[str, Any] | None = None
    run_id: str | None = None

    @classmethod
    def create(cls, text: str, channel: str = "api", **kwargs: Any) -> "Task":
        return cls(id=new_id("task_"), text=text.strip(), channel=channel, **kwargs)


class ApprovalDecision(str, Enum):
    pending = "pending"
    approved = "approved"
    rejected = "rejected"
    expired = "expired"


class Approval(BaseModel):
    id: str
    task_id: str
    step_id: str | None = None
    reason: str
    status: ApprovalDecision = ApprovalDecision.pending
    screenshot: str | None = None
    created_at: datetime = Field(default_factory=utcnow)
    decided_at: datetime | None = None


class ActionResult(BaseModel):
    ok: bool
    detail: str = ""
    url: str = ""
    text: str = ""
    html: str = ""
    screenshot_before: str | None = None
    screenshot_after: str | None = None
    data: dict[str, Any] = Field(default_factory=dict)


class VerifyResult(BaseModel):
    ok: bool
    reason: str
    change_percent: float | None = None
    model_used: bool = False


class ExplainEvent(BaseModel):
    step: str
    action: str
    reason: str
    alternatives_considered: list[str] = Field(default_factory=list)
    evidence: str | None = None
    verifier_result: str = ""
    model_tier: str | None = None
    attempt: int = 1
    ts: str = ""


class RunResult(BaseModel):
    run_id: str
    task_id: str
    status: TaskStatus
    steps_total: int
    steps_ok: int
    success_rate: float
    llm_calls: int
    duration_ms: int
    summary: str
    plan_source: str = ""
    artifacts: list[str] = Field(default_factory=list)


class LLMResponse(BaseModel):
    text: str
    provider: str
    tier: str
    tokens: int = 0
    cost_usd: float = 0.0
    duration_ms: int = 0
