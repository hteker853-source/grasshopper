# Competition Portfolio, Revenue Model, and Labor Budget (INCOME PLAN)

> [!IMPORTANT]
> **Honesty & Methodology Notice:** The probabilities and Expected Value (EV) calculations in this document are derived from AI jury scorings and correlated Monte Carlo simulations (`scripts/ev_model.py`). They do not represent a financial guarantee; they serve as a strategic planning guide.

---

## 1. Timeline and Cash Potential Across 19 Competitions

| Class | Competition | Deadline | 1st Place (Cash) | Total Pool | Mandatory Sponsor Tech |
| --- | --- | --- | --- | --- | --- |
| **A** | **Amazon Build, Ship, Shape** | Oct 23, 2026 | $25,000 (Alexa+) + $5,000 (OSS) | $54,000 | Alexa+ / MCP Streamable HTTP |
| **A** | **Nebius Token Factory** | Oct 30, 2026 | $20,000 | $45,000 | NVIDIA Nemotron / Token Factory API |
| **A** | **Vultr Agent Rush** | Nov 08, 2026 | $9,000 | $15,000 | Vultr Cloud API / Sandbox Runner |
| **A** | **Open Agent Hackathon** | Oct 20, 2026 | $8,000 | $15,000 | Open Agent Function Calling |
| **B** | **ASUS UGen AI (Stage I)** | Oct 14, 2026 | Stage II Hardware + $10,000 | $20,000 | ROG NPU / Local Edge Inference |
| **B** | **OpenCV AI Competition** | Oct 26, 2026 | $5,000 | $12,000 | OpenCV 5 + AWS Cloud |
| **B** | **Build With AI** | Oct 26, 2026 | $3,000 | $8,000 | Multi-agent Architecture |
| **B** | **ClimateChain** | Oct 31, 2026 | $2,000 | $5,000 | Green Claim Verification + Web3 |
| **B** | **Imagine Cup 2027** | Jan 08, 2027 | $100,000 | $100,000 | Azure AI Foundry + Azure Speech |
| **C** | **ING Hackathon** | Oct 04–09 | Internship / Offer (No Cash) | - | ING Banking Sandbox |
| **C** | **YTU x Meta Llama** | Oct 11, 2026 | ~50,000 TL (~$1,400) | ~$3,000 | Meta Llama 3 (Istanbul In-Person) |
| **C** | **Kestra Automation** | Oct 15, 2026 | Cloud Credits | Credits | Kestra Workflows |
| **C** | **Hackster Nordic** | Oct 20, 2026 | Hardware Kit | Hardware | Nordic nRF54 |
| **C** | **AssemblyAI Voice** | Sep 30, 2026 | $2,500 | $5,000 | AssemblyAI Lemur |
| **C** | **Arbiter Protocol** | Nov 01, 2026 | Credits / Tokens | Credits | Arbiter Consensus |
| **C** | **HETIC Digital** | Nov 15, 2026 | Certificate | - | Paris On-Site |
| **D** | **Gemma Sprint** | Oct 18, 2026 | Credits ($1,000) | Credits | Gemma 2 |
| **D** | **Solana Radar / Colosseum** | Out of Scope | $25,000 | $500,000 | Excluded per devnet rule |

---

## 2. Reality Check on the '$20,000 Average' Assumption

Halil's assumption of *"averaging $20,000 across 19 competitions"* was scrutinized:

1. **Mathematical Impossibility:** An average of $20,000 across 19 hackathons demands **$380,000** in cash winnings. Even if 1st place were won in every eligible hackathon simultaneously, total cash pool is ~$180,000 (excluding Imagine Cup, which requires student eligibility in Jan 2027). Thus, this assumption is **unrealistic**.
2. **Probability of Earning $20,000+ Total Cash:**
   - **Bear Scenario:** 1.1%
   - **Base Scenario:** **2.0%** (Expected Value: **$1,601**)
   - **Bull Scenario:** **2.8%** (Expected Value: **$2,290**)
3. **Crucial Dependencies for $20,000+:**
   - **Amazon ($25,000) and Nebius ($20,000)** represent the financial engine of the portfolio.
   - Without winning 1st place in at least one of these two competitions, reaching $20,000 is mathematically impossible even if all other tier-B/C competitions are won.

---

## 3. Labor Budget (Person-Hours Breakdown)

Total Operator Labor Budget: **60 Hours** (Average 2.5 hours/day over 24 days).

| Category | Hours Budget | Description |
| --- | --- | --- |
| **Amazon Alexa+ & OSS Mini** | 18 hours | Live demo recording, AWS App Runner deployment, Alexa Developer Console portal setup, friction log. |
| **Nebius Token Factory** | 10 hours | Live Nebius API verification, video voiceover, Devpost form submission. |
| **Vultr Agent Rush** | 8 hours | Live Vultr cloud test, sandbox video capture, Devpost entry. |
| **Open Agent** | 8 hours | Oct 15–20 module commits, Tinkerer track video. |
| **ASUS Stage I** | 4 hours | 20-slide presentation PDF conversion, narrated slide capture. |
| **OpenCV AI** | 4 hours | Vision service AWS App Runner test, 2-minute video. |
| **All Others (Forms/Backups)**| 8 hours | Rapid submissions and reserve checks. |
| **TOTAL** | **60 hours** | |

---

## 4. Critical Risks

1. **Disqualification Pitfalls:**
   - *Video Length:* Exceeding 3 minutes by even 1 second results in automatic score zeroing in many hackathons (Amazon, ASUS, Vultr). Mitigation: strictly enforce <= 180s.
   - *Mandatory Sponsor Tech:* Failure to expose MCP on Amazon or Nemotron on Nebius results in exclusion during triage.
   - *Build Timeline Violations:* In Open Agent, commits prior to Oct 15 do not count as new work. Strict adherence to `docs/OPEN_AGENT_PLAN.md` is mandatory.
2. **Sponsor Credentials Risk:**
   - When live Bedrock or Vultr funding is unavailable, the project operates in fake server mode. Transparency rules require stating this openly on submission forms.
3. **On-Site Attendance Conditions:**
   - YTU x Meta (Istanbul in Dec) and HETIC (Paris) require physical attendance. Do not allocate hours unless travel is confirmed.

---

## 5. Strategic Recommendations: Where to Focus

### Focus Competitions (Allocate 90% of Effort):
1. **Amazon Build, Ship, Shape (Oct 23):** Highest EV and cash prize ($30,000 pool). MCP server and Web Speech interface are fully operational.
2. **Nebius Token Factory (Oct 30):** $20,000 1st place cash. Nemotron routing, token budgeting, and zero-cost replay architecture are robust.
3. **Vultr Agent Rush (Nov 08):** $9,000 1st place cash. Blast Radius Zero reporting and sandbox container isolation align with evaluation rubric.
4. **Open Agent Hackathon (Oct 20):** $8,000 1st place cash. Achievable via a clean commit sequence between Oct 15–20.
5. **ASUS UGen AI Stage I (Oct 14):** 20-slide technical presentation ready to submit for Stage II hardware award.

### Definite Passes:
- **Solana Radar / Colosseum:** Mainnet RPC requirement strictly refused per AGENTS.md rules.
- **AssemblyAI:** Sep 30 deadline lacks live keys and test suites; insufficient runway.
- **Kestra, Arbiter, HETIC, Nordic:** No substantial cash prizes (hardware/credits only).
- **ING:** Pass unless a 2nd team member is onboarded for enterprise recruitment track.
