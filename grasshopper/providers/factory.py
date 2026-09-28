"""Build a provider from Settings. Unconfigured real providers fall back to mock."""

from __future__ import annotations

import logging

from grasshopper.config import Settings, assert_not_mainnet, mask_secret
from grasshopper.providers.llm_bedrock import BedrockLLM
from grasshopper.providers.llm_mock import MockLLM
from grasshopper.providers.llm_ollama import OllamaLLM
from grasshopper.providers.llm_openai_compat import OpenAICompatLLM
from grasshopper.providers.notify_console import ConsoleNotifier
from grasshopper.providers.notify_fanout import FanoutNotifier
from grasshopper.providers.notify_telegram import TelegramNotifier
from grasshopper.providers.notify_whatsapp import WhatsAppNotifier
from grasshopper.providers.search_mock import MockSearch
from grasshopper.providers.search_tavily import TavilySearch
from grasshopper.providers.stt_assemblyai import AssemblyAISTT
from grasshopper.providers.stt_azure import AzureSTT
from grasshopper.providers.stt_mock import MockSTT

log = logging.getLogger("grasshopper.providers")


def _fallback(kind: str, reason: str):
    log.warning("%s is not active (%s). Falling back to mock.", kind, reason)
    return None


def build_llm(provider_name: str, settings: Settings, *, tier: str) -> MockLLM | OpenAICompatLLM | BedrockLLM | OllamaLLM:
    name = (provider_name or "mock").strip().lower()
    if name in {"", "mock"} or name.startswith("mock_"):
        return MockLLM(name if name.startswith("mock_") else "mock")
    real = None
    if name == "nebius":
        real = OpenAICompatLLM(
            name="nebius",
            api_key=settings.nebius_api_key,
            base_url=settings.nebius_base_url,
            model=settings.nebius_fast_model,
        )
    elif name == "meta":
        api_key = settings.meta_api_key or settings.nebius_api_key
        base_url = settings.meta_base_url or ("https://api.tokenfactory.nebius.com/v1" if settings.nebius_api_key else "")
        model = settings.meta_model or "NousResearch/Hermes-4-405B"
        real = OpenAICompatLLM(
            name="meta",
            api_key=api_key,
            base_url=base_url,
            model=model,
        )
    elif name == "openai_compat":
        real = OpenAICompatLLM(
            name="openai_compat",
            api_key=settings.openai_compat_api_key,
            base_url=settings.openai_compat_base_url,
            model=settings.openai_compat_model,
        )
    elif name == "azure":
        real = OpenAICompatLLM(
            name="azure",
            api_key=settings.azure_openai_api_key,
            base_url=settings.azure_openai_endpoint,
            model=settings.azure_openai_deployment,
            azure=True,
        )
    elif name == "bedrock":
        if not settings.allow_bedrock:
            _fallback("bedrock", "ALLOW_BEDROCK is not 1")
            return MockLLM("mock")
        real = BedrockLLM(
            region=settings.aws_region,
            access_key=settings.aws_access_key_id,
            secret_key=settings.aws_secret_access_key,
            model_id=settings.bedrock_model_id,
        )
    elif name == "ollama":
        real = OllamaLLM(base_url=settings.ollama_base_url, model=settings.gemma_model)
    else:
        _fallback(name, "unknown provider name")
        return MockLLM("mock")
    if not real.configured():
        _fallback(name, "missing key or model — set the variables in .env")
        return MockLLM("mock")
    log.info("LLM tier %s using %s (key %s)", tier, name, mask_secret(getattr(real, "api_key", "") or "set"))
    return real


def build_stt(settings: Settings):
    name = settings.stt_provider.lower()
    if name == "assemblyai":
        real = AssemblyAISTT(settings.assemblyai_api_key, settings.assemblyai_base_url)
        if real.configured():
            return real
        _fallback("assemblyai", "ASSEMBLYAI_API_KEY empty")
    elif name == "azure":
        real = AzureSTT(settings.azure_speech_key, settings.azure_speech_region, settings.azure_speech_endpoint)
        if real.configured():
            return real
        _fallback("azure stt", "AZURE_SPEECH_KEY or region empty")
    elif name != "mock":
        _fallback(name, "unknown STT provider")
    return MockSTT()


def build_search(settings: Settings):
    name = settings.search_provider.lower()
    if name == "tavily":
        real = TavilySearch(settings.tavily_api_key, settings.tavily_base_url)
        if real.configured():
            return real
        _fallback("tavily", "TAVILY_API_KEY empty")
    elif name != "mock":
        _fallback(name, "unknown search provider")
    return MockSearch()


def build_wallet(settings: Settings, db):
    name = settings.wallet_provider.lower()
    if name == "solana_devnet":
        try:
            assert_not_mainnet(settings.solana_rpc_url)
        except RuntimeError:
            log.error("Wallet refused to start because SOLANA_RPC_URL points at mainnet")
            raise
        from grasshopper.providers.wallet_solana_devnet import SolanaDevnetWallet

        real = SolanaDevnetWallet(
            db,
            rpc_url=settings.solana_rpc_url,
            keypair_path=settings.wallet_keypair_path,
            daily_limit=settings.wallet_daily_limit_sol,
            per_tx_limit=settings.wallet_per_tx_limit_sol,
        )
        if real.configured():
            log.info("Wallet: solana devnet (keypair set, RPC host only)")
            return real
        _fallback("solana_devnet", "WALLET_KEYPAIR_PATH missing or unreadable — using the mock ledger")
    elif name != "mock":
        _fallback(name, "unknown wallet provider")
    from grasshopper.providers.wallet_mock import MockWallet

    return MockWallet(
        db,
        daily_limit=settings.wallet_daily_limit_sol,
        per_tx_limit=settings.wallet_per_tx_limit_sol,
    )


def build_notifier(settings: Settings) -> FanoutNotifier:
    notifiers = [ConsoleNotifier()]
    telegram = TelegramNotifier(
        settings.telegram_bot_token,
        settings.telegram_allowed_user_id,
        settings.telegram_api_base,
    )
    if telegram.configured():
        notifiers.append(telegram)
    else:
        if settings.telegram_bot_token or settings.telegram_allowed_user_id:
            _fallback("telegram", "need both TELEGRAM_BOT_TOKEN and TELEGRAM_ALLOWED_USER_ID")
    whatsapp = WhatsAppNotifier(
        settings.whatsapp_token,
        settings.whatsapp_phone_number_id,
        settings.whatsapp_to,
        settings.whatsapp_api_base,
    )
    if settings.whatsapp_token and not whatsapp.configured():
        _fallback("whatsapp", "need WHATSAPP_TOKEN, WHATSAPP_PHONE_NUMBER_ID, and WHATSAPP_TO")
    elif whatsapp.configured():
        notifiers.append(whatsapp)
    return FanoutNotifier(notifiers)


def build_provider(kind: str, settings: Settings, db=None):
    if kind == "llm_fast":
        return build_llm(settings.llm_fast_provider, settings, tier="fast")
    if kind == "llm_strong":
        return build_llm(settings.llm_strong_provider, settings, tier="strong")
    if kind == "llm_vision":
        return build_llm(settings.llm_vision_provider, settings, tier="vision")
    if kind == "llm_repair":
        return build_llm(settings.llm_repair_provider, settings, tier="repair")
    if kind == "stt":
        return build_stt(settings)
    if kind == "search":
        return build_search(settings)
    if kind == "wallet":
        if db is None:
            raise RuntimeError("wallet provider needs a database")
        return build_wallet(settings, db)
    if kind == "notifier":
        return build_notifier(settings)
    raise KeyError(f"Unknown provider kind: {kind}")


def provider_status(settings: Settings) -> list[dict]:
    """Dashboard badges. Does not instantiate wallets (that needs the db)."""
    rows = []

    def add(label: str, selected: str, live: bool):
        rows.append({"label": label, "selected": selected, "mode": "REAL" if live else "MOCK"})

    fast = build_llm(settings.llm_fast_provider, settings, tier="fast")
    strong = build_llm(settings.llm_strong_provider, settings, tier="strong")
    vision = build_llm(settings.llm_vision_provider, settings, tier="vision")
    repair = build_llm(settings.llm_repair_provider, settings, tier="repair")
    stt = build_stt(settings)
    search = build_search(settings)
    add("LLM fast", settings.llm_fast_provider, not isinstance(fast, MockLLM))
    add("LLM strong", settings.llm_strong_provider, not isinstance(strong, MockLLM))
    add("LLM vision", settings.llm_vision_provider, not isinstance(vision, MockLLM))
    add("LLM repair", settings.llm_repair_provider, not isinstance(repair, MockLLM))
    add("STT", settings.stt_provider, not isinstance(stt, MockSTT))
    add("Search", settings.search_provider, not isinstance(search, MockSearch))
    wallet_live = settings.wallet_provider == "solana_devnet" and bool(settings.wallet_keypair_path)
    add("Wallet", settings.wallet_provider, wallet_live)
    add("Telegram", "telegram" if settings.telegram_bot_token else "off", bool(settings.telegram_bot_token and settings.telegram_allowed_user_id))
    add("WhatsApp", "whatsapp" if settings.whatsapp_token else "off", bool(settings.whatsapp_token and settings.whatsapp_phone_number_id and settings.whatsapp_to))
    return rows
