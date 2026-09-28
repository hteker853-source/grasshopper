"""Deterministic offline LLM. Keyword plans, council personalities, and a call counter."""

from __future__ import annotations

import hashlib
import time

_PERSONALITIES = {
    "mock_a": "practical founder who ships the smallest public demo",
    "mock_b": "skeptical engineer who cuts scope that cannot be verified",
    "mock_c": "growth marketer who wants a 3-minute story a judge can retell",
    "mock_d": "designer who insists the mobile approval screen is the product",
    "mock_e": "security reviewer who blocks mainnet keys and live payments",
    "mock_f": "investor who funds only one wedge with a measurable success rate",
}


class MockLLM:
    name = "mock"
    calls = 0

    def __init__(self, name: str = "mock", personality: str | None = None):
        self.name = name
        self.personality = personality or _PERSONALITIES.get(name, "calm generalist")

    def configured(self) -> bool:
        return True

    async def complete(self, prompt: str, *, tier: str = "fast", system: str = "") -> str:
        MockLLM.calls += 1
        started = time.perf_counter()
        text = self._answer(prompt)
        _ = int((time.perf_counter() - started) * 1000)
        return text

    def _answer(self, prompt: str) -> str:
        if prompt.startswith("REALWEB_DECIDE"):
            from grasshopper.realweb.heuristic import decide_json

            return decide_json(prompt)
        lower = prompt.lower()
        if "was this step successful" in lower or "step successful" in lower:
            if "evidence_ok=yes" in lower:
                return "YES"
            return "NO"
        if "vote for the single strongest" in lower or "reply with vote" in lower:
            return "VOTE: 1"
        if "devil's advocate" in lower or lower.startswith("write a devil"):
            return (
                "This idea cannot win if the demo needs a paid API key or a live payment. "
                "Judges will only see what runs offline against the sandbox."
            )
        if "single strongest" in lower or "final idea" in lower or "strengthen your idea" in lower:
            return self._personality_idea(prompt)
        if "unified diff" in lower or "produce a unified diff" in lower:
            return (
                "--- a/playbooks/broken_export.yaml\n"
                "+++ b/playbooks/broken_export.yaml\n"
                "@@\n"
                "- selector: \"[data-testid=export-btn]\"\n"
                "+ selector: \"[data-testid=export-btn-renamed]\"\n"
            )
        if "plan" in lower and "json" in lower:
            return self._plan_json(lower)
        digest = hashlib.sha256(prompt.encode()).hexdigest()[:8]
        return f"{self.name} ({self.personality}): noted {digest}. Prefer a verifiable sandbox demo."

    def _personality_idea(self, prompt: str) -> str:
        if "security" in self.personality:
            return "Ship the approval-gated devnet wallet demo and refuse mainnet. One payment, one receipt."
        if "marketer" in self.personality or "growth" in self.personality:
            return "Ship the Alexa+ MCP demo: a phone speaks a task, the agent runs it, the timeline explains why."
        if "designer" in self.personality:
            return "Ship the mobile approval screen with the screenshot, the reason, and two giant buttons."
        if "investor" in self.personality:
            return "Ship one wedge: playbook replay at 98% step success, shown live on the shop listings task."
        if "skeptical" in self.personality:
            return "Ship the verifier plus the broken-selector repair. Cut every provider that is not mocked."
        return (
            "Ship Grasshopper's sandbox worker: research on ai-alpha, explain every step, "
            "and submit the Alexa+ MCP track because it already runs."
        )

    def _plan_json(self, lower: str) -> str:
        # Fallback only when no playbook matched. Kept tiny and valid.
        if "news" in lower or "headline" in lower:
            site = "news"
            goal = "Read the news headlines"
            criteria = "text:trend"
        else:
            site = "news"
            goal = "Open the sandbox news desk and report the top headline"
            criteria = "text:trend"
        return (
            '{"steps":[{"id":"read","goal":"%s","site":"%s","success_criteria":"%s",'
            '"risk_level":"low","requires_approval":false,"reason":"No playbook matched; '
            'read a deterministic sandbox page.","actions":[{"type":"goto","url":"{sandbox}/%s"},'
            '{"type":"read_text","selector":"body","save_as":"page"},'
            '{"type":"notify","text":"Headline scan:\\n{{var:page}}"}]}],"source":"llm"}'
            % (goal, site, criteria, site)
        )
