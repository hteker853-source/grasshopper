#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
export BROWSER_DRIVER="${BROWSER_DRIVER:-http}"
export SANDBOX_DELAY_MIN_MS="${SANDBOX_DELAY_MIN_MS:-0}"
export SANDBOX_DELAY_MAX_MS="${SANDBOX_DELAY_MAX_MS:-30}"
export GRASSHOPPER_EMBED_SANDBOX=0
if ! curl -fsS "${SANDBOX_BASE_URL:-http://127.0.0.1:8090}/health" >/dev/null 2>&1; then
  .venv/bin/python -m uvicorn sandbox_web.app:app --host 127.0.0.1 --port "${SANDBOX_PORT:-8090}" &
  SANDBOX_PID=$!
  trap 'kill $SANDBOX_PID 2>/dev/null || true' EXIT
  for _ in 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 19 20; do
    curl -fsS "http://127.0.0.1:${SANDBOX_PORT:-8090}/health" >/dev/null 2>&1 && break
    sleep 0.3
  done
  export SANDBOX_BASE_URL="http://127.0.0.1:${SANDBOX_PORT:-8090}"
fi
.venv/bin/python -m grasshopper.demo
