"""Always-on notifier. Secrets in the message are masked before they hit the log."""

from __future__ import annotations

import logging
import re

log = logging.getLogger("grasshopper.notify")
_KEYISH = re.compile(r"(sk-[A-Za-z0-9]+|AKIA[0-9A-Z]{16}|[0-9a-fA-F]{64,})")


def redact(message: str) -> str:
    return _KEYISH.sub(lambda match: "****" + match.group(0)[-4:], message)


class ConsoleNotifier:
    name = "console"

    def __init__(self):
        self.messages: list[dict] = []

    async def notify(self, message: str, *, kind: str = "info", payload: dict | None = None) -> None:
        safe = redact(message)
        self.messages.append({"kind": kind, "message": safe, "payload": payload or {}})
        log.info("[%s] %s", kind, safe)
