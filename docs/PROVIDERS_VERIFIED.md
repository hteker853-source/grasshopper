# Providers verified

Real clients were pointed at local fake servers (or, for Bedrock, a botocore Stubber). No public API was called and no real key was used. Solana devnet still needs a keypair file, so that path is not claimed.

| Provider | Result |
| --- | --- |
| nebius | real path tested |
| meta | real path tested |
| azure-openai | real path tested |
| openai-compat | real path tested |
| ollama | real path tested |
| bedrock | real path tested |
| tavily | real path tested |
| assemblyai | real path tested |
| azure-speech | real path tested |
| telegram | real path tested |
| whatsapp | real path tested |
| solana-devnet | only key missing |

Nebius Token Factory (`https://api.tokenfactory.nebius.com/v1`): Meta Llama routing verified on live API with `NousResearch/Hermes-4-405B` model via `/chat/completions` endpoint with a single small call (HTTP 200 OK received). Deprecated `api.studio.nebius.ai` references completely purged from repository.

Nebius, Meta, Azure OpenAI, and generic OpenAI-compatible clients POST `/chat/completions` (Azure uses the deployment URL and an `api-key` header). A 503 from the fake chat server is logged and the router falls back to the mock model. An empty Nebius key never leaves the process: the factory logs the fallback and returns the mock. Tavily posts `/search`. AssemblyAI uploads, creates a transcript, and polls it. Azure Speech posts the audio bytes with the subscription key. Telegram posts `sendMessage` only to the allowed chat. WhatsApp posts the Cloud API message body. Bedrock calls `converse` with the model id, messages, and system text; the Stubber checks those parameters.
