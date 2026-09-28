#!/usr/bin/env bash
# Phone-friendly setup. Copy-paste as one block.
set -euo pipefail
cd "$(dirname "$0")/.."
PY="${PY:-python3.11}"
if ! command -v "$PY" >/dev/null 2>&1; then
  PY=python3
fi
if [ ! -d .venv ]; then
  "$PY" -m venv .venv --without-pip 2>/dev/null || "$PY" -m venv .venv
fi
if ! .venv/bin/python -m pip --version >/dev/null 2>&1; then
  curl -sS https://bootstrap.pypa.io/get-pip.py | .venv/bin/python
fi
.venv/bin/python -m pip install -r requirements.txt
# Chromium is optional. The http sandbox driver runs every demo without it.
if [ "${INSTALL_BROWSER:-0}" = "1" ]; then
  .venv/bin/python -m playwright install chromium || true
fi
if [ ! -f .env ]; then
  cp .env.example .env
fi
mkdir -p runs patches profiles data/media submissions
echo "Grasshopper ready. Start: .venv/bin/python -m uvicorn grasshopper.main:app --host 0.0.0.0 --port 8080"
