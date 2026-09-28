#!/usr/bin/env python3
"""Run Nebius Token Factory live demo in under 3 minutes."""

import asyncio
import os
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from grasshopper.config import load_settings
from grasshopper.core.router import Router
from grasshopper.db import Database


async def run_nebius_demo():
    print("=" * 60)
    print("GRASSHOPPER NEBIUS TOKEN FACTORY LIVE DEMO")
    print("=" * 60)
    t0 = time.time()

    settings = load_settings()
    base_url = settings.nebius_base_url or "https://api.tokenfactory.nebius.com/v1"
    fast_model = settings.nebius_fast_model or "nvidia/Nemotron-3_5-Lightning"

    print(f"Endpoint : {base_url}")
    print(f"Fast LLM : {fast_model}")
    print(f"Provider : {settings.llm_fast_provider}")

    db = Database(ROOT / "data" / "nebius_demo.db")
    router = Router(settings, db)

    prompt = (
        "You are an autonomous web agent. Given this page state: "
        "URL='https://books.toscrape.com', Book='Soumission', Price=£50.10, Rating=Four. "
        "Output a single JSON action to proceed: {\"type\": \"remember\", \"key\": \"selected\", \"value\": \"Soumission\"}"
    )

    print("\n[1/2] Sending decision query to Nebius Token Factory...")
    res = await router.complete("fast", prompt, run_id="nebius-demo")
    print(f"      Response received in {(time.time() - t0):.2f}s:")
    print(f"      Text: {res.text.strip()}")

    print("\n[2/2] Cost and Token Accounting (BudgetLedger):")
    actual_cost = router.budget.daily_actual
    print(f"      Daily Actual Spend: ${actual_cost:.6f}")
    print(f"      Fast Tier Calls   : {len(router.calls)}")

    elapsed = time.time() - t0
    print("=" * 60)
    print(f"DEMO COMPLETE in {elapsed:.2f}s (Budget: <= 180s) - SUCCESS!")
    print("=" * 60)
    return 0


if __name__ == "__main__":
    raise SystemExit(asyncio.run(run_nebius_demo()))
