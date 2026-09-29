"""Budget ceiling and the real-site allow/deny gate."""

from __future__ import annotations

import asyncio
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

import httpx
import pytest

from grasshopper.core.budget import BudgetExceeded, BudgetLedger
from grasshopper.providers.llm_mock import MockLLM
from grasshopper.realweb.policy import (
    CODE_ALLOWLIST,
    PolicyError,
    classify,
    clear_policy_cache,
    enforce,
)


class _Settings:
    def __init__(self, allowlist: str = "", delay: float = 0.0):
        self.real_sites_allowlist = allowlist
        self.real_site_delay_sec = delay


def test_code_allowlist_contains_the_required_hosts():
    for host in (
        "books.toscrape.com",
        "quotes.toscrape.com",
        "saucedemo.com",
        "the-internet.herokuapp.com",
        "webscraper.io",
        "wikipedia.org",
        "arxiv.org",
        "news.ycombinator.com",
        "github.com",
    ):
        assert host in CODE_ALLOWLIST


def test_denylist_blocks_shops_social_login_and_payment_pages():
    settings = _Settings()
    blocked = {
        "https://www.etsy.com/listing/1": "denylist",
        "https://www.amazon.com/dp/1": "denylist",
        "https://amazon.co.uk/s?k=book": "denylist",
        "https://twitter.com/grasshopper": "social media",
        "https://www.facebook.com/": "social media",
        "https://accounts.google.com/signin": "google login",
        "https://www.google.com/signin/v2": "google login",
        "https://checkout.stripe.com/pay/cs_test": "payment page",
        "https://example.com/checkout": "payment page",
        "https://github.com/login": "github login",
        "https://example.com/hello": "outside REAL_SITES_ALLOWLIST",
    }
    for url, reason in blocked.items():
        verdict = classify(url, settings)
        assert verdict.allowed is False
        assert verdict.reason == reason
    assert classify("https://books.toscrape.com/index.html", settings).allowed
    assert classify("https://en.wikipedia.org/wiki/Book", settings).allowed
    assert classify("https://www.saucedemo.com/checkout-step-two.html", settings).allowed
    assert classify("https://news.ycombinator.com/", settings).allowed


def test_env_allowlist_can_only_narrow_the_code_list():
    settings = _Settings("books.toscrape.com")
    assert classify("https://books.toscrape.com/", settings).allowed
    quotes = classify("https://quotes.toscrape.com/", settings)
    assert quotes.allowed is False
    assert quotes.reason == "REAL_SITES_ALLOWLIST narrowing"
    # A host outside the code list stays outside even if the env names it.
    forced = _Settings("example.com")
    verdict = classify("https://example.com/hello", forced)
    assert verdict.allowed is False
    assert verdict.reason == "outside REAL_SITES_ALLOWLIST"


def test_per_run_cap_stops_before_the_call_and_notifies(ctx):
    router = ctx.router
    original_budget = router.budget
    original_notifier = router.notifier
    router.budget = BudgetLedger(daily_usd=0.50, per_run_usd=0.0)
    before = len(router.calls)
    notes = []

    class _Note:
        async def notify(self, message, *, kind="info", payload=None):
            notes.append((kind, message))

    router.notifier = _Note()
    try:
        with pytest.raises(BudgetExceeded) as caught:
            asyncio.run(router.complete("strong", "x" * 400, run_id="run-budget"))
        assert caught.value.scope == "run"
        assert len(router.calls) == before
        assert notes and notes[0][0] == "budget"
        assert "per-run" in notes[0][1]
    finally:
        router.budget = original_budget
        router.notifier = original_notifier


def test_daily_cap_counts_catalog_reserve_across_runs():
    ledger = BudgetLedger(daily_usd=0.00001, per_run_usd=1.0)
    with pytest.raises(BudgetExceeded) as caught:
        ledger.authorize("strong", "y" * 800, "run-a")
    assert caught.value.scope == "day"
    # A call that fits is reserved only after commit, so a refused call adds nothing.
    assert ledger.daily_estimated == 0.0
    small = BudgetLedger(daily_usd=1.0, per_run_usd=1.0)
    estimate = small.authorize("fast", "hi", "run-b")
    small.commit("run-b", estimate, 0.0)
    assert small.run_estimated["run-b"] == estimate
    assert small.daily_actual == 0.0


def test_mock_actual_cost_stays_zero_while_the_reserve_is_counted(ctx):
    response = asyncio.run(ctx.router.complete("fast", "budget-probe", run_id="run-mock-cost"))
    assert isinstance(ctx.router.fast, MockLLM) or response.provider == "mock"
    assert response.cost_usd == 0.0
    assert ctx.router.budget.run_estimated["run-mock-cost"] > 0


class _Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path.startswith("/robots.txt"):
            body = b"User-agent: *\nDisallow: /private\n"
        elif self.path.startswith("/private"):
            body = b"secret"
        else:
            body = b"<html><body>public</body></html>"
        self.send_response(200)
        self.send_header("Content-Type", "text/plain")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, *_args):
        return


@pytest.fixture
def local_site():
    server = ThreadingHTTPServer(("127.0.0.1", 0), _Handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    base = f"http://127.0.0.1:{server.server_address[1]}"
    clear_policy_cache()
    yield base
    server.shutdown()
    clear_policy_cache()


def test_robots_disallow_and_the_gap_between_requests(local_site):
    settings = _Settings(delay=0.15)

    async def blocked():
        async with httpx.AsyncClient() as client:
            await enforce(local_site + "/private", settings, client=client, govern_local=True)

    with pytest.raises(PolicyError) as caught:
        asyncio.run(blocked())
    assert "robots" in str(caught.value)

    async def spaced():
        async with httpx.AsyncClient() as client:
            await enforce(local_site + "/open", settings, client=client, govern_local=True)
            started = time.monotonic()
            await enforce(local_site + "/open", settings, client=client, govern_local=True)
            return time.monotonic() - started

    # robots is cached, so the second call only waits the configured gap.
    assert asyncio.run(spaced()) >= 0.12
