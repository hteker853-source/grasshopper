"""The readiness report keeps unverified rules and skips Colosseum."""

from pathlib import Path


def test_facts_mark_unverified_rules_and_the_report_does_not_treat_them_as_wins():
    facts = Path("docs/rules/facts.md").read_text(encoding="utf-8")
    report = Path("docs/READINESS.md").read_text(encoding="utf-8")
    assert "UNVERIFIED" in facts
    assert "August proposal phase UNVERIFIED" in facts
    assert "Secondary source. UNVERIFIED" in facts
    assert "Turkey eligibility UNVERIFIED" in facts
    assert "2027 rules UNVERIFIED" in facts
    assert "ESTIMATE" in report
    assert "guaranteed win" not in report.lower()
    assert "| Colosseum | — | will not enter | 0 | 0 | SKIP |" in report
    assert "make share" in report
    assert "test_s9_mcp_client" in report
    assert "test_bedrock_converse_is_stubbed" in report
