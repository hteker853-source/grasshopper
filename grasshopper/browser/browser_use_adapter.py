"""Optional browser-use adapter. Import failures stay inside this module."""

from __future__ import annotations

import logging

log = logging.getLogger("grasshopper.browser_use")


class BrowserUseAdapter:
    name = "browser-use"

    def __init__(self):
        self.available = False
        self._error = ""
        try:
            import browser_use  # noqa: F401

            self.available = True
        except Exception as exc:  # optional dependency
            self._error = str(exc)
            log.info("browser-use is not installed (%s). Mock mode does not need it.", exc)

    async def run_goal(self, goal: str, url: str) -> str:
        if not self.available:
            raise RuntimeError(
                "browser-use is optional and only used when MODE=real. "
                f"Install requirements-real.txt. Detail: {self._error}"
            )
        raise RuntimeError(
            "browser-use is installed but Grasshopper still executes the action schema itself. "
            f"Goal was noted, not delegated: {goal} @ {url}"
        )
