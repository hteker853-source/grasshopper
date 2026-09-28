"""Sandbox Web: seven fake sites on one FastAPI app. State lives in SQLite."""

from __future__ import annotations

import hashlib
import os
import random
import sqlite3
from datetime import datetime, timedelta, timezone
from pathlib import Path

from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse, Response
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
DB_PATH = Path(os.environ.get("SANDBOX_DB", ROOT / "data" / "sandbox.db"))
MEDIA_DIR = Path(os.environ.get("SANDBOX_MEDIA_DIR", ROOT / "data" / "media"))

app = FastAPI(title="Grasshopper Sandbox")


def _conn() -> sqlite3.Connection:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    MEDIA_DIR.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(DB_PATH), check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def _init() -> None:
    conn = _conn()
    conn.executescript(
        """
        CREATE TABLE IF NOT EXISTS users (
            site TEXT, email TEXT, password TEXT, name TEXT,
            research INTEGER DEFAULT 0, phone TEXT DEFAULT '', bio TEXT DEFAULT '', company TEXT DEFAULT '',
            PRIMARY KEY (site, email)
        );
        CREATE TABLE IF NOT EXISTS shares (
            id TEXT PRIMARY KEY, email TEXT, body TEXT
        );
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT, site TEXT, email TEXT, role TEXT, body TEXT
        );
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY, title TEXT, created_at TEXT, price TEXT
        );
        CREATE TABLE IF NOT EXISTS receipts (
            id INTEGER PRIMARY KEY AUTOINCREMENT, email TEXT, plan TEXT, amount TEXT, tx_hash TEXT, created_at TEXT
        );
        CREATE TABLE IF NOT EXISTS images (
            id TEXT PRIMARY KEY, session_id TEXT, prompt TEXT, path TEXT, created_at TEXT
        );
        CREATE TABLE IF NOT EXISTS bank_audit (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ts TEXT, event TEXT, amount TEXT, detail TEXT
        );
        CREATE TABLE IF NOT EXISTS bank_account (
            id INTEGER PRIMARY KEY CHECK (id = 1),
            balance TEXT, spent_today TEXT
        );
        """
    )
    conn.execute("INSERT OR IGNORE INTO bank_account (id, balance, spent_today) VALUES (1, '1000', '0')")
    count = conn.execute("SELECT COUNT(*) AS n FROM products").fetchone()["n"]
    if count == 0:
        now = datetime.now(timezone.utc)
        rows = [
            (1, "Linen notebook", now - timedelta(days=200), "24"),
            (2, "Oak desk tray", now - timedelta(days=160), "38"),
            (3, "Brass pen", now - timedelta(days=12), "18"),
            (4, "Wool sleeve", now - timedelta(days=6), "22"),
            (5, "Ink sampler", now - timedelta(days=3), "14"),
            (6, "Cedar box", now - timedelta(days=140), "54"),
        ]
        conn.executemany("INSERT INTO products (id, title, created_at, price) VALUES (?, ?, ?, ?)", [
            (i, title, created.isoformat(), price) for i, title, created, price in rows
        ])
    conn.execute(
        "INSERT OR IGNORE INTO users (site, email, password, name) VALUES (?, ?, ?, ?)",
        ("shop", "demo@grasshopper.local", "demo-password", "Demo Seller"),
    )
    conn.execute(
        "INSERT OR IGNORE INTO users (site, email, password, name) VALUES (?, ?, ?, ?)",
        ("ai-beta", "demo@grasshopper.local", "demo-password", "Demo"),
    )
    conn.commit()
    conn.close()


_init()


@app.middleware("http")
async def delay_and_banner_cookie(request: Request, call_next):
    lo = int(os.environ.get("SANDBOX_DELAY_MIN_MS", "100"))
    hi = int(os.environ.get("SANDBOX_DELAY_MAX_MS", "800"))
    if hi < lo:
        hi = lo
    if hi > 0:
        import asyncio
        await asyncio.sleep(random.uniform(lo, hi) / 1000)
    return await call_next(request)


def _page(request: Request, title: str, body: str) -> HTMLResponse:
    banner = ""
    if request.cookies.get("gh_banner") != "1":
        nxt = request.url.path
        banner = f"""
        <form method="post" action="/banner/dismiss" data-testid="cookie-banner">
          <p>This sandbox stores a single preference cookie.</p>
          <input type="hidden" name="next" value="{nxt}">
          <button data-testid="dismiss-banner" type="submit">Accept</button>
        </form>
        """
    html = f"""<!doctype html>
<html><head><meta charset="utf-8"><title>{title}</title>
<style>
body{{font-family:system-ui;margin:24px;background:#f6f4ee;color:#1c1a16}}
a,button{{font-size:16px}} input,textarea{{font-size:16px;padding:8px;width:min(480px,100%)}}
button{{padding:8px 14px;margin-top:8px}} article{{padding:8px 0;border-bottom:1px solid #ddd}}
</style></head><body>
<header><a href="/">Sandbox</a></header>
<h1>{title}</h1>
{banner}
{body}
</body></html>"""
    return HTMLResponse(html)


def _redirect(url: str, **cookies) -> RedirectResponse:
    response = RedirectResponse(url, status_code=303)
    for key, value in cookies.items():
        response.set_cookie(key, value, httponly=False, samesite="lax")
    return response


@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return _page(request, "Sandbox Web", """
    <ul>
      <li><a href="/ai-alpha">ai-alpha</a></li>
      <li><a href="/ai-beta">ai-beta</a></li>
      <li><a href="/shop">shop</a></li>
      <li><a href="/news">news</a></li>
      <li><a href="/media">media</a></li>
      <li><a href="/competitions">competitions</a></li>
      <li><a href="/broken">broken</a></li>
    </ul>
    """)


@app.post("/banner/dismiss")
def dismiss(next: str = Form("/")):
    safe = next if next.startswith("/") else "/"
    return _redirect(safe, gh_banner="1")


@app.get("/health")
def health():
    return {"ok": True, "service": "sandbox"}


# --- ai-alpha -----------------------------------------------------------------

@app.get("/ai-alpha", response_class=HTMLResponse)
def alpha_home(request: Request):
    return _page(request, "AI Alpha", """
    <p><a data-testid="go-signup" href="/ai-alpha/signup">Sign up</a></p>
    <p><a data-testid="go-login" href="/ai-alpha/login">Log in</a></p>
    """)


@app.get("/ai-alpha/signup", response_class=HTMLResponse)
def alpha_signup_form(request: Request):
    return _page(request, "Create your Alpha account", """
    <form method="post" action="/ai-alpha/signup">
      <p><input data-testid="name" name="name" placeholder="Name"></p>
      <p><input data-testid="email" name="email" placeholder="Email"></p>
      <p><input data-testid="password" name="password" type="password" placeholder="Password"></p>
      <button data-testid="signup-submit" type="submit">Create account</button>
    </form>
    """)


@app.post("/ai-alpha/signup")
def alpha_signup(name: str = Form(""), email: str = Form(""), password: str = Form("")):
    conn = _conn()
    existing = conn.execute("SELECT password FROM users WHERE site='ai-alpha' AND email=?", (email,)).fetchone()
    if existing is None:
        conn.execute(
            "INSERT INTO users (site, email, password, name) VALUES ('ai-alpha', ?, ?, ?)",
            (email, password, name or "Demo"),
        )
        conn.commit()
    conn.close()
    return _redirect("/ai-alpha/home", aa_user=email)


@app.get("/ai-alpha/login", response_class=HTMLResponse)
def alpha_login_form(request: Request):
    return _page(request, "Alpha login", """
    <form method="post" action="/ai-alpha/login">
      <p><input data-testid="email" name="email"></p>
      <p><input data-testid="password" name="password" type="password"></p>
      <button data-testid="login-submit" type="submit">Log in</button>
    </form>
    """)


@app.post("/ai-alpha/login")
def alpha_login(email: str = Form(""), password: str = Form("")):
    conn = _conn()
    row = conn.execute(
        "SELECT email FROM users WHERE site='ai-alpha' AND email=? AND password=?",
        (email, password),
    ).fetchone()
    conn.close()
    if row is None:
        return HTMLResponse("Login failed", status_code=401)
    return _redirect("/ai-alpha/home", aa_user=email)


def _alpha_user(request: Request):
    email = request.cookies.get("aa_user")
    if not email:
        return None
    conn = _conn()
    row = conn.execute("SELECT * FROM users WHERE site='ai-alpha' AND email=?", (email,)).fetchone()
    conn.close()
    return row


@app.get("/ai-alpha/home", response_class=HTMLResponse)
def alpha_dashboard(request: Request):
    user = _alpha_user(request)
    if user is None:
        return _redirect("/ai-alpha/login")
    return _page(request, "Alpha home", f"""
    <p data-testid="dashboard">Signed in as {user['email']}</p>
    <p><a href="/ai-alpha/settings">Settings</a></p>
    <p><a href="/ai-alpha/chat">Chat</a></p>
    <p><a href="/ai-alpha/profile">Profile</a></p>
    """)


@app.get("/ai-alpha/settings", response_class=HTMLResponse)
def alpha_settings(request: Request):
    user = _alpha_user(request)
    if user is None:
        return _redirect("/ai-alpha/login")
    state = "Research mode is ON" if user["research"] else "Research mode is OFF"
    return _page(request, "Alpha settings", f"""
    <p data-testid="research-state">{state}</p>
    <form method="post" action="/ai-alpha/settings">
      <button data-testid="enable-research" type="submit" name="research_mode" value="on">Enable research mode</button>
    </form>
    """)


@app.post("/ai-alpha/settings")
def alpha_settings_post(request: Request, research_mode: str = Form("")):
    user = _alpha_user(request)
    if user is None:
        return _redirect("/ai-alpha/login")
    conn = _conn()
    conn.execute(
        "UPDATE users SET research=? WHERE site='ai-alpha' AND email=?",
        (1 if research_mode == "on" else 0, user["email"]),
    )
    conn.commit()
    conn.close()
    return _redirect("/ai-alpha/settings")


def _alpha_answer(message: str, research: int) -> str:
    lower = message.lower()
    if "solar" in lower and research:
        return (
            "Research complete: solar panels convert sunlight into electricity. "
            "Output depends on orientation, shade, and inverter quality."
        )
    if "solar" in lower:
        return "Enable research mode for a sourced answer about solar panels."
    if "planner" in lower or "product description" in lower:
        return (
            "The Northwind Weekly Planner is a linen-bound desk planner with weekly spreads, "
            "habit dots, and a pocket for loose receipts. It is designed for people who want "
            "one calm place to plan deep work without another app."
        )
    return f"Alpha reply: {message[:180]}"


@app.get("/ai-alpha/chat", response_class=HTMLResponse)
def alpha_chat(request: Request):
    user = _alpha_user(request)
    if user is None:
        return _redirect("/ai-alpha/login")
    conn = _conn()
    last = conn.execute(
        "SELECT body FROM messages WHERE site='ai-alpha' AND email=? AND role='assistant' ORDER BY id DESC LIMIT 1",
        (user["email"],),
    ).fetchone()
    conn.close()
    answer = last["body"] if last else ""
    return _page(request, "Alpha chat", f"""
    <div data-testid="last-answer">{answer}</div>
    <form method="post" action="/ai-alpha/chat">
      <p><textarea data-testid="chat-input" name="message"></textarea></p>
      <button data-testid="chat-send" type="submit">Send</button>
    </form>
    <form method="post" action="/ai-alpha/share">
      <button data-testid="share-submit" type="submit">Share</button>
    </form>
    """)


@app.post("/ai-alpha/chat")
def alpha_chat_post(request: Request, message: str = Form("")):
    user = _alpha_user(request)
    if user is None:
        return _redirect("/ai-alpha/login")
    answer = _alpha_answer(message, user["research"])
    conn = _conn()
    conn.execute(
        "INSERT INTO messages (site, email, role, body) VALUES ('ai-alpha', ?, 'user', ?)",
        (user["email"], message),
    )
    conn.execute(
        "INSERT INTO messages (site, email, role, body) VALUES ('ai-alpha', ?, 'assistant', ?)",
        (user["email"], answer),
    )
    conn.commit()
    conn.close()
    return _redirect("/ai-alpha/chat")


@app.post("/ai-alpha/share")
def alpha_share(request: Request):
    user = _alpha_user(request)
    if user is None:
        return _redirect("/ai-alpha/login")
    conn = _conn()
    last = conn.execute(
        "SELECT body FROM messages WHERE site='ai-alpha' AND email=? AND role='assistant' ORDER BY id DESC LIMIT 1",
        (user["email"],),
    ).fetchone()
    body = last["body"] if last else ""
    share_id = hashlib.sha256(f"{user['email']}:{body}".encode()).hexdigest()[:10]
    conn.execute("INSERT OR REPLACE INTO shares (id, email, body) VALUES (?, ?, ?)", (share_id, user["email"], body))
    conn.commit()
    conn.close()
    return _redirect(f"/ai-alpha/s/{share_id}")


@app.get("/ai-alpha/s/{share_id}", response_class=HTMLResponse)
def alpha_share_page(request: Request, share_id: str):
    conn = _conn()
    row = conn.execute("SELECT body FROM shares WHERE id=?", (share_id,)).fetchone()
    conn.close()
    body = row["body"] if row else ""
    link = f"/ai-alpha/s/{share_id}"
    return _page(request, "Shared research", f"""
    <p data-testid="share-link">Share link: {link}</p>
    <div data-testid="shared-body">{body}</div>
    """)


@app.get("/ai-alpha/profile", response_class=HTMLResponse)
def alpha_profile(request: Request):
    user = _alpha_user(request)
    if user is None:
        return _redirect("/ai-alpha/login")
    missing = []
    blocks = []
    for field in ("phone", "bio", "company"):
        if not (user[field] or "").strip():
            missing.append(field)
            blocks.append(f'<p data-testid="missing-{field}">Missing: {field}</p>')
    suggestion = (
        "Suggest fixes: add phone, bio, and company so shared research shows a complete profile."
        if missing else "Profile is complete."
    )
    return _page(request, "Alpha profile", f"""
    <p data-testid="profile-name">{user['name']} · {user['email']}</p>
    {''.join(blocks)}
    <p data-testid="profile-suggestion">{suggestion}</p>
    """)


# --- ai-beta ------------------------------------------------------------------

@app.get("/ai-beta", response_class=HTMLResponse)
def beta_home(request: Request):
    return _page(request, "AI Beta", '<p><a data-testid="go-login" href="/ai-beta/login">Log in</a></p>')


@app.get("/ai-beta/login", response_class=HTMLResponse)
def beta_login_form(request: Request):
    return _page(request, "Beta login", """
    <form method="post" action="/ai-beta/login">
      <p><input data-testid="email" name="email"></p>
      <p><input data-testid="password" name="password" type="password"></p>
      <button data-testid="login-submit" type="submit">Log in</button>
    </form>
    """)


@app.post("/ai-beta/login")
def beta_login(email: str = Form(""), password: str = Form("")):
    conn = _conn()
    row = conn.execute(
        "SELECT email FROM users WHERE site='ai-beta' AND email=? AND password=?",
        (email, password),
    ).fetchone()
    conn.close()
    if row is None:
        return HTMLResponse("Login failed", status_code=401)
    return _redirect("/ai-beta/chat", ab_user=email)


def _beta_answer(message: str) -> str:
    lower = message.lower()
    if "shorten" in lower:
        core = message
        idx = lower.rfind("shorten")
        core = message[idx + len("shorten"):].strip(" :\n")
        words = core.split()
        return "Shortened: " + " ".join(words[:12])
    return f"Beta reply: {message[:160]}"


@app.get("/ai-beta/chat", response_class=HTMLResponse)
def beta_chat(request: Request):
    if not request.cookies.get("ab_user"):
        return _redirect("/ai-beta/login")
    conn = _conn()
    last = conn.execute(
        "SELECT body FROM messages WHERE site='ai-beta' AND email=? AND role='assistant' ORDER BY id DESC LIMIT 1",
        (request.cookies.get("ab_user"),),
    ).fetchone()
    conn.close()
    answer = last["body"] if last else ""
    return _page(request, "Beta chat", f"""
    <div data-testid="last-answer">{answer}</div>
    <form method="post" action="/ai-beta/chat">
      <p><textarea data-testid="prompt" name="message"></textarea></p>
      <button data-testid="send" type="submit">Ask Beta</button>
    </form>
    """)


@app.post("/ai-beta/chat")
def beta_chat_post(request: Request, message: str = Form("")):
    email = request.cookies.get("ab_user")
    if not email:
        return _redirect("/ai-beta/login")
    answer = _beta_answer(message)
    conn = _conn()
    conn.execute("INSERT INTO messages (site, email, role, body) VALUES ('ai-beta', ?, 'user', ?)", (email, message))
    conn.execute("INSERT INTO messages (site, email, role, body) VALUES ('ai-beta', ?, 'assistant', ?)", (email, answer))
    conn.commit()
    conn.close()
    return _redirect("/ai-beta/chat")


# --- shop ---------------------------------------------------------------------

def _shop_user(request: Request) -> str | None:
    return request.cookies.get("shop_user")


@app.get("/shop", response_class=HTMLResponse)
def shop_home(request: Request):
    return _page(request, "Shop", '<p><a data-testid="go-login" href="/shop/login">Seller login</a></p>')


@app.get("/shop/login", response_class=HTMLResponse)
def shop_login_form(request: Request):
    return _page(request, "Shop login", """
    <form method="post" action="/shop/login">
      <p><input data-testid="email" name="email"></p>
      <p><input data-testid="password" name="password" type="password"></p>
      <button data-testid="login-submit" type="submit">Log in</button>
    </form>
    """)


@app.post("/shop/login")
def shop_login(email: str = Form(""), password: str = Form("")):
    conn = _conn()
    row = conn.execute(
        "SELECT email FROM users WHERE site='shop' AND email=? AND password=?",
        (email, password),
    ).fetchone()
    conn.close()
    if row is None:
        return HTMLResponse("Login failed", status_code=401)
    return _redirect("/shop/dashboard", shop_user=email)


@app.get("/shop/dashboard", response_class=HTMLResponse)
def shop_dashboard(request: Request):
    if not _shop_user(request):
        return _redirect("/shop/login")
    return _page(request, "Seller dashboard", """
    <p data-testid="dashboard">Seller dashboard</p>
    <p><a data-testid="old-filter" href="/shop/listings?older_than_months=4">Listings older than 4 months</a></p>
    <p><a href="/shop/listings">All listings</a></p>
    <p><a data-testid="go-subscribe" href="/shop/subscribe">Pro plan</a></p>
    """)


@app.get("/shop/listings", response_class=HTMLResponse)
def shop_listings(request: Request, older_than_months: int = 0, page: int = 1):
    if not _shop_user(request):
        return _redirect("/shop/login")
    conn = _conn()
    rows = conn.execute("SELECT id, title, created_at, price FROM products ORDER BY id").fetchall()
    conn.close()
    now = datetime.now(timezone.utc)
    items = []
    for row in rows:
        created = datetime.fromisoformat(row["created_at"])
        age_days = (now - created).days
        old = age_days >= int(older_than_months * 30) if older_than_months else False
        if older_than_months and not old:
            continue
        items.append((row, age_days, old))
    page_size = 3
    start = max(0, (page - 1) * page_size)
    view = items[start:start + page_size]
    cards = []
    for row, age_days, old in view:
        testid = ' data-testid="old-listing"' if (older_than_months and old) or (not older_than_months and age_days >= 120) else ""
        cards.append(
            f"<article{testid}><h2>{row['title']}</h2><p>{age_days} days old · ${row['price']}</p></article>"
        )
    suggestions = ""
    if older_than_months:
        names = ", ".join(row["title"] for row, _, _ in items)
        suggestions = f"""
        <section data-testid="old-report">
          <p>Stale listings: {names}.</p>
          <p>Suggestions: refresh photos, lower the price 10%, and rewrite the first line of the description.</p>
        </section>
        """
    pager = ""
    if start + page_size < len(items):
        pager = f'<p><a data-testid="next-page" href="/shop/listings?older_than_months={older_than_months}&page={page+1}">Next page</a></p>'
    return _page(request, "Listings", "".join(cards) + suggestions + pager)


@app.get("/shop/subscribe", response_class=HTMLResponse)
def shop_subscribe(request: Request):
    if not _shop_user(request):
        return _redirect("/shop/login")
    return _page(request, "Pro plan", """
    <p data-testid="plan-pro">Pro plan is 0.05 SOL per month.</p>
    <form method="post" action="/shop/pay">
      <input type="hidden" name="plan" value="pro">
      <input type="hidden" name="amount" value="0.05">
      <p><input data-testid="tx-hash" name="tx_hash" placeholder="Wallet tx hash"></p>
      <button data-testid="pay-submit" type="submit">Confirm payment</button>
    </form>
    """)


@app.post("/shop/pay")
def shop_pay(request: Request, plan: str = Form("pro"), amount: str = Form("0.05"), tx_hash: str = Form("")):
    email = _shop_user(request)
    if not email:
        return _redirect("/shop/login")
    if not tx_hash:
        return HTMLResponse("Missing tx hash", status_code=400)
    conn = _conn()
    conn.execute(
        "INSERT INTO receipts (email, plan, amount, tx_hash, created_at) VALUES (?, ?, ?, ?, ?)",
        (email, plan, amount, tx_hash, datetime.now(timezone.utc).isoformat()),
    )
    conn.commit()
    conn.close()
    return _redirect("/shop/receipt")


@app.get("/shop/receipt", response_class=HTMLResponse)
def shop_receipt(request: Request):
    email = _shop_user(request)
    if not email:
        return _redirect("/shop/login")
    conn = _conn()
    row = conn.execute(
        "SELECT plan, amount, tx_hash FROM receipts WHERE email=? ORDER BY id DESC LIMIT 1",
        (email,),
    ).fetchone()
    conn.close()
    if row is None:
        return _page(request, "Receipt", "<p>No receipt yet.</p>")
    return _page(request, "Receipt", f"""
    <article data-testid="receipt">
      <p>Receipt for {row['plan']} plan</p>
      <p>Amount {row['amount']} SOL</p>
      <p data-testid="receipt-hash">{row['tx_hash']}</p>
    </article>
    """)


# --- news ---------------------------------------------------------------------

@app.get("/news", response_class=HTMLResponse)
def news(request: Request):
    return _page(request, "News desk", """
    <article data-testid="top-headline">
      <h2>City bees adapt to night markets</h2>
      <p>Trend score <span data-testid="trend-score">92</span></p>
    </article>
    <article data-testid="headline">
      <h2>Council debates fountain hours</h2>
      <p>Trend score <span>41</span></p>
    </article>
    <article data-testid="headline">
      <h2>Library adds a quiet room</h2>
      <p>Trend score <span>63</span></p>
    </article>
    """)


# --- media --------------------------------------------------------------------

def _media_session(request: Request) -> tuple[str, bool]:
    sid = request.cookies.get("media_sid")
    if sid:
        return sid, False
    return hashlib.sha256(str(random.random()).encode()).hexdigest()[:12], True


@app.get("/media", response_class=HTMLResponse)
def media_home(request: Request):
    return _page(request, "Media bench", """
    <form method="post" action="/media/generate">
      <p><input data-testid="prompt" name="prompt" placeholder="Prompt"></p>
      <button data-testid="generate" type="submit">Generate</button>
    </form>
    <form method="post" action="/media/merge">
      <button data-testid="merge" type="submit">Merge last two</button>
    </form>
    """)


@app.post("/media/generate")
def media_generate(request: Request, prompt: str = Form("frame")):
    sid, fresh = _media_session(request)
    image_id = hashlib.sha256(f"{sid}:{prompt}:{random.random()}".encode()).hexdigest()[:10]
    path = MEDIA_DIR / f"{image_id}.png"
    _paint(path, prompt or "frame", (40, 90, 70))
    conn = _conn()
    conn.execute(
        "INSERT INTO images (id, session_id, prompt, path, created_at) VALUES (?, ?, ?, ?, ?)",
        (image_id, sid, prompt, str(path), datetime.now(timezone.utc).isoformat()),
    )
    conn.commit()
    conn.close()
    response = _redirect(f"/media/view/{image_id}")
    if fresh:
        response.set_cookie("media_sid", sid)
    return response


@app.get("/media/view/{image_id}", response_class=HTMLResponse)
def media_view(request: Request, image_id: str):
    return _page(request, "Generated frame", f"""
    <p data-testid="image-id">{image_id}</p>
    <img alt="generated" src="/media/files/{image_id}.png">
    <form method="post" action="/media/generate">
      <p><input data-testid="prompt" name="prompt"></p>
      <button data-testid="generate" type="submit">Generate</button>
    </form>
    <form method="post" action="/media/merge">
      <button data-testid="merge" type="submit">Merge last two</button>
    </form>
    """)


@app.post("/media/merge")
def media_merge(request: Request):
    sid = request.cookies.get("media_sid")
    if not sid:
        return HTMLResponse("Generate two images first", status_code=400)
    conn = _conn()
    rows = conn.execute(
        "SELECT id, path FROM images WHERE session_id=? ORDER BY created_at DESC LIMIT 2",
        (sid,),
    ).fetchall()
    if len(rows) < 2:
        conn.close()
        return HTMLResponse("Need two images", status_code=400)
    merged_id = "m" + hashlib.sha256((rows[0]["id"] + rows[1]["id"]).encode()).hexdigest()[:9]
    out = MEDIA_DIR / f"{merged_id}.png"
    _merge(Path(rows[1]["path"]), Path(rows[0]["path"]), out)
    conn.execute(
        "INSERT OR REPLACE INTO images (id, session_id, prompt, path, created_at) VALUES (?, ?, ?, ?, ?)",
        (merged_id, sid, "merge", str(out), datetime.now(timezone.utc).isoformat()),
    )
    conn.commit()
    conn.close()
    return _redirect(f"/media/merged/{merged_id}")


@app.get("/media/merged/{image_id}", response_class=HTMLResponse)
def media_merged(request: Request, image_id: str):
    return _page(request, "Merged", f"""
    <p data-testid="merged-image">Merged image {image_id}</p>
    <img alt="merged" src="/media/files/{image_id}.png">
    """)


@app.get("/media/files/{name}")
def media_file(name: str):
    path = MEDIA_DIR / name
    if not path.exists() or path.suffix.lower() != ".png":
        return Response(status_code=404)
    return Response(content=path.read_bytes(), media_type="image/png")


def _paint(path: Path, label: str, color: tuple[int, int, int]) -> None:
    image = Image.new("RGB", (320, 180), color)
    draw = ImageDraw.Draw(image)
    draw.text((12, 80), (label or "frame")[:40], fill=(255, 255, 255))
    path.parent.mkdir(parents=True, exist_ok=True)
    image.save(path)


def _merge(left: Path, right: Path, out: Path) -> None:
    a = Image.open(left).convert("RGB").resize((320, 180))
    b = Image.open(right).convert("RGB").resize((320, 180))
    canvas = Image.new("RGB", (640, 180), (0, 0, 0))
    canvas.paste(a, (0, 0))
    canvas.paste(b, (320, 0))
    canvas.save(out)


# --- competitions -------------------------------------------------------------

@app.get("/competitions", response_class=HTMLResponse)
def competitions(request: Request):
    import json
    path = ROOT / "data" / "competitions.json"
    rows = json.loads(path.read_text(encoding="utf-8")) if path.exists() else []
    eligible = []
    other = []
    for row in rows:
        block = f"<article><h2>{row['name']}</h2><p>{row.get('prize','')}</p><p>Due {row.get('deadline','')}</p></article>"
        if row.get("eligible", True):
            eligible.append(block)
        else:
            other.append(block)
    return _page(request, "Competitions", f"""
    <section data-testid="eligible-list">{''.join(eligible)}</section>
    <section data-testid="ineligible-list">{''.join(other)}</section>
    """)


@app.get("/competitions/{slug}", response_class=HTMLResponse)
def competition_detail(request: Request, slug: str):
    import json
    path = ROOT / "data" / "competitions.json"
    rows = json.loads(path.read_text(encoding="utf-8")) if path.exists() else []
    row = next((item for item in rows if item.get("slug") == slug), None)
    if row is None:
        return HTMLResponse("Not found", status_code=404)
    return _page(request, row["name"], f"""
    <p>{row.get('summary','')}</p>
    <p>Required: {row.get('required','')}</p>
    <p>Flag: {row.get('flag','')}</p>
    """)


# --- broken -------------------------------------------------------------------

@app.get("/broken", response_class=HTMLResponse)
def broken(request: Request):
    return _page(request, "Broken export", """
    <p>The export control was renamed during a redesign.</p>
    <form method="post" action="/broken/export">
      <button data-testid="export-btn-renamed" type="submit">Download report</button>
    </form>
    """)


@app.post("/broken/export")
def broken_export():
    return HTMLResponse("<p data-testid='exported'>Exported.</p>")


# --- mock bank (ING template: approval, limit, audit) -------------------------

_BANK_PER_TX = 100.0
_BANK_DAILY = 500.0


def _bank_note(conn, event: str, amount: float, detail: str) -> None:
    conn.execute(
        "INSERT INTO bank_audit (ts, event, amount, detail) VALUES (?, ?, ?, ?)",
        (datetime.now(timezone.utc).isoformat(), event, f"{amount:.2f}", detail),
    )


@app.get("/bank", response_class=HTMLResponse)
def bank_home(request: Request):
    conn = _conn()
    row = conn.execute("SELECT balance, spent_today FROM bank_account WHERE id=1").fetchone()
    notes = conn.execute("SELECT event, amount, detail FROM bank_audit ORDER BY id").fetchall()
    conn.close()
    items = "".join(f"<li>{item['event']} {item['amount']} {item['detail']}</li>" for item in notes)
    balance = row["balance"] if row else "0"
    return _page(request, "Mock bank", f"""
    <p data-testid="balance">Balance {balance}</p>
    <form method="post" action="/bank/transfer">
      <input name="amount" data-testid="amount">
      <input name="memo" value="invoice">
      <button data-testid="transfer" type="submit">Transfer</button>
    </form>
    <ul data-testid="audit">{items}</ul>
    """)


@app.post("/bank/transfer", response_class=HTMLResponse)
def bank_transfer(request: Request, amount: str = Form(...), memo: str = Form("transfer")):
    value = float(amount)
    conn = _conn()
    row = conn.execute("SELECT balance, spent_today FROM bank_account WHERE id=1").fetchone()
    spent = float(row["spent_today"])
    _bank_note(conn, "request", value, memo)
    if value <= 0 or value > _BANK_PER_TX or spent + value > _BANK_DAILY:
        reason = "per-transfer limit" if value > _BANK_PER_TX else "daily limit" if spent + value > _BANK_DAILY else "amount"
        _bank_note(conn, "refused", value, reason)
        conn.commit()
        conn.close()
        return _page(request, "Mock bank", f"<p data-testid='refused'>Refused: {reason}</p>")
    _bank_note(conn, "approval_required", value, memo)
    conn.commit()
    conn.close()
    return _page(request, "Mock bank", f"""
    <p data-testid="needs-approval">Approval required for {value:.2f}</p>
    <form method="post" action="/bank/approve">
      <input type="hidden" name="amount" value="{value:.2f}">
      <input type="hidden" name="memo" value="{memo}">
      <button name="decision" value="approved" data-testid="approve" type="submit">Approve</button>
      <button name="decision" value="rejected" type="submit">Reject</button>
    </form>
    """)


@app.post("/bank/approve", response_class=HTMLResponse)
def bank_approve(
    request: Request,
    amount: str = Form(...),
    memo: str = Form("transfer"),
    decision: str = Form(...),
):
    value = float(amount)
    conn = _conn()
    row = conn.execute("SELECT balance, spent_today FROM bank_account WHERE id=1").fetchone()
    if decision != "approved" or value > _BANK_PER_TX:
        _bank_note(conn, "rejected", value, decision)
        conn.commit()
        conn.close()
        return _page(request, "Mock bank", "<p data-testid='rejected'>Rejected</p>")
    balance = round(float(row["balance"]) - value, 2)
    spent = round(float(row["spent_today"]) + value, 2)
    conn.execute("UPDATE bank_account SET balance=?, spent_today=? WHERE id=1", (f"{balance:.2f}", f"{spent:.2f}"))
    _bank_note(conn, "approved", value, memo)
    conn.commit()
    conn.close()
    return _page(request, "Mock bank", f"<p data-testid='approved'>Approved. Balance {balance:.2f}</p>")
