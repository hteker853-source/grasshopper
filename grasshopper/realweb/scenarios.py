"""Real-site goals. Success is checked from the page, not from the model's sentence."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class Scenario:
    id: str
    goal: str
    start_url: str
    max_steps: int = 24
    max_seconds: float = 90
    upload_path: str = ""
    urls: dict = field(default_factory=dict)


def is_done(scenario_id: str, memory: dict, obs: dict) -> bool:
    if scenario_id == "R1":
        chosen = memory.get("chosen") or {}
        summary = memory.get("author_summary") or ""
        if chosen.get("rating") != "Four":
            return False
        if abs(float(chosen.get("price") or -1) - float(memory.get("min_four_price") or -2)) > 1e-6:
            return False
        return len(summary) >= 40
    if scenario_id == "R2":
        total = str(memory.get("total") or "")
        clicked = memory.get("clicked") or []
        return len(clicked) >= 2 and "total" in total.lower() and "$" in total
    if scenario_id == "R3":
        items = memory.get("summaries") or []
        return len(items) >= 3 and all(len(str(item)) > 8 for item in items[:3])
    if scenario_id == "R4":
        papers = memory.get("papers_saved") or []
        return len(papers) >= 3 and all(paper.get("title") for paper in papers[:3])
    if scenario_id == "R5":
        return bool(memory.get("dynamic") and memory.get("dropdown") and memory.get("upload"))
    if scenario_id == "REC":
        return bool(memory.get("landed"))
    return False


def live_scenarios() -> list[Scenario]:
    return [
        Scenario(
            "R1",
            "find the cheapest 4-star book on books.toscrape and summarize its author on Wikipedia",
            "https://books.toscrape.com/index.html",
            max_steps=70,
            max_seconds=240,
            urls={"wiki": "https://en.wikipedia.org/wiki/"},
        ),
        Scenario(
            "R2",
            "log into saucedemo, add two items, read the total in checkout summary",
            "https://www.saucedemo.com/",
            max_steps=20,
            max_seconds=90,
        ),
        Scenario(
            "R3",
            "summarize the top three Hacker News headlines",
            "https://news.ycombinator.com/",
            max_steps=6,
            max_seconds=40,
        ),
        Scenario(
            "R4",
            "write the latest three papers in arXiv 'browser agents' search",
            "https://export.arxiv.org/api/query?search_query=all:browser+agents&start=0&max_results=3",
            max_steps=6,
            max_seconds=40,
        ),
        Scenario(
            "R5",
            "the-internet dynamic loading, dropdown list and file upload",
            "https://the-internet.herokuapp.com/dynamic_loading/2",
            max_steps=16,
            max_seconds=90,
            urls={
                "dynamic": "https://the-internet.herokuapp.com/dynamic_loading/2",
                "dropdown": "https://the-internet.herokuapp.com/dropdown",
                "upload": "https://the-internet.herokuapp.com/upload",
            },
        ),
    ]


def fixture_scenarios(base: str, upload_path: str) -> dict[str, Scenario]:
    root = base.rstrip("/")
    return {
        "R1": Scenario(
            "R1",
            "fixture cheapest four-star book and a wiki paragraph",
            f"{root}/catalogue/page-1.html",
            max_steps=12,
            max_seconds=20,
            urls={"wiki": f"{root}/wiki?q="},
        ),
        "R2": Scenario(
            "R2",
            "fixture shop login, two items, total",
            f"{root}/login",
            max_steps=16,
            max_seconds=20,
        ),
        "R3": Scenario(
            "R3",
            "fixture three headlines",
            f"{root}/hn",
            max_steps=4,
            max_seconds=10,
        ),
        "R4": Scenario(
            "R4",
            "fixture three papers",
            f"{root}/arxiv",
            max_steps=4,
            max_seconds=10,
        ),
        "R5": Scenario(
            "R5",
            "fixture resilience pack",
            f"{root}/dynamic",
            max_steps=14,
            max_seconds=20,
            upload_path=upload_path,
            urls={
                "dynamic": f"{root}/dynamic",
                "dropdown": f"{root}/dropdown",
                "upload": f"{root}/upload",
            },
        ),
        "REC": Scenario(
            "REC",
            "Continue after the id disappears",
            f"{root}/recovery-broken",
            max_steps=6,
            max_seconds=10,
        ),
    }
