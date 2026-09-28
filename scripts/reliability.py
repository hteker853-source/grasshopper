#!/usr/bin/env python3
"""Measure S1 and S3 on real Chromium with sandbox delay and the cookie banner.

Each scenario runs 50 times. The sandbox delay stays at the product default
(100–800 ms) and the cookie banner is left on (no gh_banner cookie is seeded).
Notification and provider secrets are forced empty so this measurement cannot
send Telegram or WhatsApp messages.
"""

from __future__ import annotations

import argparse
import asyncio
import json
import os
import shutil
import sys
import tempfile
import threading
import time
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

REPEATS = 50
SCENARIOS = ("S3", "S1")


def _blank_secrets() -> None:
    for key in (
        "TELEGRAM_BOT_TOKEN",
        "TELEGRAM_ALLOWED_USER_ID",
        "WHATSAPP_TOKEN",
        "WHATSAPP_PHONE_NUMBER_ID",
        "WHATSAPP_VERIFY_TOKEN",
        "WHATSAPP_TO",
        "NEBIUS_API_KEY",
        "AWS_ACCESS_KEY_ID",
        "AWS_SECRET_ACCESS_KEY",
        "AZURE_OPENAI_API_KEY",
        "AZURE_SPEECH_KEY",
        "META_API_KEY",
        "OPENAI_COMPAT_API_KEY",
        "ASSEMBLYAI_API_KEY",
        "TAVILY_API_KEY",
        "WALLET_KEYPAIR_PATH",
    ):
        os.environ[key] = ""


def _prepare_env(tmp: Path, port: int) -> None:
    _blank_secrets()
    os.environ["MODE"] = "mock"
    os.environ["BROWSER_DRIVER"] = "playwright"
    os.environ["API_TOKEN"] = "reliability-token"
    os.environ["LLM_FAST_PROVIDER"] = "mock"
    os.environ["LLM_STRONG_PROVIDER"] = "mock"
    os.environ["LLM_VISION_PROVIDER"] = "mock"
    os.environ["LLM_REPAIR_PROVIDER"] = "mock"
    os.environ["STT_PROVIDER"] = "mock"
    os.environ["SEARCH_PROVIDER"] = "mock"
    os.environ["WALLET_PROVIDER"] = "mock"
    os.environ["GRASSHOPPER_EMBED_SANDBOX"] = "0"
    os.environ["APPROVAL_TIMEOUT_SEC"] = "8"
    # Product defaults: random delay on, banner shown until the visitor accepts.
    os.environ["SANDBOX_DELAY_MIN_MS"] = "100"
    os.environ["SANDBOX_DELAY_MAX_MS"] = "800"
    os.environ["SANDBOX_BASE_URL"] = f"http://127.0.0.1:{port}"
    os.environ["GRASSHOPPER_DATA_DIR"] = str(tmp)
    os.environ["GRASSHOPPER_DB"] = str(tmp / "grasshopper.db")
    os.environ["GRASSHOPPER_RUNS_DIR"] = str(tmp / "runs")
    os.environ["SANDBOX_DB"] = str(tmp / "sandbox.db")
    os.environ["SANDBOX_MEDIA_DIR"] = str(tmp / "media")
    os.environ["WALLET_DAILY_LIMIT_SOL"] = "0.5"
    os.environ["WALLET_PER_TX_LIMIT_SOL"] = "0.1"


def _start_sandbox(port: int):
    import uvicorn

    config = uvicorn.Config(
        "sandbox_web.app:app",
        host="127.0.0.1",
        port=port,
        log_level="warning",
    )
    server = uvicorn.Server(config)
    thread = threading.Thread(target=server.run, daemon=True)
    thread.start()
    import httpx

    deadline = time.time() + 20
    url = f"http://127.0.0.1:{port}/health"
    while time.time() < deadline:
        try:
            httpx.get(url, timeout=0.3)
            return server
        except Exception:
            time.sleep(0.1)
    raise RuntimeError("sandbox did not start")


def _failure_reason(result, runs_dir: Path) -> str:
    path = runs_dir / result.run_id / "explain.jsonl"
    last_fail = ""
    if path.exists():
        for line in path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            event = json.loads(line)
            verdict = event.get("verifier_result") or ""
            if verdict.startswith("fail:"):
                last_fail = f"{event.get('step')}: {verdict}"
    summary = (result.summary or "").replace("\n", " ")
    if last_fail:
        return last_fail[:300]
    if summary.startswith("Stuck on"):
        return summary[:300]
    return f"{result.status.value}: {summary[:240]}"


async def _measure(ctx, repeats: int) -> dict:
    from grasshopper.demo_scenarios import S1, S3, run_scenario

    texts = {"S1": S1, "S3": S3}
    report: dict[str, dict] = {}
    for name in SCENARIOS:
        passed = 0
        reasons: list[str] = []
        for index in range(1, repeats + 1):
            result = await run_scenario(ctx, texts[name], approve=True)
            ok = result.status.value == "done" and result.success_rate == 1.0
            if ok:
                passed += 1
                detail = "ok"
            else:
                detail = _failure_reason(result, Path(ctx.settings.runs_dir))
                reasons.append(detail)
            print(f"{name} {index}/{repeats} {detail if not ok else 'ok'}", flush=True)
            shutil.rmtree(Path(ctx.settings.runs_dir) / result.run_id, ignore_errors=True)
            shutil.rmtree(Path(ctx.settings.profiles_dir) / result.run_id, ignore_errors=True)
        report[name] = {"runs": repeats, "passed": passed, "reasons": reasons}
    return report


def _write(path: Path, report: dict) -> float:
    total_runs = 0
    total_passed = 0
    lines = [
        "# Reliability",
        "",
        "S3 (shop listings older than 4 months) and S1 (ai-alpha research) on real Chromium.",
        "Sandbox delay is 100–800 ms. The cookie banner is shown (no `gh_banner` cookie is set ahead of the run).",
        "A run passes only when status is `done` and every step succeeds.",
        "",
        "| Scenario | Runs | Passed | Failed | Success rate |",
        "| --- | ---: | ---: | ---: | ---: |",
    ]
    for name in SCENARIOS:
        row = report[name]
        runs = row["runs"]
        passed = row["passed"]
        failed = runs - passed
        rate = passed / runs if runs else 0.0
        total_runs += runs
        total_passed += passed
        lines.append(f"| {name} | {runs} | {passed} | {failed} | {rate * 100:.1f}% |")
    overall = total_passed / total_runs if total_runs else 0.0
    lines.append(f"| Total | {total_runs} | {total_passed} | {total_runs - total_passed} | {overall * 100:.1f}% |")
    lines.extend(["", "## Failed steps", ""])
    any_fail = False
    for name in SCENARIOS:
        counts = Counter(report[name]["reasons"])
        if not counts:
            continue
        any_fail = True
        lines.append(f"### {name}")
        lines.append("")
        lines.append("| Count | Reason |")
        lines.append("| ---: | --- |")
        for reason, count in counts.most_common():
            safe = reason.replace("|", "\\|")
            lines.append(f"| {count} | {safe} |")
        lines.append("")
    if not any_fail:
        lines.append("No failed steps.")
        lines.append("")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")
    return overall


def main() -> int:
    parser = argparse.ArgumentParser(description="Chromium reliability measurement for S1 and S3")
    parser.add_argument("--repeats", type=int, default=REPEATS)
    parser.add_argument("--port", type=int, default=18770)
    parser.add_argument("--out", type=Path, default=ROOT / "docs" / "RELIABILITY.md")
    args = parser.parse_args()
    if args.repeats < 1:
        raise SystemExit("repeats must be >= 1")

    tmp = Path(tempfile.mkdtemp(prefix="grasshopper-reliability-"))
    _prepare_env(tmp, args.port)
    _start_sandbox(args.port)

    from grasshopper.runtime import get_context, reset_context

    reset_context()
    ctx = get_context()
    names = [getattr(item, "name", "") for item in ctx.notifier.notifiers]
    if "telegram" in names or "whatsapp" in names:
        raise SystemExit("refusing to measure while a real notifier is configured")
    if ctx.settings.browser_driver != "playwright":
        raise SystemExit("browser driver is not playwright")

    report = asyncio.run(_measure(ctx, args.repeats))
    rate = _write(args.out, report)
    print(f"rate={rate * 100:.1f} wrote={args.out}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
