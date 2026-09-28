"""Telegram notifier. Stays silent when TELEGRAM_BOT_TOKEN is empty."""

from __future__ import annotations

import json
import logging
from pathlib import Path

import httpx

from grasshopper.providers.notify_console import redact

log = logging.getLogger("grasshopper.telegram")


def approval_keyboard(approval_id: str) -> dict:
    return {
        "inline_keyboard": [[
            {"text": "Approve", "callback_data": f"approve:{approval_id}"},
            {"text": "Reject", "callback_data": f"reject:{approval_id}"},
        ]]
    }


class TelegramNotifier:
    name = "telegram"

    def __init__(self, token: str, allowed_user_id: str, api_base: str = "https://api.telegram.org"):
        self.token = token
        self.allowed_user_id = allowed_user_id
        self.api_base = (api_base or "https://api.telegram.org").rstrip("/")

    def configured(self) -> bool:
        return bool(self.token and self.allowed_user_id)

    async def notify(self, message: str, *, kind: str = "info", payload: dict | None = None) -> None:
        if not self.configured():
            log.info("Telegram notifier is passive (no token)")
            return
        payload = payload or {}
        approval_id = payload.get("approval_id")
        screenshot = payload.get("screenshot") if kind == "approval" else None
        path = Path(screenshot) if screenshot else None
        if path is not None and path.is_file():
            await self._send_photo(redact(message), path, approval_id)
            return
        body: dict = {"chat_id": self.allowed_user_id, "text": redact(message)[:4000]}
        if approval_id:
            body["reply_markup"] = approval_keyboard(str(approval_id))
        await self._post("sendMessage", json_body=body)

    async def _send_photo(self, message: str, path: Path, approval_id: str | None) -> None:
        data = {"chat_id": self.allowed_user_id, "caption": message[:1024]}
        if approval_id:
            data["reply_markup"] = json.dumps(approval_keyboard(str(approval_id)))
        with path.open("rb") as handle:
            await self._post("sendPhoto", data=data, files={"photo": (path.name, handle, "image/png")})

    async def _post(self, method: str, *, json_body: dict | None = None, data: dict | None = None, files=None) -> None:
        url = f"{self.api_base}/bot{self.token}/{method}"
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.post(url, json=json_body, data=data, files=files)
        if response.status_code >= 400:
            log.warning("Telegram %s failed: HTTP %s", method, response.status_code)
