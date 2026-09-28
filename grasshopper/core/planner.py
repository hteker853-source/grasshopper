"""Playbook first. The strong model is only asked when nothing in the library matches."""

from __future__ import annotations

import json
import logging
import re

from pydantic import ValidationError

from grasshopper.memory.skills import SkillLibrary
from grasshopper.memory.store import MemoryStore
from grasshopper.schemas import Plan

log = logging.getLogger("grasshopper.planner")


class Planner:
    def __init__(self, skills: SkillLibrary, memory: MemoryStore, router):
        self.skills = skills
        self.memory = memory
        self.router = router

    async def plan(self, task_text: str, *, run_id: str | None = None) -> Plan:
        skill = self.skills.match(task_text)
        if skill is not None:
            plan = skill.to_plan()
            plan.alternatives_considered = [f"playbook:{skill.id}", "llm_skipped"]
            log.info("Plan from playbook %s (LLM calls skipped)", skill.id)
            return plan
        memories = self.memory.search(task_text, k=5)
        context = "\n".join(f"- ({item['kind']}) {item['text']}" for item in memories) or "(none)"
        prompt = (
            "Return ONLY JSON for a plan with key steps (list of objects with id, goal, site, "
            "success_criteria, risk_level, requires_approval, reason, actions). "
            "actions use type goto|click|type|read_text|notify and url may contain {sandbox}.\n"
            f"Task: {task_text}\nMemories:\n{context}\nJSON:"
        )
        last_error = "no response"
        for _ in range(3):
            response = await self.router.complete("strong", prompt, run_id=run_id)
            try:
                plan = _parse_plan(response.text)
                plan.source = "llm"
                plan.alternatives_considered = ["playbook:none", f"llm:{response.provider}"]
                return plan
            except (json.JSONDecodeError, ValidationError, KeyError, TypeError) as exc:
                last_error = str(exc)
                prompt = prompt + f"\nThe previous JSON was invalid ({last_error}). Return ONLY JSON."
        raise RuntimeError(f"Planner could not produce a valid plan: {last_error}")


def _parse_plan(text: str) -> Plan:
    match = re.search(r"\{.*\}", text, re.S)
    if not match:
        raise json.JSONDecodeError("no object", text, 0)
    payload = json.loads(match.group(0))
    payload["source"] = payload.get("source") or "llm"
    return Plan.model_validate(payload)
