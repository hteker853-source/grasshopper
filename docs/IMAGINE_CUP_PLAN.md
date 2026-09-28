# Imagine Cup 2027 — iki Azure servisi

Kod bu dosyayla değişmez. 2027 kuralları DOĞRULANMADI.

| Servis | Nereye bağlanır | Anahtar | Kod |
| --- | --- | --- | --- |
| Azure AI Foundry / AI Studio | Güçlü katman (GPT-4o, Phi-3.5, Llama 3.1). Çoklu model yönetimi, prompt catalog ve güvenlik filtresi (Content Safety). | `LLM_STRONG_PROVIDER=azure`, `AZURE_OPENAI_ENDPOINT`, `AZURE_OPENAI_API_KEY`, `AZURE_OPENAI_DEPLOYMENT` | `grasshopper/providers/factory.py` içinde `azure` dalı, `llm_openai_compat.py` |
| Azure AI Speech | Konuşmayı metne çeviren katman. Web mikrofonu ve yüklenen ses buraya gider. Whisper veya neural voice modelleri. | `STT_PROVIDER=azure`, `AZURE_SPEECH_KEY`, `AZURE_SPEECH_REGION` | `grasshopper/providers/stt_azure.py` |
| Azure Content Safety | Karar ve gözlem katmanında güvenlik denetimi. Zararlı web içeriği veya prompt injection tespiti. | `AZURE_CONTENT_SAFETY_KEY`, `AZURE_CONTENT_SAFETY_ENDPOINT` | `grasshopper/realweb/policy.py` genişletme yuvası |

Anahtar boşsa tüm servisler mock çalışır. Canlı çağrı ölçülmedi. `ALLOW_BEDROCK` bu plana dahil değil.

