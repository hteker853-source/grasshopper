"""AssemblyAI batch transcription."""

from __future__ import annotations

import asyncio
from pathlib import Path

import httpx

from grasshopper.providers.base import ProviderError


class AssemblyAISTT:
    name = "assemblyai"

    def __init__(self, api_key: str, base_url: str = "https://api.assemblyai.com"):
        self.api_key = api_key
        self.base_url = (base_url or "https://api.assemblyai.com").rstrip("/")

    def configured(self) -> bool:
        return bool(self.api_key)

    async def transcribe(self, audio_path: str) -> str:
        if not self.configured():
            raise ProviderError("ASSEMBLYAI_API_KEY is empty")
        headers = {"authorization": self.api_key}
        data = Path(audio_path).read_bytes()
        async with httpx.AsyncClient(timeout=120) as client:
            upload = await client.post(f"{self.base_url}/v2/upload", headers=headers, content=data)
            if upload.status_code >= 400:
                raise ProviderError(f"AssemblyAI upload HTTP {upload.status_code}")
            created = await client.post(
                f"{self.base_url}/v2/transcript",
                headers=headers,
                json={"audio_url": upload.json()["upload_url"]},
            )
            if created.status_code >= 400:
                raise ProviderError(f"AssemblyAI create HTTP {created.status_code}")
            tid = created.json()["id"]
            for _ in range(60):
                polled = await client.get(f"{self.base_url}/v2/transcript/{tid}", headers=headers)
                body = polled.json()
                if body.get("status") == "completed":
                    return body.get("text") or ""
                if body.get("status") == "error":
                    raise ProviderError(body.get("error") or "AssemblyAI error")
                await asyncio.sleep(1.5)
        raise ProviderError("AssemblyAI transcription timed out")
