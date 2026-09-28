"""The Amazon folder is a review draft, not a submission."""

from pathlib import Path


def test_amazon_draft_is_marked_for_halil_and_cites_the_demo_logs():
    root = Path("submissions/amazon")
    description = (root / "DESCRIPTION.md").read_text(encoding="utf-8")
    script = (root / "VIDEO_SCRIPT.md").read_text(encoding="utf-8")
    friction = (root / "FRICTION_LOG.md").read_text(encoding="utf-8")
    for text in (description, script, friction):
        assert "Halil should review" in text
        assert "not" in text.lower() and "submit" in text.lower()
    assert "run_ed76f4a16239" in description
    assert "180 seconds" in script
    assert "0:00–0:20" in script and "2:45–3:00" in script
    assert "run_9f24d8fa5fad" in friction
    assert "export-btn-renamed" in friction
    assert "Task group is not initialized" in friction
