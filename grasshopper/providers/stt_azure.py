"""Azure Speech fast transcription (short audio, REST)."""

from __future__ import annotations

from pathlib import Path

import httpx

from grasshopper.providers.base import ProviderError


class AzureSTT:
    name = "azure"

    def __init__(self, key: str, region: str, endpoint: str = ""):
        self.key = key
        self.region = region
        self.endpoint = (endpoint or "").strip()

    def configured(self) -> bool:
        return bool(self.key and self.region)

    async def transcribe(self, audio_path: str) -> str:
        if not self.configured():
            raise ProviderError("Azure Speech needs AZURE_SPEECH_KEY and AZURE_SPEECH_REGION")
        url = self.endpoint or (
            f"https://{self.region}.stt.speech.microsoft.com/speech/recognition/conversation/cognitiveservices/v1"
            "?language=en-US"
        )
        headers = {
            "Ocp-Apim-Subscription-Key": self.key,
            "Content-Type": "audio/wav",
            "Accept": "application/json",
        }
        async with httpx.AsyncClient(timeout=60) as client:
            response = await client.post(url, headers=headers, content=Path(audio_path).read_bytes())
        if response.status_code >= 400:
            raise ProviderError(f"Azure STT HTTP {response.status_code}: {response.text[:180]}")
        return response.json().get("DisplayText") or response.json().get("NBest", [{}])[0].get("Display", "")
