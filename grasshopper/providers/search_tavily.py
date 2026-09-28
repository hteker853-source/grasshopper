"""Tavily web search."""

from __future__ import annotations

import httpx

from grasshopper.providers.base import ProviderError


class TavilySearch:
    name = "tavily"

    def __init__(self, api_key: str, base_url: str = "https://api.tavily.com"):
        self.api_key = api_key
        self.base_url = (base_url or "https://api.tavily.com").rstrip("/")

    def configured(self) -> bool:
        return bool(self.api_key)

    async def search(self, query: str, *, max_results: int = 5) -> list[dict]:
        if not self.configured():
            raise ProviderError("TAVILY_API_KEY is empty")
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.post(
                f"{self.base_url}/search",
                json={"api_key": self.api_key, "query": query, "max_results": max_results},
            )
        if response.status_code >= 400:
            raise ProviderError(f"Tavily HTTP {response.status_code}: {response.text[:180]}")
        results = []
        for item in response.json().get("results", []):
            results.append(
                {"title": item.get("title", ""), "url": item.get("url", ""), "snippet": item.get("content", "")}
            )
        return results
