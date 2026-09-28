"""The readiness report keeps unverified rules and skips Colosseum."""

from pathlib import Path


def test_facts_mark_unverified_rules_and_the_report_does_not_treat_them_as_wins():
    facts = Path("docs/rules/facts.md").read_text(encoding="utf-8")
    report = Path("docs/READINESS.md").read_text(encoding="utf-8")
    assert "DOĞRULANMADI" in facts
    assert "Ağustos teklif aşaması DOĞRULANMADI" in facts
    assert "İkincil kaynak. DOĞRULANMADI" in facts
    assert "Türkiye uygunluğu DOĞRULANMADI" in facts
    assert "2027 kuralları DOĞRULANMADI" in facts
    assert "TAHMİN" in report
    assert "kesin kazan" not in report.lower()
    assert "| Colosseum | — | girilmeyecek | 0 | 0 | ATLA |" in report
    assert "make share" in report
    assert "test_s9_mcp_client" in report
    assert "test_bedrock_converse_is_stubbed" in report
