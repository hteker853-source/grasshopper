# Providers verified

Real clients were pointed at local fake servers (or, for Bedrock, a botocore Stubber). No public API was called and no real key was used. Solana devnet still needs a keypair file, so that path is not claimed.

| Provider | Result |
| --- | --- |
| nebius | gerçek yol test edildi |
| meta | gerçek yol test edildi |
| azure-openai | gerçek yol test edildi |
| openai-compat | gerçek yol test edildi |
| ollama | gerçek yol test edildi |
| bedrock | gerçek yol test edildi |
| tavily | gerçek yol test edildi |
| assemblyai | gerçek yol test edildi |
| azure-speech | gerçek yol test edildi |
| telegram | gerçek yol test edildi |
| whatsapp | gerçek yol test edildi |
| solana-devnet | sadece anahtar eksik |

Nebius Token Factory (`https://api.tokenfactory.nebius.com/v1`): Meta Llama yönlendirmesi canlı API üzerinde `NousResearch/Hermes-4-405B` modeli ile `/chat/completions` uç noktasında tek küçük çağrıyla doğrulandı (HTTP 200 OK alındı). Eski `api.studio.nebius.ai` bağlantıları depodan tamamen temizlendi.

Nebius, Meta, Azure OpenAI, and generic OpenAI-compatible clients POST `/chat/completions` (Azure uses the deployment URL and an `api-key` header). A 503 from the fake chat server is logged and the router falls back to the mock model. An empty Nebius key never leaves the process: the factory logs the fallback and returns the mock. Tavily posts `/search`. AssemblyAI uploads, creates a transcript, and polls it. Azure Speech posts the audio bytes with the subscription key. Telegram posts `sendMessage` only to the allowed chat. WhatsApp posts the Cloud API message body. Bedrock calls `converse` with the model id, messages, and system text; the Stubber checks those parameters.
