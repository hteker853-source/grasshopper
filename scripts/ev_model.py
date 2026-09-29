#!/usr/bin/env python3
"""Monte Carlo expected value with correlation and 3 scenarios (Bear, Base, Bull)."""

from __future__ import annotations

import random
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.scores import COMPETITIONS, place_probability, weighted

WARNING = (
    "WARNING: Assuming competitions are fully independent produces overly optimistic estimates. "
    "Shared evaluation criteria, common code base, and the same submission window introduce positive correlation. "
    "In reality, complete independence is overly optimistic; a general defect or jury skepticism on a bad day causes batch rejection."
)


def contest_outcomes(contest: dict, multiplier: float = 1.0) -> list[tuple[str, float, float]]:
    """Mutually exclusive places. Probabilities are scaled if they would exceed 1."""
    score = weighted(contest["criteria"])
    rows = []
    for name, dollars, base in contest["prizes"]:
        prob = place_probability(base, score) * multiplier
        rows.append((name, float(dollars), min(1.0, prob)))
    total = sum(item[2] for item in rows)
    if total > 1:
        rows = [(name, dollars, prob / total) for name, dollars, prob in rows]
    return rows


def run_scenario(scenario: str, draws: int = 20000, seed: int = 20260928) -> dict:
    """Run Monte Carlo for 'bear', 'base', or 'bull' scenario with quality correlation."""
    rng = random.Random(seed)

    sc_mult = {"bear": 0.55, "base": 1.00, "bull": 1.45}[scenario]
    prepared = [(contest["id"], contest["prizes"], weighted(contest["criteria"])) for contest in COMPETITIONS if contest["prizes"]]

    totals = []
    for _ in range(draws):
        # Latent day/run quality shock (correlation factor Q around 1.0)
        quality = 1.0 + rng.uniform(-0.35, 0.35)
        run_mult = max(0.1, sc_mult * quality)

        money = 0.0
        for _cid, prizes, score in prepared:
            roll = rng.random()
            cursor = 0.0
            for _name, dollars, base in prizes:
                prob = min(1.0, place_probability(base, score) * run_mult)
                cursor += prob
                if roll < cursor:
                    money += float(dollars)
                    break
        totals.append(money)

    any_prize = sum(1 for value in totals if value > 0) / draws
    over_10 = sum(1 for value in totals if value >= 10000) / draws
    over_20 = sum(1 for value in totals if value >= 20000) / draws
    expected = sum(totals) / draws

    return {
        "scenario": scenario,
        "draws": draws,
        "seed": seed,
        "expected_usd": expected,
        "p_any": any_prize,
        "p_10k": over_10,
        "p_20k": over_20,
        "warning": WARNING,
    }


def simulate(draws: int = 20000, seed: int = 20260928) -> dict:
    """Standard base simulation compatible with test_scorecard."""
    return run_scenario("base", draws=draws, seed=seed)


def simulate_all() -> dict[str, dict]:
    return {
        "bear": run_scenario("bear"),
        "base": run_scenario("base"),
        "bull": run_scenario("bull"),
    }


def render(result: dict | None = None) -> str:
    if result is not None and "expected_usd" in result and "bear" not in result:
        return "\n".join([
            "# Expected value (ESTIMATE)",
            "",
            "This is not a measurement. It is an ESTIMATE.",
            "",
            result.get("warning", WARNING),
            "",
            f"Draws: {result['draws']}. Seed: {result.get('seed', 20260928)}.",
            "",
            "| Outcome | Value |",
            "| --- | --- |",
            f"| Expected value | ${result['expected_usd']:.0f} |",
            f"| At least 1 prize | {result['p_any']:.1%} |",
            f"| $10,000+ | {result['p_10k']:.1%} |",
            f"| $20,000+ | {result['p_20k']:.1%} |",
            "",
            "The assumption of independent draws across competitions is overly optimistic.",
            "",
        ])

    results = simulate_all()
    bear = results["bear"]
    base = results["base"]
    bull = results["bull"]

    lines = [
        "# Earnings Model and Expected Value (EV) Report",
        "",
        "> [!IMPORTANT]",
        "> This is not a guaranteed income commitment. It is an ESTIMATE based on AI jury scores and Monte Carlo simulation.",
        "",
        WARNING,
        "",
        "## 1. Three Scenario Analysis (Correlated Model)",
        "",
        "| Metric | Bear | Base | Bull |",
        "| --- | --- | --- | --- |",
        f"| **Expected Value (EV)** | **${bear['expected_usd']:.0f}** | **${base['expected_usd']:.0f}** | **${bull['expected_usd']:.0f}** |",
        f"| **At Least 1 Prize Probability** | {bear['p_any']:.1%} | {base['p_any']:.1%} | {bull['p_any']:.1%} |",
        f"| **$10,000+ Earnings Probability** | {bear['p_10k']:.1%} | {base['p_10k']:.1%} | {bull['p_10k']:.1%} |",
        f"| **$20,000+ Earnings Probability** | {bear['p_20k']:.1%} | {base['p_20k']:.1%} | {bull['p_20k']:.1%} |",
        "",
        "## 2. Reality Check on the '$20,000 Average' Premise",
        "",
        "- **$20,000 average across 19 competitions:** That would mean $380,000 in cash prizes. This premise is **IMPOSSIBLE**; the entire first-place cash prize pool of all 19 competitions combined is only ~$180,000, and several contests (ING, Kestra, Arbiter, Nordic) award credits or certificates rather than cash.",
        "- **Probability of winning $20,000+ total:**",
        f"  - In the Base scenario, the probability of total income reaching $20,000 or more is **{base['p_20k']*100:.1f}%**, and in the Bull scenario it is **{bull['p_20k']*100:.1f}%**.",
        "- **Which competitions are critical for $20,000?**",
        "  - **Amazon (Alexa+ 1st: $25,000)** and **Nebius (1st: $20,000)** form the backbone of this goal. Without these two competitions, even winning all other contests in the portfolio makes reaching $20,000 in cash virtually impossible (Vultr 9K + Open Agent 8K = 17K).",
        "",
        "## 3. Assumptions and Notes",
        "- The simulation runs 20,000 draws for each scenario.",
        "- Placement outcomes within the same competition are mutually exclusive (one cannot place 1st and 2nd simultaneously).",
        "- A latent quality correlation shock (±0.35) models co-dependent success/failure tendencies across contests.",
        "",
    ]
    return "\n".join(lines)


def main() -> int:
    text = render()
    dest = ROOT / "docs" / "EV.md"
    dest.write_text(text, encoding="utf-8")
    print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
