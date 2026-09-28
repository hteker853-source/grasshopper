# Competitions

Source of truth: [`data/competitions.json`](../data/competitions.json). Generate a kit with:

```bash
.venv/bin/python -m grasshopper.publish.submission_kit --competition amazon-alexa
```

The kit is written to `submissions/<slug>/`. Nothing is submitted automatically.

| Competition | Deadline | Flag | How to turn it on |
| --- | --- | --- | --- |
| Amazon Alexa+ | 2026-10-23 | `mcp` | Ready. `/mcp` and `/alexa`. |
| Amazon AWS Builder | 2026-10-23 | `bedrock` | `LLM_STRONG_PROVIDER=bedrock` plus AWS credentials and `BEDROCK_MODEL_ID`. |
| Amazon Open Source | 2026-10-23 | `mit` | Ready. MIT `LICENSE`. |
| Nebius x NVIDIA | 2026-10-30 | `nebius` | `LLM_FAST_PROVIDER=nebius` plus `NEBIUS_API_KEY`, `NEBIUS_BASE_URL`, `NEBIUS_FAST_MODEL`. |
| Nebius Tavily bonus | 2026-10-30 | `tavily` | `SEARCH_PROVIDER=tavily` and `TAVILY_API_KEY`. |
| Open Agent Hackathon | 2026-10-20 | `explainer` | Ready. `runs/<id>/explain.jsonl`. |
| OpenCV AI Competition | 2026-10-26 | `opencv` | Ready. `opencv-python-headless` 5 in `browser/vision.py`. |
| Colosseum Crypto World's Fair | 2026-10-12 | `solana-devnet` | `WALLET_PROVIDER=solana_devnet` and a devnet keypair. Mainnet RPC is refused. |
| Build With AI: Basics | 2026-10-26 | `prototype` | Ready. |
| AI GENESIS | 2026-11-02 | `agent` | Ready. |
| Rise of AI Agents | 2026-11-03 | `agent` | Ready. Confirm the date with the organizers. |
| Kaggle Gemma 4 paper track | 2026-11-12 | `gemma` | `LLM_REPAIR_PROVIDER=ollama` and `GEMMA_MODEL`. |
| HETIC AI Agents for Founders | 2026-12-18 | `founder` | Ready. Shop and research playbooks. |
| Arbiter Hacks V1 | 2026-12-21 | `agent` | Ready, marked ineligible for the demo profile until independent teams are confirmed. |
| Microsoft Imagine Cup 2027 | 2027-01-08 | `azure` | `LLM_STRONG_PROVIDER=azure` and `STT_PROVIDER=azure` with both key sets. |
| Meta Global AI Developer Hackathon | TBA | `meta` | `LLM_STRONG_PROVIDER=meta` plus `WHATSAPP_*`. |

Hackathon-window work should be tagged `v0.x-<slug>` and described in `submissions/<slug>/CHANGES_DURING_HACKATHON.md`.
