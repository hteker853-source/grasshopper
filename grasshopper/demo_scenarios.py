"""Shared scenario text for the e2e tests and scripts/demo_all.sh."""

from __future__ import annotations

import asyncio
from datetime import datetime, timezone

S1 = (
    "Go to ai-alpha, sign up with demo account, enable research mode, "
    "research 'solar panels', share the result, find missing profile fields and suggest fixes."
)
S2 = (
    "Ask ai-alpha to write a product description for a planner, copy it, "
    "paste it into ai-beta and ask to shorten it, send me the result."
)
S3 = "Log into shop, find listings older than 4 months, report them with suggestions."
S4 = (
    "In 20 seconds, check news; if a headline has trend score > 80, write a short video script, "
    "generate 2 images on media, merge them, notify me."
)
S5 = (
    "Find competitions I'm eligible for on competitions site, run council with 3 models, "
    "3 rounds, devil's advocate, pick the single strongest project idea."
)
S6 = "Subscribe to the Pro plan on shop using the wallet."
S7 = "Click the export button on broken."
S9 = "Check the news headlines and notify me with the top trend."

ORDER = [
    ("S1", S1, "done"),
    ("S2", S2, "done"),
    ("S3", S3, "done"),
    ("S4", S4, "done"),
    ("S5", S5, "done"),
    ("S6", S6, "done"),
    ("S7", S7, "waiting_approval"),
    ("S8", S3, "done"),
    ("S9", S9, "done"),
]


async def run_scenario(ctx, text: str, *, approve: bool = True):
    task = ctx.orchestrator.accept(text, channel="demo")
    scheduled = task.scheduled_at
    if scheduled and scheduled > datetime.now(timezone.utc):
        delay = (scheduled - datetime.now(timezone.utc)).total_seconds()
        await asyncio.sleep(max(0.0, delay) + 0.3)
        claimed = ctx.queue.claim_next()
        if claimed is None:
            raise RuntimeError("scheduled task was not claimable")
        task_id = claimed.id
    else:
        task_id = task.id

    async def watcher():
        while True:
            if approve:
                for item in ctx.gate.pending(task_id):
                    # Stuck repairs stay pending when approve is False.
                    ctx.gate.decide(item.id, "approved")
            await asyncio.sleep(0.05)

    watch = asyncio.create_task(watcher())
    try:
        return await ctx.orchestrator.execute(task_id)
    finally:
        watch.cancel()
        try:
            await watch
        except asyncio.CancelledError:
            pass
