# Competition Inventory Matrix

Date: 2026-09-28  
Rule: "Working" claims require concrete proof (test name, run ID, or benchmark metric); unverified states are labeled "unmeasured" or "untested". Zero fabricated data.

---

## 1. General Inventory Table (19 Competitions)

| No | Competition | Prize | Date / Build Window | Eligibility & Team | Jury Criteria & Weights | Code Implementation | Status & Evidence | Gaps & Expectations | Verification Status |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **1** | **Amazon Build, Ship, Shape (Alexa+)** | $25K/$15K/$4K cash + AWS credits; OSS mini $5K, AWS Builder $5K | Oct 23, 2026 12:00 PT | Individual or team (1-5) | Tech (25%), Design (25%), Impact (25%), Quality (25%) | `grasshopper/mcp_server/`, `grasshopper/channels/alexa_sim.py`, `/alexa` | **WORKING** (`test_s9_mcp_client`, `test_dashboard_ux.py`, 111 tests green) | Alexa-AI CLI hardware test requires human action; live Bedrock key absent. | UNVERIFIED (briefing ~15,800 participants; Devpost official rules referenced) |
| **2** | **Nebius x NVIDIA Global AI** | $20K/$10K/$6K cash + Tavily $3K + Jetson | Oct 30, 2026 23:59 PT | Individual or team | Tech (25%), Design (25%), Impact (25%), Quality (25%) | `grasshopper/providers/factory.py`, `grasshopper/core/router.py` | **WORKING** (41 live LLM calls, $0.0238 spend, `test_nemotron_sponsor.py`) | Tavily live key empty (mock search active). | UNVERIFIED (cash tiers from briefing; equal weights from official Devpost) |
| **3** | **Open Agent Hackathon** | $8K/$4K/$2K cash ($20K pool) | Reg Oct 13, Build Oct 15-20 | Tinkerer Track (existing projects) | Impact (30%), Tech (20%), Innovation (15%), Demo (15%), UX (10%), Sponsor (10%) | `grasshopper/core/explainer.py`, `docs/OPEN_AGENT_PLAN.md` | **WORKING** (`test_s5_council`, `test_explainer_records_step`, `test_nemotron_sponsor.py`) | No new module code permitted before Oct 15 (frozen per rules). | UNVERIFIED (briefing tiers; genai.works official rubric) |
| **4** | **OpenCV AI Competition** | $5K/$3K/$2K + $1K Agentic Vision | Oct 26, 2026 | Individual or team | Tech Execution (30%), Innovation (20%), Impact (20%), UX (10%), Presentation (20%) | `grasshopper/browser/vision.py`, `vision_service/` | **WORKING** (`test_vision_finds_button`, `test_vision_service_app`, OpenCV 5.0.0.93) | Live AWS cloud deployment unperformed (`docs/OPENCV_AWS.md` is guide). | UNVERIFIED (prizes and rubric from official site; proposal stage unverified) |
| **5** | **Vultr Agent Rush** | $9K cash + $5K credits (1st: $5K) | Nov 3–8, 2026 | Individual or team | Tech (25%), Presentation (25%), Business (25%), Originality (25%) | `grasshopper/sandbox_runner/vultr.py`, `runs/blast_radius.json` | **WORKING (MOCK/FAKE)** (`tests/test_vultr_sandbox.py` 3/3 green with fake server) | Live funded Vultr account not connected; live VM unprovisioned. | UNVERIFIED (lablab.ai secondary source rules) |
| **6** | **IEEE ClimateChain** | $1.5K/$1K/$0.5K cash ($3K pool) | Oct 5–25, 2026 | Individual or team | Climate impact, blockchain verification, feasibility | `grasshopper/realweb/climate.py` | **WORKING (SIMULATION)** (`tests/test_climate.py`) | No real IoT/climate sensor stream; Turkiye residency requirement unverified. | UNVERIFIED (Devpost page referenced) |
| **7** | **YTU x Meta Student Hackathon** | $6,000 prize pool | Reg Oct 11, Final Dec 4-6 (In-person) | Student team (Istanbul on-site) | Technical novelty, Llama integration, prototype quality | `grasshopper/providers/factory.py` (`meta` provider) | **WAITING FOR KEY** (`WHATSAPP_TOKEN`, `META_API_KEY` empty) | In-person attendance is human operational task; jury scoring rubric pending. | UNVERIFIED (YTU Startup House announcement) |
| **8** | **ING Hubs Agentic AI** | 2 MacBook Neo / 2 iPad / 2 Apple Watch | Reg Oct 4, Build Oct 9-18, Final Nov 3 | 2-4 person team, Turkiye | Business impact, technical architecture, financial safety | `grasshopper/core/gate.py`, `grasshopper/core/budget.py` | **WORKING** (`test_gate_approvals`, `test_wallet_limits`) | No cash prizes (hardware awards); problem statements announced Oct 9. | UNVERIFIED (ING Hubs Turkiye official announcement) |
| **9** | **Kestra Hacktober** | MacBook Neo / iPad / Swag | Oct 1–31, 2026 | Individual GitHub contribution | PR quality, plugin or blueprint utility | `submissions/kestra/` | **HUMAN ACTION** (Opening PR from this repo against Kestra repo is human work) | PR not yet opened against official Kestra repo. | UNVERIFIED (kestra.io announcement) |
| **10** | **ASUS UGen AI League** | $4.5K + UGen300 (Hailo-10H 40 TOPS) | Stage I: Oct 14, 2026 | Individual or team | Hardware fit, local NPU performance, innovation | `submissions/asus/PRESENTATION.md` | **UNTESTED (NO HARDWARE)** | UGen300 hardware and Hailo NPU not present; local inference unmeasured. | UNVERIFIED (ASUS UGen AI League / Bhuntr) |
| **11** | **Microsoft Imagine Cup 2027** | $100,000 grand prize | Deadline: Jan 8, 2027 | Student team, global | Impact, technology depth (Azure AI), business model | `docs/IMAGINE_CUP_PLAN.md` | **WAITING FOR KEY** (`AZURE_OPENAI_ENDPOINT`, `AZURE_SPEECH_KEY`) | Live Azure subscription and credentials unlinked; 2027 rules unverified. | UNVERIFIED (Microsoft official sources) |
| **12** | **Meta Global AI Developer** | Grand prize pool (cash + Llama grants) | TBA (Late 2026) | Individual or team | Development with Llama models, global impact | `grasshopper/providers/factory.py` | **WAITING FOR KEY** | Dates and official rules not yet finalized on official page. | UNVERIFIED |
| **13** | **Build With AI: Basics** | $2,500 cash | Oct 26, 2026 | Individual / open | Working prototype, problem solving | Core agent engine (`grasshopper/`) | **WORKING** (111 tests green, `make run`) | Prototype ready, submitting form is human action. | UNVERIFIED (Devpost page) |
| **14** | **AI GENESIS (lablab.ai)** | Certificate + accelerator access | Nov 2, 2026 | lablab team | Agent autonomy, multi-step execution | `grasshopper/core/orchestrator.py` | **WORKING** (`test_stage4.py`, `test_orchestrator`) | Cash prize unconfirmed; community voting required. | UNVERIFIED (lablab.ai) |
| **15** | **Rise of AI Agents (lablab.ai)**| Certificate + sponsor grants | Nov 3, 2026 | lablab team | Agent architecture, reliability | `grasshopper/realweb/engine.py` | **WORKING** (`test_realweb.py`) | Cash prize unconfirmed. | UNVERIFIED (lablab.ai) |
| **16** | **Kaggle Gemma 4 Paper Track** | $35,000 cash | Nov 12, 2026 | Individual or team | Academic innovation, Gemma architecture, paper format | `grasshopper/providers/llm_mock.py` | **UNTESTED (POOR FIT)** | `GEMMA_MODEL` empty; academic paper unwritten; poor architectural fit. | UNVERIFIED (Kaggle) |
| **17** | **HETIC AI Agents for Founders** | $1,100 cash | Dec 18, 2026 | Founders / entrepreneurs | Founder-focused automation, cost reduction | `grasshopper/publish/live_feed.py`, shop playbooks | **WORKING** (`test_s3_old_listings`, `#savings` panel) | Adapting submission text to French/English is human work. | UNVERIFIED (briefing) |
| **18** | **AssemblyAI Voice Agent** | $10,000 cash + credits | Sep 30, 2026 23:59 PT | Individual or team | Voice accuracy, latency, intelligent agent | `grasshopper/providers/stt_assemblyai.py` | **WAITING FOR KEY** (`ASSEMBLYAI_API_KEY` empty) | Timeline very tight (Sep 30); live voice pipeline unmeasurable without key. | UNVERIFIED (Devpost) |
| **19** | **Colosseum / Arbiter** | Various | Oct / Dec 2026 | Private | - | `eligible=false` | **NOT ENTERING** | Decision: Colosseum and Arbiter excluded (probability = 0). | UNVERIFIED |

---

## 2. Gaps and Incomplete Items

1. **Pathways Operating Solely on Mock / Fakes:**
   - **Vultr Cloud Deployment:** `grasshopper/sandbox_runner/vultr.py` API integration verified against `tests/fakes/vultr_app.py` fake server and local Docker. Real funded account and SSH tunnel unprovisioned.
   - **Amazon Bedrock:** Tested with `botocore.stub.Stubber` (`ALLOW_BEDROCK=1`); billed live Bedrock calls unexecuted.
   - **Tavily Search:** Without `TAVILY_API_KEY`, search falls back to offline mock indexes.
   - **Meta / WhatsApp:** Without `WHATSAPP_TOKEN` and `META_API_KEY`, live Webhook unverified; router operates in simulation.
   - **Solana Devnet Wallet:** Without `WALLET_KEYPAIR_PATH`, transactions simulate on mock ledger.

2. **Unverified Claims and Mitigations:**
   - **User Studies:** No live human user field tests conducted. [docs/UX_EVALUATION.md](docs/UX_EVALUATION.md) documents heuristic walkthroughs simulated via AI personas and automated DOM assertions.
   - **Live Web Learning:** Zero model calls on learned recipes proven on local fixtures (`tests/test_realweb.py`); on live sites (saucedemo, books.toscrape), DOM variation triggered stuck detection, truthfully documented in [RELIABILITY_REAL.md](docs/RELIABILITY_REAL.md).
   - **Jury Scores & EV:** Scores represent estimations from AI models (Nebius Nemotron Ultra 550B), not decisions by official juries. Monte Carlo EV figures depend circularly on these scores.

3. **Human Operational Tasks (Beyond Automation):**
   - **Submission Portals:** No automated submissions permitted to Devpost, lablab.ai, genai.works; final review and submission must be performed by human.
   - **Kestra PR Submission:** Submitting blueprint to official Kestra repo requires manual human PR creation.
   - **YTU x Meta Hackathon:** Requires physical on-site presence in Istanbul on Dec 4–6.
   - **ASUS UGen Hardware Testing:** Local inference benchmarks require physical Hailo-10H NPU hardware.
