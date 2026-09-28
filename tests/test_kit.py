"""Competition kits are drafts with a hook and an English form."""

from __future__ import annotations

from grasshopper.publish.submission_kit import build_kit


def test_kit_script_opens_with_a_hook_and_the_form_is_english(tmp_path):
    dest = build_kit("hetic", tmp_path)
    script = (dest / "VIDEO_SCRIPT.md").read_text(encoding="utf-8")
    form = (dest / "FORM.md").read_text(encoding="utf-8")
    missing = (dest / "MISSING.md").read_text(encoding="utf-8")
    assert "0:00–0:20" in script
    assert "180 seconds" in script
    assert "Halil should review" in script
    assert "not a submission" in script
    assert "Project: Grasshopper" in form
    assert "ölçülmedi" in missing or "RELIABILITY_REAL" in script
