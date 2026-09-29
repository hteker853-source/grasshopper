"""Stage-4 gates: catalog cost, climate evidence, and the mock bank."""

from __future__ import annotations

import asyncio

import httpx

from grasshopper.realweb.bank import BankLimit, BankSandbox
from grasshopper.realweb.climate import record_if_supported
from grasshopper.realweb.costing import catalog_table, render_table, tavily_status


def test_catalog_fast_is_cheaper_than_strong_and_live_nebius_is_unmeasured():
    prompt = "Nemotron fast tier versus the strong tier on one fixed prompt."
    row = catalog_table(prompt)
    assert row["fast_usd"] < row["strong_usd"]
    assert row["tokens_estimated"] == max(1, len(prompt) // 4)
    assert row["live_nebius"] == "unmeasured"
    assert row["source"] == "catalog price"
    text = render_table(prompt, tavily=tavily_status(""))
    assert "waiting for key" in text
    assert tavily_status("present") == "key present"


def test_climate_sentence_is_written_only_when_the_page_says_it(ctx):
    html = "<p>The station record lists a 1.1 degree rise in the cited series.</p>"
    hit = record_if_supported(ctx.wallet, html, "1.1 degree", "https://en.wikipedia.org/wiki/Climate")
    assert hit["verified"] is True
    assert "1.1 degree" in hit["sentence"]
    memo = hit["memo"]
    assert any(row["memo"] == memo for row in ctx.wallet.ledger())
    miss = record_if_supported(ctx.wallet, html, "9.9 degree", "https://en.wikipedia.org/wiki/Climate")
    assert miss["verified"] is False
    assert miss["tx"] == ""


def test_bank_refuses_over_the_limit_and_records_approval():
    bank = BankSandbox(per_tx=100, daily=500)
    try:
        bank.request_transfer(150, "too big")
        raised = False
    except BankLimit:
        raised = True
    assert raised
    assert bank.audit[-1]["event"] == "refused"
    assert bank.request_transfer(40, "invoice") == "approval_required"
    assert bank.decide("rejected") == "rejected"
    assert bank.balance == 1000
    assert bank.request_transfer(40, "invoice") == "approval_required"
    assert bank.decide("approved") == "approved"
    assert bank.balance == 960
    events = [row["event"] for row in bank.audit]
    assert "approval_required" in events and "approved" in events


def test_bank_pages_refuse_and_then_approve(sandbox_url):
    client = httpx.Client(base_url=sandbox_url, follow_redirects=True, timeout=10)
    refused = client.post("/bank/transfer", data={"amount": "150", "memo": "rent"})
    assert refused.status_code == 200
    assert "Refused" in refused.text
    asked = client.post("/bank/transfer", data={"amount": "25", "memo": "rent"})
    assert "Approval required" in asked.text
    approved = client.post("/bank/approve", data={"amount": "25", "memo": "rent", "decision": "approved"})
    assert "Approved" in approved.text
    home = client.get("/bank")
    assert "approved" in home.text
    assert "refused" in home.text


def test_meta_llama_routing_and_nebius_fallback():
    from grasshopper.config import Settings
    from grasshopper.providers.factory import build_llm
    from grasshopper.providers.llm_mock import MockLLM
    from grasshopper.providers.llm_openai_compat import OpenAICompatLLM

    # 1. No keys -> fallback to MockLLM
    s_mock = Settings(llm_fast_provider="meta", meta_api_key="", nebius_api_key="")
    llm1 = build_llm("meta", s_mock, tier="fast")
    assert isinstance(llm1, MockLLM)

    # 2. Direct Meta key
    s_direct = Settings(
        llm_fast_provider="meta",
        meta_api_key="direct-meta-key",
        meta_base_url="https://api.meta.example.com/v1",
        meta_model="meta-llama/Meta-Llama-3-70B",
    )
    llm2 = build_llm("meta", s_direct, tier="fast")
    assert isinstance(llm2, OpenAICompatLLM)
    assert llm2.name == "meta"
    assert llm2.model == "meta-llama/Meta-Llama-3-70B"

    # 3. Via Nebius
    s_nebius = Settings(
        llm_fast_provider="meta",
        meta_api_key="",
        nebius_api_key="nebius-key",
        nebius_base_url="https://api.tokenfactory.nebius.com/v1",
    )
    llm3 = build_llm("meta", s_nebius, tier="fast")
    assert isinstance(llm3, OpenAICompatLLM)
    assert llm3.name == "meta"
    assert llm3.model == "NousResearch/Hermes-4-405B"
    assert "tokenfactory.nebius.com" in llm3.base_url

