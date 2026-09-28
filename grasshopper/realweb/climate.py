"""Climate-claim check. A sentence is stored only when the page contains it."""

from __future__ import annotations

import hashlib
import re

from bs4 import BeautifulSoup


def extract_sentence(html: str, claim: str) -> str:
    """Return the page sentence that contains the claim, or an empty string."""
    text = BeautifulSoup(html or "", "html.parser").get_text(" ", strip=True)
    needle = claim.strip().lower()
    if not needle or needle not in text.lower():
        return ""
    for sentence in re.split(r"(?<=[.!?])\s+", text):
        if needle in sentence.lower():
            return " ".join(sentence.split())
    return ""


def evidence_memo(sentence: str, source_url: str) -> str:
    digest = hashlib.sha256(sentence.encode()).hexdigest()[:16]
    return f"climate evidence {digest} source={source_url}"


def record_if_supported(wallet, html: str, claim: str, source_url: str, *, amount_sol: float = 0.001) -> dict:
    sentence = extract_sentence(html, claim)
    if not sentence:
        return {"verified": False, "tx": "", "sentence": ""}
    memo = evidence_memo(sentence, source_url)
    tx = wallet.pay(amount_sol, memo, task_id=None)
    return {"verified": True, "tx": tx, "sentence": sentence, "memo": memo}
