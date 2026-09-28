"""Session sandbox + isolated Grasshopper data directory."""

from __future__ import annotations

import os
import tempfile
import threading
import time
from pathlib import Path

import httpx
import pytest
import uvicorn

_TMP = Path(tempfile.mkdtemp(prefix="grasshopper-tests-"))
os.environ["MODE"] = "mock"
os.environ["BROWSER_DRIVER"] = "http"
os.environ["API_TOKEN"] = "test-token"
os.environ["SANDBOX_DELAY_MIN_MS"] = "0"
os.environ["SANDBOX_DELAY_MAX_MS"] = "15"
os.environ["GRASSHOPPER_EMBED_SANDBOX"] = "0"
os.environ["APPROVAL_TIMEOUT_SEC"] = "8"
os.environ["GRASSHOPPER_DATA_DIR"] = str(_TMP)
os.environ["GRASSHOPPER_DB"] = str(_TMP / "grasshopper.db")
os.environ["GRASSHOPPER_RUNS_DIR"] = str(_TMP / "runs")
os.environ["SANDBOX_DB"] = str(_TMP / "sandbox.db")
os.environ["SANDBOX_MEDIA_DIR"] = str(_TMP / "media")
os.environ["WALLET_DAILY_LIMIT_SOL"] = "0.5"
os.environ["WALLET_PER_TX_LIMIT_SOL"] = "0.1"
os.environ["LLM_FAST_PROVIDER"] = "mock"
os.environ["LLM_STRONG_PROVIDER"] = "mock"
os.environ["LLM_VISION_PROVIDER"] = "mock"
os.environ["LLM_REPAIR_PROVIDER"] = "mock"
os.environ["STT_PROVIDER"] = "mock"
os.environ["SEARCH_PROVIDER"] = "mock"
os.environ["WALLET_PROVIDER"] = "mock"
os.environ["ALLOW_BEDROCK"] = "0"
os.environ["REAL_SITE_DELAY_SEC"] = "0"
os.environ["BUDGET_USD_DAILY"] = "0.50"
os.environ["BUDGET_USD_PER_RUN"] = "0.05"

# Assignment, not setdefault: load_dotenv must not revive secrets from .env.
for _secret in (
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
    os.environ[_secret] = ""


@pytest.fixture(scope="session", autouse=True)
def sandbox_url():
    port = 18765
    os.environ["SANDBOX_BASE_URL"] = f"http://127.0.0.1:{port}"
    config = uvicorn.Config("sandbox_web.app:app", host="127.0.0.1", port=port, log_level="warning")
    server = uvicorn.Server(config)
    thread = threading.Thread(target=server.run, daemon=True)
    thread.start()
    deadline = time.time() + 15
    while time.time() < deadline:
        try:
            httpx.get(f"http://127.0.0.1:{port}/health", timeout=0.3)
            break
        except Exception:
            time.sleep(0.1)
    else:
        raise RuntimeError("sandbox did not start")
    from grasshopper.runtime import reset_context

    reset_context()
    yield os.environ["SANDBOX_BASE_URL"]


@pytest.fixture
def ctx(sandbox_url):
    from grasshopper.runtime import get_context

    return get_context()
