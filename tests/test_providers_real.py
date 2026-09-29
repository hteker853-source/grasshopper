"""Real provider clients against local fakes. No public API and no real key."""

from __future__ import annotations

import asyncio
import logging
from pathlib import Path

import boto3
import pytest
from botocore.stub import Stubber

from grasshopper.config import get_settings, reset_settings
from grasshopper.core.router import Router
from grasshopper.db import Database
from grasshopper.providers.base import ProviderError
from grasshopper.providers.factory import build_llm, build_notifier, build_search, build_stt
from grasshopper.providers.llm_mock import MockLLM
from tests.fakes.serve import start_fakes

pytestmark = pytest.mark.filterwarnings("ignore::DeprecationWarning")


def _token() -> str:
    return "87654321:" + ("c" * 32)


@pytest.fixture(scope="module")
def fake_server():
    url, capture = start_fakes()
    capture.requests.clear()
    return url, capture


@pytest.fixture
def fakes(fake_server):
    url, capture = fake_server
    capture.requests.clear()
    capture.fail_chat = False
    capture.fail_search = False
    return url, capture


@pytest.fixture
def configured(monkeypatch):
    def apply(**env):
        for key, value in env.items():
            monkeypatch.setenv(key, value)
        reset_settings()
        return get_settings()

    yield apply
    for key in (
        "LLM_FAST_PROVIDER",
        "LLM_STRONG_PROVIDER",
        "LLM_REPAIR_PROVIDER",
        "STT_PROVIDER",
        "SEARCH_PROVIDER",
    ):
        monkeypatch.setenv(key, "mock")
    for key in (
        "NEBIUS_API_KEY",
        "NEBIUS_BASE_URL",
        "NEBIUS_FAST_MODEL",
        "META_API_KEY",
        "META_BASE_URL",
        "META_MODEL",
        "AZURE_OPENAI_API_KEY",
        "AZURE_OPENAI_ENDPOINT",
        "AZURE_OPENAI_DEPLOYMENT",
        "OPENAI_COMPAT_API_KEY",
        "OPENAI_COMPAT_BASE_URL",
        "OPENAI_COMPAT_MODEL",
        "OLLAMA_BASE_URL",
        "GEMMA_MODEL",
        "TAVILY_API_KEY",
        "TAVILY_BASE_URL",
        "ASSEMBLYAI_API_KEY",
        "ASSEMBLYAI_BASE_URL",
        "AZURE_SPEECH_KEY",
        "AZURE_SPEECH_REGION",
        "AZURE_SPEECH_ENDPOINT",
        "TELEGRAM_BOT_TOKEN",
        "TELEGRAM_ALLOWED_USER_ID",
        "TELEGRAM_API_BASE",
        "WHATSAPP_TOKEN",
        "WHATSAPP_PHONE_NUMBER_ID",
        "WHATSAPP_TO",
        "WHATSAPP_API_BASE",
        "AWS_REGION",
        "AWS_ACCESS_KEY_ID",
        "AWS_SECRET_ACCESS_KEY",
        "BEDROCK_MODEL_ID",
        "ALLOW_BEDROCK",
    ):
        monkeypatch.setenv(key, "")
    reset_settings()


def test_nebius_chat_completions_headers_and_body(fakes, configured):
    base, capture = fakes
    settings = configured(
        LLM_FAST_PROVIDER="nebius",
        NEBIUS_API_KEY="fake-nebius-key",
        NEBIUS_BASE_URL=base,
        NEBIUS_FAST_MODEL="fake-fast",
    )
    provider = build_llm(settings.llm_fast_provider, settings, tier="fast")
    assert provider.name == "nebius"
    assert asyncio.run(provider.complete("say hi", system="be brief")) == "from-fake-llm"
    sent = capture.requests[-1]
    assert sent["path"] == "/chat/completions"
    assert sent["headers"]["authorization"] == "Bearer fake-nebius-key"
    assert sent["body"]["model"] == "fake-fast"
    assert sent["body"]["messages"][0] == {"role": "system", "content": "be brief"}
    assert sent["body"]["messages"][1] == {"role": "user", "content": "say hi"}


def test_meta_and_openai_compat_use_the_same_chat_path(fakes, configured):
    base, capture = fakes
    meta = configured(
        LLM_STRONG_PROVIDER="meta",
        META_API_KEY="fake-meta-key",
        META_BASE_URL=base,
        META_MODEL="fake-meta",
    )
    provider = build_llm(meta.llm_strong_provider, meta, tier="strong")
    assert asyncio.run(provider.complete("meta ping")) == "from-fake-llm"
    assert capture.requests[-1]["headers"]["authorization"] == "Bearer fake-meta-key"
    assert capture.requests[-1]["body"]["model"] == "fake-meta"
    compat = configured(
        LLM_FAST_PROVIDER="openai_compat",
        OPENAI_COMPAT_API_KEY="fake-compat-key",
        OPENAI_COMPAT_BASE_URL=base,
        OPENAI_COMPAT_MODEL="fake-compat",
    )
    provider = build_llm(compat.llm_fast_provider, compat, tier="fast")
    assert asyncio.run(provider.complete("compat ping")) == "from-fake-llm"
    assert capture.requests[-1]["body"]["model"] == "fake-compat"


def test_azure_openai_sends_api_key_header_not_bearer(fakes, configured):
    base, capture = fakes
    settings = configured(
        LLM_STRONG_PROVIDER="azure",
        AZURE_OPENAI_API_KEY="fake-azure-key",
        AZURE_OPENAI_ENDPOINT=base,
        AZURE_OPENAI_DEPLOYMENT="gpt-dep",
    )
    provider = build_llm(settings.llm_strong_provider, settings, tier="strong")
    assert asyncio.run(provider.complete("azure ping")) == "azure:gpt-dep"
    sent = capture.requests[-1]
    assert sent["path"] == "/openai/deployments/gpt-dep/chat/completions"
    assert "api-version=2024-10-21" in sent["query"]
    assert sent["headers"]["api-key"] == "fake-azure-key"
    assert "authorization" not in sent["headers"]
    assert "model" not in sent["body"]
    assert sent["body"]["messages"][0]["content"] == "azure ping"


def test_ollama_generate_body(fakes, configured):
    base, capture = fakes
    settings = configured(
        LLM_REPAIR_PROVIDER="ollama",
        OLLAMA_BASE_URL=base,
        GEMMA_MODEL="gemma-test",
    )
    provider = build_llm(settings.llm_repair_provider, settings, tier="repair")
    assert asyncio.run(provider.complete("fix it", system="repair")) == "from-fake-ollama"
    sent = capture.requests[-1]
    assert sent["path"] == "/api/generate"
    assert sent["body"]["model"] == "gemma-test"
    assert sent["body"]["stream"] is False
    assert sent["body"]["prompt"].startswith("repair")


def test_chat_error_falls_back_to_mock_with_a_warning(fakes, configured, tmp_path, caplog):
    base, capture = fakes
    settings = configured(
        LLM_FAST_PROVIDER="nebius",
        NEBIUS_API_KEY="fake-nebius-key",
        NEBIUS_BASE_URL=base,
        NEBIUS_FAST_MODEL="fake-fast",
    )
    capture.fail_chat = True
    router = Router(settings, Database(tmp_path / "calls.db"))
    with caplog.at_level(logging.WARNING, logger="grasshopper.router"):
        response = asyncio.run(router.complete("fast", "hello there"))
    assert response.provider == "mock"
    assert "noted" in response.text
    assert "Falling back to mock" in caplog.text
    assert capture.requests[-1]["path"] == "/chat/completions"


def test_missing_nebius_key_logs_mock_fallback(configured, caplog):
    settings = configured(LLM_FAST_PROVIDER="nebius", NEBIUS_API_KEY="", NEBIUS_BASE_URL="", NEBIUS_FAST_MODEL="")
    with caplog.at_level(logging.WARNING, logger="grasshopper.providers"):
        provider = build_llm(settings.llm_fast_provider, settings, tier="fast")
    assert isinstance(provider, MockLLM)
    assert "not active" in caplog.text
    assert "Falling back to mock" in caplog.text


def test_tavily_search_body_and_http_error(fakes, configured):
    base, capture = fakes
    settings = configured(SEARCH_PROVIDER="tavily", TAVILY_API_KEY="fake-tavily-key", TAVILY_BASE_URL=base)
    search = build_search(settings)
    found = asyncio.run(search.search("solar panels", max_results=2))
    assert found == [{"title": "Solar", "url": "https://example.test/solar", "snippet": "panels"}]
    sent = capture.requests[-1]
    assert sent["path"] == "/search"
    assert sent["body"] == {"api_key": "fake-tavily-key", "query": "solar panels", "max_results": 2}
    capture.fail_search = True
    with pytest.raises(ProviderError) as raised:
        asyncio.run(search.search("solar panels"))
    assert "502" in str(raised.value)


def test_assemblyai_upload_and_transcript(fakes, configured, tmp_path):
    base, capture = fakes
    audio = tmp_path / "note.wav"
    audio.write_bytes(b"RIFF-fake-audio")
    settings = configured(STT_PROVIDER="assemblyai", ASSEMBLYAI_API_KEY="fake-assembly-key", ASSEMBLYAI_BASE_URL=base)
    stt = build_stt(settings)
    assert asyncio.run(stt.transcribe(str(audio))) == "solar panels on the roof"
    paths = capture.paths()
    assert paths == ["/v2/upload", "/v2/transcript", "/v2/transcript/tr_1"]
    assert capture.requests[0]["headers"]["authorization"] == "fake-assembly-key"
    assert capture.requests[0]["body"]["bytes"] == len(b"RIFF-fake-audio")
    assert capture.requests[1]["body"]["audio_url"] == "http://fake.local/audio"


def test_azure_speech_posts_the_audio_and_key(fakes, configured, tmp_path):
    base, capture = fakes
    audio = tmp_path / "note.wav"
    audio.write_bytes(b"RIFF")
    settings = configured(
        STT_PROVIDER="azure",
        AZURE_SPEECH_KEY="fake-speech-key",
        AZURE_SPEECH_REGION="eastus",
        AZURE_SPEECH_ENDPOINT=base + "/speech",
    )
    stt = build_stt(settings)
    assert asyncio.run(stt.transcribe(str(audio))) == "enable research mode"
    sent = capture.requests[-1]
    assert sent["path"] == "/speech"
    assert sent["headers"]["ocp-apim-subscription-key"] == "fake-speech-key"
    assert sent["body"]["bytes"] == 4


def test_telegram_send_message_uses_the_allowed_chat(fakes, configured):
    base, capture = fakes
    token = _token()
    settings = configured(
        TELEGRAM_BOT_TOKEN=token,
        TELEGRAM_ALLOWED_USER_ID="42",
        TELEGRAM_API_BASE=base,
    )
    notifier = build_notifier(settings)
    telegram = next(item for item in notifier.notifiers if item.name == "telegram")
    asyncio.run(telegram.notify("hello report", kind="done"))
    sent = capture.requests[-1]
    assert sent["path"].endswith("/sendMessage")
    assert sent["path"].startswith("/bot")
    assert sent["body"]["token_len"] == len(token)
    assert sent["body"]["json"]["chat_id"] == "42"
    assert sent["body"]["json"]["text"] == "hello report"


def test_whatsapp_message_shape(fakes, configured):
    base, capture = fakes
    settings = configured(
        WHATSAPP_TOKEN="fake-wa-key",
        WHATSAPP_PHONE_NUMBER_ID="555",
        WHATSAPP_TO="15550001111",
        WHATSAPP_API_BASE=base,
    )
    notifier = build_notifier(settings)
    whatsapp = next(item for item in notifier.notifiers if item.name == "whatsapp")
    asyncio.run(whatsapp.notify("ping shop", kind="done"))
    sent = capture.requests[-1]
    assert sent["path"] == "/v20.0/555/messages"
    assert sent["headers"]["authorization"] == "Bearer fake-wa-key"
    assert sent["body"]["messaging_product"] == "whatsapp"
    assert sent["body"]["to"] == "15550001111"
    assert sent["body"]["text"]["body"] == "ping shop"


def test_bedrock_converse_is_stubbed(configured, monkeypatch):
    seen = {}

    def wrapped(service_name, **kwargs):
        client = _real_client(service_name, **kwargs)
        if service_name == "bedrock-runtime":
            stub = Stubber(client)
            stub.add_response(
                "converse",
                {
                    "output": {"message": {"role": "assistant", "content": [{"text": "from-bedrock"}]}},
                    "stopReason": "end_turn",
                    "usage": {"inputTokens": 3, "outputTokens": 2, "totalTokens": 5},
                    "metrics": {"latencyMs": 8},
                },
                expected_params={
                    "modelId": "amazon.nova-lite-v1:0",
                    "messages": [{"role": "user", "content": [{"text": "ping"}]}],
                    "system": [{"text": "be brief"}],
                },
            )
            stub.activate()
            seen["stub"] = stub
            seen["region"] = kwargs.get("region_name")
            seen["access"] = kwargs.get("aws_access_key_id")
        return client

    monkeypatch.setattr(boto3, "client", wrapped)
    blocked = configured(
        LLM_STRONG_PROVIDER="bedrock",
        AWS_REGION="us-east-1",
        AWS_ACCESS_KEY_ID="test-access",
        AWS_SECRET_ACCESS_KEY="test-secret",
        BEDROCK_MODEL_ID="amazon.nova-lite-v1:0",
        ALLOW_BEDROCK="0",
    )
    assert build_llm(blocked.llm_strong_provider, blocked, tier="strong").name == "mock"
    settings = configured(
        LLM_STRONG_PROVIDER="bedrock",
        AWS_REGION="us-east-1",
        AWS_ACCESS_KEY_ID="test-access",
        AWS_SECRET_ACCESS_KEY="test-secret",
        BEDROCK_MODEL_ID="amazon.nova-lite-v1:0",
        ALLOW_BEDROCK="1",
    )
    provider = build_llm(settings.llm_strong_provider, settings, tier="strong")
    assert asyncio.run(provider.complete("ping", system="be brief")) == "from-bedrock"
    seen["stub"].assert_no_pending_responses()
    assert seen["region"] == "us-east-1"
    assert seen["access"] == "test-access"


def _real_client(service_name, **kwargs):
    import botocore.session

    session = botocore.session.get_session()
    return session.create_client(service_name, **kwargs)


def test_provider_report_lists_what_this_module_proved():
    text = Path("docs/PROVIDERS_VERIFIED.md").read_text(encoding="utf-8")
    proved = (
        "nebius",
        "meta",
        "azure-openai",
        "openai-compat",
        "ollama",
        "bedrock",
        "tavily",
        "assemblyai",
        "azure-speech",
        "telegram",
        "whatsapp",
    )
    for name in proved:
        assert f"| {name} | real path tested |" in text
    assert "| solana-devnet | only key missing |" in text
