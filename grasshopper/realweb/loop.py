"""Observe, decide, act, verify, repair. Step budget, time budget, stuck detection."""

from __future__ import annotations

import json
import logging
import time
from dataclasses import dataclass, field
from pathlib import Path

log = logging.getLogger("grasshopper.realweb")

from grasshopper.browser.controller import BrowserController
from grasshopper.core.budget import BudgetExceeded
from grasshopper.realweb.blast import runner_label, write_blast
from grasshopper.realweb.learning import LearningStore
from grasshopper.realweb.observe import observe
from grasshopper.schemas import Action


@dataclass
class WebReport:
    scenario_id: str
    ok: bool
    steps: int
    llm_calls: int
    tokens: int
    usd_estimated: float
    usd_actual: float
    seconds: float
    summary: str
    error: str = ""
    domains: list[str] = field(default_factory=list)
    files: list[str] = field(default_factory=list)
    vision_calls: int = 0


def _prompt(scenario, obs: dict, memory: dict, last_error: str, tier: str) -> str:
    slim = {key: value for key, value in memory.items() if key != "books"}
    if "books" in memory:
        slim["book_count"] = len(memory["books"])
    observation = {
        "url": obs.get("url"),
        "text": (obs.get("text") or "")[:800],
        "next_url": obs.get("next_url") or "",
        "book_count": len(obs.get("books") or []),
        "hn_count": len(obs.get("hn") or []),
        "papers": (obs.get("papers") or [])[:3],
        "wiki_paragraph": obs.get("wiki_paragraph") or "",
        "wiki_results": obs.get("wiki_results") or [],
        "wiki_base": scenario.urls.get("wiki", ""),
        "selected": obs.get("selected") or {},
        "elements": (obs.get("elements") or [])[:30],
        "total_line": obs.get("total_line") or "",
    }
    payload = {
        "scenario": scenario.id,
        "goal": scenario.goal,
        "tier": tier,
        "memory": slim,
        "last_error": last_error,
        "urls": scenario.urls,
        "upload_path": scenario.upload_path,
        "observation": observation,
    }
    return "REALWEB_DECIDE\n" + json.dumps(payload, ensure_ascii=False)


REALWEB_SYSTEM = (
    "You are an autonomous web browser agent. You receive a scenario goal, memory, and observation. "
    "Respond ONLY with a single valid JSON object for the next action to take: "
    "{\"type\": \"goto\", \"url\": \"...\"} or "
    "{\"type\": \"type\", \"selector\": \"...\", \"text\": \"...\", \"flag\": \"optional_flag\"} or "
    "{\"type\": \"click\", \"selector\": \"...\", \"flag\": \"optional_flag\", \"push\": \"optional_key\"} or "
    "{\"type\": \"select\", \"selector\": \"...\", \"value\": \"...\", \"flag\": \"optional_flag\"} or "
    "{\"type\": \"wait_for\", \"selector\": \"...\"} or "
    "{\"type\": \"upload_file\", \"selector\": \"...\", \"file_path\": \"...\", \"flag\": \"optional_flag\"} or "
    "{\"type\": \"remember\", \"key\": \"...\", \"text\": \"...\"} or "
    "{\"type\": \"flag\", \"key\": \"...\"} or "
    "{\"type\": \"choose_book\"} or "
    "{\"type\": \"finish\"}. "
    "Output strictly JSON without markdown formatting or commentary."
)


def _parse(text: str) -> dict:
    start = text.find("{")
    end = text.rfind("}")
    if start < 0 or end < start:
        raise ValueError("decision was not JSON")
    return json.loads(text[start:end + 1])


def _absorb(obs: dict, memory: dict) -> None:
    for book in obs.get("books") or []:
        if book.get("href"):
            memory.setdefault("books", {})[book["href"]] = book
    if obs.get("books") and not obs.get("next_url"):
        memory["catalog_done"] = True
    if obs.get("hn"):
        memory["hn"] = obs["hn"][:3]
    chosen = memory.get("chosen") or {}
    href = chosen.get("href") or ""
    if href and href in (obs.get("url") or ""):
        memory["visited_book"] = True


def _choose(memory: dict) -> str:
    books = list((memory.get("books") or {}).values())
    four = [book for book in books if book.get("rating") == "Four"]
    if not four:
        return "no four-star book in the pages scanned"
    chosen = min(four, key=lambda book: float(book["price"]))
    memory["chosen"] = chosen
    memory["min_four_price"] = chosen["price"]
    memory["catalog_done"] = True
    return ""


def _done(scenario, memory: dict, obs: dict) -> bool:
    from grasshopper.realweb.scenarios import is_done

    return is_done(scenario.id, memory, obs)


async def _apply(browser, action: dict, memory: dict, stem: str):
    kind = action.get("type")
    if kind == "remember":
        memory[action["key"]] = action["value"] if "value" in action else action.get("text", "")
        return None
    if kind == "flag":
        memory[action["key"]] = True
        return None
    if kind == "choose_book":
        error = _choose(memory)
        if error:
            raise RuntimeError(error)
        return None
    if kind == "finish":
        return None
    act = Action(
        type=kind,
        url=action.get("url"),
        selector=action.get("selector"),
        text=action.get("text"),
        value=action.get("value"),
        file_path=action.get("file_path"),
        key=action.get("key"),
    )
    result = await browser.run(act, stem=stem)
    if not result.ok:
        raise RuntimeError(result.detail or "action failed")
    if action.get("flag"):
        memory[action["flag"]] = True
    if action.get("push"):
        bucket = memory.setdefault(action["push"], [])
        selector = action.get("selector") or ""
        if selector not in bucket:
            bucket.append(selector)
    return result


async def _vision(result, run_dir: Path, stem: str) -> None:
    if result is None or not result.screenshot_before:
        return
    from grasshopper.browser.vision import change_percent, detect_regions

    annotated = run_dir / f"{stem}_regions.png"
    detect_regions(result.screenshot_before, annotated, min_area=200)
    if result.screenshot_after:
        change_percent(result.screenshot_before, result.screenshot_after)


async def run_web(scenario, settings, router, run_dir: Path, *, replay: bool = True) -> WebReport:
    run_dir = Path(run_dir)
    run_dir.mkdir(parents=True, exist_ok=True)
    store = LearningStore(Path(settings.data_dir) / "learning.json")
    started = time.perf_counter()
    calls_before = len(router.calls)
    estimate_before = router.budget.run_estimated.get(run_dir.name, 0.0)
    actual_before = router.budget.run_actual.get(run_dir.name, 0.0)
    memory: dict = {}
    error = ""
    vision_calls = 0
    actions: list[dict] = []
    steps = 0
    ok = False

    async with BrowserController(settings, run_dir) as browser:
        try:
            await _apply(browser, {"type": "goto", "url": scenario.start_url}, memory, "start")
            actions.append({"type": "goto", "url": scenario.start_url})
            steps += 1
        except Exception as exc:
            error = str(exc)
        saved = store.row(scenario.id) if replay else None
        had_trace = bool(saved and saved.get("actions"))
        replayed = False
        if had_trace and not error:
            replayed = True
            obs = observe(browser.driver.html if browser.driver else "", browser.driver.url if browser.driver else "")
            _absorb(obs, memory)
            for index, action in enumerate(saved["actions"]):
                if time.perf_counter() - started > scenario.max_seconds:
                    error = "time budget"
                    replayed = False
                    break
                try:
                    await _apply(browser, action, memory, f"replay_{index}")
                    steps += 1
                    obs = observe(browser.driver.html if browser.driver else "", browser.driver.url if browser.driver else "")
                    _absorb(obs, memory)
                except Exception as exc:
                    error = str(exc)
                    replayed = False
                    break
            if replayed and _done(scenario, memory, obs):
                ok = True
                store.save_replay(scenario.id, 0)
        if not ok and not (error or "").startswith("time") and "robots.txt" not in (error or ""):
            last_error = error
            error = ""
            last_signature = ""
            repeats = 0
            for index in range(scenario.max_steps):
                if time.perf_counter() - started > scenario.max_seconds:
                    error = "time budget"
                    break
                html = browser.driver.html if browser.driver else ""
                url = browser.driver.url if browser.driver else ""
                obs = observe(html, url)
                if scenario.urls.get("wiki"):
                    obs["wiki_base"] = scenario.urls["wiki"]
                _absorb(obs, memory)
                if _done(scenario, memory, obs):
                    ok = True
                    break
                tier = "strong" if last_error else "fast"
                try:
                    response = await router.complete(
                        tier,
                        _prompt(scenario, obs, memory, last_error, tier),
                        system=REALWEB_SYSTEM,
                        run_id=run_dir.name,
                    )
                except BudgetExceeded as exc:
                    error = str(exc)
                    break
                try:
                    action = _parse(response.text)
                except ValueError as exc:
                    last_error = str(exc)
                    continue
                signature = json.dumps(action, sort_keys=True)
                if signature == last_signature:
                    repeats += 1
                else:
                    repeats = 0
                    last_signature = signature
                if repeats >= 2:
                    error = "stuck"
                    break
                try:
                    result = await _apply(browser, action, memory, f"step_{index}")
                    if action.get("repair"):
                        vision_calls += 1
                        try:
                            await _vision(result, run_dir, f"step_{index}")
                        except Exception:
                            log.warning("vision repair pass failed", exc_info=True)
                    actions.append({key: value for key, value in action.items() if key != "repair"})
                    steps += 1
                    last_error = ""
                except Exception as exc:
                    last_error = str(exc)
                    error = last_error
                    if "robots.txt" in last_error:
                        break
            else:
                if not ok:
                    error = error or "step budget"
            obs = observe(browser.driver.html if browser.driver else "", browser.driver.url if browser.driver else "")
            _absorb(obs, memory)
            if _done(scenario, memory, obs):
                ok = True
                error = ""
        if ok and not had_trace:
            calls = len(router.calls) - calls_before
            store.save_first(scenario.id, actions[1:], calls)
        domains = sorted(browser.visited_hosts)
    calls = len(router.calls) - calls_before
    tokens = sum(call.tokens for call in router.calls[calls_before:])
    estimated = router.budget.run_estimated.get(run_dir.name, 0.0) - estimate_before
    actual = router.budget.run_actual.get(run_dir.name, 0.0) - actual_before
    seconds = time.perf_counter() - started
    summary = _summary(scenario.id, memory, ok, error)
    files = sorted(path.name for path in run_dir.iterdir() if path.is_file())
    write_blast(
        run_dir / "blast_radius.json",
        files=files,
        domains=domains,
        seconds=seconds,
        cost_usd=actual,
        runner=runner_label(),
    )
    if ok and scenario.id == "R3" and getattr(router, "notifier", None) is not None:
        try:
            await router.notifier.notify(f"Hacker News:\n{summary}", kind="info")
        except Exception:
            pass
    return WebReport(
        scenario_id=scenario.id,
        ok=ok,
        steps=steps,
        llm_calls=calls,
        tokens=tokens,
        usd_estimated=estimated,
        usd_actual=actual,
        seconds=seconds,
        summary=summary,
        error="" if ok else error,
        domains=domains,
        files=files + ["blast_radius.json"],
        vision_calls=vision_calls,
    )


def _summary(scenario_id: str, memory: dict, ok: bool, error: str) -> str:
    if scenario_id == "R1" and memory.get("chosen"):
        chosen = memory["chosen"]
        text = f"{chosen.get('title')} £{chosen.get('price')} — {(memory.get('author_summary') or '')[:180]}"
        return text if ok else f"{text} ({error})"
    if scenario_id == "R2":
        return memory.get("total") or error or "checkout total missing"
    if scenario_id == "R3":
        return " | ".join(memory.get("summaries") or []) or error
    if scenario_id == "R4":
        titles = [item.get("title", "") for item in (memory.get("papers_saved") or [])]
        return " | ".join(titles) or error
    if scenario_id == "R5":
        return "dynamic+dropdown+upload" if ok else (error or "resilience pack incomplete")
    if scenario_id == "REC":
        return "recovered" if ok else (error or "not recovered")
    return "ok" if ok else error
