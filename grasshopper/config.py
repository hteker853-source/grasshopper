"""Environment, safety checks, and the single provider factory."""

from __future__ import annotations

import logging
import os
import re
from pathlib import Path

from pydantic import BaseModel, Field

ROOT = Path(__file__).resolve().parents[1]
log = logging.getLogger("grasshopper.config")

_SECRET_PATTERNS = (
    re.compile(r"sk-[A-Za-z0-9]{16,}"),
    re.compile(r"AKIA[0-9A-Z]{16}"),
    re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----"),
    re.compile(r"\b[0-9a-fA-F]{64,}\b"),
)
_SKIP_DIRS = {
    ".venv", "venv", "node_modules", ".git", "runs", "profiles", "patches",
    "__pycache__", "dist", ".output", "data", "screenshots", "artifacts",
    "src", "public", "server", "migrations", "scripts",
}


def load_dotenv(path: Path | None = None) -> None:
    """Load KEY=VALUE lines. Existing environment variables win."""
    env_path = path or (ROOT / ".env")
    if not env_path.exists():
        return
    for raw in env_path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        os.environ.setdefault(key, value)


def mask_secret(value: str | None) -> str:
    if not value:
        return ""
    if len(value) <= 4:
        return "****"
    return "****" + value[-4:]


def scan_repo_for_secrets(root: Path | None = None) -> list[str]:
    """Return human-readable hits. Warn only — never print the secret itself."""
    base = root or ROOT
    hits: list[str] = []
    for dirpath, dirnames, filenames in os.walk(base):
        dirnames[:] = [d for d in dirnames if d not in _SKIP_DIRS and not d.startswith(".git")]
        for name in filenames:
            if name.endswith((".png", ".jpg", ".jpeg", ".webp", ".mp4", ".db", ".pyc", ".lock")):
                continue
            if name in {"package-lock.json", "yarn.lock"}:
                continue
            path = Path(dirpath) / name
            try:
                text = path.read_text(encoding="utf-8", errors="ignore")
            except OSError:
                continue
            for pattern in _SECRET_PATTERNS:
                if pattern.search(text):
                    rel = path.relative_to(base)
                    hits.append(f"{rel} matches {pattern.pattern}")
                    break
    return hits


class Settings(BaseModel):
    mode: str = "mock"
    api_token: str = "change-me"
    dashboard_host: str = "0.0.0.0"
    dashboard_port: int = 8080
    sandbox_port: int = 8090
    sandbox_base_url: str = ""
    max_concurrent_browsers: int = 2
    max_concurrent_tasks: int = 2
    browser_driver: str = "auto"
    llm_fast_provider: str = "mock"
    llm_strong_provider: str = "mock"
    llm_vision_provider: str = "mock"
    llm_repair_provider: str = "mock"
    council_providers: list[str] = Field(default_factory=lambda: ["mock_a", "mock_b", "mock_c"])
    council_voters: list[str] = Field(
        default_factory=lambda: ["mock_a", "mock_b", "mock_c", "mock_d", "mock_e", "mock_f"]
    )
    nebius_api_key: str = ""
    nebius_base_url: str = ""
    nebius_fast_model: str = ""
    aws_region: str = ""
    aws_access_key_id: str = ""
    aws_secret_access_key: str = ""
    bedrock_model_id: str = ""
    azure_openai_endpoint: str = ""
    azure_openai_api_key: str = ""
    azure_openai_deployment: str = ""
    azure_speech_key: str = ""
    azure_speech_region: str = ""
    azure_speech_endpoint: str = ""
    meta_api_key: str = ""
    meta_base_url: str = ""
    meta_model: str = ""
    openai_compat_api_key: str = ""
    openai_compat_base_url: str = ""
    openai_compat_model: str = ""
    ollama_base_url: str = "http://localhost:11434"
    gemma_model: str = ""
    stt_provider: str = "mock"
    assemblyai_api_key: str = ""
    assemblyai_base_url: str = "https://api.assemblyai.com"
    search_provider: str = "mock"
    tavily_api_key: str = ""
    tavily_base_url: str = "https://api.tavily.com"
    wallet_provider: str = "mock"
    solana_rpc_url: str = "https://api.devnet.solana.com"
    wallet_keypair_path: str = ""
    wallet_daily_limit_sol: float = 0.5
    wallet_per_tx_limit_sol: float = 0.1
    telegram_bot_token: str = ""
    telegram_allowed_user_id: str = ""
    telegram_api_base: str = "https://api.telegram.org"
    whatsapp_token: str = ""
    whatsapp_phone_number_id: str = ""
    whatsapp_verify_token: str = ""
    whatsapp_to: str = ""
    whatsapp_api_base: str = "https://graph.facebook.com"
    shop_email: str = "demo@grasshopper.local"
    shop_password: str = "demo-password"
    ai_alpha_email: str = "demo@grasshopper.local"
    ai_alpha_password: str = "demo-password"
    ai_beta_email: str = "demo@grasshopper.local"
    ai_beta_password: str = "demo-password"
    approval_timeout_sec: int = 1800
    mcp_bearer_token: str = ""
    mcp_allowed_origins: str = ""
    budget_usd_daily: float = 0.50
    budget_usd_per_run: float = 0.05
    allow_bedrock: bool = False
    real_site_delay_sec: float = 1.0
    real_sites_allowlist: str = ""
    embed_sandbox: bool = True
    sandbox_delay_min_ms: int = 100
    sandbox_delay_max_ms: int = 800
    data_dir: Path = Field(default_factory=lambda: ROOT / "data")
    runs_dir: Path = Field(default_factory=lambda: ROOT / "runs")
    playbook_dir: Path = Field(default_factory=lambda: ROOT / "playbooks")
    patches_dir: Path = Field(default_factory=lambda: ROOT / "patches")
    profiles_dir: Path = Field(default_factory=lambda: ROOT / "profiles")
    db_path: Path = Field(default_factory=lambda: ROOT / "data" / "grasshopper.db")

    @property
    def sandbox_url(self) -> str:
        if self.sandbox_base_url:
            return self.sandbox_base_url.rstrip("/")
        if self.embed_sandbox:
            return f"http://127.0.0.1:{self.sandbox_port}"
        return f"http://127.0.0.1:{self.dashboard_port}"

    def secret_map(self) -> dict[str, str]:
        return {
            "shop_email": self.shop_email,
            "shop_password": self.shop_password,
            "ai_alpha_email": self.ai_alpha_email,
            "ai_alpha_password": self.ai_alpha_password,
            "ai_beta_email": self.ai_beta_email,
            "ai_beta_password": self.ai_beta_password,
        }


def _csv(value: str) -> list[str]:
    return [part.strip() for part in value.split(",") if part.strip()]


def _flag(name: str, default: str = "0") -> bool:
    return os.environ.get(name, default).strip().lower() in {"1", "true", "yes", "on"}


def load_settings() -> Settings:
    load_dotenv()
    raw_data = (os.environ.get("GRASSHOPPER_DATA_DIR") or "").strip()
    data_dir = Path(raw_data) if raw_data else (ROOT / "data")
    raw_runs = (os.environ.get("GRASSHOPPER_RUNS_DIR") or "").strip()
    runs_dir = Path(raw_runs) if raw_runs else (ROOT / "runs")
    raw_db = (os.environ.get("GRASSHOPPER_DB") or "").strip()
    db_path = Path(raw_db) if raw_db else (data_dir / "grasshopper.db")
    patches = data_dir / "patches" if raw_data else ROOT / "patches"
    if (os.environ.get("GRASSHOPPER_PATCHES") or "").strip():
        patches = Path(os.environ["GRASSHOPPER_PATCHES"].strip())
    settings = Settings(
        mode=os.environ.get("MODE", "mock"),
        api_token=os.environ.get("API_TOKEN", "change-me"),
        dashboard_port=int(os.environ.get("DASHBOARD_PORT", "8080")),
        sandbox_port=int(os.environ.get("SANDBOX_PORT", "8090")),
        sandbox_base_url=os.environ.get("SANDBOX_BASE_URL", ""),
        max_concurrent_browsers=int(os.environ.get("MAX_CONCURRENT_BROWSERS", "2")),
        max_concurrent_tasks=int(os.environ.get("MAX_CONCURRENT_TASKS", "2")),
        browser_driver=os.environ.get("BROWSER_DRIVER", "auto"),
        llm_fast_provider=os.environ.get("LLM_FAST_PROVIDER", "mock"),
        llm_strong_provider=os.environ.get("LLM_STRONG_PROVIDER", "mock"),
        llm_vision_provider=os.environ.get("LLM_VISION_PROVIDER", "mock"),
        llm_repair_provider=os.environ.get("LLM_REPAIR_PROVIDER", "mock"),
        council_providers=_csv(os.environ.get("COUNCIL_PROVIDERS", "mock_a,mock_b,mock_c")),
        council_voters=_csv(os.environ.get("COUNCIL_VOTERS", "mock_a,mock_b,mock_c,mock_d,mock_e,mock_f")),
        nebius_api_key=os.environ.get("NEBIUS_API_KEY", ""),
        nebius_base_url=os.environ.get("NEBIUS_BASE_URL", ""),
        nebius_fast_model=os.environ.get("NEBIUS_FAST_MODEL", ""),
        aws_region=os.environ.get("AWS_REGION", ""),
        aws_access_key_id=os.environ.get("AWS_ACCESS_KEY_ID", ""),
        aws_secret_access_key=os.environ.get("AWS_SECRET_ACCESS_KEY", ""),
        bedrock_model_id=os.environ.get("BEDROCK_MODEL_ID", ""),
        azure_openai_endpoint=os.environ.get("AZURE_OPENAI_ENDPOINT", ""),
        azure_openai_api_key=os.environ.get("AZURE_OPENAI_API_KEY", ""),
        azure_openai_deployment=os.environ.get("AZURE_OPENAI_DEPLOYMENT", ""),
        azure_speech_key=os.environ.get("AZURE_SPEECH_KEY", ""),
        azure_speech_region=os.environ.get("AZURE_SPEECH_REGION", ""),
        azure_speech_endpoint=os.environ.get("AZURE_SPEECH_ENDPOINT", ""),
        meta_api_key=os.environ.get("META_API_KEY", ""),
        meta_base_url=os.environ.get("META_BASE_URL", ""),
        meta_model=os.environ.get("META_MODEL", ""),
        openai_compat_api_key=os.environ.get("OPENAI_COMPAT_API_KEY", ""),
        openai_compat_base_url=os.environ.get("OPENAI_COMPAT_BASE_URL", ""),
        openai_compat_model=os.environ.get("OPENAI_COMPAT_MODEL", ""),
        ollama_base_url=os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434"),
        gemma_model=os.environ.get("GEMMA_MODEL", ""),
        stt_provider=os.environ.get("STT_PROVIDER", "mock"),
        assemblyai_api_key=os.environ.get("ASSEMBLYAI_API_KEY", ""),
        assemblyai_base_url=os.environ.get("ASSEMBLYAI_BASE_URL") or "https://api.assemblyai.com",
        search_provider=os.environ.get("SEARCH_PROVIDER", "mock"),
        tavily_api_key=os.environ.get("TAVILY_API_KEY", ""),
        tavily_base_url=os.environ.get("TAVILY_BASE_URL") or "https://api.tavily.com",
        wallet_provider=os.environ.get("WALLET_PROVIDER", "mock"),
        solana_rpc_url=os.environ.get("SOLANA_RPC_URL", "https://api.devnet.solana.com"),
        wallet_keypair_path=os.environ.get("WALLET_KEYPAIR_PATH", ""),
        wallet_daily_limit_sol=float(os.environ.get("WALLET_DAILY_LIMIT_SOL", "0.5")),
        wallet_per_tx_limit_sol=float(os.environ.get("WALLET_PER_TX_LIMIT_SOL", "0.1")),
        telegram_bot_token=os.environ.get("TELEGRAM_BOT_TOKEN", ""),
        telegram_allowed_user_id=os.environ.get("TELEGRAM_ALLOWED_USER_ID", ""),
        telegram_api_base=os.environ.get("TELEGRAM_API_BASE") or "https://api.telegram.org",
        whatsapp_token=os.environ.get("WHATSAPP_TOKEN", ""),
        whatsapp_phone_number_id=os.environ.get("WHATSAPP_PHONE_NUMBER_ID", ""),
        whatsapp_verify_token=os.environ.get("WHATSAPP_VERIFY_TOKEN", ""),
        whatsapp_to=os.environ.get("WHATSAPP_TO", ""),
        whatsapp_api_base=os.environ.get("WHATSAPP_API_BASE") or "https://graph.facebook.com",
        shop_email=os.environ.get("SHOP_EMAIL", "demo@grasshopper.local"),
        shop_password=os.environ.get("SHOP_PASSWORD", "demo-password"),
        ai_alpha_email=os.environ.get("AI_ALPHA_EMAIL", "demo@grasshopper.local"),
        ai_alpha_password=os.environ.get("AI_ALPHA_PASSWORD", "demo-password"),
        ai_beta_email=os.environ.get("AI_BETA_EMAIL", "demo@grasshopper.local"),
        ai_beta_password=os.environ.get("AI_BETA_PASSWORD", "demo-password"),
        approval_timeout_sec=int(os.environ.get("APPROVAL_TIMEOUT_SEC", "1800")),
        mcp_bearer_token=os.environ.get("MCP_BEARER_TOKEN", ""),
        mcp_allowed_origins=os.environ.get("MCP_ALLOWED_ORIGINS", ""),
        budget_usd_daily=float(os.environ.get("BUDGET_USD_DAILY", "0.50")),
        budget_usd_per_run=float(os.environ.get("BUDGET_USD_PER_RUN", "0.05")),
        allow_bedrock=_flag("ALLOW_BEDROCK", "0"),
        real_site_delay_sec=float(os.environ.get("REAL_SITE_DELAY_SEC", "1")),
        real_sites_allowlist=os.environ.get("REAL_SITES_ALLOWLIST", ""),
        embed_sandbox=_flag("GRASSHOPPER_EMBED_SANDBOX", "1"),
        sandbox_delay_min_ms=int(os.environ.get("SANDBOX_DELAY_MIN_MS", "100")),
        sandbox_delay_max_ms=int(os.environ.get("SANDBOX_DELAY_MAX_MS", "800")),
        data_dir=data_dir,
        runs_dir=runs_dir,
        db_path=db_path,
        patches_dir=patches,
    )
    settings.data_dir.mkdir(parents=True, exist_ok=True)
    settings.runs_dir.mkdir(parents=True, exist_ok=True)
    settings.patches_dir.mkdir(parents=True, exist_ok=True)
    settings.profiles_dir.mkdir(parents=True, exist_ok=True)
    (settings.data_dir / "media").mkdir(parents=True, exist_ok=True)
    return settings


_settings: Settings | None = None


def get_settings() -> Settings:
    global _settings
    if _settings is None:
        _settings = load_settings()
    return _settings


def reset_settings() -> Settings:
    global _settings
    _settings = None
    return get_settings()


def assert_not_mainnet(rpc_url: str) -> None:
    if rpc_url and "mainnet" in rpc_url.lower():
        raise RuntimeError(
            "Refusing to start the wallet: SOLANA_RPC_URL contains 'mainnet'. "
            "Grasshopper only signs on devnet."
        )


def get_provider(kind: str):
    """Return the provider for kind. Missing keys log a warning and fall back to mock."""
    from grasshopper.providers.factory import build_provider

    return build_provider(kind, get_settings())
