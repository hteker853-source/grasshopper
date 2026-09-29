"""The real-site loop against a local stand-in, plus the vision measurements."""

from __future__ import annotations

import asyncio
import json
from pathlib import Path

from grasshopper.config import get_settings
from grasshopper.core.router import Router
from grasshopper.db import Database
from grasshopper.demo_scenarios import run_scenario
from grasshopper.realweb.blast import runner_label
from grasshopper.realweb.learning import LearningStore
from grasshopper.realweb.loop import run_web
from grasshopper.realweb.recovery import measure_change_accuracy, measure_dom_recovery
from grasshopper.realweb.scenarios import fixture_scenarios
from tests.realweb_site import serve


def _router(tmp_path: Path):
    settings = get_settings().model_copy(update={
        "browser_driver": "http",
        "real_site_delay_sec": 0.0,
        "data_dir": tmp_path,
        "runs_dir": tmp_path / "runs",
        "profiles_dir": tmp_path / "profiles",
    })
    settings.data_dir.mkdir(parents=True, exist_ok=True)
    return settings, Router(settings, Database(tmp_path / "web.db"))


def test_fixture_scenarios_succeed_and_the_second_r1_run_calls_no_model(tmp_path: Path):
    server, base = serve()
    try:
        settings, router = _router(tmp_path)
        upload = tmp_path / "note.txt"
        upload.write_text("hello fixture", encoding="utf-8")
        scenarios = fixture_scenarios(base, str(upload))
        first = asyncio.run(run_web(scenarios["R1"], settings, router, tmp_path / "r1a"))
        assert first.ok, first.error
        assert "Gamma Tale" in first.summary
        assert first.llm_calls > 0
        assert first.usd_actual == 0.0
        assert (tmp_path / "r1a" / "blast_radius.json").is_file()
        second = asyncio.run(run_web(scenarios["R1"], settings, router, tmp_path / "r1b"))
        assert second.ok, second.error
        assert second.llm_calls == 0
        panel = LearningStore(tmp_path / "learning.json").panel()
        assert panel["label"] == "measured"
        assert panel["first_calls"] == first.llm_calls
        assert panel["second_calls"] == 0
        for key in ("R2", "R3", "R4", "R5"):
            report = asyncio.run(run_web(scenarios[key], settings, router, tmp_path / key))
            assert report.ok, (key, report.error, report.summary)
            if key == "R2":
                assert "$" in report.summary
                assert report.summary.lower().startswith("total")
        broken = asyncio.run(run_web(scenarios["REC"], settings, router, tmp_path / "rec"))
        assert broken.ok, broken.error
        assert broken.vision_calls >= 1
    finally:
        server.shutdown()


def test_vision_change_and_dom_recovery_are_measured(tmp_path: Path):
    change = measure_change_accuracy(tmp_path / "change", n_each=10)
    recovery = measure_dom_recovery(tmp_path / "recover", n=20)
    assert change["total"] == 20
    assert change["correct"] == change["total"]
    assert recovery["n"] == 20
    assert recovery["hits"] == recovery["n"]
    assert 0.0 <= change["accuracy"] <= 1.0
    assert 0.0 <= recovery["rate"] <= 1.0


def test_a_sandbox_run_writes_a_blast_radius_file(ctx):
    result = asyncio.run(run_scenario(ctx, "Check the news headlines and notify me with the top trend."))
    path = Path(ctx.settings.runs_dir) / result.run_id / "blast_radius.json"
    payload = json.loads(path.read_text(encoding="utf-8"))
    assert "duration_sec" in payload
    assert "domains" in payload
    assert "files_touched" in payload
    assert payload["runner"] == runner_label()
    assert payload["cost_usd"] == 0.0


def test_arxiv_api_allowlist_and_robots_policy():
    from grasshopper.config import get_settings
    from grasshopper.realweb.policy import (
        CODE_ALLOWLIST,
        classify,
        path_blocked,
    )

    assert "export.arxiv.org" in CODE_ALLOWLIST
    settings = get_settings()
    verdict = classify("https://export.arxiv.org/api/query?search_query=all:browser+agents", settings)
    assert verdict.allowed
    assert not path_blocked("/api/query", ["/"], host="export.arxiv.org")
    assert path_blocked("/other", ["/"], host="export.arxiv.org")

