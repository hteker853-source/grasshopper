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
        "source": "katalog fiyatı",
        "live_nebius": "ölçülmedi",
        "fast_model_slot": "NEBIUS_FAST_MODEL (NVIDIA Nemotron adı buraya yazılır)",
    }


def tavily_status(api_key: str) -> str:
    if (api_key or "").strip():
        return "anahtar var"
    return "anahtar bekliyor"


def render_table(prompt: str, *, tavily: str) -> str:
    row = catalog_table(prompt)
    return "\n".join([
        "# Fast ve strong katalog maliyeti",
        "",
        "Canlı Nebius faturası ölçülmedi. Aşağıdaki dolar katalog fiyatıdır.",
        "",
        "| | fast | strong |",
        "| --- | --- | --- |",
        f"| 1.000 token fiyatı | ${PRICE_PER_1K['fast']} | ${PRICE_PER_1K['strong']} |",
        f"| Bu metin ({row['tokens_estimated']} token tahmini) | ${row['fast_usd']:.6f} | ${row['strong_usd']:.6f} |",
        "",
        f"Strong / fast oranı: {row['ratio_strong_over_fast']:.1f}.",
        f"Fast yuva: {row['fast_model_slot']}.",
        f"Tavily: {tavily}.",
        "",
    ])
