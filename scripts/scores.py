"""Jury estimates. These are not measurements. Each number is a judgment plus a file."""

from __future__ import annotations

PERSONAS = ("teknik", "urun", "tasarim", "etki", "supheci")


def mean(scores: dict[str, float]) -> float:
    return sum(scores[name] for name in PERSONAS) / len(PERSONAS)


def weighted(criteria: list[dict]) -> float:
    total = 0.0
    weight = 0.0
    for item in criteria:
        total += mean(item["after"]) * item["weight"]
        weight += item["weight"]
    return total / weight if weight else 0.0


def weighted_before(criteria: list[dict]) -> float:
    total = 0.0
    weight = 0.0
    for item in criteria:
        total += mean(item["before"]) * item["weight"]
        weight += item["weight"]
    return total / weight if weight else 0.0


def _row(name: str, weight: int, before: tuple[int, ...], after: tuple[int, ...], evidence: str) -> dict:
    return {
        "name": name,
        "weight": weight,
        "before": dict(zip(PERSONAS, before)),
        "after": dict(zip(PERSONAS, after)),
        "evidence": evidence,
    }


# Five-tuples are teknik, urun, tasarim, etki, supheci.
# Evaluated by independent jury (Nebius Nemotron Ultra 550B).
# Before is initial independent jury evaluation; After is after closing the lowest criteria with tests & UX evaluation.

AMAZON = [
    _row("Tech Implementation", 25, (9, 8, 7, 8, 6), (9, 8, 7, 8, 6),
         "MCP SDK 2.x Streamable HTTP mounted at /mcp/ with 7 tools, 97 passing pytest tests, hard budget ledger enforced, live Nebius Nemotron loop."),
    _row("Design", 25, (7, 6, 6, 7, 4), (8, 7, 8, 8, 6),
         "tests/test_dashboard_ux.py (#learning, #savings, #isolated, viewport responsive) and docs/UX_EVALUATION.md heuristic evaluation simulated with AI personas (not real user testing) prepared."),
    _row("Potential Impact", 25, (8, 8, 7, 9, 5), (8, 8, 7, 9, 5),
         "docs/RELIABILITY_REAL.md: $0.0238 spend measured on 5 real sites, approval gates, zero LLM call playbook replay on second run."),
    _row("Quality of the Idea", 25, (8, 8, 6, 8, 5), (8, 8, 6, 8, 5),
         "Approval gate architecture, budget ledger, docs/FRICTION_LOG.md real SDK/Playwright friction records."),
]

NEBIUS = [
    _row("Technological Implementation", 25, (9, 8, 7, 8, 7), (9, 8, 7, 8, 7),
         "Live Nebius Token Factory (Nemotron 3.5 Lightning & Nemotron Ultra 550B), invoiced dollar/token accounting ($0.0238/41 calls), 97 green tests."),
    _row("Design", 25, (8, 8, 9, 8, 6), (8, 8, 9, 8, 6),
         "Dashboard learning curve bar chart, savings panel, live stream feed, and responsive layout."),
    _row("Potential Impact", 25, (8, 9, 8, 9, 5), (8, 9, 8, 9, 5),
         "Playbook caching and budget cap proving marginal model cost is zeroed on repeated tasks."),
    _row("Quality of the Idea", 25, (9, 8, 7, 8, 6), (9, 8, 7, 8, 6),
         "Two-tier routing (fast default, strong on repair), CV fallback DOM recovery."),
]

OPEN_AGENT = [
    _row("Impact", 30, (6, 7, 5, 8, 4), (6, 7, 5, 8, 4),
         "Safe browser automation via allowlist and approval gate; docs/OPEN_AGENT_PLAN.md Tinkerer schedule."),
    _row("Technical", 20, (8, 7, 5, 7, 6), (8, 7, 5, 7, 6),
         "Multi-agent council consensus (council_ask), reasoning traces (explain.jsonl), 97 passing tests."),
    _row("Innovation", 15, (8, 7, 5, 8, 5), (8, 7, 5, 8, 5),
         "Zero-cost playbook playback on rerun, hard budget protection."),
    _row("Demo", 15, (6, 7, 7, 7, 4), (6, 7, 7, 7, 4),
         "62-second video videos/demo.mp4; dashboard, learning curve, and protection demo."),
    _row("Product & UX", 10, (7, 8, 8, 7, 5), (7, 8, 8, 7, 5),
         "Run overview, live frames, step targets, and budget metrics."),
    _row("Sponsor Tech", 10, (7, 6, 5, 7, 4), (9, 8, 6, 8, 6),
         "tests/test_nemotron_sponsor.py proves NVIDIA Nemotron integration, Open Agent function schema, and two-tier pricing."),
]

VULTR = [
    _row("Application of Technology", 25, (6, 7, 5, 6, 4), (8, 8, 6, 7, 6),
         "tests/test_vultr_sandbox.py: VultrAPI lifecycle (get, list, user_data), error recovery, sandbox cleanup, and isolated execution proven by tests."),
    _row("Presentation", 25, (6, 7, 6, 6, 4), (6, 7, 6, 6, 4),
         "Isolation moment in 62s video videos/demo.mp4, docs/rules/vultr.md full rule documentation."),
    _row("Business Value", 25, (7, 8, 5, 8, 5), (7, 8, 5, 8, 5),
         "Enterprise safety via hard budget stop ($0.50/$0.05), allow/denylist, approval gate on sensitive actions."),
    _row("Originality", 25, (7, 8, 6, 7, 5), (7, 8, 6, 7, 5),
         "Blast Radius Zero architecture logging touched files, domains, duration, and spend in blast_radius.json for each run."),
]

OPENCV = [
    _row("Technical execution", 30, (6, 5, 4, 4, 4), (7, 6, 5, 5, 5),
         "test_vision_finds_button and test_vision_change_and_dom_recovery_are_measured. OpenCV 5 pinned."),
    _row("Innovation", 20, (5, 4, 4, 4, 3), (6, 5, 5, 4, 4),
         "Continue button selection via vision upon selector break measured on controlled dataset."),
    _row("Real-world impact", 20, (3, 3, 2, 3, 2), (4, 3, 3, 3, 2),
         "Live third-party page not intentionally broken. Impact unmeasured."),
    _row("User experience", 10, (5, 5, 6, 4, 3), (6, 5, 6, 4, 4),
         "Repair halts on human approval. No standalone vision UI."),
    _row("Documentation and presentation", 10, (4, 4, 4, 3, 3), (6, 5, 5, 4, 4),
         "docs/AGENTIC_VISION.md and docs/OPENCV_AWS.md."),
    _row("Responsible cloud delivery", 10, (1, 1, 1, 1, 1), (2, 2, 2, 2, 2),
         "Account not opened. Steps documented, deployment unmeasured."),
]

DEFAULT = [
    _row("Technical", 25, (4, 4, 3, 3, 3), (6, 5, 4, 4, 4), "Relevant test file and default rubric."),
    _row("Innovation", 20, (4, 3, 3, 3, 2), (5, 4, 4, 3, 3), "Existing agent loop. Contest-specific novel thesis is limited."),
    _row("Impact", 20, (3, 3, 2, 2, 2), (3, 3, 2, 2, 2), "Users or revenue unmeasured."),
    _row("Demo", 20, (4, 4, 4, 3, 3), (5, 5, 4, 4, 3), "videos/demo.mp4 64s. Contest-specific title clip generated separately."),
    _row("UX", 15, (5, 5, 6, 4, 3), (6, 5, 6, 4, 4), "Dashboard learning and cost panel."),
]


def _default(evidence: str) -> list[dict]:
    rows = []
    for item in DEFAULT:
        copy = {
            "name": item["name"],
            "weight": item["weight"],
            "before": dict(item["before"]),
            "after": dict(item["after"]),
            "evidence": evidence,
        }
        rows.append(copy)
    return rows


COMPETITIONS = [
    {"id": "amazon", "class": "A", "rubric": "official, equal 25%", "criteria": AMAZON,
     "prizes": [("Alexa+ 1st", 25000, 0.005), ("Alexa+ 2nd", 15000, 0.008), ("Alexa+ 3rd", 4000, 0.01), ("OSS mini", 5000, 0.02)]},
    {"id": "nebius", "class": "A", "rubric": "official, equal 25%", "criteria": NEBIUS,
     "prizes": [("1st", 20000, 0.005), ("2nd", 10000, 0.008), ("3rd", 6000, 0.01), ("Tavily", 3000, 0.01)]},
    {"id": "open-agent", "class": "A", "rubric": "briefing, no official page", "criteria": OPEN_AGENT,
     "prizes": [("1st", 8000, 0.005), ("2nd", 4000, 0.008), ("3rd", 2000, 0.01)]},
    {"id": "vultr", "class": "A", "rubric": "default rubric", "criteria": VULTR,
     "prizes": [("1st cash", 5000, 0.01), ("2nd cash", 3000, 0.015), ("3rd cash", 1000, 0.02)]},
    {"id": "opencv", "class": "B", "rubric": "official OpenCV weights", "criteria": OPENCV,
     "prizes": [("1st", 5000, 0.01), ("2nd", 3000, 0.012), ("3rd", 2000, 0.015), ("Agentic Vision", 1000, 0.02)]},
    {"id": "build-with-ai", "class": "B", "rubric": "default rubric", "criteria": _default("make test passes without keys. Prototype satisfies core condition. Headcount unknown."),
     "prizes": [("1st", 2500, 0.05)]},
    {"id": "hetic", "class": "B", "rubric": "default rubric", "criteria": _default("playbooks/shop_old_listings.yaml and test_s3_old_listings."),
     "prizes": [("1st", 1100, 0.02)]},
    {"id": "climatechain", "class": "B", "rubric": "default rubric", "criteria": _default("grasshopper/realweb/climate.py only records text present on page. Not a dedicated climate product."),
     "prizes": [("1st", 1500, 0.005)]},
    {"id": "ytu-meta", "class": "B", "rubric": "default rubric", "criteria": _default("Onsite hackathon. $6,000 pool. Individual share unknown, excluded from EV."),
     "prizes": []},
    {"id": "imagine-cup", "class": "B", "rubric": "default rubric", "criteria": _default("docs/IMAGINE_CUP_PLAN.md. Two Azure services not wired. 2027 rules UNVERIFIED."),
     "prizes": [("grand", 100000, 0.002)]},
    {"id": "gemma", "class": "B", "rubric": "default rubric", "criteria": _default("Weak alignment. GEMMA_MODEL empty. test_ollama_generate_body fake server."),
     "prizes": [("paper", 35000, 0.002)]},
    {"id": "assemblyai", "class": "B", "rubric": "default rubric", "criteria": _default("No voice agent demo. No key. Window too short."),
     "prizes": [("cash", 5000, 0.002)]},
    {"id": "asus", "class": "B", "rubric": "default rubric", "criteria": _default("submissions/asus/PRESENTATION.md. UGen300 unavailable. Hardware unmeasured."),
     "prizes": [("Lightning", 4500, 0.005)]},
    {"id": "ing", "class": "B", "rubric": "default rubric", "criteria": _default("Mock bank approval, limit, ledger. Device prize, cash excluded from EV."),
     "prizes": []},
    {"id": "kestra", "class": "B", "rubric": "default rubric", "criteria": _default("No Kestra PR in this repository."),
     "prizes": []},
    {"id": "hackster-nordic", "class": "B", "rubric": "default rubric", "criteria": _default("Prize and date unknown. Cash excluded from EV."),
     "prizes": []},
    {"id": "arbiter", "class": "B", "rubric": "default rubric", "criteria": _default("eligible=false. Will not enter. Probability 0."),
     "prizes": []},
]


def place_probability(base: float, score: float) -> float:
    factor = min(3.0, (score / 6.0) ** 2)
    return base * factor


def lowest_three(criteria: list[dict]) -> list[dict]:
    ranked = sorted(criteria, key=lambda item: (mean(item["after"]), -item["weight"]))
    return ranked[:3]
