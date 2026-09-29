"""Write a submission folder. This never submits anything."""

from __future__ import annotations

import json
from pathlib import Path

from grasshopper.config import ROOT


def load_competitions() -> list[dict]:
    path = ROOT / "data" / "competitions.json"
    return json.loads(path.read_text(encoding="utf-8"))


def build_kit(slug: str, dest_root: Path | None = None) -> Path:
    rows = load_competitions()
    row = next((item for item in rows if item["slug"] == slug), None)
    if row is None:
        known = ", ".join(item["slug"] for item in rows)
        raise SystemExit(f"Unknown competition {slug!r}. Known: {known}")
    dest = (dest_root or (ROOT / "submissions")) / slug
    dest.mkdir(parents=True, exist_ok=True)
    measured = _measured_line()
    (dest / "README.md").write_text(_readme(row, measured), encoding="utf-8")
    if slug != "amazon":
        (dest / "DESCRIPTION.md").write_text(
            row.get("summary", "") + "\n\n" + row.get("how_to_enable", "") + "\n\n"
            "Demo video: https://youtu.be/3MFjYfCec4c\n\n"
            "Halil should review this draft. It is not submitted.\n",
            encoding="utf-8",
        )
        (dest / "VIDEO_SCRIPT.md").write_text(_script(row, measured), encoding="utf-8")
    (dest / "FORM.md").write_text(_form(row, measured), encoding="utf-8")
    (dest / "ENV.md").write_text(_env_flags(row), encoding="utf-8")
    (dest / "MISSING.md").write_text(_missing(row), encoding="utf-8")
    (dest / "CHECKLIST.md").write_text(
        f"- [ ] Required piece present: {row.get('required', '')}\n"
        f"- [ ] Flag `{row.get('flag', '')}` demonstrated\n"
        "- [ ] Video under 3 minutes\n"
        "- [ ] No secrets in the repo\n"
        "- [ ] MIT license included\n"
        "- [ ] Final submit button left for a human\n",
        encoding="utf-8",
    )
    (dest / "TECH.md").write_text(
        "- Python, FastAPI, Playwright, OpenCV 5, SQLite, MCP Streamable HTTP\n"
        f"- Enable: {row.get('how_to_enable', '')}\n",
        encoding="utf-8",
    )
    (dest / "CHANGES_DURING_HACKATHON.md").write_text(
        f"# Changes during {row['name']}\n\n"
        f"Suggested git tag: `{row.get('tag', 'v0.1-' + slug)}`\n\n"
        "- Date:\n- What shipped during the window:\n- What already existed before the window:\n",
        encoding="utf-8",
    )
    return dest


def _measured_line() -> str:
    path = ROOT / "docs" / "RELIABILITY_REAL.md"
    if not path.is_file():
        return "Measured real-site success: unmeasured."
    text = path.read_text(encoding="utf-8")
    if "Success:" not in text and "Ba\u015far\u0131:" not in text:
        return "Measured real-site success: unmeasured."
    return "Measured real-site numbers are in docs/RELIABILITY_REAL.md. Read them on camera. Do not invent a percentage."


def _readme(row: dict, measured: str) -> str:
    return (
        f"# {row['name']}\n\n"
        f"Deadline: {row['deadline']}\n\n"
        f"Prize: {row.get('prize', '')}\n\n"
        f"Verification: {row.get('verification', 'unknown')}\n\n"
        f"{row.get('summary', '')}\n\n"
        f"{measured}\n\n"
        "Grasshopper is an open-source multi-step browser worker. "
        "This folder is a kit only. Nothing here is submitted automatically. "
        "Halil should review this draft.\n"
    )


def _script(row: dict, measured: str) -> str:
    return (
        f"# {row['name']} — 3 minute script\n\n"
        "Halil should review this draft. It is not a submission.\n\n"
        "0:00–0:20 Hook. One sentence: a worker that checks its own clicks, stops before it spends, "
        f"and shows the cost. Name the sponsor piece for this kit: {row.get('required', '')}.\n\n"
        f"0:20–1:10 Measured number. {measured} If the file says unmeasured, say unmeasured.\n\n"
        "1:10–2:20 Live path. Dashboard, one task, the timeline, the approval gate.\n\n"
        "2:20–2:45 What is still missing. Read MISSING.md. Do not claim a key you do not have.\n\n"
        "2:45–3:00 Close on the license and the three setup commands. Keep the cut under 180 seconds.\n"
    )


def _form(row: dict, measured: str) -> str:
    return (
        f"# Submission form draft — {row['name']}\n\n"
        "English draft for Halil to edit. Do not submit this text as-is.\n\n"
        f"Project: Grasshopper, an open-source multi-step browser worker (MIT).\n\n"
        f"What it does: {row.get('summary', '')}\n\n"
        f"Required technology: {row.get('required', '')}\n\n"
        f"How to run: bash scripts/setup.sh, then make test. Mock mode needs no API key.\n\n"
        f"Evidence: {measured}\n\n"
        "The demo video is under three minutes. The repository is the source of truth. "
        "A person submits. The agent does not.\n"
    )


def _env_flags(row: dict) -> str:
    flag = row.get("flag", "")
    lines = [
        "# Environment flags",
        "",
        "MODE=mock",
        "BUDGET_USD_DAILY=0.50",
        "BUDGET_USD_PER_RUN=0.05",
        "ALLOW_BEDROCK=0",
        "",
        f"Competition flag: {flag}",
        row.get("how_to_enable", ""),
        "",
    ]
    return "\n".join(lines) + "\n"


def _missing(row: dict) -> str:
    return (
        f"# Still missing — {row['name']}\n\n"
        "- Halil reviews the draft.\n"
        "- The form is not submitted.\n"
        "- A public repository URL is not recorded here.\n"
        "- Live provider spend for this kit: unmeasured unless docs/RELIABILITY_REAL.md says otherwise.\n"
        f"- Enable when ready: {row.get('how_to_enable', '')}\n"
    )


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--competition", default="")
    parser.add_argument("--all", action="store_true")
    args = parser.parse_args()
    if args.all:
        for row in load_competitions():
            if row.get("eligible") is False:
                continue
            print(build_kit(row["slug"]))
        return
    if not args.competition:
        raise SystemExit("pass --competition or --all")
    print(build_kit(args.competition))


if __name__ == "__main__":
    main()
