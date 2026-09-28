"""Offline search index used when Tavily is not configured."""

from __future__ import annotations


_DOCS = [
    {
        "title": "Sandbox news desk",
        "url": "{sandbox}/news",
        "snippet": "Headlines with a trend score. Scores above 80 are worth a short video.",
    },
    {
        "title": "Shop listings older than four months",
        "url": "{sandbox}/shop/listings?older_than_months=4",
        "snippet": "Seller dashboard filter for stale listings.",
    },
    {
        "title": "Grasshopper competitions board",
        "url": "{sandbox}/competitions",
        "snippet": "Hackathons the demo profile can enter, including Alexa+ MCP.",
    },
]


class MockSearch:
    name = "mock"

    def configured(self) -> bool:
        return True

    async def search(self, query: str, *, max_results: int = 5) -> list[dict]:
        words = set(query.lower().split())
        ranked = []
        for doc in _DOCS:
            hay = (doc["title"] + " " + doc["snippet"]).lower()
            score = sum(1 for word in words if word in hay)
            ranked.append((score, doc))
        ranked.sort(key=lambda item: item[0], reverse=True)
        return [dict(item[1]) for item in ranked[:max_results]]
