"""Audit classifications: keys wait, fake tests fail, secrets are filenames only."""

from __future__ import annotations

from pathlib import Path

from scripts.audit import (
    FAIL,
    PASS,
    WAIT,
    competition_row,
    env_is_tracked,
    fake_tests,
    mcp_tools_ok,
    missing_keys,
    readme_gaps,
    secret_hits,
)


def test_missing_keys_are_waiting_not_failed():
    assert missing_keys(["AWS_ACCESS_KEY_ID", "BEDROCK_MODEL_ID"], {"AWS_ACCESS_KEY_ID": ""}) == [
        "AWS_ACCESS_KEY_ID",
        "BEDROCK_MODEL_ID",
    ]
    row = competition_row(
        {"name": "AWS", "slug": "amazon-aws", "flag": "bedrock", "required": "Amazon Bedrock", "eligible": True},
        {},
        video_ok=True,
        mcp_ok=True,
        has_form=False,
        has_pr=False,
    )
    assert row.status == WAIT
    assert row.status != FAIL
    assert "AWS_ACCESS_KEY_ID" in row.missing
    assert "anahtar" in row.missing


def test_video_form_and_pr_gaps_fail_when_no_key_is_required(tmp_path):
    row = competition_row(
        {
            "name": "Pitch",
            "slug": "pitch",
            "flag": "prototype",
            "required": "A working prototype, a pitch video, a signup form, and a pull request",
            "eligible": True,
        },
        {},
        video_ok=False,
        mcp_ok=True,
        has_form=False,
        has_pr=False,
    )
    assert row.status == FAIL
    assert "video" in row.missing
    assert "form" in row.missing
    assert "PR" in row.missing


def test_ready_flag_passes_and_mcp_tools_are_required():
    row = competition_row(
        {"name": "OpenCV", "slug": "opencv", "flag": "opencv", "required": "Meaningful image analysis with OpenCV 5", "eligible": True},
        {},
        video_ok=True,
        mcp_ok=True,
        has_form=False,
        has_pr=False,
    )
    assert row.status == PASS
    assert mcp_tools_ok({"run_task", "get_task_status", "approve", "council_ask"})
    assert not mcp_tools_ok({"run_task"})


def test_fake_tests_and_constant_asserts_are_rejected(tmp_path):
    sample = tmp_path / "test_sample.py"
    sample.write_text(
        "def test_empty():\n"
        "    x = 1\n"
        "def test_true():\n"
        "    assert True\n"
        "def test_same():\n"
        "    assert 1 == 1\n"
        "def test_real():\n"
        "    assert 1 == len([1])\n"
        "def test_raises():\n"
        "    import pytest\n"
        "    with pytest.raises(RuntimeError):\n"
        "        raise RuntimeError('no')\n",
        encoding="utf-8",
    )
    found = fake_tests([sample])
    assert "test_sample.py:test_empty" in found
    assert "test_sample.py:test_true" in found
    assert "test_sample.py:test_same" in found
    assert "test_sample.py:test_real" not in found
    assert "test_sample.py:test_raises" not in found


def test_secret_scan_reports_the_file_not_the_value(tmp_path):
    leaked = tmp_path / "notes.md"
    token = "123456789:" + ("A" * 35)
    leaked.write_text("bot " + token + "\n", encoding="utf-8")
    clean = tmp_path / "readme.md"
    clean.write_text("no secrets here\n", encoding="utf-8")
    hits = secret_hits([leaked, clean])
    assert hits == [str(leaked)]
    assert token not in " ".join(hits)
    assert env_is_tracked(["README.md", ".env"])
    assert not env_is_tracked(["README.md", ".env.example"])


def test_readme_needs_setup_and_a_competition_table():
    assert readme_gaps("# Grasshopper\n\nbash scripts/setup.sh\n\n| Competition | Flag |\n") == []
    assert readme_gaps("# Hi\n") == ["kurulum", "yarışma tablosu"]
    text = Path("README.md").read_text(encoding="utf-8")
    assert readme_gaps(text) == []
