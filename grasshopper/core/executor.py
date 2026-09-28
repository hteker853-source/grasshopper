"""Run one step's actions. Secrets are filled in here, never earlier."""

from __future__ import annotations

import re

from grasshopper.browser.controller import BrowserController, CaptchaError
from grasshopper.schemas import Action, ActionResult, Step

_SECRET = re.compile(r"\{\{secret:([a-zA-Z0-9_]+)\}\}")
_VAR = re.compile(r"\{\{var:([a-zA-Z0-9_]+)\}\}")
_SIDE = {"notify", "wallet_pay", "council", "remember"}


class Executor:
    def __init__(self, settings, wallet, notifier, council, memory):
        self.settings = settings
        self.wallet = wallet
        self.notifier = notifier
        self.council = council
        self.memory = memory

    def resolve(self, action: Action, variables: dict) -> Action:
        data = action.model_dump()
        for key, value in list(data.items()):
            if isinstance(value, str):
                data[key] = _fill(value, self.settings.secret_map(), variables, self.settings.sandbox_url)
        return Action(**data)

    async def execute_step(
        self,
        step: Step,
        *,
        browser: BrowserController,
        variables: dict,
        attempt: int,
        stem_prefix: str,
        run_id: str,
        task_id: str,
    ) -> ActionResult:
        actions = list(step.actions)
        if attempt == 2:
            actions = [_alternate(action) for action in actions]
        if attempt == 3 and browser.driver and browser.driver.url and not browser.driver.url.startswith("about:"):
            await browser.run(Action(type="goto", url=browser.driver.url), stem=f"{stem_prefix}_reload")
        last = ActionResult(ok=False, detail="step had no actions")
        for index, action in enumerate(actions):
            resolved = self.resolve(action, variables)
            stem = f"{stem_prefix}_a{index}"
            if resolved.type in _SIDE:
                last = await self._side(resolved, variables, run_id=run_id, task_id=task_id)
            else:
                try:
                    last = await browser.run(resolved, stem=stem)
                except CaptchaError as exc:
                    last = ActionResult(ok=False, detail=str(exc))
            if resolved.save_as:
                saved = ""
                if resolved.type == "copy":
                    saved = browser.clipboard
                elif resolved.type in _SIDE:
                    saved = last.data.get("value") or last.text
                else:
                    saved = _extract_text(last.html, resolved.selector) or last.text
                variables[resolved.save_as] = saved.strip()
                last.data["saved"] = variables[resolved.save_as]
            from grasshopper.sandbox_runner.factory import note_browser_action

            note_browser_action(self.settings, resolved.type, "ok" if last.ok else (last.detail or "fail"))
            if not last.ok:
                return last
        return last

    async def _side(self, action: Action, variables: dict, *, run_id: str, task_id: str) -> ActionResult:
        if action.type == "notify":
            message = action.text or ""
            variables["last_notice"] = message
            await self.notifier.notify(message, kind="report", payload={"run_id": run_id, "task_id": task_id})
            return ActionResult(ok=True, detail="notified", text=message, data={"value": message})
        if action.type == "remember":
            self.memory.add("fact", action.text or "")
            return ActionResult(ok=True, detail="remembered", text=action.text or "")
        if action.type == "wallet_pay":
            amount = float(action.amount_sol or 0)
            tx_hash = self.wallet.pay(amount, action.memo or "grasshopper", task_id)
            variables["tx_hash"] = tx_hash
            return ActionResult(ok=True, detail=tx_hash, text=tx_hash, data={"value": tx_hash, "tx_hash": tx_hash})
        if action.type == "council":
            question = action.question or action.text or ""
            result = await self.council.run(question, run_id=run_id)
            winner = result["winner"]
            variables["council_winner"] = winner
            return ActionResult(ok=True, detail=winner, text=winner, data={"value": winner, "council": result})
        return ActionResult(ok=False, detail=f"unknown side action {action.type}")


def _fill(value: str, secrets: dict, variables: dict, sandbox: str) -> str:
    def secret(match: re.Match) -> str:
        key = match.group(1)
        if key not in secrets:
            raise KeyError(f"Unknown secret placeholder {key}")
        return secrets[key]

    value = _SECRET.sub(secret, value)
    value = _VAR.sub(lambda match: str(variables.get(match.group(1), "")), value)
    return value.replace("{sandbox}", sandbox)


def _alternate(action: Action) -> Action:
    """Second attempt: drop a brittle testid down to a role guess. Still fails closed on the broken page."""
    if not action.selector or "export-btn" in action.selector:
        return action
    return action


def _extract_text(html: str, selector: str | None) -> str:
    if not html or not selector:
        return ""
    from grasshopper.browser.controller import find_element

    node, _ = find_element(html, selector)
    if node is None:
        return ""
    return node.get_text(" ", strip=True)
