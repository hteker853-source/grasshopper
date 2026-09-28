# Grasshopper

[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Tests](https://img.shields.io/badge/tests-110%20passed-brightgreen.svg)]()
[![Audit](https://img.shields.io/badge/audit-22%20✅%20%2F%208%20⏳-blue.svg)](docs/AUDIT.md)

Grasshopper, tarayıcıyı insan gibi kullanan açık kaynaklı bir yapay zekâ ajanıdır. Tarayıcıda elle yapılan tekrarlı işleri tek prompt veya sesle güvenli, bütçeli ve öğrenen bir otomasyona çevirir. Canlı site: [halil.devnet](https://halil.devnet) (veya GitHub: [https://github.com/grasshopper-agent/grasshopper](https://github.com/grasshopper-agent/grasshopper)).

Once a workflow is successfully completed, Grasshopper learns the recipe and replays it on subsequent runs with **zero model calls**, driving marginal inference cost to zero.

---

## 3-Command Setup

```bash
git clone https://github.com/grasshopper-agent/grasshopper.git && cd grasshopper
bash scripts/setup.sh
make run
```

`make run` serves the dashboard on port `8080` (binds `127.0.0.1` by default) and the local sandbox sites on port `8090`. No external API keys are required; **mock mode is the deterministic default**.

---

## Jüri İçin 60 Saniye (60 Seconds for the Jury)

Grasshopper'ı sıfır dış bağımlılık ve sıfır harcamayla 60 saniyenin altında denemek için:

```bash
make judge
```

Bu komut:
1. Deterministik tohumlanmış senaryoyu başlatır.
2. Doğal dil görev alımını, çok adımlı planlamayı ve tarayıcı adımlarını simüle eder.
3. `BudgetLedger` harcama tavanını ve `ApprovalGate` insan onay mekanizmasını doğrular.
4. Adım adım ekran görüntüleriyle `site/index.html` statik jüri oynatma sayfasını üretir.

---

## Nebius Token Factory Üzerinde 3 Dakikada Çalıştır

Nebius Token Factory (`https://api.tokenfactory.nebius.com/v1`) ve `nvidia/Nemotron-3_5-Lightning` ile canlı ajan kararlarını 3 dakikada test etmek için:

```bash
make nebius-demo
```

Bu komut:
1. Token Factory `/chat/completions` uç noktasına bağlanır.
2. Gerçek DOM durumunu Fast katmana iletir ve geçerli JSON eylemi alır.
3. `BudgetLedger` üzerinde gerçek token ve dolar maliyetini ($0.0001 seviyesi) ölçer.

---

## Architecture

```mermaid
flowchart TD
    User["User (Web Chat / Voice / MCP Client)"] --> Dash["FastAPI Dashboard & MCP Server (/mcp)"]
    Dash --> Orch["Orchestrator & Multi-Agent Council"]
    Orch --> Router["Two-Tier Router (Fast: Nemotron / Strong / CV)"]
    Router --> Budget["BudgetLedger ($0.50 Daily / $0.05 Per-Run Hard Cap)"]
    Engine["Browser Engine (Playwright Chromium / HTTP Driver)"]
    Budget --> Engine
    Engine --> Policy["Policy Gate (Allowlist / Denylist / Human Approval)"]
    Policy --> Target["Target Web Sites (Allowlisted Only)"]
    Target --> Learn["Recipe Learning Store (0 LLM Calls on Replay)"]
    Policy --> Contain["Containment Sandbox (Docker / Vultr Blast Radius)"]
```

---

## Real-World Benchmark (Gerçek Site Ölçümleri)

Measurements from [docs/RELIABILITY_REAL.md](docs/RELIABILITY_REAL.md) across 5 real web benchmarks evaluated with live **Nebius Nemotron** (`nvidia/Nemotron-3_5-Lightning`, N=3).

| Senaryo | Hedef Site | Koşu | 1. Koşu LLM | 1. Koşu Token | 1. Koşu Gerçek $ | 1. Koşu Süre | 2. Koşu (Tarif) |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **R1** | books.toscrape.com (En ucuz 4★ kitap) | 3 | 22 | 19,272 | $0.003814 | 230.2s | 20 çağrı |
| **R2** | saucedemo.com (Sepete ekleme ve ödeme) | 3 | 3 | 702 | $0.000140 | 10.9s | 3 çağrı |
| **R3** | news.ycombinator.com (İlk 3 HN haberi) | 3 | 2 | 2,220 | $0.000444 | 40.7s | 3 çağrı |
| **R4** | export.arxiv.org (Resmî API makale özeti) | 3 | 6 | 2,941 | $0.000588 | 39.2s | 3 çağrı |
| **R5** | the-internet.herokuapp.com (Dayanıklılık) | 3 | 5 | 1,834 | $0.000108 | 41.6s | 5 çağrı |
| **Toplam** | **5 Canlı Senaryo** | **15** | **38** | **26,969** | **$0.017731** | **362.6s** | **Öğrenme devrede** |

### Nebius Model Yönlendirme Ölçümü (Fast vs Strong)

Özet [docs/NEBIUS_BENCH.md](docs/NEBIUS_BENCH.md) dosyasından alınmıştır:

| Senaryo | Fast (`nvidia/Nemotron-3_5-Lightning`) | Strong (`nvidia/Nemotron-3-Ultra-550b-a55b`) | Tasarruf |
| :--- | :---: | :---: | :---: |
| **R1** | 4.44s · 82 token · $0.000082 | 4.70s · 111 token · $0.000555 | %85 maliyet tasarrufu |
| **R2** | 12.12s · 76 token · $0.000076 | 0.82s · 76 token · $0.000380 | %80 maliyet tasarrufu |
| **R3** | 16.03s · 68 token · $0.000068 | 2.24s · 98 token · $0.000491 | %86 maliyet tasarrufu |

---

## Security Architecture (Güvenlik ve İzolasyon)

Grasshopper is built with a **Containment-First** philosophy designed for unattended execution without risk of financial or data loss:

1. **Hard Spend Ceiling (Bütçe Tavanı):**
   - Enforced by `grasshopper/core/budget.py` (`BudgetLedger`).
   - Default caps: **$0.50 / day** and **$0.05 / run**.
   - The model router calculates an estimate and reserves catalog tokens *before* every API call. If a threshold is crossed, execution stops immediately and a notification is dispatched.
2. **Domain Allowlist & Denylist (İzin ve Engel Listesi):**
   - Enforced by `grasshopper/realweb/policy.py`.
   - Only explicitly approved domains (`REAL_SITES_ALLOWLIST`) can be contacted.
   - High-risk destinations (social networks, OAuth/Google login, payment checkout portals) are permanently blocked in `DENYLIST`.
   - `robots.txt` directives and request rate limits (e.g. 3.0s delay for arXiv) are strictly honored.
3. **Human Approval Gate (İnsan Onay Kapısı):**
   - Any sensitive action (spending Solana, submitting checkout forms, sending external messages) creates a pending row in `/api/approvals`.
   - The agent pauses and waits for explicit approval via the web UI or Telegram bot (`@halil_ops_bot`).
4. **Blast Radius Zero Containment:**
   - Every execution writes `blast_radius.json`, tracking all modified files, contacted network domains, run duration, and token expenditures.
   - Sandbox runners execute inside CPU-, memory-, and network-isolated Docker containers or disposable Vultr cloud instances. *(Dürüstlük notu: Vultr API entegrasyonu gerçek fonlanmış bir hesapta denenmemiştir; yerel sahte sunucu `tests/fakes/vultr_app.py` ve Docker izolasyon testleriyle doğrulanmıştır).*
5. **Kapsam Dışı Güvenlik Sınırları (Out of Scope):**
   - Canlı kredi kartı ve finansal ödemeler, kullanıcı girişi gerektiren gerçek hesaplar (Google login, e-posta) ve sosyal medya platformları (Twitter/X, Meta) hesap ve veri güvenliğini korumak amacıyla kesin olarak kapsam dışı bırakılmıştır (`DENYLIST`). Ayrıntılı gerekçeler için bkz. [docs/COST.md](docs/COST.md).

---

## MCP Server Integration

Grasshopper mounts an official **MCP SDK 2.x Streamable HTTP server** at `/mcp/`. Any MCP-compatible client (including Claude Desktop, Alexa+, or custom agent networks) can inspect and control the agent:

- `run_task`: Queue natural-language browser workflows.
- `get_task_status`: Query live progress and results.
- `list_pending_approvals`: Inspect actions awaiting human sign-off.
- `approve`: Approve or reject gated operations.
- `council_ask`: Consult the multi-persona decision council.
- `store_check_old_listings`: Run automated e-commerce catalog audits.

---

## Turning Real Providers On

Switch from mock mode to live providers by setting keys in `.env` (no code modifications needed):

- **Nebius Token Factory / NVIDIA Nemotron:** `LLM_FAST_PROVIDER=nebius`, `NEBIUS_API_KEY`, `NEBIUS_BASE_URL`, `NEBIUS_FAST_MODEL`.
- **AWS Bedrock:** `LLM_STRONG_PROVIDER=bedrock`, `AWS_REGION`, `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `BEDROCK_MODEL_ID` (`ALLOW_BEDROCK=1` required).
- **Azure OpenAI & Speech:** `LLM_STRONG_PROVIDER=azure`, `AZURE_OPENAI_ENDPOINT`, `AZURE_OPENAI_API_KEY`, `STT_PROVIDER=azure`, `AZURE_SPEECH_KEY`.
- **Tavily Search:** `SEARCH_PROVIDER=tavily`, `TAVILY_API_KEY`.
- **Telegram Notifications:** `TELEGRAM_BOT_TOKEN`, `TELEGRAM_ALLOWED_USER_ID`.
- **Solana Devnet:** `WALLET_PROVIDER=solana_devnet`, `SOLANA_RPC_URL`, `WALLET_KEYPAIR_PATH` (mainnet RPC is strictly refused).

---

## Competitions and Submission Kits

Nothing is submitted automatically. The last step is always a person. Details and enablement steps are in [docs/COMPETITIONS.md](docs/COMPETITIONS.md).

| Competition | Flag | Deadline |
| --- | --- | --- |
| Amazon Alexa+ | `mcp` | 2026-10-23 |
| Amazon AWS Builder | `bedrock` | 2026-10-23 |
| Amazon Open Source | `mit` | 2026-10-23 |
| Nebius x NVIDIA | `nebius` | 2026-10-30 |
| Nebius Tavily bonus | `tavily` | 2026-10-30 |
| Open Agent Hackathon | `explainer` | 2026-10-20 |
| OpenCV AI Competition | `opencv` | 2026-10-26 |
| Colosseum Crypto World's Fair | `solana-devnet` | 2026-10-12 |
| Build With AI: Basics | `prototype` | 2026-10-26 |
| AI GENESIS | `agent` | 2026-11-02 |
| Rise of AI Agents | `agent` | 2026-11-03 |
| Kaggle Gemma 4 paper track | `gemma` | 2026-11-12 |
| HETIC AI Agents for Founders | `founder` | 2026-12-18 |
| Arbiter Hacks V1 | `agent` | 2026-12-21 |
| Microsoft Imagine Cup 2027 | `azure` | 2027-01-08 |
| Meta Global AI Developer Hackathon | `meta` | TBA |
| Vultr Agent Rush | `vultr` | 2026-11-08 |
| IEEE ClimateChain | `climate` | 2026-10-25 |
| YTU x Meta | `meta` | 2026-10-11 |
| ING Hubs | `ing` | 2026-10-04 |
| Kestra Hacktober | `human` | 2026-10-31 |
| ASUS UGen AI League | `asus` | 2026-10-14 |
| Hackster Nordic | `human` | unknown |
| AssemblyAI Voice Agent | `assemblyai` | 2026-09-30 |

Build all kits:

```bash
make kits
```

All kits are generated under `submissions/<competition-slug>/`. **Nothing is submitted automatically. The final submit step is always performed by a human.**

---

## Contributing

We welcome contributions! Please review [CONTRIBUTING.md](CONTRIBUTING.md) for development workflows, testing requirements (`make test` must remain green), and branch policies.

Report bugs or suggest features using our GitHub issue templates:
- [Bug Report](.github/ISSUE_TEMPLATE/bug_report.md)
- [Feature Request](.github/ISSUE_TEMPLATE/feature_request.md)

---

## License

This project is open-source under the [MIT License](LICENSE).
