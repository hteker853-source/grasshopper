"""Fan-out wrapper so the orchestrator can treat every channel as one notifier."""

from __future__ import annotations

import logging

log = logging.getLogger("grasshopper.notify")


class FanoutNotifier:
    name = "fanout"

    def __init__(self, notifiers: list):
        self.notifiers = notifiers

    async def notify(self, message: str, *, kind: str = "info", payload: dict | None = None) -> None:
        for notifier in self.notifiers:
            try:
                await notifier.notify(message, kind=kind, payload=payload)
            except Exception as exc:  # a dead channel must not kill the run
                log.warning("Notifier %s failed: %s", getattr(notifier, "name", "?"), exc)
