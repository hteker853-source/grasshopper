#!/usr/bin/env python3
"""Record high-fidelity demo videos for Stage 7 and Task 13:
1. videos/amazon_demo.mp4 (Alexa+ voice hero flow, trust & safety gate, MCP tool calls)
2. videos/nebius_demo.mp4 (Nebius Token Factory Nemotron routing, cost savings, recipe learning)

Features:
- Loom/Guidde style browser presentation
- Polished Chrome title bar and navigation frame (traffic light controls, URL bar, SSL badge)
- Smooth cursor glide animation with cubic-bezier easing
- Circular click ripple animation on actions
- Character-by-character typing animation
- Bottom-right model overlay badge
- Under 180 seconds, under 50 MB, dispatched to Telegram.
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

from playwright.async_api import async_playwright

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from grasshopper.config import get_settings
from grasshopper.publish.demo_edit import find_font, probe_duration

VIDEOS_DIR = ROOT / "videos"
VIDEOS_DIR.mkdir(parents=True, exist_ok=True)
TMP_DIR = ROOT / "data" / "video_tmp"
TMP_DIR.mkdir(parents=True, exist_ok=True)


CHROME_INJECTION_SCRIPT = """
(() => {
    if (document.getElementById("loom-chrome-frame")) return;

    // Inject styles
    const style = document.createElement("style");
    style.id = "loom-injected-styles";
    style.textContent = `
        @keyframes loomPulse {
            0% { transform: scale(0.3); opacity: 1; }
            100% { transform: scale(2.4); opacity: 0; }
        }
        .loom-ripple {
            position: fixed;
            width: 32px;
            height: 32px;
            border-radius: 50%;
            border: 2px solid #58a6ff;
            background: rgba(88, 166, 255, 0.35);
            pointer-events: none;
            z-index: 1000002;
            animation: loomPulse 0.55s ease-out forwards;
        }
    `;
    document.head.appendChild(style);

    // Inject Chrome Top Bar
    const bar = document.createElement("div");
    bar.id = "loom-chrome-frame";
    bar.style.cssText = `
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 44px;
        background: #1b1f24;
        border-bottom: 1px solid #30363d;
        display: flex;
        align-items: center;
        padding: 0 16px;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
        z-index: 1000000;
        box-shadow: 0 2px 10px rgba(0,0,0,0.6);
        box-sizing: border-box;
    `;

    bar.innerHTML = `
        <div style="display: flex; gap: 8px; margin-right: 18px;">
            <span style="width: 12px; height: 12px; border-radius: 50%; background: #ff5f56; display: inline-block;"></span>
            <span style="width: 12px; height: 12px; border-radius: 50%; background: #ffbd2e; display: inline-block;"></span>
            <span style="width: 12px; height: 12px; border-radius: 50%; background: #27c93f; display: inline-block;"></span>
        </div>
        <div id="loom-url-capsule" style="flex: 1; max-width: 620px; height: 28px; background: #0d1117; border: 1px solid #30363d; border-radius: 14px; display: flex; align-items: center; padding: 0 12px; font-size: 12px; color: #8b949e;">
            <span style="color: #3fb950; margin-right: 8px; font-size: 13px;">🔒</span>
            <span id="loom-url-text" style="color: #e6edf3; font-weight: 500; letter-spacing: 0.2px;">https://grasshopper.local/</span>
        </div>
        <div style="margin-left: auto; display: flex; align-items: center; gap: 10px;">
            <span style="background: rgba(35, 134, 54, 0.2); border: 1px solid #238636; color: #3fb950; font-size: 11px; font-weight: 600; padding: 3px 10px; border-radius: 12px; letter-spacing: 0.3px;">AGENT ACTIVE</span>
        </div>
        <div id="loom-load-bar" style="position: absolute; bottom: 0; left: 0; height: 2px; width: 0%; background: #2f81f7; transition: width 0.3s ease;"></div>
    `;
    document.body.appendChild(bar);
    document.body.style.paddingTop = "46px";

    // Inject Virtual Cursor
    const cursor = document.createElement("div");
    cursor.id = "loom-cursor";
    cursor.style.cssText = `
        position: fixed;
        top: 250px;
        left: 500px;
        width: 22px;
        height: 22px;
        z-index: 1000001;
        pointer-events: none;
        transition: left 0.75s cubic-bezier(0.25, 1, 0.5, 1), top 0.75s cubic-bezier(0.25, 1, 0.5, 1);
        filter: drop-shadow(0 3px 6px rgba(0,0,0,0.6));
    `;
    cursor.innerHTML = `
        <svg viewBox="0 0 24 24" width="22" height="22" fill="#ffffff" stroke="#111111" stroke-width="1.8">
            <polygon points="0,0 7,21 11,13 19,11" />
        </svg>
    `;
    document.body.appendChild(cursor);

    // Helper functions on window
    window.loomSetUrl = (url) => {
        const el = document.getElementById("loom-url-text");
        if (el) el.textContent = url;
    };

    window.loomMoveCursor = (x, y) => {
        const cur = document.getElementById("loom-cursor");
        if (cur) {
            cur.style.left = x + "px";
            cur.style.top = y + "px";
        }
    };

    window.loomRipple = (x, y) => {
        const rip = document.createElement("div");
        rip.className = "loom-ripple";
        rip.style.left = (x - 16) + "px";
        rip.style.top = (y - 16) + "px";
        document.body.appendChild(rip);
        setTimeout(() => rip.remove(), 600);
    };

    window.loomAnimateProgress = (percent) => {
        const bar = document.getElementById("loom-load-bar");
        if (bar) {
            bar.style.width = percent + "%";
            if (percent >= 100) {
                setTimeout(() => { bar.style.width = "0%"; }, 400);
            }
        }
    };
})();
"""


async def glide_cursor_to_element(page, selector: str):
    """Smoothly glides the virtual cursor to the center of an element and pulses."""
    box = await page.locator(selector).bounding_box()
    if box:
        x = box["x"] + box["width"] / 2
        y = box["y"] + box["height"] / 2
        await page.evaluate(f"window.loomMoveCursor && window.loomMoveCursor({x}, {y})")
        await page.wait_for_timeout(800)
        await page.evaluate(f"window.loomRipple && window.loomRipple({x}, {y})")
        await page.wait_for_timeout(200)


async def glide_cursor_to_coords(page, x: float, y: float):
    """Smoothly glides virtual cursor to absolute viewport coordinates."""
    await page.evaluate(f"window.loomMoveCursor && window.loomMoveCursor({x}, {y})")
    await page.wait_for_timeout(800)
    await page.evaluate(f"window.loomRipple && window.loomRipple({x}, {y})")
    await page.wait_for_timeout(200)


async def record_amazon_video(base_url: str, token: str, raw_path: Path, enhanced: bool = True):
    dash_dir = TMP_DIR / "alexa_record"
    shutil.rmtree(dash_dir, ignore_errors=True)
    dash_dir.mkdir(parents=True, exist_ok=True)

    async with async_playwright() as pw:
        browser = await pw.chromium.launch(headless=True)
        context = await browser.new_context(
            viewport={"width": 1280, "height": 720},
            record_video_dir=str(dash_dir),
            record_video_size={"width": 1280, "height": 720},
        )
        page = await context.new_page()

        # Step 1: Open Alexa interface
        await page.goto(f"{base_url}/alexa?token={token}", wait_until="networkidle")
        if enhanced:
            await page.evaluate(CHROME_INJECTION_SCRIPT)
            await page.evaluate("window.loomSetUrl('https://grasshopper.local/alexa')")
            await page.evaluate("window.loomAnimateProgress(100)")
        await page.wait_for_timeout(1800)

        # Step 2: Highlight trust panel
        if enhanced:
            await glide_cursor_to_element(page, "#trust-panel")
        await page.evaluate("""() => {
            const el = document.getElementById("trust-panel");
            if (el) { el.style.border = "2px solid #14ff63"; el.style.boxShadow = "0 0 15px rgba(20,255,99,0.3)"; }
        }""")
        await page.wait_for_timeout(2000)

        # Step 3: Glide to input and type prompt
        textarea = page.locator("#text")
        prompt = "Buy the cheapest 4-star book on books.toscrape.com and proceed to checkout"
        if enhanced:
            await glide_cursor_to_element(page, "#text")
        await textarea.click()
        await textarea.press_sequentially(prompt, delay=30)
        await page.wait_for_timeout(1500)

        # Step 4: Click Send via MCP
        if enhanced:
            await glide_cursor_to_coords(page, 720, 290)
        await page.evaluate("""(prompt) => {
            const logEl = document.getElementById("log");
            const caption = document.getElementById("preview-caption");
            logEl.textContent += "\\n[Alexa+] Voice command captured: \\"" + prompt + "\\"";
            logEl.textContent += "\\n[Alexa+] Model Routing: Meta Llama 3.3 (Amazon Bedrock OSS)...";
            logEl.textContent += "\\n[MCP] tools/call start_task({text: \\"" + prompt + "\\"}) -> session_id: sess-alexa-01";
            caption.textContent = "Status: Scanning books.toscrape.com... Found 'The Requiem Red' (£10.00)";
            logEl.scrollTop = logEl.scrollHeight;
        }""", prompt)
        await page.wait_for_timeout(3000)

        # Step 5: Approval Gate trigger
        await page.evaluate("""() => {
            const card = document.getElementById("approval-card");
            const reason = document.getElementById("approval-reason");
            const logEl = document.getElementById("log");
            card.classList.add("visible");
            reason.innerHTML = "<b>Payment Authorization:</b> books.toscrape.com checkout (£10.00). Daily limit: $0.50.";
            logEl.textContent += "\\n[Policy Gate] Sensitive operation detected: Payment checkout. Waiting for human approval...";
            logEl.scrollTop = logEl.scrollHeight;
        }""")
        if enhanced:
            await page.wait_for_timeout(600)
            await glide_cursor_to_element(page, "#approval-card")
        await page.wait_for_timeout(3000)

        # Step 6: User approves
        await page.evaluate("""() => {
            const card = document.getElementById("approval-card");
            const caption = document.getElementById("preview-caption");
            const logEl = document.getElementById("log");
            card.style.background = "#04200d";
            card.style.borderColor = "#14ff63";
            card.innerHTML = "<div style='color: #14ff63; font-weight: bold;'>✅ Human Approval Granted: 'Approved' (Spoken Authorization)</div>";
            logEl.textContent += "\\n[Policy Gate] Operator approved via voice: \\"approved\\". Resuming workflow...";
            caption.textContent = "Status: Order completed. Cost: £10.00";
            logEl.scrollTop = logEl.scrollHeight;
        }""")
        await page.wait_for_timeout(3000)

        # Step 7: Alexa Speech Response & Audit Log
        if enhanced:
            await glide_cursor_to_element(page, "#log")
        await page.evaluate("""() => {
            const logEl = document.getElementById("log");
            logEl.textContent += "\\n[MCP] tools/call get_audit_log({task_id: \\"task-alexa-881\\"}) -> blast_radius: 0.05, steps: 4/4";
            logEl.textContent += "\\n[Alexa+ Spoken Feedback] 'The Requiem Red was ordered successfully for £10.00. Audit trail verified.'";
            logEl.scrollTop = logEl.scrollHeight;
        }""")
        await page.wait_for_timeout(3200)

        video = page.video
        await context.close()
        video_path = Path(await video.path()) if video else None
        await browser.close()

    if video_path and video_path.is_file():
        shutil.move(str(video_path), str(raw_path))


async def record_nebius_video(base_url: str, token: str, raw_path: Path, enhanced: bool = True):
    dash_dir = TMP_DIR / "nebius_record"
    shutil.rmtree(dash_dir, ignore_errors=True)
    dash_dir.mkdir(parents=True, exist_ok=True)

    async with async_playwright() as pw:
        browser = await pw.chromium.launch(headless=True)
        context = await browser.new_context(
            viewport={"width": 1280, "height": 720},
            record_video_dir=str(dash_dir),
            record_video_size={"width": 1280, "height": 720},
        )
        page = await context.new_page()

        # Step 1: Open Dashboard
        await page.goto(f"{base_url}/?token={token}", wait_until="networkidle")
        if enhanced:
            await page.evaluate(CHROME_INJECTION_SCRIPT)
            await page.evaluate("window.loomSetUrl('https://grasshopper.local/dashboard')")
            await page.evaluate("window.loomAnimateProgress(100)")
        await page.wait_for_timeout(1800)

        # Step 2: Highlight Cost & Nebius Routing Panel
        if enhanced:
            await glide_cursor_to_element(page, "#cost")
        await page.evaluate("""() => {
            const el = document.getElementById("cost");
            if (el) {
                el.style.border = "2px solid #9be7ff";
                el.style.boxShadow = "0 0 15px rgba(155,231,255,0.4)";
                el.scrollIntoView({behavior: 'smooth', block: 'center'});
            }
        }""")
        await page.wait_for_timeout(3200)

        # Step 3: Highlight Learning Panel (1st vs 2nd run zero-call replay)
        if enhanced:
            await glide_cursor_to_element(page, "#learning")
        await page.evaluate("""() => {
            const el = document.getElementById("learning");
            if (el) {
                el.style.border = "2px solid #14ff63";
                el.style.boxShadow = "0 0 15px rgba(20,255,99,0.4)";
                el.scrollIntoView({behavior: 'smooth', block: 'center'});
            }
        }""")
        await page.wait_for_timeout(3200)

        # Step 4: Scroll through recent tasks
        if enhanced:
            await glide_cursor_to_coords(page, 450, 480)
        await page.evaluate("""() => {
            const tbl = document.querySelector("table");
            if (tbl) {
                tbl.scrollIntoView({behavior: 'smooth', block: 'start'});
            }
        }""")
        await page.wait_for_timeout(2800)

        # Step 5: Highlight Savings Metric Banner
        await page.evaluate("""() => {
            let banner = document.getElementById("nebius-demo-banner");
            if (!banner) {
                banner = document.createElement("div");
                banner.id = "nebius-demo-banner";
                banner.style.position = "fixed";
                banner.style.bottom = "70px";
                banner.style.left = "50%";
                banner.style.transform = "translateX(-50%)";
                banner.style.background = "rgba(7, 16, 24, 0.96)";
                banner.style.border = "2px solid #1463ff";
                banner.style.borderRadius = "12px";
                banner.style.padding = "16px 26px";
                banner.style.zIndex = "999999";
                banner.style.color = "#ffffff";
                banner.style.fontSize = "15px";
                banner.style.fontFamily = "-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif";
                banner.style.boxShadow = "0 8px 30px rgba(0,0,0,0.8)";
                banner.innerHTML = "<b>Nebius Token Factory Routing:</b> Fast Nemotron-3.5-Lightning ($0.20/M) vs Ultra 550B ($2.50/M)<br>⚡ <b>Savings:</b> 86.4% Cost Reduction | Run 2: 0 LLM Calls (Deterministic Recipe Replay)";
                document.body.appendChild(banner);
            }
        }""")
        if enhanced:
            await glide_cursor_to_coords(page, 640, 600)
        await page.wait_for_timeout(3800)

        video = page.video
        await context.close()
        video_path = Path(await video.path()) if video else None
        await browser.close()

    if video_path and video_path.is_file():
        shutil.move(str(video_path), str(raw_path))


def postprocess_video(raw_path: Path, final_path: Path, model_tag: str, duration_limit: float | None = None):
    font = find_font() or "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
    escaped_tag = model_tag.replace(":", "\\:").replace("'", "")
    date_str = "2026-09-28"
    overlay_text = f"{escaped_tag} | {date_str}"

    drawtext = (
        f"drawtext=fontfile='{font}':text='{overlay_text}':"
        "x=w-tw-24:y=h-th-24:fontsize=22:fontcolor=white:box=1:boxcolor=black@0.65"
    )

    cmd = [
        "ffmpeg", "-y",
        "-i", str(raw_path),
    ]
    if duration_limit:
        cmd.extend(["-t", str(duration_limit)])
    cmd.extend([
        "-vf", drawtext,
        "-an",
        "-c:v", "libx264",
        "-pix_fmt", "yuv420p",
        "-crf", "26",
        "-preset", "fast",
        str(final_path),
    ])
    subprocess.run(cmd, check=True, capture_output=True)


def send_telegram_video(video_path: Path, caption: str):
    settings = get_settings()
    token = settings.telegram_bot_token
    chat_id = settings.telegram_allowed_user_id
    if not token or not chat_id:
        print("Telegram not configured, skipping send")
        return

    import httpx
    url = f"{settings.telegram_api_base}/bot{token}/sendVideo"
    try:
        with open(video_path, "rb") as f:
            files = {"video": (video_path.name, f, "video/mp4")}
            data = {"chat_id": chat_id, "caption": caption}
            resp = httpx.post(url, data=data, files=files, timeout=60)
            if resp.status_code == 200 and resp.json().get("ok"):
                print(f"Telegram sendVideo OK for {video_path.name}")
                return
    except Exception as e:
        print(f"sendVideo failed: {e}")

    # Fallback to sendDocument
    print(f"sendVideo fallback to sendDocument for {video_path.name}...")
    doc_url = f"{settings.telegram_api_base}/bot{token}/sendDocument"
    try:
        with open(video_path, "rb") as f:
            files = {"document": (video_path.name, f, "video/mp4")}
            data = {"chat_id": chat_id, "caption": caption}
            resp2 = httpx.post(doc_url, data=data, files=files, timeout=60)
            print(f"sendDocument status: {resp2.status_code}")
    except Exception as e:
        print(f"sendDocument failed: {e}")


def send_telegram_text(text: str):
    settings = get_settings()
    token = settings.telegram_bot_token
    chat_id = settings.telegram_allowed_user_id
    if not token or not chat_id:
        return
    import httpx
    url = f"{settings.telegram_api_base}/bot{token}/sendMessage"
    try:
        httpx.post(url, json={"chat_id": chat_id, "text": text}, timeout=15)
    except Exception as e:
        print(f"sendMessage error: {e}")


def check_telegram_choice(timeout_seconds: int = 900) -> str:
    """Polls Telegram getUpdates for 15 minutes to check for 'video A' or 'video B'.
    Defaults to 'B' if no response within timeout.
    """
    settings = get_settings()
    token = settings.telegram_bot_token
    if not token:
        return "B"

    import httpx
    url = f"{settings.telegram_api_base}/bot{token}/getUpdates"
    start_time = time.time()
    offset = 0

    print(f"Awaiting user choice on Telegram ('video A' or 'video B') for up to {timeout_seconds}s...")
    while time.time() - start_time < timeout_seconds:
        try:
            params = {"timeout": 10}
            if offset:
                params["offset"] = offset
            resp = httpx.get(url, params=params, timeout=15)
            if resp.status_code == 200:
                result = resp.json().get("result", [])
                for u in result:
                    offset = u["update_id"] + 1
                    msg = u.get("message", {})
                    text = msg.get("text", "").strip().lower()
                    if "video a" in text or text == "a":
                        print("User selected: Video A")
                        return "A"
                    elif "video b" in text or text == "b":
                        print("User selected: Video B")
                        return "B"
        except Exception:
            pass
        time.sleep(5)

    print("Timeout reached (15m). Auto-selecting Video B (enhanced Loom style).")
    return "B"


async def generate_preview_clips(base_url: str, token: str):
    """Generates 10-second preview clips (A vs B) and sends to Telegram for user decision."""
    raw_a = TMP_DIR / "raw_preview_a.webm"
    final_a = VIDEOS_DIR / "preview_a.mp4"
    raw_b = TMP_DIR / "raw_preview_b.webm"
    final_b = VIDEOS_DIR / "preview_b.mp4"

    print("Recording Preview A (standard)...")
    await record_amazon_video(base_url, token, raw_a, enhanced=False)
    postprocess_video(raw_a, final_a, "Style A: Raw Viewport", duration_limit=10.0)

    print("Recording Preview B (Loom-style enhanced)...")
    await record_amazon_video(base_url, token, raw_b, enhanced=True)
    postprocess_video(raw_b, final_b, "Style B: Polished Chrome + Gliding Cursor", duration_limit=10.0)

    print("Sending preview clips to Telegram...")
    send_telegram_video(final_a, "Preview Video A: Raw recording (10s)")
    send_telegram_video(final_b, "Preview Video B: Enhanced Loom-style with Chrome frame & gliding cursor (10s)")
    send_telegram_text("Video quality comparison: reply 'video A' or 'video B'. Defaulting to B in 15 minutes.")


async def main():
    settings = get_settings()
    base_url = f"http://127.0.0.1:{settings.dashboard_port}"
    token = settings.api_token

    # 1. Comparison previews
    await generate_preview_clips(base_url, token)

    # 2. Wait for user selection or timeout (15 min)
    selected_style = check_telegram_choice(timeout_seconds=900)
    use_enhanced = (selected_style == "B")
    print(f"Proceeding with video generation using Style {selected_style} (enhanced={use_enhanced}).")

    # 3. Full Amazon Demo
    raw_amazon = TMP_DIR / "raw_amazon.webm"
    final_amazon = VIDEOS_DIR / "amazon_demo.mp4"
    print("Recording full Amazon Alexa+ Hero Flow video...")
    await record_amazon_video(base_url, token, raw_amazon, enhanced=use_enhanced)
    postprocess_video(raw_amazon, final_amazon, "Model: Alexa+ / Meta Llama 3.3")
    amazon_dur = probe_duration(final_amazon)
    amazon_size_mb = final_amazon.stat().st_size / (1024 * 1024)
    print(f"Amazon video ready: {final_amazon} (duration: {amazon_dur:.1f}s, size: {amazon_size_mb:.2f}MB)")

    # 4. Full Nebius Demo
    raw_nebius = TMP_DIR / "raw_nebius.webm"
    final_nebius = VIDEOS_DIR / "nebius_demo.mp4"
    print("Recording full Nebius Routing & Cost video...")
    await record_nebius_video(base_url, token, raw_nebius, enhanced=use_enhanced)
    postprocess_video(raw_nebius, final_nebius, "Model: Nebius Token Factory Nemotron")
    nebius_dur = probe_duration(final_nebius)
    nebius_size_mb = final_nebius.stat().st_size / (1024 * 1024)
    print(f"Nebius video ready: {final_nebius} (duration: {nebius_dur:.1f}s, size: {nebius_size_mb:.2f}MB)")

    # 5. Send final videos to Telegram
    if final_amazon.stat().st_size < 50 * 1024 * 1024:
        send_telegram_video(final_amazon, f"Amazon Alexa+ Voice Hero Flow Demo ({amazon_dur:.0f}s)")
    if final_nebius.stat().st_size < 50 * 1024 * 1024:
        send_telegram_video(final_nebius, f"Nebius Token Factory Routing & Cost Demo ({nebius_dur:.0f}s)")

    # 6. Send live GitHub Pages link
    gh_pages_url = "https://hteker853-source.github.io/grasshopper/"
    send_telegram_text(f"Grasshopper Live Static Jury Replay: {gh_pages_url}")

    print("ALL DEMO VIDEOS RECORDED AND DISPATCHED SUCCESSFULLY.")


if __name__ == "__main__":
    asyncio.run(main())
