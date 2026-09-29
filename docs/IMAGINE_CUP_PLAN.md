# Imagine Cup 2027 — Dual Azure Services Architecture

Code is not modified by this document. 2027 rules UNVERIFIED.

| Service | Connection Point | Environment Variable / Key | Code Implementation |
| --- | --- | --- | --- |
| Azure AI Foundry / AI Studio | Strong tier (GPT-4o, Phi-3.5, Llama 3.1). Multi-model routing, prompt catalog, and safety filters (Content Safety). | `LLM_STRONG_PROVIDER=azure`, `AZURE_OPENAI_ENDPOINT`, `AZURE_OPENAI_API_KEY`, `AZURE_OPENAI_DEPLOYMENT` | `grasshopper/providers/factory.py` under `azure` branch, `llm_openai_compat.py` |
| Azure AI Speech | Speech-to-text layer. Web microphone and uploaded audio processed here. Whisper or neural voice models. | `STT_PROVIDER=azure`, `AZURE_SPEECH_KEY`, `AZURE_SPEECH_REGION` | `grasshopper/providers/stt_azure.py` |
| Azure Content Safety | Safety audit layer for decision and observation streams. Malicious web payload and prompt injection detection. | `AZURE_CONTENT_SAFETY_KEY`, `AZURE_CONTENT_SAFETY_ENDPOINT` | Extension hook in `grasshopper/realweb/policy.py` |

When API keys are unset, all services execute deterministically in mock mode. Live calls unmeasured. `ALLOW_BEDROCK` is not included in this plan.
