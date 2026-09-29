#!/usr/bin/env python3
"""Record S3, S6, and S7 on real Chromium and the dashboard, then stitch videos/demo.mp4.

The dashboard and sandbox listen on 127.0.0.1. Notification secrets are blanked in the
server so the recording itself does not message Telegram. The finished file is sent
with sendVideo only when it is under 50 MB.
"""

from __future__ import annotations

import asyncio
import json
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path

import httpx

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from grasshopper.demo_scenarios import S3, S6, S7
from grasshopper.publish.demo_edit import (
    find_font,
    probe_duration,
    side_by_side_filter,
    speed_factor,
    under_telegram_limit,
)

PORT = 8080
SANDBOX_PORT = 8090
API_TOKEN = "record-demo"
SCENES = (
    ("S3", "S3 old listings", S3, "done", False),
    ("S6", "S6 approved payment", S6, "done", True),
    ("S7", "S7 stuck repair", S7, "waiting_approval", False),
)


def _blank(env: dict) -> None:
    for key in (
        "TELEGRAM_BOT_TOKEN",
        "TELEGRAM_ALLOWED_USER_ID",
        "WHATSAPP_TOKEN",
        "WHATSAPP_PHONE_NUMBER_ID",
        "WHATSAPP_VERIFY_TOKEN",
        "WHATSAPP_TO",
        "NEBIUS_API_KEY",
        "AWS_ACCESS_KEY_ID",
        "AWS_SECRET_ACCESS_KEY",
        "AZURE_OPENAI_API_KEY",
        "AZURE_SPEECH_KEY",
        "META_API_KEY",
        "OPENAI_COMPAT_API_KEY",
        "ASSEMBLYAI_API_KEY",
        "TAVILY_API_KEY",
        "WALLET_KEYPAIR_PATH",
    ):
        env[key] = ""


def _free(port: int) -> bool:
    import socket

    sock = socket.socket()
    try:
        sock.bind(("127.0.0.1", port))
    except OSError:
        return False
    finally:
        sock.close()
    return True


def _env(work: Path) -> dict:
    env = os.environ.copy()
    _blank(env)
    env.update({
        "MODE": "mock",
        "BROWSER_DRIVER": "playwright",
        "API_TOKEN": API_TOKEN,
        "GRASSHOPPER_EMBED_SANDBOX": "1",
        "DASHBOARD_PORT": str(PORT),
        "SANDBOX_PORT": str(SANDBOX_PORT),
        "SANDBOX_BASE_URL": "",
        "GRASSHOPPER_DATA_DIR": str(work),
        "GRASSHOPPER_DB": str(work / "grasshopper.db"),
        "GRASSHOPPER_RUNS_DIR": str(work / "runs"),
        "SANDBOX_DB": str(work / "sandbox.db"),
        "SANDBOX_MEDIA_DIR": str(work / "media"),
        "APPROVAL_TIMEOUT_SEC": "180",
    })
    return env


def _start_server(env: dict, log_path: Path) -> subprocess.Popen:
    handle = log_path.open("w", encoding="utf-8")
    proc = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "grasshopper.main:app", "--host", "127.0.0.1", "--port", str(PORT)],
        cwd=ROOT,
        env=env,
        stdout=handle,
        stderr=subprocess.STDOUT,
    )
    proc._log_handle = handle  # type: ignore[attr-defined]
    deadline = time.time() + 40
    url = f"http://127.0.0.1:{PORT}/health"
    while time.time() < deadline:
        if proc.poll() is not None:
            handle.close()
            raise RuntimeError(f"dashboard exited early, see {log_path}")
        try:
            httpx.get(url, timeout=0.4)
            httpx.get(f"http://127.0.0.1:{SANDBOX_PORT}/health", timeout=0.4)
            return proc
        except Exception:
            time.sleep(0.2)
    proc.terminate()
    handle.close()
    raise RuntimeError(f"dashboard did not start, see {log_path}")


def _stop(proc: subprocess.Popen | None) -> None:
    if proc is None or proc.poll() is not None:
        return
    proc.terminate()
    try:
        proc.wait(timeout=8)
    except subprocess.TimeoutExpired:
        proc.kill()
    handle = getattr(proc, "_log_handle", None)
    if handle is not None:
        handle.close()


def _overview() -> dict:
    response = httpx.get(
        f"http://127.0.0.1:{PORT}/api/overview",
        headers={"Authorization": f"Bearer {API_TOKEN}"},
        timeout=5,
    )
    response.raise_for_status()
    return response.json()


def _task(text: str) -> dict | None:
    for task in _overview().get("tasks") or []:
        if task.get("text") == text:
            return task
    return None


def _newest_webm(folder: Path) -> Path | None:
    files = [path for path in folder.glob("*.webm") if path.is_file() and path.stat().st_size > 0]
    if not files:
        return None
    return max(files, key=lambda path: path.stat().st_mtime)


def _wait_webm(folder: Path, timeout: float = 20) -> Path:
    deadline = time.time() + timeout
    while time.time() < deadline:
        found = _newest_webm(folder)
        if found is not None:
            return found
        time.sleep(0.3)
    raise RuntimeError(f"no video in {folder}")


def _run_ffmpeg(cmd: list[str]) -> None:
    proc = subprocess.run(cmd, capture_output=True, text=True)
    if proc.returncode != 0:
        tail = (proc.stderr or "")[-800:]
        raise RuntimeError(f"ffmpeg failed: {tail}")


def _encode_pair(agent: Path, dashboard: Path, out: Path, title: str) -> None:
    left = probe_duration(agent)
    right = probe_duration(dashboard)
    graph, label = side_by_side_filter(
        title,
        find_font(),
        left_pad=max(0.0, right - left),
        right_pad=max(0.0, left - right),
    )
    _run_ffmpeg([
        "ffmpeg", "-y", "-i", str(agent), "-i", str(dashboard),
        "-filter_complex", graph, "-map", f"[{label}]",
        "-an", "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "30", "-preset", "veryfast",
        str(out),
    ])


def _concat(parts: list[Path], out: Path) -> None:
    cmd = ["ffmpeg", "-y"]
    for part in parts:
        cmd += ["-i", str(part)]
    labels = "".join(f"[{index}:v]" for index in range(len(parts)))
    cmd += [
        "-filter_complex", f"{labels}concat=n={len(parts)}:v=1:a=0[v]",
        "-map", "[v]", "-an", "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "30", "-preset", "veryfast",
        str(out),
    ]
    _run_ffmpeg(cmd)


def _fit(src: Path, dest: Path) -> float:
    duration = probe_duration(src)
    factor = speed_factor(duration)
    if factor is None:
        if src.resolve() != dest.resolve():
            shutil.copyfile(src, dest)
        return duration
    _run_ffmpeg([
        "ffmpeg", "-y", "-i", str(src),
        "-filter:v", f"setpts=PTS/{factor:.6f}",
        "-an", "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "30", "-preset", "veryfast",
        str(dest),
    ])
    return probe_duration(dest)


def _telegram() -> tuple[str, str]:
    token = ""
    chat = ""
    env_path = ROOT / ".env"
    if not env_path.exists():
        return token, chat
    for raw in env_path.read_text(encoding="utf-8").splitlines():
        if raw.startswith("TELEGRAM_BOT_TOKEN="):
            token = raw.split("=", 1)[1].strip().strip('"').strip("'")
        elif raw.startswith("TELEGRAM_ALLOWED_USER_ID="):
            chat = raw.split("=", 1)[1].strip().strip('"').strip("'")
    return token, chat


def _send_video(path: Path) -> str:
    size = path.stat().st_size
    if not under_telegram_limit(size):
        return f"skipped {size} bytes"
    token, chat = _telegram()
    if not token or not chat:
        return "skipped, telegram is not configured"
    proc = subprocess.run(
        [
            "curl", "-sS",
            f"https://api.telegram.org/bot{token}/sendVideo",
            "-F", f"chat_id={chat}",
            "-F", f"video=@{path}",
            "-F", "caption=Grasshopper demo",
        ],
        capture_output=True,
        text=True,
    )
    try:
        body = json.loads(proc.stdout or "{}")
    except json.JSONDecodeError:
        return "send failed"
    if body.get("ok"):
        return "sent"
    return "send failed: " + str(body.get("description") or "error")


async def _record_scene(name: str, title: str, text: str, expect: str, approve: bool, work: Path) -> Path:
    from playwright.async_api import async_playwright

    dash_dir = work / "dashboard" / name
    dash_dir.mkdir(parents=True, exist_ok=True)
    base = f"http://127.0.0.1:{PORT}"
    async with async_playwright() as pw:
        browser = await pw.chromium.launch(headless=True)
        context = await browser.new_context(
            viewport={"width": 1280, "height": 720},
            record_video_dir=str(dash_dir),
            record_video_size={"width": 1280, "height": 720},
        )
        page = await context.new_page()
        await page.goto(base + "/?token=" + API_TOKEN, wait_until="domcontentloaded")
        box = page.locator("textarea")
        await box.click()
        await box.press_sequentially(text, delay=12)
        await page.get_by_role("button", name="Send").click()
        task = await _wait_task(text, {"waiting_approval", "done", "failed"}, timeout=240)
        if approve and task["status"] == "waiting_approval":
            await page.get_by_role("button", name="Approve").click(timeout=30000)
            task = await _wait_task(text, {"done", "failed"}, timeout=180)
        elif task["status"] not in {expect, "done"}:
            task = await _wait_task(text, {expect, "failed", "done"}, timeout=180)
        if task["status"] != expect:
            raise RuntimeError(f"{name} ended {task['status']}, expected {expect}")
        if expect == "waiting_approval":
            await page.get_by_text("Needs you").wait_for(timeout=15000)
            await page.wait_for_timeout(1500)
        run_id = task.get("run_id") or ""
        if not run_id:
            raise RuntimeError(f"{name} has no run id")
        await page.goto(f"{base}/runs/{run_id}", wait_until="domcontentloaded")
        await page.locator("article").first.wait_for(timeout=15000)
        await page.wait_for_timeout(1500)
        await page.goto(base, wait_until="domcontentloaded")
        await page.locator("#learning").wait_for(timeout=10000)
        await page.locator("#learning").scroll_into_view_if_needed()
        await page.wait_for_timeout(2500)
        video = page.video
        await context.close()
        dashboard = None
        if video is not None:
            try:
                dashboard = Path(await video.path())
            except Exception:
                dashboard = None
        await browser.close()
    if dashboard is None or not dashboard.is_file():
        dashboard = _wait_webm(dash_dir)
    agent = _wait_webm(work / "runs" / run_id / "video")
    out = work / "parts" / f"{name}.mp4"
    out.parent.mkdir(parents=True, exist_ok=True)
    _encode_pair(agent, dashboard, out, title)
    print(f"{name} paired", flush=True)
    return out


async def _wait_task(text: str, wanted: set[str], timeout: float) -> dict:
    deadline = time.time() + timeout
    last = None
    while time.time() < deadline:
        last = _task(text)
        if last and last.get("status") in wanted:
            return last
        await asyncio.sleep(0.4)
    raise RuntimeError(f"timed out waiting for {wanted}: {last}")


def stamp_competition_titles() -> str:
    """Write videos/kits/<slug>.mp4 with the competition name on the opening seconds."""
    src = ROOT / "videos" / "demo.mp4"
    out_dir = ROOT / "videos" / "kits"
    out_dir.mkdir(parents=True, exist_ok=True)
    if not src.is_file():
        note = "unmeasured: videos/demo.mp4 missing"
        (out_dir / "TITLES.md").write_text(note + "\n", encoding="utf-8")
        return note
    font = find_font()
    if not shutil.which("ffmpeg") or not font:
        note = "unmeasured: ffmpeg or font missing"
        (out_dir / "TITLES.md").write_text(note + "\n", encoding="utf-8")
        return note
    rows = json.loads((ROOT / "data" / "competitions.json").read_text(encoding="utf-8"))
    for row in rows:
        slug = str(row["slug"])
        text_file = out_dir / f"{slug}.title.txt"
        text_file.write_text(str(row["name"]).replace(":", " - "), encoding="utf-8")
        dest = out_dir / f"{slug}.mp4"
        _run_ffmpeg([
            "ffmpeg", "-y", "-i", str(src),
            "-vf",
            "drawtext=fontfile='%s':textfile='%s':fontsize=28:fontcolor=white:box=1:boxcolor=black@0.55:x=36:y=36:enable='lt(t,4)'" % (font, text_file),
            "-an", "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "30", "-preset", "veryfast",
            str(dest),
        ])
    return f"{len(rows)} titled copies in {out_dir}"


def main() -> int:
    if "--titles-only" in sys.argv:
        print(stamp_competition_titles(), flush=True)
        return 0
    if not shutil.which("ffmpeg") or not shutil.which("ffprobe"):
        raise SystemExit("ffmpeg and ffprobe are required")
    font = find_font()
    print("titles=" + ("on" if font else "off, no font"), flush=True)
    for port in (PORT, SANDBOX_PORT):
        if not _free(port):
            raise SystemExit(f"127.0.0.1:{port} is already in use")
    work = ROOT / "runs" / "demo-record"
    if work.exists():
        shutil.rmtree(work)
    work.mkdir(parents=True)
    learning_src = ROOT / "data" / "learning.json"
    if learning_src.is_file():
        shutil.copyfile(learning_src, work / "learning.json")
    else:
        (work / "learning.json").write_text(
            json.dumps({"scenarios": {"R1": {"first_calls": 53, "second_calls": 0, "actions": []}}}),
            encoding="utf-8",
        )
    proc = _start_server(_env(work), work / "server.log")
    try:
        parts = []
        for name, title, text, expect, approve in SCENES:
            parts.append(asyncio.run(_record_scene(name, title, text, expect, approve, work)))
        combined = work / "combined.mp4"
        _concat(parts, combined)
        dest = ROOT / "videos" / "demo.mp4"
        dest.parent.mkdir(parents=True, exist_ok=True)
        duration = _fit(combined, dest)
        sent = _send_video(dest)
        print(f"duration={duration:.1f} bytes={dest.stat().st_size} send={sent}", flush=True)
        print(stamp_competition_titles(), flush=True)
    finally:
        _stop(proc)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
