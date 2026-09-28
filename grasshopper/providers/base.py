"""Provider protocols. Real adapters must not be imported at process start unless selected."""

from __future__ import annotations

from typing import Protocol, runtime_checkable


class ProviderError(RuntimeError):
    """Raised when a real provider is selected but cannot run. Callers fall back to mock."""


@runtime_checkable
class LLMProvider(Protocol):
    name: str

    async def complete(self, prompt: str, *, tier: str = "fast", system: str = "") -> str: ...


@runtime_checkable
class STTProvider(Protocol):
    name: str

    async def transcribe(self, audio_path: str) -> str: ...


@runtime_checkable
class SearchProvider(Protocol):
    name: str

    async def search(self, query: str, *, max_results: int = 5) -> list[dict]: ...


@runtime_checkable
class WalletProvider(Protocol):
    name: str

    def balance(self) -> float: ...

    def pay(self, amount_sol: float, memo: str, task_id: str | None = None) -> str: ...


@runtime_checkable
class NotifierProvider(Protocol):
    name: str

    async def notify(self, message: str, *, kind: str = "info", payload: dict | None = None) -> None: ...
