"""Playbook loader. YAML files are approved skills; learned plans start as candidates."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

import yaml

from grasshopper.db import Database
from grasshopper.schemas import Action, Plan, RiskLevel, Step, new_id


class Skill:
    def __init__(self, skill_id: str, name: str, triggers: list[str], site: str, steps: list[dict], status: str, success_count: int):
        self.id = skill_id
        self.name = name
        self.triggers = triggers
        self.site = site
        self.steps = steps
        self.status = status
        self.success_count = success_count

    def to_plan(self) -> Plan:
        steps = []
        for raw in self.steps:
            actions = [Action(**action) for action in raw.get("actions", [])]
            steps.append(
                Step(
                    id=raw["id"],
                    goal=raw["goal"],
                    site=raw.get("site") or self.site,
                    action_hint=raw.get("action_hint"),
                    success_criteria=raw["success_criteria"],
                    risk_level=RiskLevel(raw.get("risk_level", "low")),
                    requires_approval=bool(raw.get("requires_approval", False)),
                    actions=actions,
                    reason=raw.get("reason", ""),
                )
            )
        return Plan(
            steps=steps,
            source="playbook",
            playbook_id=self.id,
            alternatives_considered=[f"playbook:{self.id}"],
        )


def score_skill(skill: Skill, text: str) -> int:
    haystack = text.lower()
    total = 0
    for trigger in skill.triggers:
        needle = trigger.lower().strip()
        if needle and needle in haystack:
            total += len(needle)
    return total


class SkillLibrary:
    def __init__(self, db: Database, playbook_dir: Path):
        self.db = db
        self.playbook_dir = playbook_dir
        self.skills: list[Skill] = []
        self.reload()

    def reload(self) -> None:
        self.skills = []
        if self.playbook_dir.exists():
            for path in sorted(self.playbook_dir.glob("*.yaml")):
                self._add_yaml(path.read_text(encoding="utf-8"), status="approved", success_count=2)
        rows = self.db.conn.execute("SELECT id, name, triggers, site, body_yaml, status, success_count FROM skills").fetchall()
        for row in rows:
            self._add_yaml(row["body_yaml"], status=row["status"], success_count=row["success_count"], skill_id=row["id"])

    def _add_yaml(self, body: str, *, status: str, success_count: int, skill_id: str | None = None) -> None:
        data = yaml.safe_load(body)
        if not data:
            return
        skill = Skill(
            skill_id=skill_id or data["id"],
            name=data.get("name", data["id"]),
            triggers=list(data.get("triggers", [])),
            site=data.get("site", ""),
            steps=list(data.get("steps", [])),
            status=status,
            success_count=success_count,
        )
        self.skills = [existing for existing in self.skills if existing.id != skill.id]
        self.skills.append(skill)

    def match(self, text: str, *, min_score: int = 6) -> Skill | None:
        ranked = sorted(self.skills, key=lambda skill: score_skill(skill, text), reverse=True)
        if not ranked:
            return None
        best = ranked[0]
        if score_skill(best, text) < min_score:
            return None
        # Prefer an approved skill when scores tie.
        tied = [skill for skill in ranked if score_skill(skill, text) == score_skill(best, text)]
        approved = [skill for skill in tied if skill.status == "approved"]
        return approved[0] if approved else tied[0]

    def record_success(self, task_text: str, plan: Plan) -> None:
        if plan.source != "llm":
            skill = self.match(task_text)
            if skill:
                skill.success_count += 1
            return
        triggers = _triggers_from_text(task_text)
        existing = self.match(task_text, min_score=6)
        body = _plan_to_yaml(task_text, triggers, plan)
        if existing and existing.status != "approved" and existing.id.startswith("learned_"):
            existing.success_count += 1
            status = "approved" if existing.success_count >= 2 else "candidate"
            existing.status = status
            self.db.conn.execute(
                "UPDATE skills SET success_count=?, status=?, body_yaml=? WHERE id=?",
                (existing.success_count, status, body, existing.id),
            )
            return
        skill_id = "learned_" + new_id()
        now = datetime.now(timezone.utc).isoformat()
        self.db.conn.execute(
            "INSERT INTO skills (id, name, triggers, site, body_yaml, status, success_count, created_at) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (skill_id, task_text[:80], ",".join(triggers), plan.steps[0].site if plan.steps else "", body, "candidate", 1, now),
        )
        self._add_yaml(body, status="candidate", success_count=1, skill_id=skill_id)


def _triggers_from_text(text: str) -> list[str]:
    cleaned = " ".join(text.lower().split())
    return [cleaned[:120]] if cleaned else ["task"]


def _plan_to_yaml(task_text: str, triggers: list[str], plan: Plan) -> str:
    payload = {
        "id": "learned",
        "name": task_text[:80],
        "triggers": triggers,
        "site": plan.steps[0].site if plan.steps else "",
        "steps": [step.model_dump(mode="json") for step in plan.steps],
    }
    return yaml.safe_dump(payload, sort_keys=False)
