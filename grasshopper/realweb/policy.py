"""Allowlist, denylist, robots.txt, and a gap between requests.

REAL_SITES_ALLOWLIST in code is mandatory. The environment variable with the
same name can only narrow that set. Localhost is left alone so the sandbox
keeps working. Tests pass govern_local=True to exercise robots and delay.
"""

from __future__ import annotations

import asyncio
import time
from dataclasses import dataclass
from urllib.parse import urlparse

import httpx

# Hosts the agent may open. Subdomains of an entry are included.
CODE_ALLOWLIST = (
    "books.toscrape.com",
    "quotes.toscrape.com",
    "saucedemo.com",
    "the-internet.herokuapp.com",
    "webscraper.io",
    "wikipedia.org",
    "arxiv.org",
    "export.arxiv.org",
    "news.ycombinator.com",
    "github.com",
)

_SOCIAL = (
    "twitter.com",
    "x.com",
    "facebook.com",
    "instagram.com",
    "tiktok.com",
    "linkedin.com",
    "reddit.com",
    "snapchat.com",
    "pinterest.com",
    "threads.net",
)
_PAYMENT_HOSTS = ("paypal.com", "stripe.com", "pay.google.com")
_PAYMENT_PATHS = ("/checkout", "/payment", "/billing", "/pay/")

_robots: dict[str, tuple[list[str], float]] = {}
_last_hit: dict[str, float] = {}


class PolicyError(RuntimeError):
    pass


@dataclass
class Verdict:
    allowed: bool
    reason: str = ""


def clear_policy_cache() -> None:
    _robots.clear()
    _last_hit.clear()


def hostname(url: str) -> str:
    try:
        return (urlparse(url).hostname or "").lower()
    except ValueError:
        return ""


def is_local(url: str) -> bool:
    host = hostname(url)
    return host in {"localhost", "127.0.0.1", "::1"} or host.endswith(".localhost")


def _host_is(host: str, name: str) -> bool:
    return host == name or host.endswith("." + name)


def _on_code_list(host: str) -> bool:
    return any(_host_is(host, entry) for entry in CODE_ALLOWLIST)


def _amazon(host: str) -> bool:
    return host == "amazon" or host.startswith("amazon.") or ".amazon." in f".{host}."


def _env_entries(settings) -> list[str]:
    raw = getattr(settings, "real_sites_allowlist", "") or ""
    return [part.strip().lower() for part in raw.split(",") if part.strip()]


def _env_allows(host: str, settings) -> bool:
    entries = _env_entries(settings)
    if not entries:
        return True
    return any(_host_is(host, entry) for entry in entries)


def classify(url: str, settings) -> Verdict:
    """Decide without fetching. Local URLs are not special here."""
    parsed = urlparse(url)
    if parsed.scheme not in {"http", "https"}:
        return Verdict(False, "yalnızca http(s)")
    host = hostname(url)
    path = (parsed.path or "/").lower()
    if not host:
        return Verdict(False, "alan adı yok")
    if _amazon(host) or _host_is(host, "etsy.com"):
        return Verdict(False, "denylist")
    if any(_host_is(host, name) for name in _SOCIAL):
        return Verdict(False, "sosyal medya")
    if any(_host_is(host, name) for name in _PAYMENT_HOSTS):
        return Verdict(False, "ödeme sayfası")
    if host == "accounts.google.com" or host.endswith(".accounts.google.com"):
        return Verdict(False, "google giriş")
    if _host_is(host, "google.com") and any(bit in path for bit in ("/signin", "/servicelogin", "/login")):
        return Verdict(False, "google giriş")
    if _host_is(host, "github.com") and path.startswith(("/login", "/session", "/sessions")):
        return Verdict(False, "github giriş")
    if not _on_code_list(host) and any(bit in path for bit in _PAYMENT_PATHS):
        return Verdict(False, "ödeme sayfası")
    if not _on_code_list(host):
        return Verdict(False, "REAL_SITES_ALLOWLIST dışında")
    if not _env_allows(host, settings):
        return Verdict(False, "REAL_SITES_ALLOWLIST daraltması")
    return Verdict(True, "")


def robots_disallow(text: str) -> tuple[list[str], float]:
    """Disallow prefixes and crawl-delay for User-agent: *."""
    agent = ""
    rules: list[str] = []
    delay = 0.0
    for raw in text.splitlines():
        line = raw.split("#", 1)[0].strip()
        if not line or ":" not in line:
            continue
        key, value = line.split(":", 1)
        key = key.strip().lower()
        value = value.strip()
        if key == "user-agent":
            agent = value.lower()
        elif agent in {"*", "grasshopper"} and key == "disallow":
            rules.append(value)
        elif agent in {"*", "grasshopper"} and key == "crawl-delay":
            try:
                delay = max(delay, float(value))
            except ValueError:
                continue
    return rules, delay


def path_blocked(path: str, rules: list[str], host: str = "") -> bool:
    if host == "export.arxiv.org" and path.startswith("/api/"):
        return False
    for rule in rules:
        if rule and path.startswith(rule):
            return True
    return False


async def _wait(host: str, delay: float) -> None:
    if delay <= 0:
        _last_hit[host] = time.monotonic()
        return
    now = time.monotonic()
    gap = delay - (now - _last_hit.get(host, 0.0))
    if gap > 0:
        await asyncio.sleep(gap)
    _last_hit[host] = time.monotonic()


async def enforce(url: str, settings, client: httpx.AsyncClient | None = None, *, govern_local: bool = False) -> None:
    """Raise PolicyError, honor robots.txt, then wait. Safe for localhost by default."""
    if is_local(url) and not govern_local:
        return
    if not (is_local(url) and govern_local):
        verdict = classify(url, settings)
        if not verdict.allowed:
            raise PolicyError(verdict.reason)
    host = hostname(url)
    path = urlparse(url).path or "/"
    owns = client is None
    if owns:
        client = httpx.AsyncClient(timeout=15, follow_redirects=True)
    try:
        if host not in _robots:
            origin = f"{urlparse(url).scheme}://{host}"
            if urlparse(url).port:
                origin += f":{urlparse(url).port}"
            await _wait(host, float(settings.real_site_delay_sec))
            try:
                response = await client.get(origin + "/robots.txt")
                body = response.text if response.status_code < 400 else ""
            except httpx.HTTPError as exc:
                raise PolicyError(f"robots.txt okunamadı: {exc.__class__.__name__}") from exc
            _robots[host] = robots_disallow(body)
        rules, crawl = _robots[host]
        if path_blocked(path, rules, host=host):
            raise PolicyError("robots.txt disallow")
        delay = max(float(settings.real_site_delay_sec), crawl)
        if host == "export.arxiv.org" or host.endswith(".arxiv.org"):
            delay = max(delay, 3.0)
        await _wait(host, delay)
    finally:
        if owns and client is not None:
            await client.aclose()
