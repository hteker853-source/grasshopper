"""Unit checks that do not need a full scenario."""

from __future__ import annotations

import asyncio
from datetime import datetime, timedelta, timezone
from pathlib import Path

import numpy as np
import pytest
from PIL import Image, ImageDraw

from grasshopper.channels.inbound import task_from_channel
from grasshopper.config import assert_not_mainnet, mask_secret, reset_settings
from grasshopper.core.verifier import check_criteria
from grasshopper.providers.factory import build_llm
from grasshopper.providers.llm_mock import MockLLM
from grasshopper.providers.stt_mock import MockSTT
from grasshopper.providers.wallet_mock import WalletLimitError
from grasshopper.queue.scheduler import parse_when


def test_notifier_list_excludes_telegram(ctx):
    names = [getattr(item, "name", "") for item in ctx.notifier.notifiers]
    assert "telegram" not in names
    assert "whatsapp" not in names


def test_channels_share_one_task_shape():
    text = "Check the news headlines and notify me with the top trend."
    tasks = [task_from_channel(text, channel) for channel in ("web", "telegram", "whatsapp", "alexa", "cli")]
    assert len({task.text for task in tasks}) == 1
    assert {task.status.value for task in tasks} == {"queued"}
    assert {task.channel for task in tasks} == {"web", "telegram", "whatsapp", "alexa", "cli"}


def test_schedule_parser():
    now = datetime(2026, 9, 27, 18, 0, tzinfo=timezone.utc)
    relative = parse_when("in 30 seconds check news", now)
    assert relative.scheduled_at == now + timedelta(seconds=30)
    turkish = parse_when("30 saniye sonra haberleri kontrol et", now)
    assert turkish.scheduled_at == now + timedelta(seconds=30)
    daily = parse_when("every day 08:00 read the news", now)
    assert daily.cron == "0 8 * * *"
    assert daily.scheduled_at.hour == 8
    tonight = parse_when("tonight 00:00 follow the news", now)
    assert tonight.scheduled_at.hour == 0
    tomorrow = parse_when("tomorrow 09:30 summarize the report", now)
    assert tomorrow.scheduled_at.day == 28
    assert tomorrow.scheduled_at.hour == 9


def test_criteria_and_mask():
    ok, _ = check_criteria("text:Solar && url:/chat", url="http://x/chat", text="Solar panels", html="", variables={})
    assert ok
    bad, reason = check_criteria("selector:[data-testid=missing]", url="", text="", html="<div></div>", variables={})
    assert not bad and "missing" in reason
    assert mask_secret("super-secret-key") == "****-key"[-8:] or mask_secret("super-secret-key").endswith("key")


def test_mainnet_refused():
    with pytest.raises(RuntimeError):
        assert_not_mainnet("https://api.mainnet-beta.solana.com")


def test_unconfigured_real_provider_falls_back(monkeypatch):
    monkeypatch.setenv("NEBIUS_API_KEY", "")
    monkeypatch.setenv("NEBIUS_BASE_URL", "")
    monkeypatch.setenv("NEBIUS_FAST_MODEL", "")
    reset_settings()
    from grasshopper.config import get_settings

    provider = build_llm("nebius", get_settings(), tier="fast")
    assert isinstance(provider, MockLLM)
    reset_settings()


def test_wallet_limits(ctx):
    wallet = ctx.wallet
    start = wallet.balance()
    with pytest.raises(WalletLimitError):
        wallet.pay(5, "too big")
    assert wallet.balance() == start


def test_stt_sibling_transcript(tmp_path: Path):
    audio = tmp_path / "note.wav"
    audio.write_bytes(b"RIFF")
    (tmp_path / "note.txt").write_text("enable research mode\n", encoding="utf-8")
    assert asyncio.run(MockSTT().transcribe(str(audio))) == "enable research mode"


def test_memory_search(ctx):
    ctx.memory.add("preference", "I like quiet brass pens and linen planners")
    hits = ctx.memory.search("linen planner", k=3)
    assert hits and "linen" in hits[0]["text"]


def test_vision_finds_button(tmp_path: Path):
    from grasshopper.browser.vision import change_percent, detect_regions

    before = tmp_path / "login.png"
    image = Image.new("RGB", (400, 240), (240, 240, 240))
    draw = ImageDraw.Draw(image)
    draw.rectangle((40, 80, 200, 130), outline=(10, 10, 10), width=3)
    draw.rectangle((40, 150, 200, 200), fill=(20, 80, 40))
    image.save(before)
    after = tmp_path / "after.png"
    Image.new("RGB", (400, 240), (20, 20, 80)).save(after)
    regions = detect_regions(before, tmp_path / "annotated.png")
    assert regions
    assert (tmp_path / "annotated.png").exists()
    assert change_percent(before, after) > 10


def test_learned_skill_skips_llm_on_second_run(ctx):
    text = "Describe the quiet brass pen maintenance ritual for a weekend stall"
    first = asyncio.run(_once(ctx, text))
    assert first.plan_source == "llm"
    assert first.llm_calls >= 1
    second = asyncio.run(_once(ctx, text))
    assert second.plan_source == "playbook"
    assert second.llm_calls == 0


async def _once(ctx, text):
    from grasshopper.demo_scenarios import run_scenario

    return await run_scenario(ctx, text, approve=True)


def test_numpy_embed_is_normalized():
    from grasshopper.memory.store import embed

    vector = embed("solar panels on a roof")
    assert vector.shape == (512,)
    assert np.isclose(np.linalg.norm(vector), 1.0)
