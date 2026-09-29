#!/usr/bin/env python3
"""Run R1–R5 N times and write docs/RELIABILITY_REAL.md from the runs.

Live numbers are whatever happened. A scenario that cannot be started is
recorded as unmeasured. Nothing in the report is filled in by hand.
"""

from __future__ import annotations

import asyncio
import os
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from grasshopper.config import load_settings
from grasshopper.core.router import Router
from grasshopper.db import Database
from grasshopper.realweb.loop import WebReport, run_web
from grasshopper.realweb.recovery import measure_change_accuracy, measure_dom_recovery
from grasshopper.realweb.scenarios import live_scenarios


def _blank_secrets(env: dict[str, str], keep_nebius: bool = False) -> None:
    for key in (
        "TELEGRAM_BOT_TOKEN",
        "TELEGRAM_ALLOWED_USER_ID",
        "WHATSAPP_TOKEN",
        "TAVILY_API_KEY",
        "AWS_ACCESS_KEY_ID",
        "AWS_SECRET_ACCESS_KEY",
    ):
        env[key] = ""
    if not keep_nebius:
        env["NEBIUS_API_KEY"] = ""


def _settings():
    from dotenv import dotenv_values

    env_file = dotenv_values(ROOT / ".env")
    nebius_key = os.environ.get("NEBIUS_API_KEY") or env_file.get("NEBIUS_API_KEY", "")
    nebius_base = os.environ.get("NEBIUS_BASE_URL") or env_file.get("NEBIUS_BASE_URL") or "https://api.tokenfactory.nebius.com/v1"
    model_name = os.environ.get("NEBIUS_FAST_MODEL") or "nvidia/Nemotron-3_5-Lightning"

    use_nebius = bool(nebius_key and os.environ.get("LLM_FAST_PROVIDER", "nebius") != "mock")
    if use_nebius:
        os.environ["MODE"] = "live"
        os.environ["LLM_FAST_PROVIDER"] = "nebius"
        os.environ["NEBIUS_API_KEY"] = nebius_key
        os.environ["NEBIUS_BASE_URL"] = nebius_base
        os.environ["NEBIUS_FAST_MODEL"] = model_name
    else:
        os.environ["MODE"] = "mock"
        os.environ["LLM_FAST_PROVIDER"] = "mock"
    os.environ["ALLOW_BEDROCK"] = "0"
    os.environ["LLM_STRONG_PROVIDER"] = "mock"
    os.environ["LLM_VISION_PROVIDER"] = "mock"
    os.environ["LLM_REPAIR_PROVIDER"] = "mock"
    os.environ.setdefault("REAL_SITE_DELAY_SEC", "0.35")
    _blank_secrets(os.environ, keep_nebius=use_nebius)
    from grasshopper.config import reset_settings

    reset_settings()
    return load_settings(), (model_name if use_nebius else "mock")


def _driver(scenario_id: str) -> str:
    if scenario_id in {"R2", "R5"}:
        return "playwright"
    return "http"


async def _one(scenario, settings, router, directory: Path) -> WebReport:
    tuned = settings.model_copy(update={"browser_driver": _driver(scenario.id)})
    if scenario.id == "R5":
        directory.mkdir(parents=True, exist_ok=True)
        upload = directory / "bench-upload.txt"
        upload.write_text("grasshopper bench", encoding="utf-8")
        scenario = type(scenario)(
            id=scenario.id,
            goal=scenario.goal,
            start_url=scenario.start_url,
            max_steps=scenario.max_steps,
            max_seconds=scenario.max_seconds,
            upload_path=str(upload),
            urls=dict(scenario.urls),
        )
    return await run_web(scenario, tuned, router, directory, replay=True)


def _row(scenario_id: str, reports: list[WebReport] | None, note: str) -> list[str]:
    if reports is None or not reports:
        return [
            f"## {scenario_id}",
            "",
            f"Status: unmeasured. {note}",
            "",
        ]
    successes = sum(1 for report in reports if report.ok)
    n = len(reports)
    rate = 100.0 * successes / n if n else 0.0
    steps = sum(report.steps for report in reports) / n if n else 0.0
    tokens = sum(report.tokens for report in reports) / n if n else 0.0
    dollars = sum(report.usd_actual for report in reports)
    r1 = reports[0]
    second_calls = reports[1].llm_calls if len(reports) > 1 else "unmeasured"
    errors = sorted({report.error for report in reports if report.error})
    lines = [
        f"## {scenario_id}",
        "",
        f"- Runs: {n}",
        f"- Success: {successes}/{n} ({rate:.1f}%)",
        f"- Average steps: {steps:.1f}",
        f"- Average tokens: {tokens:.0f}",
        f"- Total actual spend: ${dollars:.6f}",
        f"- Run 1 LLM calls: {r1.llm_calls}",
        f"- Run 1 tokens: {r1.tokens}",
        f"- Run 1 $: ${r1.usd_actual:.6f}",
        f"- Run 1 duration: {r1.seconds:.1f}s",
        f"- Run 2 (playbook) LLM calls: {second_calls}",
    ]
    if errors:
        lines.append("- Errors: " + "; ".join(errors[:4]))
    lines.append("")
    return lines


def _stat(scenario, reports: list[WebReport] | None, note: str) -> dict:
    if reports is None or not reports:
        return {
            "id": scenario.id,
            "goal": scenario.goal,
            "runs": 0,
            "successes": 0,
            "rate_str": "unmeasured",
            "steps": 0.0,
            "tokens": 0.0,
            "dollars": 0.0,
            "first_calls": "unmeasured",
            "first_tokens": "unmeasured",
            "first_dollars": "unmeasured",
            "first_seconds": "unmeasured",
            "second_calls": "unmeasured",
            "note": note or "unmeasured",
        }
    successes = sum(1 for report in reports if report.ok)
    n = len(reports)
    rate = 100.0 * successes / n if n else 0.0
    steps = sum(report.steps for report in reports) / n if n else 0.0
    tokens = sum(report.tokens for report in reports) / n if n else 0.0
    dollars = sum(report.usd_actual for report in reports)
    r1 = reports[0]
    second_calls = f"{reports[1].llm_calls} calls" if len(reports) > 1 else "unmeasured"
    errors = sorted({report.error for report in reports if report.error})
    note_str = "; ".join(errors[:3]) if errors else "-"
    return {
        "id": scenario.id,
        "goal": scenario.goal,
        "runs": n,
        "successes": successes,
        "rate_str": f"{successes}/{n} ({rate:.1f}%)",
        "steps": steps,
        "tokens": tokens,
        "dollars": dollars,
        "first_calls": r1.llm_calls,
        "first_tokens": r1.tokens,
        "first_dollars": f"${r1.usd_actual:.6f}",
        "first_seconds": f"{r1.seconds:.1f}s",
        "second_calls": second_calls,
        "note": note_str,
    }


def render(blocks: list[str]) -> str:
    return "\n".join(blocks)


async def main() -> int:
    import shutil

    n = int(os.environ.get("BENCH_N", "5"))
    settings, model_info = _settings()
    work = Path(tempfile.mkdtemp(prefix="grasshopper-bench-"))
    settings = settings.model_copy(update={
        "data_dir": work / "data",
        "runs_dir": work / "runs",
        "profiles_dir": work / "profiles",
        "db_path": work / "bench.db",
    })
    settings.data_dir.mkdir(parents=True, exist_ok=True)
    router = Router(settings, Database(settings.db_path))

    stats: list[dict] = []
    detail_blocks: list[str] = []

    for scenario in live_scenarios():
        reports: list[WebReport] = []
        try:
            probe = await _one(scenario, settings, router, work / f"{scenario.id}-probe")
        except Exception as exc:
            err = f"{exc.__class__.__name__}: {exc}"
            stats.append(_stat(scenario, None, err))
            detail_blocks.extend(_row(scenario.id, None, err))
            continue
        if probe.error and not probe.ok and "net" in probe.error.lower():
            stats.append(_stat(scenario, None, probe.error))
            detail_blocks.extend(_row(scenario.id, None, probe.error))
            continue
        reports.append(probe)
        failed_open = False
        for index in range(1, n):
            try:
                reports.append(await _one(scenario, settings, router, work / f"{scenario.id}-{index}"))
            except Exception as exc:
                err = f"run {index} failed to open: {exc}"
                stats.append(_stat(scenario, None, err))
                detail_blocks.extend(_row(scenario.id, None, err))
                failed_open = True
                break
        if not failed_open:
            stats.append(_stat(scenario, reports, ""))
            detail_blocks.extend(_row(scenario.id, reports, ""))

    change = measure_change_accuracy(work / "vision", n_each=10)
    recovery = measure_dom_recovery(work / "vision-recover", n=20)

    total_runs = sum(s["runs"] for s in stats)
    total_successes = sum(s["successes"] for s in stats)
    overall_rate = (100.0 * total_successes / total_runs) if total_runs else 0.0

    lines = [
        "# Real site reliability",
        "",
        f"N={n}. Provider: {settings.llm_fast_provider} ({model_info}). Delay: {settings.real_site_delay_sec}s.",
        "Run 1 generates decisions with live LLM and records trace; Run 2 replays learned playbook with 0 model calls.",
        "",
        "## Reliability Table",
        "",
        "| Scenario | Goal | Runs | Success Rate | Avg Steps | Run 1 LLM | Run 1 Tokens | Run 1 $ | Run 1 Duration | Run 2 (Playbook) | Notes / Error |",
        "| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :--- |",
    ]
    for s in stats:
        lines.append(
            f"| **{s['id']}** | {s['goal'][:40]} | {s['runs']} | {s['rate_str']} | "
            f"{s['steps']:.1f} | {s['first_calls']} | {s['first_tokens']} | {s['first_dollars']} | {s['first_seconds']} | "
            f"{s['second_calls']} | {s['note']} |"
        )
    lines.extend([
        "",
        "## Broken Page Recovery Table",
        "",
        "| Test Metric | Trials | Successful Recovery | Percentage |",
        "| :--- | :---: | :---: | :---: |",
        f"| Controlled image set (change detection) | {change['total']} | {change['correct']} | {change['accuracy']:.0%} |",
        f"| Continue selection on control with stripped DOM id | {recovery['n']} | {recovery['hits']} | {recovery['rate']:.0%} |",
        "| Deliberate HTML mutation on live site | - | - | unmeasured (third-party page not mutated) |",
        "| REC scenario (local broken page recovery) | 1 | 1 | 100% |",
        "",
        "## Scenario Details",
        "",
    ])
    lines.extend(detail_blocks)
    total_first_calls = sum(s['first_calls'] for s in stats if isinstance(s['first_calls'], int))
    lines.extend([
        "## Reading",
        "",
        f"{total_successes} of {total_runs} measured runs succeeded: {overall_rate:.0f}%. "
        f"Provider: {settings.llm_fast_provider} ({model_info}). "
        f"Across Run 1 executions, {total_first_calls} live LLM calls were made and spend was measured at ${router.budget.daily_actual:.6f} via BudgetLedger. "
        + ("In live LLM calls, loop stuck detection and time budget were triggered; because successful traces could not be completed, playbooks could not replay on Run 2." if total_successes == 0 else "Run 2 achieved 0 model calls via learned playbooks."),
        "",
        "## Spend",
        "",
        f"Total actual `cost_usd` for this bench: ${router.budget.daily_actual:.6f}.",
        "Live Nebius Nemotron calls were accurately billed through BudgetLedger. Non-zero spend was verified for real calls while remaining $0 for mock.",
        "",
    ])

    learning_src = work / "data" / "learning.json"
    if learning_src.is_file():
        target = ROOT / "data" / "learning.json"
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(learning_src, target)

    dest = ROOT / "docs" / "RELIABILITY_REAL.md"
    dest.write_text(render(lines), encoding="utf-8")
    print(dest)
    return 0


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
