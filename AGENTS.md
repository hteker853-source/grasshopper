# Agent notes

- Grasshopper is an open-source (MIT) multi-step browser agent. It runs fully in mock mode with no API key.
- Never read, print or commit .env or any secret. Never send a secret to any service other than its own API.
- Mock is the default. Real providers turn on only through .env, no code change needed.
- `make test` must be green before every commit. Never weaken, delete or skip tests. No placeholder tests.
- Only touch ~/grasshopper. Servers bind to 127.0.0.1 unless told otherwise.
- Never auto-submit to any competition. The final submit is always a human.
- Crypto is devnet only. Mainnet RPC URLs are refused.
- Log one line per decision in docs/DECISIONS.md. Do not ask the user questions, pick the simplest safe option.
- Telegram bot is @halil_ops_bot. It answers only the user id set in .env.
