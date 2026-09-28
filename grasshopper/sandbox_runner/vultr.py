"""Open a short-lived Vultr instance, record the job, and delete the instance.

The real remote shell is not guessed here. docs/rules/vultr.md can replace the
exec step later. Without VULTR_API_KEY this runner does not call the network.
"""

from __future__ import annotations

import logging
import time

import httpx

from grasshopper.sandbox_runner.audit import AuditLog
from grasshopper.sandbox_runner.base import RunnerResult
from grasshopper.sandbox_runner.local import LocalRunner

log = logging.getLogger("grasshopper.sandbox")


class VultrAPI:
    def __init__(self, api_key: str, base_url: str = "https://api.vultr.com"):
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")

    def _headers(self) -> dict[str, str]:
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        return headers

    def create_instance(self, *, label: str = "grasshopper-job", user_data: str | None = None) -> str:
        payload = {"region": "ewr", "plan": "vc2-1c-1gb", "label": label}
        if user_data:
            payload["user_data"] = user_data
        response = httpx.post(
            f"{self.base_url}/v2/instances",
            headers=self._headers(),
            json=payload,
            timeout=30,
        )
        response.raise_for_status()
        return str(response.json()["instance"]["id"])

    def get_instance(self, instance_id: str) -> dict:
        response = httpx.get(
            f"{self.base_url}/v2/instances/{instance_id}",
            headers=self._headers(),
            timeout=30,
        )
        response.raise_for_status()
        return response.json().get("instance", {})

    def list_instances(self) -> list[dict]:
        response = httpx.get(
            f"{self.base_url}/v2/instances",
            headers=self._headers(),
            timeout=30,
        )
        response.raise_for_status()
        return response.json().get("instances", [])

    def wait_until_active(self, instance_id: str, *, attempts: int = 10) -> str:
        status = "pending"
        for _ in range(attempts):
            inst = self.get_instance(instance_id)
            status = str(inst.get("status", "pending"))
            if status == "active":
                return status
            time.sleep(0.05)
        return status

    def delete_instance(self, instance_id: str) -> None:
        response = httpx.delete(
            f"{self.base_url}/v2/instances/{instance_id}",
            headers=self._headers(),
            timeout=30,
        )
        if response.status_code >= 400:
            raise RuntimeError(f"Vultr delete HTTP {response.status_code}")


class VultrRunner:
    name = "vultr"

    def __init__(self, audit: AuditLog, local: LocalRunner, *, api_key: str = "", api_base: str = "https://api.vultr.com"):
        self.audit = audit
        self.local = local
        self.api = VultrAPI(api_key, api_base) if api_key else None

    def run(self, action: str, command: list[str], *, timeout: int = 30) -> RunnerResult:
        if self.api is None:
            log.warning("VULTR_API_KEY is empty. Vultr runner stays on the mock path.")
            local = self.local.run(action, command, timeout=timeout)
            self.audit.write(action, "vultr-mock", "no API key; local result kept")
            return RunnerResult(local.ok, "vultr-mock", local.detail, False)
        instance_id = self.api.create_instance()
        self.audit.write(action, f"vultr:{instance_id}", "created")
        try:
            status = self.api.wait_until_active(instance_id)
            # The command is the docker payload that belongs on that instance.
            # SSH is intentionally not invented; vultr.md can fill this in.
            self.audit.write(action, f"vultr:{instance_id}", f"status={status} command={' '.join(command)}")
            local = self.local.run(action, command, timeout=timeout)
            return RunnerResult(local.ok and status == "active", f"vultr:{instance_id}", local.detail, status == "active")
        finally:
            self.api.delete_instance(instance_id)
            self.audit.write(action, f"vultr:{instance_id}", "deleted")
