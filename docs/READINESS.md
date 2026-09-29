# Readiness and Win Potential

Date: 2026-09-28. Evidence: `make test` 111 passed, `make audit` 22 ✅ / 8 ⏳ / 0 ❌, `docs/PROVIDERS_VERIFIED.md`, `docs/AUDIT.md`, `submissions/amazon/` drafts, `runs/demo-record` records (`run_ed76f4a16239`, `run_2036d34900f2`, `run_9f24d8fa5fad`), `videos/main_demo.mp4` (audit: 62s).

Probabilities are an ESTIMATE. Intervals do not represent certainty. Unknown items remain marked "unknown". No competition is deemed eliminated or won based on UNVERIFIED notes.

Strengths: 111 green pytest tests in keyless mock mode, official MCP SDK 2.x tests (`tests/test_mcp_official_sdk.py`), 8 digital worker core capabilities (`tests/test_working_core.py`), Web Speech API voice control interface (`/alexa`), 1 fps live preview, risk approval gate, demo video under 3 minutes (62s), blast radius container isolation report, ASUS 20-slide presentation draft.

## 1. Competition Status

| Competition | Status | Solid Working (Evidence) | Missing | Remaining Effort |
| --- | --- | --- | --- | --- |
| Amazon Alexa+ | HUMAN TASK | MCP Streamable HTTP official SDK tests (`test_mcp_official_sdk.py`, `test_s9_mcp_client`), <500ms tool benchmark, `/alexa` Web Speech API voice listen/speak and 1 fps live preview, voice approval card, `make share-mcp` tunnel, video 62s. `docs/DEPLOY_PUBLIC.md` and `docs/ALEXA_ONBOARDING.md`. | Halil must review video and copy. AWS App Runner deploy and portal testing are human tasks. No physical Alexa+ device. | 8–16 hours, human |
| Amazon Open Source mini | HUMAN TASK | MIT `LICENSE`. `make test` 111 green. Audit "LICENSE is MIT" ✅. | Remote and public repo proof (Halil pushing). Application form. | 4–8 hours, human |
| Amazon AWS Builder mini | WAITING FOR KEY | Bedrock `converse` path present via stub (`test_bedrock_converse_is_stubbed`). | `AWS_REGION`, `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `BEDROCK_MODEL_ID`. No live call. | 4–8 hours upon receiving key |
| Nebius x NVIDIA | WAITING FOR KEY | OpenAI-compatible client against mock server, Meta Llama Nebius routing (`test_meta_llama_routing_and_nebius_fallback`), 111 green tests. Live token accounting ($0.0238/41 calls). | Live `NEBIUS_API_KEY` and Nebius Studio model name. Halil video and form submission. | 6–10 hours with key and form |
| Nebius Tavily bonus | WAITING FOR KEY | Tavily fallback and mock search (`test_capability_c_research_and_report_generation`). | Live `TAVILY_API_KEY`. | 1 hour upon receiving key |
| Open Agent Hackathon | HUMAN TASK | MCP tool schemas compliant with Open Agent protocol (`test_nemotron_open_agent_tool_schema_compliance`), 8 digital worker core capabilities. Schedule in `docs/OPEN_AGENT_PLAN.md`. | Visible new commit series required between Oct 15–20. Registration Oct 13. | 15–25 hours during window |
| OpenCV AI Competition | RULE UNCERTAIN | OpenCV 5 diffs and bounding regions (`test_vision_finds_button`), `test_vision_service.py`, `docs/OPENCV_AWS.md` deployment steps. | Halil must set up AWS account and execute service. | 4–8 hours |
| Vultr Agent Rush | RULE UNCERTAIN | `LocalRunner`, Docker limits, fake Vultr API lifecycle, blast radius report generation (`test_vultr_blast_radius_report_generation`). Honesty disclaimer present. | Not tested on real account (fake server test). Creating live Vultr box rests with Halil. | 6–10 hours |
| ASUS UGen AI League | HUMAN TASK | `submissions/asus/PRESENTATION.md` 20-slide presentation ready. 62s video ready. | Slide voiceover, YouTube upload. | 3–4 hours human |
| ING Hubs | HUMAN TASK | Agent skeleton in place. | Registration Oct 4, 2-person team, challenges unknown until Oct 9. Hardware prize. | Registration a few hours; code estimate pending challenge |
| Kestra Hacktober | HUMAN TASK | No Kestra PR in this repository. | Merged author-written Kestra PRs. Outside this product scope. | Separate task, no hourly estimate |
| YTU x Meta | HUMAN TASK | Meta and WhatsApp clients on fake server. | Registration, training, Dec onsite hackathon in Istanbul. Student requirement not explicit in briefing; onsite presence is human. | Registration a few hours; hackathon week separate |
| Imagine Cup 2027 | RULE UNCERTAIN | Azure OpenAI and Azure Speech on fake server (`test_azure_openai_sends_api_key_header_not_bearer`, `test_azure_speech_posts_the_audio_and_key`). | Missing live keys for both services. 2027 rules UNVERIFIED. | 16–30 hours post-key and rule verification |
| Kaggle Gemma 4 | WAITING FOR KEY | Ollama client with fake `/api/generate`. Repair patch generated in S7 but not applied. | `GEMMA_MODEL` empty. Weak alignment: paper or Kaggle contest is not this sandbox demo. | Low alignment; 30+ hours and still weak |
| Build With AI Basics | HUMAN TASK | End-to-end sandbox demo and 68 tests. Audit prototype ✅. | Application form and human approval. | 4–8 hours |
| AssemblyAI Voice Agent | WAITING FOR KEY | AssemblyAI upload+transcript on fake server. | 2 days to Sep 30. No `ASSEMBLYAI_API_KEY`. Product is not a dedicated voice agent demo; STT defaults to mock. | Cannot close in remaining window with this demo |
| HETIC | HUMAN TASK | Shop and research playbooks (`test_s3_old_listings`, `test_s1_account_research_share`). | Application. Small prize pool. | 4–6 hours |
| Arbiter | HUMAN TASK | Agent code present. | `eligible=false` in `data/competitions.json`. No independent team confirmation. | Do not enter |
| Colosseum | HUMAN TASK | Devnet wallet code and mainnet refusal (`test_mainnet_refused`). | Decision: will not enter. Missing key. | 0, SKIP |

## 2. Probabilities (ESTIMATE)

Even where participant counts are reported, distribution within tracks is unknown. Interval applies to "as-is, with sandbox demo, submitted on time".

- Amazon Alexa+ $25,000: <1%. Roughly 15,800 participants. Jury evaluates design and impact. MCP and simulated page satisfy technical checks; impact is moderate without physical Alexa+ hardware and live third-party sites. $15,000 and $4,000 tiers also <1%. Track participant breakdown unknown; top 3 across thousands remains between <1% and 1–3%. No evidence supports claiming upper bounds, hence <1%.
- Amazon Open Source mini $5,000: 1–3%. Technical requirements (MIT, passing tests) met. Public repo and form pending. Total mini entrants unknown.
- Amazon AWS mini $5,000: <1% today. No live Bedrock calls.
- Nebius 1st place $20,000 and other tiers: <1%. Entrant count unknown. No live Nebius + NVIDIA models connected. That is the fundamental prerequisite of the contest.
- Tavily $3,000: <1% keyless. Even with key, search plays a secondary role in this demo.
- Open Agent $8,000 / $4,000 / $2,000: <1% with current repo because score rewards newly authored work and ~1,200 participants are registered. If visible new modules ship during the window, 1–3% is possible; this is an ESTIMATE.
- OpenCV $5,000 and lower tiers: no figure given since rules are UNVERIFIED. If proposal phase was missed, probability is 0. If open and without AWS, still <1%.
- Vultr $5,000 cash: rules UNVERIFIED. Theme aligns well with codebase. No records of execution on real Vultr instances. Early for an ESTIMATE; upper bound 1–3% if rules match our theme and execution works on Vultr, otherwise <1%.
- IEEE $1,500: <1%, and likely near 0. Project is not climate-specific. Student and Turkey eligibility UNVERIFIED.
- ASUS $4,500: <1%. Hardware integration absent.
- ING hardware prize: challenge unknown, 2-person team and registration are human tasks. Probability unknown.
- Kestra hardware/gift card: no relationship with this repo. <1%.
- YTU $6,000 pool: onsite student hackathon. Bringing this demo alone is insufficient. Probability unknown; no evidence for remote participation.
- Imagine Cup $100,000: <1%. Rules UNVERIFIED, two live Microsoft services unlinked, date distant.
- Gemma $37,000 / $35,000: <1%. Weak alignment and unlinked model.
- Build With AI $2,500: 3–8%. Entrant volume unknown. Existing prototype matches criteria well; jury may still view sandbox as narrow, so not claiming 15%+.
- AssemblyAI $5,000 cash: <1%. Two days remain and voice agent demo is absent.
- HETIC $1,100: 1–3%. Small scope, unknown volume, working demo playbooks.
- Arbiter $3,800: <1%. `eligible=false` in JSON.

Win probability is limited across several contests due to lack of non-sandbox evidence: Nebius, Gemma, OpenCV (without AWS), AssemblyAI Voice Agent, IEEE, ASUS, Imagine Cup 1st, Amazon Alexa+ 1st. No certainty is claimed anywhere.

## 3. Table by Prize Size

Expected value = probability interval × cash prize. Upper bound 1% used for <1%, lower bound 0. Non-cash prizes excluded from cash multiplication.

| Competition | Prize | Probability Interval | Expected Value | Remaining Effort | Recommendation |
| --- | --- | --- | --- | --- | --- |
| Imagine Cup 2027 | $100,000 | <1% | $0–$1,000 | 16–30 hours | SKIP (for now) |
| Kaggle Gemma main | $37,000 | <1% | $0–$370 | 30+ hours | SKIP |
| Gemma Paper | $35,000 | <1% | $0–$350 | 30+ hours | SKIP |
| Amazon Alexa+ 1st | $25,000 | <1% | $0–$250 | 8–16 hours | PRIORITY (as track, not 1st) |
| Nebius 1st | $20,000 | <1% | $0–$200 | 12–24 hours | SKIP (keyless) |
| Amazon Alexa+ 2nd | $15,000 | <1% | $0–$150 | same submission | PRIORITY |
| Open Agent 1st | $8,000 | <1% (1–3% with new work) | $0–$240 | 20–40 hours | BONUS |
| YTU x Meta pool | $6,000 | unknown | uncalculated | registration | BONUS (if onsite) |
| Amazon AWS mini | $5,000 | <1% | $0–$50 | 4–8 hours | BONUS (if key provided) |
| Amazon OSS mini | $5,000 | 1–3% | $50–$150 | 4–8 hours | PRIORITY |
| OpenCV 1st | $5,000 | rule uncertain | uncalculated | 8–16 hours | SKIP (unconfirmed) |
| Vultr 1st cash | $5,000 | rule uncertain; 1–3% if theme matches | $0–$150 | 8–16 hours | BONUS |
| AssemblyAI cash | $5,000 | <1% | $0–$50 | infeasible | SKIP |
| ASUS Lightning | $4,500 | <1% | $0–$45 | 40 hours + device | SKIP |
| Amazon Alexa+ 3rd | $4,000 | <1% | $0–$40 | same submission | PRIORITY |
| Arbiter | $3,800 | <1% | $0–$38 | — | SKIP |
| Nebius Tavily | $3,000 | <1% | $0–$30 | 2–4 hours | BONUS |
| Build With AI Basics | $2,500 | 3–8% | $75–$200 | 4–8 hours | PRIORITY |
| Open Agent 2nd / 3rd | $4,000 / $2,000 | <1% | $0–$40 | window | BONUS |
| IEEE 1st | $1,500 | <1% | $0–$15 | misaligned | SKIP |
| HETIC | $1,100 | 1–3% | $11–$33 | 4–6 hours | BONUS |
| Kestra card | $150 or device | <1% | non-cash | separate work | SKIP |
| ING | MacBook / iPad / watch | unknown | non-cash | registration | BONUS (if team formed) |
| Colosseum | — | will not enter | 0 | 0 | SKIP |

Alexa+ rows share the same submission package. Due to the track + single mini constraint, AWS and OSS cannot be co-selected. OSS is preferred as it requires no API key.

## 4. Realistic Targets

Highest probability, though modest:

1. Amazon Open Source mini ($5,000) — technical requirements met in repository; public repo and form submission are human tasks. Interval 1–3%.
2. Entering the Amazon Alexa+ track — MCP and simulated page tested. Cash prize interval <1%; serves as the primary showcase for the package. Single submission with one mini.
3. Build With AI Basics ($2,500) — existing prototype fits criteria. Interval 3–8%. Entrant volume unknown.
4. HETIC ($1,100) — working playbook demo, small prize pool. Interval 1–3%.
5. Open Agent, only if a new module ships Oct 15–20. Distant with current codebase.

Distant possibilities: Nebius 1st place, Gemma, Imagine Cup $100,000, OpenCV (proposal phase unconfirmed), Alexa+ 1st place, AssemblyAI (window and voice), ASUS (hardware), IEEE (topic and country eligibility).

## 5. Outstanding Technical Tasks

Engineering tasks in priority order:

1. Nothing non-public is "published" through code alone; this task is human. Engineering package ready: tests, MIT, MCP, video assets.
2. Executing real commands on Vultr (via SSH or their provided pathway once `docs/rules/vultr.md` is confirmed). Instance create/destroy exists; remote docker execution absent.
3. Deploying the vision service to AWS, per the OpenCV requirement. Service and Dockerfile exist; cloud deployment pending.
4. Live provider smoke tests once keys are added to `.env`: Nebius, Tavily, Bedrock, Azure, AssemblyAI, Gemma. Client pathways verified on mock server; live account verification pending.

Human action items:

1. Making the repo public and submitting application forms. The agent does not submit.
2. Reviewing `submissions/amazon/` drafts (video script, friction log, description).
3. Mini selection: OSS (keyless) recommended. AWS only if key and 30-second live Bedrock clip exist.
4. ING application by Oct 4 with a 2nd teammate; no coding prior to challenge announcement.
5. If entering Open Agent, performing all commits strictly inside the Oct 15–20 window.
6. Confirming rules for OpenCV and Vultr without locking to UNVERIFIED dates.
7. Avoiding spent effort on Colosseum, Arbiter, IEEE, ASUS, Gemma, AssemblyAI Voice Agent.

## Live Link

Dashboard does not bind outside 127.0.0.1 by default. Run `make share` for tunnel. `SHARE_MINUTES` defaults to 60. Run `make unshare` to terminate. Token is never printed to terminal; link is dispatched exclusively to the authorized Telegram user.
