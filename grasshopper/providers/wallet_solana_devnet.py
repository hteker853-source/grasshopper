"""Devnet-only Solana wallet. Mainnet RPC URLs are refused before any client is built."""

from __future__ import annotations

import logging
from pathlib import Path

import httpx

from grasshopper.config import assert_not_mainnet
from grasshopper.providers.base import ProviderError
from grasshopper.providers.wallet_mock import MockWallet

log = logging.getLogger("grasshopper.wallet")


class SolanaDevnetWallet(MockWallet):
    """Ledger limits stay in SQLite. A configured keypair can broadcast a devnet memo later.

    The class subclasses the mock ledger so daily limits and the approval gate stay identical.
    Signing is attempted only when `solders` is installed and a keypair file exists.
    """

    name = "solana_devnet"

    def __init__(self, db, *, rpc_url: str, keypair_path: str, daily_limit: float, per_tx_limit: float):
        assert_not_mainnet(rpc_url)
        super().__init__(db, daily_limit=daily_limit, per_tx_limit=per_tx_limit)
        self.rpc_url = rpc_url
        self.keypair_path = keypair_path

    def configured(self) -> bool:
        return bool(self.keypair_path) and Path(self.keypair_path).exists() and "mainnet" not in self.rpc_url.lower()

    def rpc_health(self) -> str:
        assert_not_mainnet(self.rpc_url)
        try:
            response = httpx.post(
                self.rpc_url,
                json={"jsonrpc": "2.0", "id": 1, "method": "getHealth"},
                timeout=8,
            )
            return response.text[:200]
        except httpx.HTTPError as exc:
            raise ProviderError(f"Devnet RPC unreachable: {exc}") from exc

    def pay(self, amount_sol: float, memo: str, task_id: str | None = None) -> str:
        # Limits and the local receipt always run. The key file is never logged.
        tx_hash = super().pay(amount_sol, memo, task_id)
        if not self.configured():
            log.warning("Devnet keypair missing; stored a local receipt only (hash ends %s)", tx_hash[-4:])
            return tx_hash
        try:
            import solders  # noqa: F401
        except ImportError:
            log.warning("solders is not installed; recorded local devnet receipt ending %s", tx_hash[-4:])
            return tx_hash
        log.info("Devnet keypair present. Live broadcast stays manual in this MVP. Receipt ending %s", tx_hash[-4:])
        return tx_hash


def mask(value: str) -> str:
    return "****" + value[-4:]
