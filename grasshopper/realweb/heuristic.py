"""Offline decision policy. The mock model returns this JSON; a live model is asked for the same shape."""

from __future__ import annotations

import json
from urllib.parse import quote


def decide_json(prompt: str) -> str:
    payload = json.loads(prompt.split("\n", 1)[1])
    return json.dumps(decide(payload), ensure_ascii=False)


def decide(payload: dict) -> dict:
    scenario = payload.get("scenario") or ""
    memory = payload.get("memory") or {}
    obs = payload.get("observation") or {}
    error = payload.get("last_error") or ""
    if scenario == "R1":
        return _r1(memory, obs)
    if scenario == "R2":
        return _r2(memory, obs)
    if scenario == "R3":
        return _r3(memory)
    if scenario == "R4":
        return _r4(memory, obs)
    if scenario == "R5":
        return _r5(memory, obs, payload, error)
    if scenario == "REC":
        return _rec(memory, obs, error)
    return {"type": "finish"}


def _selectors(obs: dict) -> list[str]:
    return [item.get("selector") or "" for item in obs.get("elements") or []]


def _has(obs: dict, selector: str) -> bool:
    return selector in _selectors(obs)


def _r1(memory: dict, obs: dict) -> dict:
    if not memory.get("catalog_done") and obs.get("next_url"):
        return {"type": "goto", "url": obs["next_url"]}
    if not memory.get("chosen"):
        return {"type": "choose_book"}
    chosen = memory.get("chosen") or {}
    href = chosen.get("href") or ""
    if href and href not in (obs.get("url") or "") and not memory.get("visited_book"):
        return {"type": "goto", "url": href}
    if not memory.get("author_summary"):
        if obs.get("wiki_paragraph"):
            return {"type": "remember", "key": "author_summary", "text": obs["wiki_paragraph"][:500]}
        results = obs.get("wiki_results") or []
        if results:
            return {"type": "goto", "url": results[0]["href"]}
        base = obs.get("wiki_base") or "https://en.wikipedia.org/wiki/"
        title = chosen.get("title") or ""
        if "?q=" in base or "search=" in base:
            target = base + quote(title)
        else:
            target = base + quote(title.replace(" ", "_"), safe="_")
        return {"type": "goto", "url": target}
    return {"type": "finish"}


def _r2(memory: dict, obs: dict) -> dict:
    if _has(obs, "#user-name") and not memory.get("user"):
        return {"type": "type", "selector": "#user-name", "text": "standard_user", "flag": "user"}
    if _has(obs, "#password") and not memory.get("password"):
        return {"type": "type", "selector": "#password", "text": "secret_sauce", "flag": "password"}
    if _has(obs, "#login-button") and not memory.get("logged_in"):
        return {"type": "click", "selector": "#login-button", "flag": "logged_in"}
    adds = [selector for selector in _selectors(obs) if "add-to-cart" in selector]
    clicked = list(memory.get("clicked") or [])
    pending = [selector for selector in adds if selector not in clicked]
    if pending and len(clicked) < 2:
        return {"type": "click", "selector": pending[0], "push": "clicked"}
    cart = next((selector for selector in _selectors(obs) if "shopping_cart" in selector), "")
    if cart and not memory.get("saw_cart"):
        return {"type": "click", "selector": cart, "flag": "saw_cart"}
    if _has(obs, "#checkout") and not memory.get("checkout"):
        return {"type": "click", "selector": "#checkout", "flag": "checkout"}
    if _has(obs, "#first-name") and not memory.get("first"):
        return {"type": "type", "selector": "#first-name", "text": "Ada", "flag": "first"}
    if _has(obs, "#last-name") and not memory.get("last"):
        return {"type": "type", "selector": "#last-name", "text": "Lovelace", "flag": "last"}
    if _has(obs, "#postal-code") and not memory.get("zip"):
        return {"type": "type", "selector": "#postal-code", "text": "34000", "flag": "zip"}
    if _has(obs, "#continue") and not memory.get("continued"):
        return {"type": "click", "selector": "#continue", "flag": "continued"}
    if obs.get("total_line") and not memory.get("total"):
        return {"type": "remember", "key": "total", "text": obs["total_line"]}
    return {"type": "finish"}


def _r3(memory: dict) -> dict:
    if memory.get("hn") and not memory.get("summaries"):
        lines = []
        for item in memory["hn"][:3]:
            lines.append(f"{item['title']} — başlık özeti; makale gövdesi allowlist dışındaysa alınmadı.")
        return {"type": "remember", "key": "summaries", "value": lines}
    return {"type": "finish"}


def _r4(memory: dict, obs: dict) -> dict:
    papers = obs.get("papers") or []
    if papers and not memory.get("papers_saved"):
        return {"type": "remember", "key": "papers_saved", "value": papers[:3]}
    return {"type": "finish"}


def _r5(memory: dict, obs: dict, payload: dict, error: str) -> dict:
    urls = payload.get("urls") or {}
    text = obs.get("text") or ""
    if not memory.get("dynamic"):
        if "Hello World" in text:
            return {"type": "flag", "key": "dynamic"}
        if memory.get("started"):
            return {"type": "wait_for", "selector": "#finish"}
        for element in obs.get("elements") or []:
            if element.get("selector") == "#start" and element.get("tag") == "a":
                return {"type": "click", "selector": "#start", "flag": "started"}
        if _has(obs, "#start") or any(element.get("text") == "Start" for element in obs.get("elements") or []):
            return {"type": "click", "selector": "#start button", "flag": "started"}
        return {"type": "goto", "url": urls.get("dynamic") or obs.get("url") or ""}
    if not memory.get("dropdown"):
        if not _has(obs, "#dropdown") and "dropdown" not in (obs.get("url") or ""):
            return {"type": "goto", "url": urls.get("dropdown") or ""}
        if not memory.get("dropdown_set"):
            return {"type": "select", "selector": "#dropdown", "value": "2", "flag": "dropdown_set"}
        selected = (obs.get("selected") or {}).get("#dropdown")
        if selected in {"2", "Option 2"} or "Option 2 selected" in text:
            return {"type": "flag", "key": "dropdown"}
        if _has(obs, "#dropdown-go"):
            return {"type": "click", "selector": "#dropdown-go"}
        return {"type": "flag", "key": "dropdown"} if selected else {"type": "finish"}
    if not memory.get("upload"):
        if not _has(obs, "#file-upload") and "upload" not in (obs.get("url") or ""):
            return {"type": "goto", "url": urls.get("upload") or ""}
        if not memory.get("file_set"):
            return {
                "type": "upload_file",
                "selector": "#file-upload",
                "file_path": payload.get("upload_path") or "",
                "flag": "file_set",
            }
        if "File Uploaded" in text:
            return {"type": "flag", "key": "upload"}
        if _has(obs, "#file-submit"):
            return {"type": "click", "selector": "#file-submit"}
        if error:
            return {"type": "click", "selector": "#file-submit"}
    return {"type": "finish"}


def _rec(memory: dict, obs: dict, error: str) -> dict:
    if memory.get("landed") or "landed" in (obs.get("text") or "").lower():
        return {"type": "flag", "key": "landed"}
    if error:
        return {"type": "click", "selector": "text=Continue", "repair": True}
    return {"type": "click", "selector": "#go"}
