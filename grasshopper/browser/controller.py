"""Action schema runner. Playwright when a browser is available, otherwise the sandbox HTTP hand."""

from __future__ import annotations

import asyncio
import logging
import re
from pathlib import Path
from urllib.parse import urljoin, urlparse

import warnings

import httpx
from bs4 import BeautifulSoup, XMLParsedAsHTMLWarning
from PIL import Image, ImageDraw

warnings.filterwarnings("ignore", category=XMLParsedAsHTMLWarning)

from grasshopper.schemas import Action, ActionResult

log = logging.getLogger("grasshopper.browser")

_TESTID = re.compile(r"""\[data-testid=(?:\"([^\"]+)\"|'([^']+)'|([^\]]+))\]""")
_ROLE = re.compile(r"""role=([a-z]+)(?:\[name=["'](.+?)["']\])?""", re.I)


class CaptchaError(RuntimeError):
    """The page asked for a CAPTCHA. The agent must not try to solve it."""


class BrowserController:
    _slots: asyncio.Semaphore | None = None

    def __init__(self, settings, run_dir: Path):
        self.settings = settings
        self.run_dir = Path(run_dir)
        self.run_dir.mkdir(parents=True, exist_ok=True)
        self.driver: HttpDriver | PlaywrightDriver | None = None
        self._slot_held = False
        self.live_goal = ""
        self.visited_hosts: set[str] = set()
        self._shot_lock = asyncio.Lock()
        self._live_stop: asyncio.Event | None = None
        self._live_task: asyncio.Task | None = None

    async def __aenter__(self) -> "BrowserController":
        if BrowserController._slots is None:
            BrowserController._slots = asyncio.Semaphore(max(1, self.settings.max_concurrent_browsers))
        await BrowserController._slots.acquire()
        self._slot_held = True
        self.driver = await _open_driver(self.settings, self.run_dir)
        if isinstance(self.driver, PlaywrightDriver):
            self._live_stop = asyncio.Event()
            from grasshopper.publish.live_feed import capture_live_frames

            self._live_task = asyncio.create_task(
                capture_live_frames(
                    self.driver,
                    self.run_dir / "live_frame.png",
                    self.settings.runs_dir,
                    self.run_dir.name,
                    lambda: self.live_goal,
                    self._live_stop,
                )
            )
        return self

    async def __aexit__(self, *_) -> None:
        if self._live_stop is not None:
            self._live_stop.set()
        if self._live_task is not None:
            try:
                await self._live_task
            except Exception:
                pass
            self._live_task = None
        if isinstance(self.driver, PlaywrightDriver):
            from grasshopper.publish.live_feed import publish_frame

            frame = self.run_dir / "live_frame.png"
            publish_frame(
                self.settings.runs_dir,
                run_id=self.run_dir.name,
                source=frame,
                url=self.driver.url,
                goal=self.live_goal,
                active=False,
            )
        if self.driver:
            await self.driver.aclose()
        if self._slot_held and BrowserController._slots is not None:
            BrowserController._slots.release()
            self._slot_held = False

    @property
    def clipboard(self) -> str:
        return self.driver.clipboard if self.driver else ""

    async def run(self, action: Action, *, stem: str) -> ActionResult:
        assert self.driver is not None
        before = self.run_dir / f"{stem}_before.png"
        after = self.run_dir / f"{stem}_after.png"
        await self._shot(before)
        try:
            await self.driver.perform(action)
            ok, detail = True, self.driver.url
        except CaptchaError as exc:
            ok, detail = False, str(exc)
        except Exception as exc:
            ok, detail = False, str(exc)
        await self._shot(after)
        host = urlparse(self.driver.url).hostname
        if host:
            self.visited_hosts.add(host.lower())
        html = self.driver.html
        if _looks_like_captcha(html):
            ok, detail = False, "CAPTCHA detected; refusing to solve it"
        return ActionResult(
            ok=ok,
            detail=detail,
            url=self.driver.url,
            text=_visible_text(html),
            html=html,
            screenshot_before=str(before),
            screenshot_after=str(after),
            data={"clipboard": self.driver.clipboard},
        )

    async def _shot(self, path: Path) -> None:
        async with self._shot_lock:
            await self.driver.screenshot(path)


def _looks_like_captcha(html: str) -> bool:
    lower = html.lower()
    return "g-recaptcha" in lower or "recaptcha" in lower or "data-testid=\"captcha\"" in lower or ">captcha<" in lower


async def _open_driver(settings, run_dir: Path):
    choice = settings.browser_driver.lower()
    if choice in {"playwright", "auto"}:
        try:
            driver = PlaywrightDriver(settings.profiles_dir / run_dir.name, run_dir / "video")
            await driver.start()
            log.info("Browser driver: playwright")
            return driver
        except Exception as exc:
            if choice == "playwright":
                raise
            log.warning("Playwright unavailable (%s). Using the HTTP sandbox driver.", exc)
    driver = HttpDriver()
    await driver.start()
    log.info("Browser driver: http")
    return driver


def _visible_text(html: str) -> str:
    if not html:
        return ""
    soup = BeautifulSoup(html, "html.parser")
    return soup.get_text("\n", strip=True)


def find_element(html: str, selector: str):
    soup = BeautifulSoup(html, "html.parser")
    return _find_in(soup, selector), soup


def _find_in(soup: BeautifulSoup, selector: str):
    selector = (selector or "").strip()
    if not selector:
        return None
    match = _TESTID.fullmatch(selector)
    if match:
        testid = next(group for group in match.groups() if group)
        return soup.select_one(f'[data-testid="{testid}"]')
    match = _ROLE.fullmatch(selector)
    if match:
        role, name = match.group(1).lower(), match.group(2)
        return _by_role(soup, role, name)
    if selector.startswith("text="):
        wanted = selector[5:].strip().strip('"').strip("'")
        matches = []
        for tag in soup.find_all(True):
            if tag.name in {"html", "body", "head", "title", "script", "style"}:
                continue
            if tag.get_text(" ", strip=True) == wanted or (tag.string and tag.string.strip() == wanted):
                matches.append(tag)
        if not matches:
            return None
        clickable = [tag for tag in matches if tag.name in {"a", "button", "input", "label"} or tag.get("href")]
        return (clickable or matches)[-1]
    css = selector[4:] if selector.startswith("css=") else selector
    try:
        return soup.select_one(css)
    except Exception:
        return None


def _by_role(soup: BeautifulSoup, role: str, name: str | None):
    if role == "button":
        nodes = soup.find_all(["button", "a"]) + soup.find_all("input", attrs={"type": "submit"})
    elif role == "link":
        nodes = soup.find_all("a")
    elif role == "textbox":
        nodes = soup.find_all(["input", "textarea"])
    else:
        nodes = soup.find_all(attrs={"role": role})
    if not name:
        return nodes[0] if nodes else None
    for node in nodes:
        label = node.get("aria-label") or node.get("value") or node.get_text(" ", strip=True)
        if label and name.lower() in label.lower():
            return node
    return None


def selector_exists(html: str, selector: str) -> bool:
    node, _ = find_element(html, selector)
    return node is not None


class HttpDriver:
    def __init__(self):
        self.client: httpx.AsyncClient | None = None
        self.url = "about:blank"
        self.html = "<html><body></body></html>"
        self.fields: dict[str, str] = {}
        self.clipboard = ""

    async def start(self) -> None:
        self.client = httpx.AsyncClient(
            follow_redirects=True,
            timeout=20,
            headers={"User-Agent": "Grasshopper/0.1 (https://github.com/grasshopper; contact@grasshopper.dev; respects robots.txt)"},
        )

    async def aclose(self) -> None:
        if self.client:
            await self.client.aclose()

    async def screenshot(self, path: Path) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        _render_card(self.url, _visible_text(self.html), path)

    async def perform(self, action: Action) -> None:
        kind = action.type
        if kind == "goto":
            await self._get(action.url or "")
        elif kind == "click":
            await self._click(action.selector or "")
        elif kind == "type":
            self._type(action.selector or "", action.text or "")
        elif kind == "paste_to":
            self._type(action.selector or "", self.clipboard)
        elif kind == "press":
            if (action.key or "").lower() == "enter":
                await self._click(action.selector or "input[type=submit], button")
        elif kind == "select":
            self._type(action.selector or "", action.value or action.text or "")
        elif kind == "read_text":
            node, _ = find_element(self.html, action.selector or "body")
            if node is None and action.selector:
                raise RuntimeError(f"selector not found: {action.selector}")
        elif kind == "extract_table":
            if not BeautifulSoup(self.html, "html.parser").find("table"):
                raise RuntimeError("no table on page")
        elif kind == "copy":
            node, _ = find_element(self.html, action.selector or "body")
            if node is None:
                raise RuntimeError(f"selector not found: {action.selector}")
            self.clipboard = node.get_text(" ", strip=True)
        elif kind == "wait_for":
            if not selector_exists(self.html, action.selector or "body"):
                await self._get(self.url)
            if not selector_exists(self.html, action.selector or "body"):
                raise RuntimeError(f"wait_for failed: {action.selector}")
        elif kind == "screenshot":
            return
        elif kind == "scroll":
            return
        elif kind == "upload_file":
            node, _ = find_element(self.html, action.selector or "input[type=file]")
            name = (node.get("name") if node is not None else None) or "upload"
            self.fields[name] = Path(action.file_path or "").name
            self.fields["upload"] = action.file_path or ""
        else:
            raise RuntimeError(f"HTTP driver cannot run action {kind}")

    def _type(self, selector: str, text: str) -> None:
        node, _ = find_element(self.html, selector)
        if node is None:
            raise RuntimeError(f"selector not found: {selector}")
        name = node.get("name") or node.get("data-testid") or selector
        self.fields[name] = text

    async def _click(self, selector: str) -> None:
        node, soup = find_element(self.html, selector)
        if node is None:
            raise RuntimeError(f"selector not found: {selector}")
        if node.name == "a" and node.get("href"):
            await self._get(urljoin(self.url, node["href"]))
            return
        form = node if node.name == "form" else node.find_parent("form")
        if form is None:
            raise RuntimeError(f"element is not clickable: {selector}")
        extra = {}
        if node.get("name"):
            extra[node.get("name")] = node.get("value", "on")
        await self._submit(form, extra)

    async def _submit(self, form, extra: dict | None = None) -> None:
        action = form.get("action") or self.url
        method = (form.get("method") or "get").lower()
        data: dict[str, str] = {}
        for field in form.find_all(["input", "textarea", "select"]):
            name = field.get("name")
            if not name:
                continue
            if name in self.fields:
                data[name] = self.fields[name]
            elif field.name == "select":
                option = field.find("option", selected=True) or field.find("option")
                data[name] = option.get("value", "") if option else ""
            else:
                data[name] = field.get("value", "") or ""
        if extra:
            data.update(extra)
        url = urljoin(self.url, action)
        assert self.client is not None
        if method == "post":
            response = await self.client.post(url, data=data)
        else:
            response = await self.client.get(url, params=data)
        self._remember(response)

    async def _get(self, url: str) -> None:
        assert self.client is not None
        absolute = urljoin(self.url if self.url.startswith("http") else "http://127.0.0.1/", url)
        from grasshopper.config import get_settings
        from grasshopper.realweb.policy import PolicyError, classify, enforce, is_local

        await enforce(absolute, get_settings(), client=self.client)
        response = await self.client.get(absolute)
        self._remember(response)
        if self.url.startswith("http") and not is_local(self.url):
            verdict = classify(self.url, get_settings())
            if not verdict.allowed:
                raise PolicyError(verdict.reason)

    def _remember(self, response: httpx.Response) -> None:
        self.url = str(response.url)
        self.html = response.text
        if response.status_code >= 400:
            raise RuntimeError(f"HTTP {response.status_code} for {self.url}")


def _render_card(url: str, text: str, path: Path) -> None:
    image = Image.new("RGB", (960, 540), (14, 18, 22))
    draw = ImageDraw.Draw(image)
    draw.rectangle((0, 0, 960, 42), fill=(28, 40, 22))
    draw.text((14, 12), (url or "about:blank")[:110], fill=(198, 241, 53))
    y = 56
    for line in (text or "(empty page)").splitlines():
        if y > 500:
            break
        draw.text((16, y), line[:110], fill=(232, 236, 230))
        y += 18
    draw.rectangle((18, 488, 210, 524), outline=(198, 241, 53), width=3)
    draw.text((28, 496), "action", fill=(198, 241, 53))
    image.save(path)


class PlaywrightDriver:
    """Real Chromium. Selector order matches the HTTP driver: testid, role, text, CSS."""

    def __init__(self, profiles_dir: Path, video_dir: Path):
        self.profiles_dir = profiles_dir
        self.video_dir = Path(video_dir)
        self.url = "about:blank"
        self.html = ""
        self.clipboard = ""
        self._pw = None
        self._browser = None
        self._context = None
        self.page = None

    async def start(self) -> None:
        from playwright.async_api import async_playwright

        self._pw = await async_playwright().start()
        user_dir = self.profiles_dir
        user_dir.mkdir(parents=True, exist_ok=True)
        self.video_dir.mkdir(parents=True, exist_ok=True)
        self._context = await self._pw.chromium.launch_persistent_context(
            user_data_dir=str(user_dir),
            headless=True,
            viewport={"width": 1280, "height": 720},
            user_agent="Grasshopper/0.1 (demo; respects robots.txt)",
            record_video_dir=str(self.video_dir),
            record_video_size={"width": 1280, "height": 720},
        )
        self.page = self._context.pages[0] if self._context.pages else await self._context.new_page()

    async def aclose(self) -> None:
        if self._context:
            await self._context.close()
        if self._pw:
            await self._pw.stop()

    async def screenshot(self, path: Path) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        if self.page:
            await self.page.screenshot(path=str(path))
        else:
            _render_card(self.url, "", path)

    async def _sync(self) -> None:
        self.url = self.page.url
        self.html = await self.page.content()

    async def perform(self, action: Action) -> None:
        page = self.page
        kind = action.type
        if kind == "goto":
            from grasshopper.config import get_settings
            from grasshopper.realweb.policy import enforce

            await enforce(action.url or "", get_settings())
            await page.goto(action.url or "", wait_until="domcontentloaded", timeout=action.timeout_ms)
        elif kind == "click":
            old_url = page.url
            await self._locator(action.selector or "").click(timeout=action.timeout_ms)
            try:
                await page.wait_for_function(
                    "(oldUrl) => window.location.href !== oldUrl",
                    arg=old_url,
                    timeout=2500,
                )
                await asyncio.sleep(0.15)
            except Exception:
                pass
        elif kind == "type":
            loc = self._locator(action.selector or "")
            await loc.fill(action.text or "", timeout=action.timeout_ms)
        elif kind == "paste_to":
            await self._locator(action.selector or "").fill(self.clipboard, timeout=action.timeout_ms)
        elif kind == "press":
            await page.keyboard.press(action.key or "Enter")
        elif kind == "select":
            await self._locator(action.selector or "").select_option(action.value or action.text or "")
        elif kind == "read_text":
            await self._locator(action.selector or "body").inner_text(timeout=action.timeout_ms)
        elif kind == "copy":
            self.clipboard = await self._locator(action.selector or "body").inner_text()
        elif kind == "wait_for":
            await self._locator(action.selector or "body").wait_for(timeout=action.timeout_ms)
        elif kind == "screenshot":
            pass
        elif kind == "scroll":
            await page.mouse.wheel(0, 800)
        elif kind == "extract_table":
            await self._locator(action.selector or "table").wait_for(timeout=action.timeout_ms)
        elif kind == "upload_file":
            await self._locator(action.selector or "input[type=file]").set_input_files(action.file_path or "")
        else:
            raise RuntimeError(f"Playwright driver cannot run action {kind}")
        await self._sync()
        from grasshopper.config import get_settings
        from grasshopper.realweb.policy import PolicyError, classify, is_local

        if self.url.startswith("http") and not is_local(self.url):
            verdict = classify(self.url, get_settings())
            if not verdict.allowed:
                raise PolicyError(verdict.reason)

    def _locator(self, selector: str):
        match = _TESTID.fullmatch(selector.strip())
        if match:
            testid = next(group for group in match.groups() if group)
            return self.page.locator(f'[data-testid="{testid}"]')
        match = _ROLE.fullmatch(selector.strip())
        if match:
            role, name = match.group(1), match.group(2)
            if name:
                return self.page.get_by_role(role, name=name)
            return self.page.get_by_role(role)
        if selector.startswith("text="):
            return self.page.get_by_text(selector[5:].strip().strip('"'))
        css = selector[4:] if selector.startswith("css=") else selector
        return self.page.locator(css)
