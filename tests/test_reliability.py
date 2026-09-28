"""100 sandbox repetitions of the shop playbook. Random delay stays on."""

from __future__ import annotations

import os

import pytest

from grasshopper.demo_scenarios import S3, run_scenario

pytestmark = pytest.mark.reliability


def test_shop_playbook_success_rate(ctx):
    os.environ["SANDBOX_DELAY_MIN_MS"] = "5"
    os.environ["SANDBOX_DELAY_MAX_MS"] = "40"
    import asyncio

    async def _all():
        results = []
        for _ in range(100):
            results.append(await run_scenario(ctx, S3, approve=True))
        return results

    results = asyncio.run(_all())
    rate = sum(result.success_rate for result in results) / len(results)
    assert rate >= 0.98
    assert all(result.status.value == "done" for result in results)
