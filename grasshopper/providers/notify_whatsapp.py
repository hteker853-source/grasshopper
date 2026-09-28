"""WhatsApp Cloud API notifier. Passive without WHATSAPP_TOKEN."""

from __future__ import annotations

import logging

import httpx

from grasshopper.providers.notify_console import redact

log = logging.getLogger("grasshopper.whatsapp")


class WhatsAppNotifier:
    name = "whatsapp"

    def __init__(self, token: str, phone_number_id: str, to: str = "", api_base: str = "https://graph.facebook.com"):
        self.token = token
        self.phone_number_id = phone_number_id
        self.to = to
        self.api_base = (api_base or "https://graph.facebook.com").rstrip("/")

    def configured(self) -> bool:
        return bool(self.token and self.phone_number_id and self.to)

    async def notify(self, message: str, *, kind: str = "info", payload: dict | None = None) -> None:
        if not self.configured():
            log.info("WhatsApp notifier is passive (no token)")
            return
        url = f"{self.api_base}/v20.0/{self.phone_number_id}/messages"
        body = {
            "messaging_product": "whatsapp",
            "to": self.to,
            "type": "text",
            "text": {"body": redact(message)[:4000]},
        }
        async with httpx.AsyncClient(timeout=20) as client:
            response = await client.post(url, headers={"Authorization": f"Bearer {self.token}"}, json=body)
        if response.status_code >= 400:
            log.warning("WhatsApp send failed: HTTP %s", response.status_code)
