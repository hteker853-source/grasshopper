"""Task lifecycle: plan, approve, act, verify, explain, remember."""

from __future__ import annotations

import asyncio
import logging
import os
import time
from pathlib import Path

from grasshopper.browser.controller import BrowserController
from grasshopper.core.budget import BudgetExceeded
from grasshopper.core.explainer import Explainer
from grasshopper.queue.scheduler import parse_when
from grasshopper.schemas import (
    ExplainEvent,
    RiskLevel,
    RunResult,
    Task,
    TaskStatus,
    new_id,
)

log = logging.getLogger("grasshopper.orchestrator")


class Orchestrator:
    def __init__(self, settings, db, queue, planner, executor, verifier, skills, memory, gate, notifier, repair):
        self.settings = settings
        self.db = db
        self.queue = queue
        self.planner = planner
        self.executor = executor
        self.verifier = verifier
        self.skills = skills
        self.memory = memory
        self.gate = gate
        self.notifier = notifier
        self.repair = repair

    def accept(self, text: str, channel: str = "api") -> Task:
        """Normalize any channel into a Task. Schedule phrases are pulled out of the text."""
        parsed = parse_when(text)
        body = parsed.remaining.strip() or text.strip()
        task = Task.create(body, channel=channel, scheduled_at=parsed.scheduled_at, cron=parsed.cron)
        # Keep the original wording so playbooks still match phrases like "in 20 seconds, check news".
        task.text = text.strip()
        return self.queue.enqueue(task)

    async def execute(self, task_id: str) -> RunResult:
        task = self.queue.get(task_id)
        if task is None:
            raise KeyError(task_id)
        if task.status == TaskStatus.queued:
            self.queue.update_status(task_id, TaskStatus.planning)
        run_id = new_id("run_")
        run_dir = Path(self.settings.runs_dir) / run_id
        run_dir.mkdir(parents=True, exist_ok=True)
        explainer = Explainer(run_dir)
        started = time.perf_counter()
        calls_before = len(self.planner.router.calls)
        council_before = self.executor.council.calls
        self._domains = set()
        self.queue.update_status(task_id, TaskStatus.planning, run_id=run_id)
        try:
            plan = await self.planner.plan(task.text, run_id=run_id)
        except BudgetExceeded as exc:
            return await self._finish(
                task, run_id, TaskStatus.failed, 0, 0, str(exc),
                "budget", started, calls_before, council_before, explainer, "",
            )
        except Exception as exc:
            return await self._finish(
                task, run_id, TaskStatus.failed, 0, 0, f"Planning failed: {exc}",
                "llm", started, calls_before, council_before, explainer, "",
            )
        self.queue.update_status(task_id, TaskStatus.running, run_id=run_id)
        variables: dict[str, str] = {}
        ok_steps = 0
        summary_bits: list[str] = []
        async with BrowserController(self.settings, run_dir) as browser:
            browser.visited_hosts = self._domains
            for index, step in enumerate(plan.steps, start=1):
                if step.risk_level == RiskLevel.high:
                    step.requires_approval = True
                if step.requires_approval:
                    shot = await _capture_frame(browser, run_dir / f"approval_{index}_{step.id}.png")
                    approved = await self._await_approval(
                        task_id, step.id, step.reason or step.goal, shot, explainer, plan, step, index,
                    )
                    if not approved:
                        return await self._finish(
                            task, run_id, TaskStatus.cancelled, len(plan.steps), ok_steps,
                            "Approval was rejected or expired", plan.source, started,
                            calls_before, council_before, explainer, "",
                        )
                last = None
                verified = None
                browser.live_goal = step.goal
                pause = float(os.environ.get("LIVE_STEP_PAUSE_SEC") or "0")
                if pause > 0:
                    await asyncio.sleep(pause)
                for attempt in range(1, 4):
                    try:
                        last = await self.executor.execute_step(
                            step,
                            browser=browser,
                            variables=variables,
                            attempt=attempt,
                            stem_prefix=f"step_{index}_try{attempt}",
                            run_id=run_id,
                            task_id=task_id,
                        )
                    except BudgetExceeded as exc:
                        return await self._finish(
                            task, run_id, TaskStatus.failed, len(plan.steps), ok_steps, str(exc),
                            "budget", started, calls_before, council_before, explainer, "",
                        )
                    except Exception as exc:
                        from grasshopper.schemas import ActionResult
                        last = ActionResult(ok=False, detail=str(exc), text=str(exc))
                    page_text = last.text or ""
                    page_html = last.html or ""
                    page_url = last.url or ""
                    if not page_html and browser.driver:
                        page_html = browser.driver.html
                        page_url = browser.driver.url
                        # Side effects such as notify must not hide the page the verifier checks.
                        page_text = _text_of(page_html) or page_text
                    try:
                        verified = await self.verifier.verify(
                            step,
                            url=page_url,
                            text=page_text if page_text else _text_of(page_html),
                            html=page_html,
                            variables=variables,
                            before=last.screenshot_before,
                            after=last.screenshot_after,
                            run_id=run_id,
                        )
                    except BudgetExceeded as exc:
                        return await self._finish(
                            task, run_id, TaskStatus.failed, len(plan.steps), ok_steps, str(exc),
                            "budget", started, calls_before, council_before, explainer, "",
                        )
                    explainer.log(
                        ExplainEvent(
                            step=step.id,
                            action=", ".join(action.type for action in step.actions) or step.goal,
                            reason=step.reason or f"Attempt {attempt} toward: {step.goal}",
                            alternatives_considered=plan.alternatives_considered + ([f"attempt:{attempt}"]),
                            evidence=last.screenshot_after,
                            verifier_result=("pass: " if verified.ok else "fail: ") + verified.reason,
                            model_tier="fast" if verified.model_used else None,
                            attempt=attempt,
                        )
                    )
                    if last.ok and verified.ok:
                        ok_steps += 1
                        if variables:
                            summary_bits.append(step.goal)
                        break
                else:
                    error = f"{step.id}: {last.detail if last else ''} {verified.reason if verified else ''}"
                    try:
                        repair = await self.repair.propose(error, run_id=run_id)
                    except BudgetExceeded as exc:
                        return await self._finish(
                            task, run_id, TaskStatus.failed, len(plan.steps), ok_steps, str(exc),
                            "budget", started, calls_before, council_before, explainer, "",
                        )
                    reason = (
                        f"Stuck on {step.goal}. {repair['explanation']} "
                        f"Patch: {repair['patch_path']} (temp check passed={repair['temp_test_passed']})."
                    )
                    stuck_shot = last.screenshot_after if last else None
                    approval = self.gate.create(
                        task_id=task_id, step_id=step.id, reason=reason, screenshot=stuck_shot,
                    )
                    await self.notifier.notify(
                        reason,
                        kind="approval",
                        payload=_approval_payload(
                            approval_id=approval.id,
                            task_id=task_id,
                            run_id=run_id,
                            screenshot=stuck_shot,
                        ),
                    )
                    self.queue.update_status(task_id, TaskStatus.waiting_approval, run_id=run_id)
                    return await self._finish(
                        task, run_id, TaskStatus.waiting_approval, len(plan.steps), ok_steps,
                        reason, plan.source, started, calls_before, council_before, explainer,
                        repair["patch_path"],
                    )
        summary = _summary(task.text, variables, summary_bits)
        self.memory.add("task_summary", f"{task.text}\n{summary}")
        self.skills.record_success(task.text, plan)
        await self.notifier.notify(summary, kind="done", payload={"run_id": run_id, "task_id": task_id})
        if task.cron:
            self._requeue_cron(task)
        return await self._finish(
            task, run_id, TaskStatus.done, len(plan.steps), ok_steps, summary,
            plan.source, started, calls_before, council_before, explainer, "",
        )

    async def _await_approval(self, task_id, step_id, reason, screenshot, explainer, plan, step, index) -> bool:
        approval = self.gate.create(task_id=task_id, step_id=step_id, reason=reason, screenshot=screenshot)
        await self.notifier.notify(
            f"Approval needed: {reason}",
            kind="approval",
            payload=_approval_payload(approval_id=approval.id, task_id=task_id, screenshot=screenshot),
        )
        self.queue.update_status(task_id, TaskStatus.waiting_approval)
        explainer.log(
            ExplainEvent(
                step=step.id,
                action="approval",
                reason=reason or "This step can spend money, share, or leave the machine.",
                alternatives_considered=plan.alternatives_considered,
                verifier_result="waiting",
                attempt=0,
            )
        )
        decision = await self.gate.wait(approval.id)
        return decision == "approved"

    def _requeue_cron(self, task: Task) -> None:
        follow = Task.create(task.text, channel=task.channel, cron=task.cron, scheduled_at=None)
        # Next fire is left to a future scheduler tick; store cron and a far marker is unnecessary.
        # The row stays queued and claim_next would grab it immediately, so park it as done's sibling
        # only when the text still contains a daily phrase — claim_next ignores cron-only future jobs
        # if scheduled_at is in the future. We set scheduled_at to tomorrow to avoid a tight loop.
        from datetime import datetime, timedelta, timezone
        follow.scheduled_at = datetime.now(timezone.utc) + timedelta(days=1)
        self.queue.enqueue(follow)

    async def _finish(
        self, task, run_id, status, total, ok_steps, summary, source, started,
        calls_before, council_before, explainer, patch,
    ) -> RunResult:
        llm_calls = (len(self.planner.router.calls) - calls_before) + (self.executor.council.calls - council_before)
        rate = (ok_steps / total) if total else 0.0
        duration_ms = int((time.perf_counter() - started) * 1000)
        result = {
            "run_id": run_id,
            "summary": summary,
            "success_rate": rate,
            "steps_total": total,
            "steps_ok": ok_steps,
            "llm_calls": llm_calls,
            "plan_source": source,
            "duration_ms": duration_ms,
            "status": status.value,
            "patch": patch,
        }
        self.queue.update_status(task.id, status, result=result, run_id=run_id)
        run_path = Path(self.settings.runs_dir) / run_id
        run_path.mkdir(parents=True, exist_ok=True)
        (run_path / "result.json").write_text(
            __import__("json").dumps(result, indent=2), encoding="utf-8"
        )
        _write_run_blast(self, run_path, run_id, duration_ms)
        return RunResult(
            run_id=run_id,
            task_id=task.id,
            status=status,
            steps_total=total,
            steps_ok=ok_steps,
            success_rate=rate,
            llm_calls=llm_calls,
            duration_ms=duration_ms,
            summary=summary,
            plan_source=source,
            artifacts=[str(explainer.path)] + ([patch] if patch else []),
        )


def _write_run_blast(orchestrator, run_path: Path, run_id: str, duration_ms: int) -> None:
    try:
        from grasshopper.realweb.blast import runner_label, write_blast

        files = sorted(path.name for path in run_path.iterdir() if path.is_file())
        write_blast(
            run_path / "blast_radius.json",
            files=files,
            domains=sorted(getattr(orchestrator, "_domains", set())),
            seconds=duration_ms / 1000,
            cost_usd=float(orchestrator.planner.router.budget.run_actual.get(run_id, 0.0)),
            runner=runner_label(),
        )
    except Exception:
        log.warning("blast radius report failed", exc_info=True)


def _approval_payload(*, approval_id: str, task_id: str, run_id: str | None = None, screenshot: str | None = None) -> dict:
    payload = {"approval_id": approval_id, "task_id": task_id}
    if run_id:
        payload["run_id"] = run_id
    if screenshot:
        payload["screenshot"] = screenshot
    return payload


async def _capture_frame(browser, dest: Path) -> str | None:
    driver = getattr(browser, "driver", None)
    if driver is None:
        return None
    try:
        await driver.screenshot(dest)
    except Exception:
        log.warning("Could not capture the frame for an approval")
        return None
    return str(dest) if dest.is_file() else None


def _text_of(html: str) -> str:
    from grasshopper.browser.controller import _visible_text
    return _visible_text(html)


def _summary(task_text: str, variables: dict, bits: list[str]) -> str:
    parts = [f"Finished: {task_text[:180]}"]
    if variables.get("council_winner"):
        parts.append("Winner: " + variables["council_winner"][:500])
    if variables.get("tx_hash"):
        parts.append("Receipt: " + variables["tx_hash"])
    for key, value in variables.items():
        if key in {"council_winner", "tx_hash"}:
            continue
        if value and len(value) < 400:
            parts.append(f"{key}: {value}")
    if not variables and bits:
        parts.append("; ".join(bits))
    return "\n".join(parts)[:2000]
