"""OpenAI-compatible chat completions. Used by Nebius, Meta, Azure, and generic endpoints."""

from __future__ import annotations

import httpx

from grasshopper.providers.base import ProviderError


class OpenAICompatLLM:
    def __init__(self, *, name: str, api_key: str, base_url: str, model: str, azure: bool = False):
        self.name = name
        self.api_key = api_key
        self.base_url = (base_url or "").rstrip("/")
        self.model = model
        self.azure = azure

    def configured(self) -> bool:
        return bool(self.api_key and self.base_url and self.model)

    async def complete(self, prompt: str, *, tier: str = "fast", system: str = "") -> str:
        if not self.configured():
            raise ProviderError(f"{self.name} is missing an API key, base URL, or model")
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})
        if self.azure:
            url = (
                f"{self.base_url}/openai/deployments/{self.model}/chat/completions"
                "?api-version=2024-10-21"
            )
            headers = {"api-key": self.api_key, "Content-Type": "application/json"}
            payload = {"messages": messages}
        else:
            url = f"{self.base_url}/chat/completions"
            headers = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}
            payload = {"model": self.model, "messages": messages}
        async with httpx.AsyncClient(timeout=60) as client:
            response = await client.post(url, headers=headers, json=payload)
        if response.status_code >= 400:
            raise ProviderError(f"{self.name} HTTP {response.status_code}: {response.text[:180]}")
        data = response.json()
        return data["choices"][0]["message"]["content"]
