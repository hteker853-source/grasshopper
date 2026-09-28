#!/usr/bin/env python3
"""Independent jury evaluation using Nebius Nemotron Ultra (550B).

Evaluates A-class competitions with 5 jury personas:
teknik, urun, tasarim, etki, supheci.
Tracks budget via BudgetLedger and writes results incrementally.
"""

from __future__ import annotations

import json
import os
import re
import sys
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from grasshopper.core.budget import BudgetLedger

MODEL = "nvidia/Nemotron-3-Ultra-550b-a55b"
BASE_URL = "https://api.tokenfactory.nebius.com/v1"
PERSONAS = ("teknik", "urun", "tasarim", "etki", "supheci")


def get_api_key() -> str:
    key = os.environ.get("NEBIUS_API_KEY", "")
    if not key and (ROOT / ".env").is_file():
        for line in (ROOT / ".env").read_text(encoding="utf-8").splitlines():
            if line.startswith("NEBIUS_API_KEY="):
                key = line.split("=", 1)[1].strip().strip('"').strip("'")
                break
    return key


COMPETITIONS = {
    "amazon": {
        "title": "Amazon Build, Ship, Shape (Alexa+ track & Open Source mini)",
        "criteria": [
            ("Tech Implementation", 25, "Project setup, required technology usage (MCP SDK 2.x Streamable HTTP, testing, architecture)."),
            ("Design", 25, "End-to-end product experience, user interface fit, telemetry visualization."),
            ("Potential Impact", 25, "Convincing rationale for customer need, measurable ROI, browser automation utility."),
            ("Quality of the Idea", 25, "Creative use of required tools vs obvious wrapper, safety architecture, friction log."),
        ],
        "evidence": (
            "- Tech: Python FastAPI open-source (MIT) browser agent. MCP SDK 2.x Streamable HTTP mounted at /mcp/ with 7 tools "
            "(approve, council_ask, get_task_status, list_pending_approvals, run_task, schedule_task, store_check_old_listings). "
            "88 pytest tests passing. Hard budget ledger ($0.50 daily, $0.05 per run limit) stopping unauthorized execution. "
            "Real-web execution loop with live Nebius Nemotron.\n"
            "- Design: Web UI dashboard with live learning curve chart and token cost savings panel, /alexa simulator page, "
            "live stream frame feed. No external user testing conducted yet.\n"
            "- Potential Impact: Automates multi-step browsing safely; second run learns recipes with 0 LLM calls; measured "
            "$0.0238 spend on real web benchmark across 5 real websites.\n"
            "- Quality of Idea: Reusable agent with approval gates for payments/actions, friction log (docs/FRICTION_LOG.md) "
            "documenting real MCP SDK 2.x lifespan session and Playwright fallback snags."
        )
    },
    "nebius": {
        "title": "Nebius x NVIDIA Global AI Hackathon",
        "criteria": [
            ("Technological Implementation", 25, "Integration with Nebius Token Factory / NVIDIA Nemotron, model routing, runtime execution."),
            ("Design", 25, "Product experience, dashboard visualization, feedback and clarity."),
            ("Potential Impact", 25, "Measurable efficiency, token cost savings, real web automation."),
            ("Quality of the Idea", 25, "Non-obvious use of models, tier routing, recipe caching, error recovery."),
        ],
        "evidence": (
            "- Tech: Live integration with Nebius Token Factory using nvidia/Nemotron-3_5-Lightning for fast web navigation and "
            "nvidia/Nemotron-3-Ultra-550b for evaluation. Real billing and token usage tracked through BudgetLedger ($0.0238 spent on 41 calls in run 1). "
            "88 pytest unit and integration tests passing.\n"
            "- Design: Dashboard displaying learning curve (calls drop to 0 on clean replay) and token savings panel. Live video recording and live frame streaming.\n"
            "- Potential Impact: Drastic reduction in LLM inference costs for repetitive web workflows via learned recipes; hard budget guards prevent runaway API bills.\n"
            "- Quality of Idea: Two-tier model routing (fast model by default, strong model on failure/repair), automated DOM recovery with computer vision fallback."
        )
    },
    "open-agent": {
        "title": "Open Agent Hackathon 2026",
        "criteria": [
            ("Impact", 30, "Solving real-world browser automation challenges safely and affordably."),
            ("Technical", 20, "Multi-agent reasoning, council consensus mechanism, explainer traces, architecture."),
            ("Innovation", 15, "Learned recipe replay (0 LLM calls), hard budget ledger, approval gate."),
            ("Demo", 15, "Recorded video demo (videos/demo.mp4, 62s), live streaming endpoint."),
            ("Product & UX", 10, "Execution dashboard, pending approvals view, step telemetry."),
            ("Sponsor Tech", 10, "NVIDIA Nemotron integration, open agent protocols."),
        ],
        "evidence": (
            "- Impact: Safe autonomous browser agent preventing financial or data loss via human approval gates and domain allowlists.\n"
            "- Technical: Multi-agent council mechanism (council_ask tool), step-by-step reasoning traces (explain.jsonl), 88 pytest tests passing.\n"
            "- Innovation: Zero-cost recipe caching on repeated workflows; hard budget ceiling enforced before model calls.\n"
            "- Demo: 62-second recorded video (videos/demo.mp4, 303 KB) showing dashboard, live execution, learning curve, and savings.\n"
            "- Product & UX: Interactive dashboard with runs overview, live screenshots, step goals, and budget metrics.\n"
            "- Sponsor Tech: Built with NVIDIA Nemotron models on Nebius cloud.\n"
            "- Constraint Note: Eligible for Tinkerer track; official build window is Oct 15-20, plan ready in docs/OPEN_AGENT_PLAN.md."
        )
    },
    "vultr": {
        "title": "Vultr Agent Rush Hackathon (Blast Radius Zero)",
        "criteria": [
            ("Application of Technology", 25, "Model integration, browser automation engine, containment sandbox execution."),
            ("Presentation", 25, "Demo clarity, documentation, containment proof in video."),
            ("Business Value", 25, "Enterprise safety, zero blast radius containment, practical automation utility."),
            ("Originality", 25, "Blast Radius Zero architecture: containment of files, domains, time, and budget."),
        ],
        "evidence": (
            "- Technology: Autonomous web agent with headless browser driver and HTTP fallback; Docker container sandbox with memory/CPU/network limits; simulated Vultr instance creation/deletion in grasshopper/sandbox_runner/vultr.py.\n"
            "- Presentation: 62-second demo video videos/demo.mp4 with containment moment; complete documentation in docs/rules/vultr.md.\n"
            "- Business Value: Protects users from rogue agent actions: hard daily/per-run budget stop ($0.50/$0.05), domain allowlist/denylist, approval gate for sensitive actions.\n"
            "- Originality: Every execution generates blast_radius.json tracking modified files, domains contacted, execution duration, and USD spent."
        )
    }
}


def parse_json_safely(raw: str) -> dict:
    raw = raw.strip()
    if "```json" in raw:
        raw = raw.split("```json", 1)[1].split("```", 1)[0].strip()
    elif "```" in raw:
        raw = raw.split("```", 1)[1].split("```", 1)[0].strip()

    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        pass

    match = re.search(r"\{.*\}", raw, re.DOTALL)
    if match:
        try:
            return json.loads(match.group(0))
        except json.JSONDecodeError:
            pass

    # Clean potential trailing commas
    cleaned = re.sub(r",\s*([\]}])", r"\1", raw)
    match = re.search(r"\{.*\}", cleaned, re.DOTALL)
    if match:
        return json.loads(match.group(0))
    return json.loads(cleaned)


def call_jury(ledger: BudgetLedger, api_key: str, comp_key: str, data: dict) -> dict:
    criteria_desc = "\n".join(f"- {name} ({weight}%): {desc}" for name, weight, desc in data["criteria"])
    sys_msg = (
        "You are an independent, highly critical hackathon jury panel evaluating the project 'Grasshopper'.\n"
        "The jury has 5 distinct personas:\n"
        "1. teknik (Technical Lead): strictly examines code architecture, real execution, API completeness, unit tests.\n"
        "2. urun (Product Manager): strictly examines real problem-solution fit, completeness, usability, feature maturity.\n"
        "3. tasarim (UX/UI Designer): strictly examines user interaction, dashboard clarity, visual feedback, user testing.\n"
        "4. etki (Business Impact): strictly examines real-world ROI, cost savings, commercial viability.\n"
        "5. supheci (Skeptic): penalizes missing live features, unverified claims, lack of live user testing.\n\n"
        "Score each criterion from 0 to 10 for each of the 5 personas.\n"
        "Do NOT inflate scores. Return ONLY valid JSON:\n"
        "{\n"
        '  "criteria": [\n'
        "    {\n"
        '      "name": "<criterion name>",\n'
        '      "scores": {"teknik": int, "urun": int, "tasarim": int, "etki": int, "supheci": int},\n'
        '      "justification": "<one concise sentence combining evidence and reasoning>"\n'
        "    }\n"
        "  ]\n"
        "}"
    )
    user_msg = (
        f"Competition: {data['title']}\n"
        f"Criteria:\n{criteria_desc}\n\n"
        f"Evidence in Grasshopper codebase:\n{data['evidence']}"
    )

    prompt_text = sys_msg + "\n" + user_msg
    est = ledger.authorize("strong", prompt_text, f"jury_{comp_key}")

    for attempt in range(2):
        req = urllib.request.Request(
            f"{BASE_URL}/chat/completions",
            headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
            data=json.dumps({
                "model": MODEL,
                "messages": [
                    {"role": "system", "content": sys_msg},
                    {"role": "user", "content": user_msg}
                ],
                "temperature": 0.1 if attempt == 0 else 0.2,
                "max_tokens": 2500
            }).encode()
        )

        with urllib.request.urlopen(req, timeout=120) as resp:
            res = json.loads(resp.read().decode())

        usage = res.get("usage", {})
        prompt_tokens = usage.get("prompt_tokens", len(prompt_text) // 4)
        completion_tokens = usage.get("completion_tokens", 800)
        actual_cost = (prompt_tokens + completion_tokens) * 0.003 / 1000.0
        ledger.commit(f"jury_{comp_key}", est, actual_cost)

        content = res["choices"][0]["message"].get("content", "")
        if not content:
            content = res["choices"][0]["message"].get("reasoning_content", "")

        try:
            parsed = parse_json_safely(content)
            return {"comp": comp_key, "results": parsed, "usage": usage, "cost_usd": actual_cost}
        except Exception as e:
            if attempt == 1:
                raise e


def main():
    api_key = get_api_key()
    if not api_key:
        print("ERROR: NEBIUS_API_KEY not found.")
        sys.exit(1)

    out_file = ROOT / "data" / "independent_jury_results.json"
    out_file.parent.mkdir(parents=True, exist_ok=True)
    all_results = {}
    if out_file.is_file():
        try:
            all_results = json.loads(out_file.read_text(encoding="utf-8"))
        except Exception:
            all_results = {}

    ledger = BudgetLedger(daily_usd=0.50, per_run_usd=0.05)
    print(f"Starting Independent Jury evaluation with {MODEL}...")

    for key, data in COMPETITIONS.items():
        if key in all_results and "results" in all_results[key]:
            print(f"Using cached result for {key} (cost: ${all_results[key].get('cost_usd', 0):.5f})")
            continue

        print(f"Evaluating {key}...")
        res = call_jury(ledger, api_key, key, data)
        all_results[key] = res
        out_file.write_text(json.dumps(all_results, indent=2, ensure_ascii=False), encoding="utf-8")
        print(f"Completed {key} (cost: ${res['cost_usd']:.5f})")

    out_file.write_text(json.dumps(all_results, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Saved all independent jury results to {out_file}")
    print(f"Session spend - estimated: ${ledger.daily_estimated:.5f}, actual: ${ledger.daily_actual:.5f}")


if __name__ == "__main__":
    main()
