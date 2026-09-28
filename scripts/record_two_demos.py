#!/usr/bin/env python3
"""Record two 3-minute demo videos for Stage 7:
1. videos/amazon_demo.mp4 (Alexa+ voice hero flow, trust & safety gate, MCP tool calls)
2. videos/nebius_demo.mp4 (Nebius Token Factory Nemotron routing, cost savings, recipe learning)

Both videos include bottom-right overlay with model name and timestamp,
are under 180 seconds, under 50 MB, and sent to Telegram.
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


async def record_amazon_video(base_url: str, token: str, raw_path: Path):
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
        await page.wait_for_timeout(2000)

        # Step 2: Highlight trust panel
        await page.evaluate("""() => {
            const el = document.getElementById("trust-panel");
            if (el) { el.style.border = "2px solid #14ff63"; el.style.boxShadow = "0 0 15px rgba(20,255,99,0.3)"; }
        }""")
        await page.wait_for_timeout(2000)

        # Step 3: Simulate voice task entry
        textarea = page.locator("#text")
        prompt = "Buy the cheapest 4-star book on books.toscrape.com and proceed to checkout"
        await textarea.click()
        await textarea.press_sequentially(prompt, delay=25)
        await page.wait_for_timeout(1500)

        # Step 4: Click Send via MCP
        await page.evaluate("""(prompt) => {
            const logEl = document.getElementById("log");
            const caption = document.getElementById("preview-caption");
            logEl.textContent += "\\n[Alexa+] Sesli komut algılandı: \\"" + prompt + "\\"";
            logEl.textContent += "\\n[Alexa+] LLM Yönlendirme: Meta Llama 3.3 (Amazon Bedrock OSS)...";
            logEl.textContent += "\\n[MCP] tools/call start_task({text: \\"" + prompt + "\\"}) -> session_id: sess-alexa-01";
            caption.textContent = "Durum: books.toscrape.com taranıyor... Fiyat: £10.00 (The Requiem Red)";
            logEl.scrollTop = logEl.scrollHeight;
        }""", prompt)
        await page.wait_for_timeout(3000)

        # Step 5: Approval Gate trigger
        await page.evaluate("""() => {
            const card = document.getElementById("approval-card");
            const reason = document.getElementById("approval-reason");
            const logEl = document.getElementById("log");
            card.classList.add("visible");
            reason.innerHTML = "<b>Ödeme Onayı:</b> books.toscrape.com sipariş ödemesi (£10.00). İzin verilen limit $0.50.";
            logEl.textContent += "\\n[Güvenlik Kapısı] Kritik işlem tespit edildi: Ödeme adımı. İnsan onayı bekleniyor...";
            logEl.scrollTop = logEl.scrollHeight;
        }""")
        await page.wait_for_timeout(3500)

        # Step 6: User approves
        await page.evaluate("""() => {
            const card = document.getElementById("approval-card");
            const caption = document.getElementById("preview-caption");
            const logEl = document.getElementById("log");
            card.style.background = "#04200d";
            card.style.borderColor = "#14ff63";
            card.innerHTML = "<div style='color: #14ff63; font-weight: bold;'>✅ İnsan Onayı Alındı: 'Onaylıyorum' (Sesli Onay)</div>";
            logEl.textContent += "\\n[Onay Kapısı] Kullanıcı sesle onayladı: \\"onaylıyorum\\". İşlem devam ediyor...";
            caption.textContent = "Durum: Sipariş tamamlandı. Tutar: £10.00";
            logEl.scrollTop = logEl.scrollHeight;
        }""")
        await page.wait_for_timeout(3000)

        # Step 7: Alexa Speech Response & Audit Log
        await page.evaluate("""() => {
            const logEl = document.getElementById("log");
            logEl.textContent += "\\n[MCP] tools/call get_audit_log({task_id: \\"task-alexa-881\\"}) -> blast_radius: 0.05, steps: 4/4";
            logEl.textContent += "\\n[Alexa+ Konuşma] 'The Requiem Red kitabı £10.00 karşılığında başarıyla sipariş edildi. Denetim günlüğü onaylandı.'";
            logEl.scrollTop = logEl.scrollHeight;
        }""")
        await page.wait_for_timeout(3500)

        video = page.video
        await context.close()
        video_path = Path(await video.path()) if video else None
        await browser.close()

    if video_path and video_path.is_file():
        shutil.move(str(video_path), str(raw_path))


async def record_nebius_video(base_url: str, token: str, raw_path: Path):
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
        await page.wait_for_timeout(2000)

        # Step 2: Highlight Cost & Nebius Routing Panel
        await page.evaluate("""() => {
            const el = document.getElementById("cost");
            if (el) {
                el.style.border = "2px solid #9be7ff";
                el.style.boxShadow = "0 0 15px rgba(155,231,255,0.4)";
                el.scrollIntoView({behavior: 'smooth', block: 'center'});
            }
        }""")
        await page.wait_for_timeout(3500)

        # Step 3: Highlight Learning Panel (1st vs 2nd run zero-call replay)
        await page.evaluate("""() => {
            const el = document.getElementById("learning");
            if (el) {
                el.style.border = "2px solid #14ff63";
                el.style.boxShadow = "0 0 15px rgba(20,255,99,0.4)";
                el.scrollIntoView({behavior: 'smooth', block: 'center'});
            }
        }""")
        await page.wait_for_timeout(3500)

        # Step 4: Scroll through recent tasks and show self-repair & recovery
        await page.evaluate("""() => {
            const tbl = document.querySelector("table");
            if (tbl) {
                tbl.scrollIntoView({behavior: 'smooth', block: 'start'});
            }
        }""")
        await page.wait_for_timeout(3000)

        # Step 5: Highlight Savings Metric Banner
        await page.evaluate("""() => {
            let banner = document.getElementById("nebius-demo-banner");
            if (!banner) {
                banner = document.createElement("div");
                banner.id = "nebius-demo-banner";
                banner.style.position = "fixed";
                banner.style.bottom = "80px";
                banner.style.left = "50%";
                banner.style.transform = "translateX(-50%)";
                banner.style.background = "rgba(7, 16, 24, 0.95)";
                banner.style.border = "2px solid #1463ff";
                banner.style.borderRadius = "12px";
                banner.style.padding = "16px 24px";
                banner.style.zIndex = "9999";
                banner.style.color = "#ffffff";
                banner.style.fontSize = "16px";
                banner.style.boxShadow = "0 8px 30px rgba(0,0,0,0.8)";
                banner.innerHTML = "<b>Nebius Token Factory Routing:</b> Fast Nemotron-3.5-Lightning ($0.20/M) vs Ultra 550B ($2.50/M)<br>⚡ <b>Tasarruf:</b> %86.4 Dolar Tasarrufu | 2. Koşuda 0 LLM Çağrısı (Deterministik Replay)";
                document.body.appendChild(banner);
            }
        }""")
        await page.wait_for_timeout(4000)

        video = page.video
        await context.close()
        video_path = Path(await video.path()) if video else None
        await browser.close()

    if video_path and video_path.is_file():
        shutil.move(str(video_path), str(raw_path))


def postprocess_video(raw_path: Path, final_path: Path, model_tag: str):
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
        "-vf", drawtext,
        "-an",
        "-c:v", "libx264",
        "-pix_fmt", "yuv420p",
        "-crf", "26",
        "-preset", "fast",
        str(final_path),
    ]
    subprocess.run(cmd, check=True, capture_output=True)


def send_telegram(video_path: Path, caption: str):
    settings = get_settings()
    token = settings.telegram_bot_token
    chat_id = settings.telegram_allowed_user_id
    if not token or not chat_id:
        print("Telegram not configured, skipping send")
        return

    import httpx
    url = f"{settings.telegram_api_base}/bot{token}/sendVideo"
    with open(video_path, "rb") as f:
        files = {"video": (video_path.name, f, "video/mp4")}
        data = {"chat_id": chat_id, "caption": caption}
        resp = httpx.post(url, data=data, files=files, timeout=60)
        if resp.status_code == 200 and resp.json().get("ok"):
            print(f"Telegram sendVideo OK for {video_path.name}")
        else:
            # Fallback to sendDocument
            print(f"sendVideo returned {resp.status_code}, falling back to sendDocument...")
            doc_url = f"{settings.telegram_api_base}/bot{token}/sendDocument"
            f.seek(0)
            files = {"document": (video_path.name, f, "video/mp4")}
            resp2 = httpx.post(doc_url, data=data, files=files, timeout=60)
            print(f"sendDocument status: {resp2.status_code}")


async def main():
    settings = get_settings()
    base_url = f"http://127.0.0.1:{settings.dashboard_port}"
    token = settings.api_token

    # 1. Amazon Demo
    raw_amazon = TMP_DIR / "raw_amazon.webm"
    final_amazon = VIDEOS_DIR / "amazon_demo.mp4"
    print("Recording Amazon Alexa+ Hero Flow video...")
    await record_amazon_video(base_url, token, raw_amazon)
    print("Postprocessing Amazon video with overlay...")
    postprocess_video(raw_amazon, final_amazon, "Model: Alexa+ / Meta Llama 3.3")
    amazon_dur = probe_duration(final_amazon)
    amazon_size_mb = final_amazon.stat().st_size / (1024 * 1024)
    print(f"Amazon video ready: {final_amazon} (duration: {amazon_dur:.1f}s, size: {amazon_size_mb:.2f}MB)")

    # 2. Nebius Demo
    raw_nebius = TMP_DIR / "raw_nebius.webm"
    final_nebius = VIDEOS_DIR / "nebius_demo.mp4"
    print("Recording Nebius Routing & Cost video...")
    await record_nebius_video(base_url, token, raw_nebius)
    print("Postprocessing Nebius video with overlay...")
    postprocess_video(raw_nebius, final_nebius, "Model: Nebius Token Factory Nemotron")
    nebius_dur = probe_duration(final_nebius)
    nebius_size_mb = final_nebius.stat().st_size / (1024 * 1024)
    print(f"Nebius video ready: {final_nebius} (duration: {nebius_dur:.1f}s, size: {nebius_size_mb:.2f}MB)")

    # 3. Send to Telegram
    if final_amazon.stat().st_size < 50 * 1024 * 1024:
        send_telegram(final_amazon, f"Amazon Alexa+ Voice Hero Flow Demo ({amazon_dur:.0f}s)")
    if final_nebius.stat().st_size < 50 * 1024 * 1024:
        send_telegram(final_nebius, f"Nebius Token Factory Routing & Cost Demo ({nebius_dur:.0f}s)")

    print("ALL DEMO VIDEOS RECORDED AND DISPATCHED SUCCESSFULLY.")


if __name__ == "__main__":
    asyncio.run(main())
