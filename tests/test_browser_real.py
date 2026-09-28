"""S3 and S6 through real Chromium against the sandbox."""

from __future__ import annotations

import asyncio
import os

import pytest

from grasshopper.demo_scenarios import S3, S6, run_scenario

pytestmark = pytest.mark.browser


@pytest.fixture
def browser_ctx(sandbox_url):
    os.environ["BROWSER_DRIVER"] = "playwright"
    from grasshopper.runtime import get_context, reset_context

    reset_context()
    ctx = get_context()
    assert ctx.settings.browser_driver == "playwright"
    try:
        yield ctx
    finally:
        os.environ["BROWSER_DRIVER"] = "http"
        reset_context()


def test_s3_old_listings_in_chromium(browser_ctx):
    result = asyncio.run(run_scenario(browser_ctx, S3, approve=True))
    assert result.status.value == "done"
    assert "Stale listings" in result.summary
    assert result.success_rate == 1


def test_s6_approved_payment_in_chromium(browser_ctx):
    result = asyncio.run(run_scenario(browser_ctx, S6, approve=True))
    assert result.status.value == "done"
    assert "Receipt:" in result.summary
    assert result.success_rate == 1
    from grasshopper.providers.wallet_mock import WalletLimitError

    with pytest.raises(WalletLimitError):
        browser_ctx.wallet.pay(0.2, "over per-tx limit")
