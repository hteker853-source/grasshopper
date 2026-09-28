"""Step checks: criteria, then the OpenCV diff, then an optional fast-model yes/no."""

from __future__ import annotations

from grasshopper.browser.controller import selector_exists
from grasshopper.browser.vision import change_percent
from grasshopper.schemas import Step, VerifyResult


def check_criteria(criteria: str, *, url: str, text: str, html: str, variables: dict) -> tuple[bool, str]:
    if not criteria or criteria.strip() in {"ok", "always"}:
        return True, "no criteria"
    failed = []
    for part in [piece.strip() for piece in criteria.split("&&")]:
        if not part:
            continue
        if part == "changed":
            continue
        if part.startswith("text:"):
            needle = part[5:]
            if needle.lower() not in text.lower():
                failed.append(f"missing text {needle!r}")
        elif part.startswith("url:"):
            needle = part[4:]
            if needle not in url:
                failed.append(f"url {url!r} lacks {needle!r}")
        elif part.startswith("selector:"):
            sel = part[9:]
            if not selector_exists(html, sel):
                failed.append(f"missing selector {sel}")
        elif part.startswith("var:"):
            key = part[4:]
            if not variables.get(key):
                failed.append(f"empty var {key}")
        else:
            if part not in text and part not in url:
                failed.append(f"missing {part!r}")
    if failed:
        return False, "; ".join(failed)
    return True, "criteria matched"


class Verifier:
    def __init__(self, router=None, change_threshold: float = 2.0):
        self.router = router
        self.change_threshold = change_threshold

    async def verify(
        self,
        step: Step,
        *,
        url: str,
        text: str,
        html: str,
        variables: dict,
        before: str | None,
        after: str | None,
        run_id: str | None = None,
    ) -> VerifyResult:
        ok, reason = check_criteria(step.success_criteria, url=url, text=text, html=html, variables=variables)
        delta = None
        if before and after:
            try:
                delta = change_percent(before, after)
            except Exception:
                delta = None
        if ok and "changed" in (step.success_criteria or "") and delta is not None and delta < self.change_threshold:
            ok = False
            reason = f"page change {delta:.2f}% below {self.change_threshold}"
        if ok:
            return VerifyResult(ok=True, reason=reason, change_percent=delta, model_used=False)
        # Structural failure never asks the model. That keeps playbook runs at zero LLM calls.
        if step.success_criteria.startswith("model:"):
            if self.router is None:
                return VerifyResult(ok=False, reason="model criteria but no router", change_percent=delta)
            prompt = (
                "Was this step successful? Reply YES or NO only.\n"
                f"goal: {step.goal}\n"
                f"evidence_ok={'yes' if ok else 'no'}\n"
                f"page:\n{text[:1500]}"
            )
            answer = await self.router.complete("fast", prompt, run_id=run_id)
            passed = answer.text.strip().upper().startswith("YES")
            return VerifyResult(ok=passed, reason=answer.text.strip(), change_percent=delta, model_used=True)
        return VerifyResult(ok=False, reason=reason, change_percent=delta, model_used=False)
