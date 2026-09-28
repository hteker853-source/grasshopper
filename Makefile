PY ?= .venv/bin/python
PIP ?= .venv/bin/pip
HOST ?= 127.0.0.1
PORT ?= 8080
SANDBOX_PORT ?= 8090

.PHONY: setup run test test-browser demo record audit share share-mcp unshare live-demo sandbox lint bench-real kit kits judge nebius-demo

setup:
	bash scripts/setup.sh

run:
	$(PY) -m uvicorn grasshopper.main:app --host $(HOST) --port $(PORT)

sandbox:
	SANDBOX_PORT=$(SANDBOX_PORT) $(PY) -m uvicorn sandbox_web.app:app --host $(HOST) --port $(SANDBOX_PORT)

test:
	$(PY) -m pytest -q

test-browser:
	BROWSER_DRIVER=playwright $(PY) -m pytest -q -m browser

demo:
	bash scripts/demo_all.sh

record:
	$(PY) scripts/record_demo.py

audit:
	$(PY) scripts/audit.py

bench-real:
	BENCH_N=$${BENCH_N:-10} $(PY) scripts/bench_real.py

kit:
	$(PY) -m grasshopper.publish.submission_kit --competition $(COMP)

kits:
	$(PY) -m grasshopper.publish.submission_kit --all

share:
	$(PY) scripts/share.py

share-mcp:
	SHARE_TARGET=mcp $(PY) scripts/share.py --mcp

unshare:
	$(PY) scripts/unshare.py

live-demo:
	$(PY) scripts/live_demo.py

judge:
	$(PY) scripts/judge_demo.py

nebius-demo:
	$(PY) scripts/nebius_demo.py

