"""Catalog fast-vs-strong cost. A live Nebius invoice is not invented here."""

from __future__ import annotations

from grasshopper.core.budget import PRICE_PER_1K


def catalog_table(prompt: str) -> dict:
    tokens = max(1, len(prompt) // 4)
    fast = PRICE_PER_1K["fast"] * tokens / 1000
    strong = PRICE_PER_1K["strong"] * tokens / 1000
    return {
        "tokens_estimated": tokens,
        "fast_usd": fast,
        "strong_usd": strong,
        "ratio_strong_over_fast": (strong / fast) if fast else 0.0,
        "source": "catalog price",
        "live_nebius": "unmeasured",
        "fast_model_slot": "NEBIUS_FAST_MODEL (NVIDIA Nemotron model name goes here)",
    }


def tavily_status(api_key: str) -> str:
    if (api_key or "").strip():
        return "key present"
    return "waiting for key"


def render_table(prompt: str, *, tavily: str) -> str:
    row = catalog_table(prompt)
    return "\n".join([
        "# Fast and strong catalog cost",
        "",
        "Live Nebius invoice is unmeasured. The dollar amounts below are catalog prices.",
        "",
        "| | fast | strong |",
        "| --- | --- | --- |",
        f"| Price per 1,000 tokens | ${PRICE_PER_1K['fast']} | ${PRICE_PER_1K['strong']} |",
        f"| This prompt ({row['tokens_estimated']} token estimate) | ${row['fast_usd']:.6f} | ${row['strong_usd']:.6f} |",
        "",
        f"Strong / fast ratio: {row['ratio_strong_over_fast']:.1f}.",
        f"Fast slot: {row['fast_model_slot']}.",
        f"Tavily: {tavily}.",
        "",
    ])
