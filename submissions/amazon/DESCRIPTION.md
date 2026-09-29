# Grasshopper — Amazon Submission Draft

**Halil should review - Draft only. Do not submit.** This folder is a hackathon kit draft. Nothing in it has been submitted automatically.

---

## Project Overview

Grasshopper is an open-source (MIT) autonomous multi-step browser agent designed to perform complex web tasks safely, reliably, and cost-effectively. A user describes a workflow in a single sentence or voice utterance. Grasshopper parses the intent into atomic observation-action-verification steps, navigates live web pages, detects navigation stalls, and pauses to request human sign-off before executing irreversible actions (such as paying, submitting forms, or sharing data).

A central innovation is **zero-cost recipe replay**: once Grasshopper discovers a successful path through a site, it compiles the execution trace into an approved playbook. Subsequent runs execute deterministically with **zero model calls**, driving marginal inference cost to zero.

- **Demo Video:** https://youtu.be/3MFjYfCec4c
- **GitHub Repository:** https://github.com/hteker853-source/grasshopper
- **Jury Replay (Static Demo):** https://hteker853-source.github.io/grasshopper/

---

## Technical Architecture & Offline-First Design

1. **Model Context Protocol (MCP SDK 2.x):**
   - Full MCP Streamable HTTP server mounted at `/mcp/`.
   - Exposes 7 production tools: `run_task`, `get_task_status`, `list_pending_approvals`, `approve`, `council_ask`, `schedule_task`, and `store_check_old_listings`.
   - Any external surface (Claude Desktop, Alexa+ skill, or custom agents) can queue tasks and review approvals via standard MCP.
2. **Deterministic Default & Zero Secrets:**
   - The test suite and default runtime operate 100% offline in mock mode without requiring API keys or network credentials.
   - 97 pytest tests pass unconditionally (`make test` is 100% green).
   - Real providers (Nebius Nemotron, AWS Bedrock, Azure OpenAI) turn on exclusively via `.env`.
3. **Hard Spend Ceiling (BudgetLedger):**
   - Hard limits of **$0.50 daily** and **$0.05 per-run** are enforced before every model call.
   - Tested live against real web benchmarks with Nebius Nemotron (`nvidia/Nemotron-3_5-Lightning`), spending an authentic **$0.0238** across 41 decision calls.
4. **Alexa Simulation Surface (`/alexa`):**
   - Interactive voice/text test interface simulating Alexa+ smart display interactions, rendering real-time execution feedback and approval cards.

---

## What the Demo Runs Actually Did (from `runs/demo-record`)

- **S3 (Shop Listings Older Than 4 Months):** Finished from the `shop_old_listings` playbook with 0 LLM calls (`run_ed76f4a16239`, about 3.4 seconds, success rate 1).
- **S6 (Pro Plan Payment):** Waited for human approval at the gate and wrote a confirmed receipt only after explicit approval (`run_2036d34900f2`, success rate 1).
- **S7 (Renamed Export Button):** Stopped safely upon discovering selector rename, and proposed an isolated patch without applying it (`run_9f24d8fa5fad`, status `waiting_approval`).

---

## Tracks Targeted

1. **Alexa+ Track (Primary):**
   - Deep integration via MCP SDK 2.x Streamable HTTP and `/alexa` interface.
   - Transparent approval gates allowing voice users to safely delegate real-world browsing.
2. **Open Source Mini Challenge:**
   - 100% MIT-licensed codebase.
   - Zero-dependency setup (`bash scripts/setup.sh` -> `make test`).
   - Honest, compiled `FRICTION_LOG.md` documenting real integration snags with MCP SDK 2.x session lifespans, Playwright fallbacks, and HTTP header parsing.
3. **AWS Builder Track (Optional Note):**
   - AWS Bedrock strong-tier routing is implemented with botocore Stubber unit test validation, awaiting live key enablement (`ALLOW_BEDROCK=1`).
