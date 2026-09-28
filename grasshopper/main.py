"""Dashboard, HTTP API, sandbox proxy, and the MCP mount."""

from __future__ import annotations

import logging
import mimetypes
import threading
import time
from contextlib import asynccontextmanager
from pathlib import Path

import httpx
import uvicorn
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse, RedirectResponse, Response
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel

from grasshopper import __version__
from grasshopper.channels.alexa_sim import router as alexa_router
from grasshopper.channels.web_chat import ingest_web_chat
from grasshopper.channels.whatsapp_webhook import router as whatsapp_router
from grasshopper.config import get_settings, scan_repo_for_secrets
from grasshopper.core.explainer import Explainer
from grasshopper.publish.live import latest_screenshot
from grasshopper.publish.live_feed import frame_path, read_status
from grasshopper.mcp_server.server import build_mcp_app, mcp_server
from grasshopper.providers.factory import provider_status
from grasshopper.sandbox_runner.factory import audit_path, runner_status
from grasshopper.realweb.learning import LearningStore
from grasshopper.runtime import get_context

log = logging.getLogger("grasshopper")
logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s %(message)s")

ROOT = Path(__file__).resolve().parents[1]
TEMPLATES = Jinja2Templates(directory=str(Path(__file__).parent / "ui" / "templates"))
MCP_APP = build_mcp_app()
_SANDBOX_THREAD: threading.Thread | None = None


def _start_sandbox(port: int) -> None:
    global _SANDBOX_THREAD
    import socket

    probe = socket.socket()
    try:
        probe.bind(("127.0.0.1", port))
    except OSError:
        probe.close()
        log.info("Sandbox already listening on %s", port)
        return
    probe.close()

    config = uvicorn.Config(
        "sandbox_web.app:app",
        host="127.0.0.1",
        port=port,
        log_level="warning",
    )
    server = uvicorn.Server(config)
    _SANDBOX_THREAD = threading.Thread(target=server.run, name="sandbox", daemon=True)
    _SANDBOX_THREAD.start()
    for _ in range(50):
        try:
            httpx.get(f"http://127.0.0.1:{port}/health", timeout=0.4)
            log.info("Sandbox ready on %s", port)
            return
        except Exception:
            time.sleep(0.1)
    log.warning("Sandbox did not answer on port %s", port)


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()
    for hit in scan_repo_for_secrets():
        log.warning("Possible secret in repo: %s", hit)
    ctx = get_context()
    app.state.ctx = ctx
    app.state.templates = TEMPLATES
    if settings.embed_sandbox:
        _start_sandbox(settings.sandbox_port)
    if getattr(mcp_server.session_manager, "_has_started", False):
        mcp_server.session_manager._has_started = False
    async with mcp_server.session_manager.run():
        ctx.start_worker()
        telegram = None
        try:
            from grasshopper.channels.telegram_bot import build_telegram_application

            telegram = build_telegram_application(ctx)
            if telegram is not None:
                await telegram.initialize()
                await telegram.start()
                if os.environ.get("TELEGRAM_POLLING", "1") != "0":
                    await telegram.updater.start_polling()
        except Exception as exc:
            log.warning("Telegram did not start: %s", exc)
            telegram = None
        yield
        if telegram is not None:
            try:
                if getattr(telegram.updater, "running", False):
                    await telegram.updater.stop()
                await telegram.stop()
                await telegram.shutdown()
            except Exception:
                pass
        await ctx.stop_worker()


app = FastAPI(title="Grasshopper", version=__version__, lifespan=lifespan)
app.mount("/mcp", MCP_APP)
app.include_router(alexa_router)
app.include_router(whatsapp_router)


def _ctx(request: Request):
    return getattr(request.app.state, "ctx", None) or get_context()


def _authorized(request: Request) -> bool:
    settings = _ctx(request).settings
    header = request.headers.get("authorization", "")
    token = header[7:].strip() if header.lower().startswith("bearer ") else ""
    if not token:
        token = request.cookies.get("gh_token", "")
    return token == settings.api_token


def _require(request: Request) -> None:
    if not _authorized(request):
        raise HTTPException(status_code=401, detail="Missing or bad API token")


def _open_path(path: str) -> bool:
    """Health, the MCP protocol, and the WhatsApp webhook do not use the dashboard token."""
    return path == "/health" or path.startswith("/mcp") or path.startswith("/webhooks/")


@app.middleware("http")
async def require_dashboard_token(request: Request, call_next):
    if request.url.path.startswith("/mcp"):
        settings = _ctx(request).settings
        if settings.mcp_bearer_token:
            auth_header = request.headers.get("authorization", "")
            expected = f"Bearer {settings.mcp_bearer_token}"
            if auth_header != expected:
                return JSONResponse({"detail": "Unauthorized MCP request"}, status_code=401)
        if settings.mcp_allowed_origins:
            origin = request.headers.get("origin")
            allowed = [o.strip() for o in settings.mcp_allowed_origins.split(",") if o.strip()]
            if origin and allowed and origin not in allowed:
                return JSONResponse({"detail": "Forbidden Origin"}, status_code=403)
        return await call_next(request)
    if _open_path(request.url.path):
        return await call_next(request)
    settings = _ctx(request).settings
    presented = request.query_params.get("token", "")
    if presented and presented == settings.api_token:
        target = request.url.path or "/"
        extra = [(key, value) for key, value in request.query_params.multi_items() if key != "token"]
        if extra:
            from urllib.parse import urlencode
            target = target + "?" + urlencode(extra)
        response = RedirectResponse(target, status_code=303)
        response.set_cookie("gh_token", settings.api_token, httponly=True, samesite="lax")
        return response
    if not _authorized(request):
        return JSONResponse({"detail": "Missing or bad API token"}, status_code=401)
    return await call_next(request)


@app.get("/health")
def health():
    return {"ok": True, "service": "grasshopper", "version": __version__}


@app.get("/", response_class=HTMLResponse)
def dashboard(request: Request):
    _ctx(request)
    return TEMPLATES.TemplateResponse(request, "dashboard.html", {})


@app.get("/runs/{run_id}", response_class=HTMLResponse)
def run_page(request: Request, run_id: str):
    ctx = _ctx(request)
    run_dir = ctx.settings.runs_dir / run_id
    events = Explainer(run_dir).read() if run_dir.exists() else []
    for event in events:
        evidence = event.get("evidence") or ""
        if evidence:
            try:
                event["evidence_rel"] = str(Path(evidence).relative_to(ctx.settings.runs_dir.parent))
            except ValueError:
                event["evidence_rel"] = ""
        else:
            event["evidence_rel"] = ""
    summary = ""
    result_path = run_dir / "result.json"
    if result_path.exists():
        summary = result_path.read_text(encoding="utf-8")
    return TEMPLATES.TemplateResponse(
        request,
        "run.html",
        {"run_id": run_id, "events": events, "summary": summary},
    )


@app.get("/api/live")
def live_status(request: Request):
    _require(request)
    ctx = _ctx(request)
    status = read_status(ctx.settings.runs_dir)
    status["shot"] = "/live/frame.png" if frame_path(ctx.settings.runs_dir).is_file() else ""
    return status


@app.get("/live/frame.png")
def live_frame(request: Request):
    _require(request)
    ctx = _ctx(request)
    path = frame_path(ctx.settings.runs_dir)
    if not path.is_file():
        raise HTTPException(404)
    return FileResponse(path, media_type="image/png", headers={"Cache-Control": "no-store"})


@app.get("/runs/{run_id}/live.png")
def live_png(run_id: str):
    """Newest browser frame for this run. The run page reloads it every second."""
    ctx = get_context()
    path = latest_screenshot(ctx.settings.runs_dir, run_id)
    if path is None:
        raise HTTPException(404)
    return FileResponse(path, media_type="image/png", headers={"Cache-Control": "no-store"})


@app.get("/artifacts/{file_path:path}")
def artifact(file_path: str):
    """Serve screenshots from the runs directory. Paths cannot escape it."""
    ctx = get_context()
    root = ctx.settings.runs_dir.resolve()
    # The UI stores paths relative to the repo root (runs/...).
    candidate = (ROOT / file_path).resolve()
    if root not in candidate.parents and candidate != root:
        raise HTTPException(404)
    if not candidate.is_file():
        raise HTTPException(404)
    media = mimetypes.guess_type(candidate.name)[0] or "application/octet-stream"
    return FileResponse(candidate, media_type=media)


class ApprovalBody(BaseModel):
    decision: str


@app.get("/api/overview")
def overview(request: Request):
    _require(request)
    ctx = _ctx(request)
    tasks = []
    for task in ctx.queue.list_recent(12):
        result = task.result or {}
        shot = _latest_shot(ctx, task.run_id)
        tasks.append({
            "id": task.id,
            "text": task.text,
            "status": task.status.value,
            "channel": task.channel,
            "run_id": task.run_id,
            "summary": result.get("summary", ""),
            "steps": f"{result.get('steps_ok', '—')}/{result.get('steps_total', '—')}" if result else "—",
            "rate": f"{int((result.get('success_rate') or 0) * 100)}%" if result else "—",
            "llm_calls": result.get("llm_calls", 0) if result else 0,
            "shot": shot,
        })
    approvals = []
    for item in ctx.gate.pending():
        rel = ""
        if item.screenshot:
            try:
                rel = str(Path(item.screenshot).resolve().relative_to(ROOT))
            except ValueError:
                rel = ""
        approvals.append({
            "id": item.id,
            "task_id": item.task_id,
            "reason": item.reason,
            "screenshot_rel": rel,
        })
    return {
        "tasks": tasks,
        "approvals": approvals,
        "providers": provider_status(ctx.settings),
        "wallet_sol": ctx.wallet.balance(),
        "daily_limit": ctx.settings.wallet_daily_limit_sol,
        "queue": ctx.queue.queued_count(),
        "fast_ratio": ctx.router.savings()["fast_ratio"],
        "cost": _cost_panel(ctx.router.savings(), ctx),
        "learning": _learning_panel(ctx),
        "runner": runner_status(audit_path(ctx.settings)),
    }


def _learning_panel(ctx) -> dict:
    return LearningStore(Path(ctx.settings.data_dir) / "learning.json").panel()


def _cost_panel(savings: dict, ctx=None) -> dict:
    counts = savings.get("by_tier") or {}
    if ctx is None:
        try:
            ctx = get_context()
        except Exception:
            ctx = None
    if ctx is not None:
        try:
            total_tasks = max(len(ctx.queue.all()), 1)
            cost_per_task = float(ctx.router.budget.daily_actual / total_tasks)
            nebius_model = getattr(ctx.settings, "nebius_fast_model", "") or "nvidia/Nemotron-3_5-Lightning"
            daily_actual = float(ctx.router.budget.daily_actual)
        except Exception:
            cost_per_task = 0.0
            nebius_model = "nvidia/Nemotron-3_5-Lightning"
            daily_actual = 0.0
    else:
        cost_per_task = 0.0
        nebius_model = "nvidia/Nemotron-3_5-Lightning"
        daily_actual = 0.0
    return {
        "fast": int(counts.get("fast", 0)),
        "strong": int(counts.get("strong", 0)),
        "vision": int(counts.get("vision", 0)),
        "saved_tokens": int(savings.get("saved_tokens") or 0),
        "saved_usd": float(savings.get("saved_usd") or 0.0),
        "cost_per_task": cost_per_task,
        "nebius_model": nebius_model,
        "daily_actual_usd": daily_actual,
    }


def _latest_shot(ctx, run_id: str | None) -> str:
    if not run_id:
        return ""
    path = latest_screenshot(ctx.settings.runs_dir, run_id)
    if path is None:
        return ""
    try:
        rel = path.resolve().relative_to(ROOT)
    except ValueError:
        return ""
    return "/artifacts/" + str(rel)


@app.post("/api/tasks")
async def create_task(request: Request):
    _require(request)
    ctx = _ctx(request)
    content = request.headers.get("content-type", "")
    audio_path = None
    if "multipart/form-data" in content:
        form = await request.form()
        text = str(form.get("text") or "")
        upload = form.get("audio")
        if upload is not None and getattr(upload, "filename", ""):
            folder = ctx.settings.data_dir / "audio"
            folder.mkdir(parents=True, exist_ok=True)
            audio_path = str(folder / Path(upload.filename).name)
            Path(audio_path).write_bytes(await upload.read())
    else:
        try:
            payload = await request.json()
        except Exception:
            payload = {}
        text = str(payload.get("text") or "")
    task = await ingest_web_chat(ctx, text, audio_path)
    return {"id": task.id, "status": task.status.value, "scheduled_at": task.scheduled_at.isoformat() if task.scheduled_at else None}


@app.get("/api/tasks/{task_id}")
def get_task(task_id: str, request: Request):
    _require(request)
    task = _ctx(request).queue.get(task_id)
    if task is None:
        raise HTTPException(404)
    return task.model_dump(mode="json")


@app.get("/api/runs/{run_id}")
def get_run(run_id: str, request: Request):
    _require(request)
    ctx = _ctx(request)
    folder = ctx.settings.runs_dir / run_id
    if not folder.exists():
        raise HTTPException(404)
    result_path = folder / "result.json"
    result = result_path.read_text(encoding="utf-8") if result_path.exists() else "{}"
    return JSONResponse({
        "run_id": run_id,
        "result": result,
        "events": Explainer(folder).read(),
    })


@app.post("/api/approvals/{approval_id}")
def post_approval(approval_id: str, body: ApprovalBody, request: Request):
    _require(request)
    if body.decision not in {"approved", "rejected"}:
        raise HTTPException(400, "decision must be approved or rejected")
    row = _ctx(request).gate.decide(approval_id, body.decision)
    if row is None:
        raise HTTPException(404)
    return {"id": row.id, "status": row.status.value}


_PROXY_PREFIXES = (
    "ai-alpha", "ai-beta", "shop", "news", "media", "competitions", "broken", "banner",
)


@app.api_route("/{prefix}", methods=["GET", "POST"])
@app.api_route("/{prefix}/{path:path}", methods=["GET", "POST"])
async def sandbox_proxy(prefix: str, request: Request, path: str = ""):
    if prefix not in _PROXY_PREFIXES:
        raise HTTPException(404)
    ctx = _ctx(request)
    target = ctx.settings.sandbox_url + request.url.path
    if request.url.query:
        target += "?" + request.url.query
    body = await request.body()
    headers = {
        key: value
        for key, value in request.headers.items()
        if key.lower() not in {"host", "content-length", "accept-encoding"}
    }
    async with httpx.AsyncClient(follow_redirects=False, timeout=30) as client:
        upstream = await client.request(request.method, target, content=body, headers=headers)
    out_headers = {}
    if "set-cookie" in upstream.headers:
        out_headers["set-cookie"] = upstream.headers["set-cookie"]
    location = upstream.headers.get("location")
    if location and location.startswith(ctx.settings.sandbox_url):
        location = location[len(ctx.settings.sandbox_url):] or "/"
        out_headers["location"] = location
    elif location and location.startswith("/"):
        out_headers["location"] = location
    media = upstream.headers.get("content-type")
    return Response(content=upstream.content, status_code=upstream.status_code, headers=out_headers, media_type=media)
