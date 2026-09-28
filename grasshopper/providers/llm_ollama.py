"""Local Ollama completion. Target model is Gemma via GEMMA_MODEL."""

from __future__ import annotations

import httpx

from grasshopper.providers.base import ProviderError


class OllamaLLM:
    name = "ollama"

    def __init__(self, *, base_url: str, model: str):
        self.base_url = (base_url or "").rstrip("/")
        self.model = model

    def configured(self) -> bool:
        return bool(self.base_url and self.model)

    async def complete(self, prompt: str, *, tier: str = "repair", system: str = "") -> str:
        if not self.configured():
            raise ProviderError("Ollama needs OLLAMA_BASE_URL and GEMMA_MODEL")
        full = f"{system}\n\n{prompt}" if system else prompt
        async with httpx.AsyncClient(timeout=120) as client:
            response = await client.post(
                f"{self.base_url}/api/generate",
                json={"model": self.model, "prompt": full, "stream": False},
            )
        if response.status_code >= 400:
            raise ProviderError(f"Ollama HTTP {response.status_code}: {response.text[:180]}")
        return response.json().get("response", "")
