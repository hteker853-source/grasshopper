# Jury Scorecard

> [!IMPORTANT]
> **Honesty and Methodology Notice:** The scores in this scorecard originate from an AI model (5 virtual personas via Nebius Nemotron Ultra 550B: technical, product, design, impact, skeptic) rather than a human jury panel. The calculated Expected Value (EV) and winning probabilities are circular with respect to these AI scores; human jury evaluations and real contest dynamics may differ substantially. Scores are ESTIMATES, not measurements.

Date: 2026-09-28. Scores are ESTIMATES. Five personas (technical, product, design, impact, skeptic) scored 0–10. Criterion score is their average. Weighted score = Σ(average × weight) / Σ weight.

Class A target is weighted score ≥ 8.0, Class B ≥ 7.0. Current evidence does not meet these targets. Scores have not been inflated.

Before: estimate before this round's loop, budget gate, and dashboard panels. After: with those components in place. Impact was not raised without live benchmark measurements.

## amazon (A)

Rubric: official, equal 25%. Before 7.00. After 7.35.

| Criterion | Weight | technical | product | design | impact | skeptic | Average |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Tech Implementation | 25 | 9 | 8 | 7 | 8 | 6 | 7.60 |
| evidence | | MCP SDK 2.x Streamable HTTP mounted at /mcp/ with 7 tools, 97 passing pytest tests, hard budget ledger enforced, live Nebius Nemotron loop. | | | | | |
| Design | 25 | 8 | 7 | 8 | 8 | 6 | 7.40 |
| evidence | | tests/test_dashboard_ux.py (#learning, #savings, #isolated, viewport responsive) and docs/UX_EVALUATION.md heuristic evaluation simulated with AI personas (not real user testing) prepared. | | | | | |
| Potential Impact | 25 | 8 | 8 | 7 | 9 | 5 | 7.40 |
| evidence | | docs/RELIABILITY_REAL.md: $0.0238 spend measured on 5 real sites, approval gates, zero LLM call playbook replay on second run. | | | | | |
| Quality of the Idea | 25 | 8 | 8 | 6 | 8 | 5 | 7.00 |
| evidence | | Approval gate architecture, budget ledger, docs/FRICTION_LOG.md real SDK/Playwright friction records. | | | | | |

Lowest three criteria, by gain/effort order:

1. Quality of the Idea (7.00). Evidence boundary defined above.
2. Design (7.40). Evidence boundary defined above.
3. Potential Impact (7.40). Evidence boundary defined above.

| Place | Base | Score multiplier | p |
| --- | --- | --- | --- |
| Alexa+ 1st | 0.005 | 1.50 | 0.0075 |
| Alexa+ 2nd | 0.008 | 1.50 | 0.0120 |
| Alexa+ 3rd | 0.010 | 1.50 | 0.0150 |
| OSS mini | 0.020 | 1.50 | 0.0300 |

p = base × min(3, (score/6)²). ESTIMATE.

## nebius (A)

Rubric: official, equal 25%. Before 7.75. After 7.75.

| Criterion | Weight | technical | product | design | impact | skeptic | Average |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Technological Implementation | 25 | 9 | 8 | 7 | 8 | 7 | 7.80 |
| evidence | | Live Nebius Token Factory (Nemotron 3.5 Lightning & Nemotron Ultra 550B), invoiced dollar/token accounting ($0.0238/41 calls), 97 green tests. | | | | | |
| Design | 25 | 8 | 8 | 9 | 8 | 6 | 7.80 |
| evidence | | Dashboard learning curve bar chart, savings panel, live stream feed, and responsive layout. | | | | | |
| Potential Impact | 25 | 8 | 9 | 8 | 9 | 5 | 7.80 |
| evidence | | Playbook caching and budget cap proving marginal model cost is zeroed on repeated tasks. | | | | | |
| Quality of the Idea | 25 | 9 | 8 | 7 | 8 | 6 | 7.60 |
| evidence | | Two-tier routing (fast default, strong on repair), CV fallback DOM recovery. | | | | | |

Lowest three criteria, by gain/effort order:

1. Quality of the Idea (7.60). Evidence boundary defined above.
2. Technological Implementation (7.80). Evidence boundary defined above.
3. Design (7.80). Evidence boundary defined above.

| Place | Base | Score multiplier | p |
| --- | --- | --- | --- |
| 1st | 0.005 | 1.67 | 0.0083 |
| 2nd | 0.008 | 1.67 | 0.0133 |
| 3rd | 0.010 | 1.67 | 0.0167 |
| Tavily | 0.010 | 1.67 | 0.0167 |

p = base × min(3, (score/6)²). ESTIMATE.

## open-agent (A)

Rubric: briefing, no official page. Before 6.32. After 6.48.

| Criterion | Weight | technical | product | design | impact | skeptic | Average |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Impact | 30 | 6 | 7 | 5 | 8 | 4 | 6.00 |
| evidence | | Safe browser automation via allowlist and approval gate; docs/OPEN_AGENT_PLAN.md Tinkerer schedule. | | | | | |
| Technical | 20 | 8 | 7 | 5 | 7 | 6 | 6.60 |
| evidence | | Multi-agent council consensus (council_ask), reasoning traces (explain.jsonl), 97 passing tests. | | | | | |
| Innovation | 15 | 8 | 7 | 5 | 8 | 5 | 6.60 |
| evidence | | Zero-cost playbook playback on rerun, hard budget protection. | | | | | |
| Demo | 15 | 6 | 7 | 7 | 7 | 4 | 6.20 |
| evidence | | 62-second video videos/demo.mp4; dashboard, learning curve, and protection demo. | | | | | |
| Product & UX | 10 | 7 | 8 | 8 | 7 | 5 | 7.00 |
| evidence | | Run overview, live frames, step targets, and budget metrics. | | | | | |
| Sponsor Tech | 10 | 9 | 8 | 6 | 8 | 6 | 7.40 |
| evidence | | tests/test_nemotron_sponsor.py proves NVIDIA Nemotron integration, Open Agent function schema, and two-tier pricing. | | | | | |

Lowest three criteria, by gain/effort order:

1. Impact (6.00). Evidence boundary defined above.
2. Demo (6.20). Evidence boundary defined above.
3. Technical (6.60). Evidence boundary defined above.

| Place | Base | Score multiplier | p |
| --- | --- | --- | --- |
| 1st | 0.005 | 1.17 | 0.0058 |
| 2nd | 0.008 | 1.17 | 0.0093 |
| 3rd | 0.010 | 1.17 | 0.0117 |

p = base × min(3, (score/6)²). ESTIMATE.

## vultr (A)

Rubric: default rubric. Before 6.15. After 6.50.

| Criterion | Weight | technical | product | design | impact | skeptic | Average |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Application of Technology | 25 | 8 | 8 | 6 | 7 | 6 | 7.00 |
| evidence | | tests/test_vultr_sandbox.py: VultrAPI lifecycle (get, list, user_data), error recovery, sandbox cleanup, and isolated execution proven by tests. | | | | | |
| Presentation | 25 | 6 | 7 | 6 | 6 | 4 | 5.80 |
| evidence | | Isolation moment in 62s video videos/demo.mp4, docs/rules/vultr.md full rule documentation. | | | | | |
| Business Value | 25 | 7 | 8 | 5 | 8 | 5 | 6.60 |
| evidence | | Enterprise safety via hard budget stop ($0.50/$0.05), allow/denylist, approval gate on sensitive actions. | | | | | |
| Originality | 25 | 7 | 8 | 6 | 7 | 5 | 6.60 |
| evidence | | Blast Radius Zero architecture logging touched files, domains, duration, and spend in blast_radius.json for each run. | | | | | |

Lowest three criteria, by gain/effort order:

1. Presentation (5.80). Evidence boundary defined above.
2. Business Value (6.60). Evidence boundary defined above.
3. Originality (6.60). Evidence boundary defined above.

| Place | Base | Score multiplier | p |
| --- | --- | --- | --- |
| 1st cash | 0.010 | 1.17 | 0.0117 |
| 2nd cash | 0.015 | 1.17 | 0.0176 |
| 3rd cash | 0.020 | 1.17 | 0.0235 |

p = base × min(3, (score/6)²). ESTIMATE.

## opencv (B)

Rubric: official OpenCV weights. Before 3.62. After 4.42.

| Criterion | Weight | technical | product | design | impact | skeptic | Average |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Technical execution | 30 | 7 | 6 | 5 | 5 | 5 | 5.60 |
| evidence | | test_vision_finds_button and test_vision_change_and_dom_recovery_are_measured. OpenCV 5 pinned. | | | | | |
| Innovation | 20 | 6 | 5 | 5 | 4 | 4 | 4.80 |
| evidence | | Continue button selection via vision upon selector break measured on controlled dataset. | | | | | |
| Real-world impact | 20 | 4 | 3 | 3 | 3 | 2 | 3.00 |
| evidence | | Live third-party page not intentionally broken. Impact unmeasured. | | | | | |
| User experience | 10 | 6 | 5 | 6 | 4 | 4 | 5.00 |
| evidence | | Repair halts on human approval. No standalone vision UI. | | | | | |
| Documentation and presentation | 10 | 6 | 5 | 5 | 4 | 4 | 4.80 |
| evidence | | docs/AGENTIC_VISION.md and docs/OPENCV_AWS.md. | | | | | |
| Responsible cloud delivery | 10 | 2 | 2 | 2 | 2 | 2 | 2.00 |
| evidence | | Account not opened. Steps documented, deployment unmeasured. | | | | | |

Lowest three criteria, by gain/effort order:

1. Responsible cloud delivery (2.00). Evidence boundary defined above.
2. Real-world impact (3.00). Evidence boundary defined above.
3. Innovation (4.80). Evidence boundary defined above.

| Place | Base | Score multiplier | p |
| --- | --- | --- | --- |
| 1st | 0.010 | 0.54 | 0.0054 |
| 2nd | 0.012 | 0.54 | 0.0065 |
| 3rd | 0.015 | 0.54 | 0.0081 |
| Agentic Vision | 0.020 | 0.54 | 0.0109 |

p = base × min(3, (score/6)²). ESTIMATE.

## build-with-ai (B)

Rubric: default rubric. Before 3.34. After 3.98.

| Criterion | Weight | technical | product | design | impact | skeptic | Average |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Technical | 25 | 6 | 5 | 4 | 4 | 4 | 4.60 |
| evidence | | make test passes without keys. Prototype satisfies core condition. Headcount unknown. | | | | | |
| Innovation | 20 | 5 | 4 | 4 | 3 | 3 | 3.80 |
| evidence | | make test passes without keys. Prototype satisfies core condition. Headcount unknown. | | | | | |
| Impact | 20 | 3 | 3 | 2 | 2 | 2 | 2.40 |
| evidence | | make test passes without keys. Prototype satisfies core condition. Headcount unknown. | | | | | |
| Demo | 20 | 5 | 5 | 4 | 4 | 3 | 4.20 |
| evidence | | make test passes without keys. Prototype satisfies core condition. Headcount unknown. | | | | | |
| UX | 15 | 6 | 5 | 6 | 4 | 4 | 5.00 |
| evidence | | make test passes without keys. Prototype satisfies core condition. Headcount unknown. | | | | | |

Lowest three criteria, by gain/effort order:

1. Impact (2.40). Evidence boundary defined above.
2. Innovation (3.80). Evidence boundary defined above.
3. Demo (4.20). Evidence boundary defined above.

| Place | Base | Score multiplier | p |
| --- | --- | --- | --- |
| 1st | 0.050 | 0.44 | 0.0220 |

p = base × min(3, (score/6)²). ESTIMATE.

## hetic (B)

Rubric: default rubric. Before 3.34. After 3.98.

| Criterion | Weight | technical | product | design | impact | skeptic | Average |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Technical | 25 | 6 | 5 | 4 | 4 | 4 | 4.60 |
| evidence | | playbooks/shop_old_listings.yaml and test_s3_old_listings. | | | | | |
| Innovation | 20 | 5 | 4 | 4 | 3 | 3 | 3.80 |
| evidence | | playbooks/shop_old_listings.yaml and test_s3_old_listings. | | | | | |
| Impact | 20 | 3 | 3 | 2 | 2 | 2 | 2.40 |
| evidence | | playbooks/shop_old_listings.yaml and test_s3_old_listings. | | | | | |
| Demo | 20 | 5 | 5 | 4 | 4 | 3 | 4.20 |
| evidence | | playbooks/shop_old_listings.yaml and test_s3_old_listings. | | | | | |
| UX | 15 | 6 | 5 | 6 | 4 | 4 | 5.00 |
| evidence | | playbooks/shop_old_listings.yaml and test_s3_old_listings. | | | | | |

Lowest three criteria, by gain/effort order:

1. Impact (2.40). Evidence boundary defined above.
2. Innovation (3.80). Evidence boundary defined above.
3. Demo (4.20). Evidence boundary defined above.

| Place | Base | Score multiplier | p |
| --- | --- | --- | --- |
| 1st | 0.020 | 0.44 | 0.0088 |

p = base × min(3, (score/6)²). ESTIMATE.

## climatechain (B)

Rubric: default rubric. Before 3.34. After 3.98.

| Criterion | Weight | technical | product | design | impact | skeptic | Average |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Technical | 25 | 6 | 5 | 4 | 4 | 4 | 4.60 |
| evidence | | grasshopper/realweb/climate.py only records text present on page. Not a dedicated climate product. | | | | | |
| Innovation | 20 | 5 | 4 | 4 | 3 | 3 | 3.80 |
| evidence | | grasshopper/realweb/climate.py only records text present on page. Not a dedicated climate product. | | | | | |
| Impact | 20 | 3 | 3 | 2 | 2 | 2 | 2.40 |
| evidence | | grasshopper/realweb/climate.py only records text present on page. Not a dedicated climate product. | | | | | |
| Demo | 20 | 5 | 5 | 4 | 4 | 3 | 4.20 |
| evidence | | grasshopper/realweb/climate.py only records text present on page. Not a dedicated climate product. | | | | | |
| UX | 15 | 6 | 5 | 6 | 4 | 4 | 5.00 |
| evidence | | grasshopper/realweb/climate.py only records text present on page. Not a dedicated climate product. | | | | | |

Lowest three criteria, by gain/effort order:

1. Impact (2.40). Evidence boundary defined above.
2. Innovation (3.80). Evidence boundary defined above.
3. Demo (4.20). Evidence boundary defined above.

| Place | Base | Score multiplier | p |
| --- | --- | --- | --- |
| 1st | 0.005 | 0.44 | 0.0022 |

p = base × min(3, (score/6)²). ESTIMATE.

## ytu-meta (B)

Rubric: default rubric. Before 3.34. After 3.98.

| Criterion | Weight | technical | product | design | impact | skeptic | Average |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Technical | 25 | 6 | 5 | 4 | 4 | 4 | 4.60 |
| evidence | | Onsite hackathon. $6,000 pool. Individual share unknown, excluded from EV. | | | | | |
| Innovation | 20 | 5 | 4 | 4 | 3 | 3 | 3.80 |
| evidence | | Onsite hackathon. $6,000 pool. Individual share unknown, excluded from EV. | | | | | |
| Impact | 20 | 3 | 3 | 2 | 2 | 2 | 2.40 |
| evidence | | Onsite hackathon. $6,000 pool. Individual share unknown, excluded from EV. | | | | | |
| Demo | 20 | 5 | 5 | 4 | 4 | 3 | 4.20 |
| evidence | | Onsite hackathon. $6,000 pool. Individual share unknown, excluded from EV. | | | | | |
| UX | 15 | 6 | 5 | 6 | 4 | 4 | 5.00 |
| evidence | | Onsite hackathon. $6,000 pool. Individual share unknown, excluded from EV. | | | | | |

Lowest three criteria, by gain/effort order:

1. Impact (2.40). Evidence boundary defined above.
2. Innovation (3.80). Evidence boundary defined above.
3. Demo (4.20). Evidence boundary defined above.

## imagine-cup (B)

Rubric: default rubric. Before 3.34. After 3.98.

| Criterion | Weight | technical | product | design | impact | skeptic | Average |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Technical | 25 | 6 | 5 | 4 | 4 | 4 | 4.60 |
| evidence | | docs/IMAGINE_CUP_PLAN.md. Two Azure services not wired. 2027 rules UNVERIFIED. | | | | | |
| Innovation | 20 | 5 | 4 | 4 | 3 | 3 | 3.80 |
| evidence | | docs/IMAGINE_CUP_PLAN.md. Two Azure services not wired. 2027 rules UNVERIFIED. | | | | | |
| Impact | 20 | 3 | 3 | 2 | 2 | 2 | 2.40 |
| evidence | | docs/IMAGINE_CUP_PLAN.md. Two Azure services not wired. 2027 rules UNVERIFIED. | | | | | |
| Demo | 20 | 5 | 5 | 4 | 4 | 3 | 4.20 |
| evidence | | docs/IMAGINE_CUP_PLAN.md. Two Azure services not wired. 2027 rules UNVERIFIED. | | | | | |
| UX | 15 | 6 | 5 | 6 | 4 | 4 | 5.00 |
| evidence | | docs/IMAGINE_CUP_PLAN.md. Two Azure services not wired. 2027 rules UNVERIFIED. | | | | | |

Lowest three criteria, by gain/effort order:

1. Impact (2.40). Evidence boundary defined above.
2. Innovation (3.80). Evidence boundary defined above.
3. Demo (4.20). Evidence boundary defined above.

| Place | Base | Score multiplier | p |
| --- | --- | --- | --- |
| grand | 0.002 | 0.44 | 0.0009 |

p = base × min(3, (score/6)²). ESTIMATE.

## gemma (B)

Rubric: default rubric. Before 3.34. After 3.98.

| Criterion | Weight | technical | product | design | impact | skeptic | Average |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Technical | 25 | 6 | 5 | 4 | 4 | 4 | 4.60 |
| evidence | | Weak alignment. GEMMA_MODEL empty. test_ollama_generate_body fake server. | | | | | |
| Innovation | 20 | 5 | 4 | 4 | 3 | 3 | 3.80 |
| evidence | | Weak alignment. GEMMA_MODEL empty. test_ollama_generate_body fake server. | | | | | |
| Impact | 20 | 3 | 3 | 2 | 2 | 2 | 2.40 |
| evidence | | Weak alignment. GEMMA_MODEL empty. test_ollama_generate_body fake server. | | | | | |
| Demo | 20 | 5 | 5 | 4 | 4 | 3 | 4.20 |
| evidence | | Weak alignment. GEMMA_MODEL empty. test_ollama_generate_body fake server. | | | | | |
| UX | 15 | 6 | 5 | 6 | 4 | 4 | 5.00 |
| evidence | | Weak alignment. GEMMA_MODEL empty. test_ollama_generate_body fake server. | | | | | |

Lowest three criteria, by gain/effort order:

1. Impact (2.40). Evidence boundary defined above.
2. Innovation (3.80). Evidence boundary defined above.
3. Demo (4.20). Evidence boundary defined above.

| Place | Base | Score multiplier | p |
| --- | --- | --- | --- |
| paper | 0.002 | 0.44 | 0.0009 |

p = base × min(3, (score/6)²). ESTIMATE.

## assemblyai (B)

Rubric: default rubric. Before 3.34. After 3.98.

| Criterion | Weight | technical | product | design | impact | skeptic | Average |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Technical | 25 | 6 | 5 | 4 | 4 | 4 | 4.60 |
| evidence | | No voice agent demo. No key. Window too short. | | | | | |
| Innovation | 20 | 5 | 4 | 4 | 3 | 3 | 3.80 |
| evidence | | No voice agent demo. No key. Window too short. | | | | | |
| Impact | 20 | 3 | 3 | 2 | 2 | 2 | 2.40 |
| evidence | | No voice agent demo. No key. Window too short. | | | | | |
| Demo | 20 | 5 | 5 | 4 | 4 | 3 | 4.20 |
| evidence | | No voice agent demo. No key. Window too short. | | | | | |
| UX | 15 | 6 | 5 | 6 | 4 | 4 | 5.00 |
| evidence | | No voice agent demo. No key. Window too short. | | | | | |

Lowest three criteria, by gain/effort order:

1. Impact (2.40). Evidence boundary defined above.
2. Innovation (3.80). Evidence boundary defined above.
3. Demo (4.20). Evidence boundary defined above.

| Place | Base | Score multiplier | p |
| --- | --- | --- | --- |
| cash | 0.002 | 0.44 | 0.0009 |

p = base × min(3, (score/6)²). ESTIMATE.

## asus (B)

Rubric: default rubric. Before 3.34. After 3.98.

| Criterion | Weight | technical | product | design | impact | skeptic | Average |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Technical | 25 | 6 | 5 | 4 | 4 | 4 | 4.60 |
| evidence | | submissions/asus/PRESENTATION.md. UGen300 unavailable. Hardware unmeasured. | | | | | |
| Innovation | 20 | 5 | 4 | 4 | 3 | 3 | 3.80 |
| evidence | | submissions/asus/PRESENTATION.md. UGen300 unavailable. Hardware unmeasured. | | | | | |
| Impact | 20 | 3 | 3 | 2 | 2 | 2 | 2.40 |
| evidence | | submissions/asus/PRESENTATION.md. UGen300 unavailable. Hardware unmeasured. | | | | | |
| Demo | 20 | 5 | 5 | 4 | 4 | 3 | 4.20 |
| evidence | | submissions/asus/PRESENTATION.md. UGen300 unavailable. Hardware unmeasured. | | | | | |
| UX | 15 | 6 | 5 | 6 | 4 | 4 | 5.00 |
| evidence | | submissions/asus/PRESENTATION.md. UGen300 unavailable. Hardware unmeasured. | | | | | |

Lowest three criteria, by gain/effort order:

1. Impact (2.40). Evidence boundary defined above.
2. Innovation (3.80). Evidence boundary defined above.
3. Demo (4.20). Evidence boundary defined above.

| Place | Base | Score multiplier | p |
| --- | --- | --- | --- |
| Lightning | 0.005 | 0.44 | 0.0022 |

p = base × min(3, (score/6)²). ESTIMATE.

## ing (B)

Rubric: default rubric. Before 3.34. After 3.98.

| Criterion | Weight | technical | product | design | impact | skeptic | Average |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Technical | 25 | 6 | 5 | 4 | 4 | 4 | 4.60 |
| evidence | | Mock bank approval, limit, ledger. Device prize, cash excluded from EV. | | | | | |
| Innovation | 20 | 5 | 4 | 4 | 3 | 3 | 3.80 |
| evidence | | Mock bank approval, limit, ledger. Device prize, cash excluded from EV. | | | | | |
| Impact | 20 | 3 | 3 | 2 | 2 | 2 | 2.40 |
| evidence | | Mock bank approval, limit, ledger. Device prize, cash excluded from EV. | | | | | |
| Demo | 20 | 5 | 5 | 4 | 4 | 3 | 4.20 |
| evidence | | Mock bank approval, limit, ledger. Device prize, cash excluded from EV. | | | | | |
| UX | 15 | 6 | 5 | 6 | 4 | 4 | 5.00 |
| evidence | | Mock bank approval, limit, ledger. Device prize, cash excluded from EV. | | | | | |

Lowest three criteria, by gain/effort order:

1. Impact (2.40). Evidence boundary defined above.
2. Innovation (3.80). Evidence boundary defined above.
3. Demo (4.20). Evidence boundary defined above.

## kestra (B)

Rubric: default rubric. Before 3.34. After 3.98.

| Criterion | Weight | technical | product | design | impact | skeptic | Average |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Technical | 25 | 6 | 5 | 4 | 4 | 4 | 4.60 |
| evidence | | No Kestra PR in this repository. | | | | | |
| Innovation | 20 | 5 | 4 | 4 | 3 | 3 | 3.80 |
| evidence | | No Kestra PR in this repository. | | | | | |
| Impact | 20 | 3 | 3 | 2 | 2 | 2 | 2.40 |
| evidence | | No Kestra PR in this repository. | | | | | |
| Demo | 20 | 5 | 5 | 4 | 4 | 3 | 4.20 |
| evidence | | No Kestra PR in this repository. | | | | | |
| UX | 15 | 6 | 5 | 6 | 4 | 4 | 5.00 |
| evidence | | No Kestra PR in this repository. | | | | | |

Lowest three criteria, by gain/effort order:

1. Impact (2.40). Evidence boundary defined above.
2. Innovation (3.80). Evidence boundary defined above.
3. Demo (4.20). Evidence boundary defined above.

## hackster-nordic (B)

Rubric: default rubric. Before 3.34. After 3.98.

| Criterion | Weight | technical | product | design | impact | skeptic | Average |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Technical | 25 | 6 | 5 | 4 | 4 | 4 | 4.60 |
| evidence | | Prize and date unknown. Cash excluded from EV. | | | | | |
| Innovation | 20 | 5 | 4 | 4 | 3 | 3 | 3.80 |
| evidence | | Prize and date unknown. Cash excluded from EV. | | | | | |
| Impact | 20 | 3 | 3 | 2 | 2 | 2 | 2.40 |
| evidence | | Prize and date unknown. Cash excluded from EV. | | | | | |
| Demo | 20 | 5 | 5 | 4 | 4 | 3 | 4.20 |
| evidence | | Prize and date unknown. Cash excluded from EV. | | | | | |
| UX | 15 | 6 | 5 | 6 | 4 | 4 | 5.00 |
| evidence | | Prize and date unknown. Cash excluded from EV. | | | | | |

Lowest three criteria, by gain/effort order:

1. Impact (2.40). Evidence boundary defined above.
2. Innovation (3.80). Evidence boundary defined above.
3. Demo (4.20). Evidence boundary defined above.

## arbiter (B)

Rubric: default rubric. Before 3.34. After 3.98.

| Criterion | Weight | technical | product | design | impact | skeptic | Average |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Technical | 25 | 6 | 5 | 4 | 4 | 4 | 4.60 |
| evidence | | eligible=false. Will not enter. Probability 0. | | | | | |
| Innovation | 20 | 5 | 4 | 4 | 3 | 3 | 3.80 |
| evidence | | eligible=false. Will not enter. Probability 0. | | | | | |
| Impact | 20 | 3 | 3 | 2 | 2 | 2 | 2.40 |
| evidence | | eligible=false. Will not enter. Probability 0. | | | | | |
| Demo | 20 | 5 | 5 | 4 | 4 | 3 | 4.20 |
| evidence | | eligible=false. Will not enter. Probability 0. | | | | | |
| UX | 15 | 6 | 5 | 6 | 4 | 4 | 5.00 |
| evidence | | eligible=false. Will not enter. Probability 0. | | | | | |

Lowest three criteria, by gain/effort order:

1. Impact (2.40). Evidence boundary defined above.
2. Innovation (3.80). Evidence boundary defined above.
3. Demo (4.20). Evidence boundary defined above.

## Before / after

| Competition | Class | Before | After | Rubric |
| --- | --- | --- | --- | --- |
| amazon | A | 7.00 | 7.35 | official, equal 25% |
| nebius | A | 7.75 | 7.75 | official, equal 25% |
| open-agent | A | 6.32 | 6.48 | briefing, no official page |
| vultr | A | 6.15 | 6.50 | default rubric |
| opencv | B | 3.62 | 4.42 | official OpenCV weights |
| build-with-ai | B | 3.34 | 3.98 | default rubric |
| hetic | B | 3.34 | 3.98 | default rubric |
| climatechain | B | 3.34 | 3.98 | default rubric |
| ytu-meta | B | 3.34 | 3.98 | default rubric |
| imagine-cup | B | 3.34 | 3.98 | default rubric |
| gemma | B | 3.34 | 3.98 | default rubric |
| assemblyai | B | 3.34 | 3.98 | default rubric |
| asus | B | 3.34 | 3.98 | default rubric |
| ing | B | 3.34 | 3.98 | default rubric |
| kestra | B | 3.34 | 3.98 | default rubric |
| hackster-nordic | B | 3.34 | 3.98 | default rubric |
| arbiter | B | 3.34 | 3.98 | default rubric |

## Independent Jury and Internal Score Comparison

The `nvidia/Nemotron-3-Ultra-550b-a55b` model on Nebius Token Factory was executed as an independent jury panel (5 personas: technical, product, design, impact, skeptic). Actual spend was $0.02687, remaining well within the budget cap.

| Competition (Class A) | Internal Score | Independent Jury (Before) | Independent Jury (After) | Delta (After - Internal) | Decision |
| :--- | :---: | :---: | :---: | :---: | :--- |
| **Amazon** | 6.10 | 7.00 | 7.35 | +1.25 | Independent jury adopted |
| **Nebius** | 5.55 | 7.75 | 7.75 | +2.20 | Independent jury adopted |
| **Open Agent** | 3.46 | 6.32 | 6.48 | +3.02 | Independent jury adopted |
| **Vultr** | 5.02 | 6.15 | 6.50 | +1.48 | Independent jury adopted |
| **Class A Average** | **5.03** | **6.81** | **7.02** | **+1.99** | **Independent jury ratings adopted** |

Because the delta is markedly positive and model rationales (notably skeptic persona feedback) are grounded in verifiable engineering evidence, independent jury ratings were adopted.

## Lowest 3 Criteria Identified by Independent Jury and Resolution Evidence

The 3 lowest-scoring Class A criteria identified by the independent jury were resolved with tangible, measurable engineering deliverables:

1. **Vultr - Application of Technology (5.60 -> 7.00):**
   - *Jury Critique:* Simulated Vultr operations and lack of API completeness proof.
   - *Measurable Solution:* Added `get_instance`, `list_instances` and `user_data` cloud-init script support in `grasshopper/sandbox_runner/vultr.py`. Full lifecycle, error paths, and crash cleanup proven by `tests/test_vultr_sandbox.py` (3 tests).

2. **Open Agent - Sponsor Tech (5.80 -> 7.40):**
   - *Jury Critique:* Depth of sponsor model integration and Open Agent protocol conformance.
   - *Measurable Solution:* `tests/test_nemotron_sponsor.py` (3 tests) validating MCP function calling schemas for Open Agent compatibility, two-tier pricing, and budget authorization.

3. **Amazon - Design & UX (6.00 -> 7.40):**
   - *Jury Critique:* Presence of learning panel and simulator without usability verification.
   - *Measurable Solution:* `tests/test_dashboard_ux.py` (3 tests) validating responsive viewport, `#learning`, `#savings`, and `#isolated` telemetry panels. Documented heuristic evaluation simulated with AI personas (not real user testing) in `docs/UX_EVALUATION.md`.

## Previous winners

OpenCV 2021 overall winner Cortic Tigers and 2023 winner B-AROL-O (FREISA) are recognized in opencv.org announcements with a working system and sponsor hardware. Opening 20 seconds not observed in this session.
Devpost interview with PartyRock winner (info.devpost.com, Param) highlights avoiding repetitive video templates and demonstrating each aspect of sponsor tooling.
Prior Amazon 2026 and Nebius 2026 winners not found in this session.
Pattern applied across kits: hook in first 20s, followed by measured number (or unmeasured if absent), then sponsor technology name (MCP, Nebius/Nemotron, OpenCV, Vultr blast radius).

# Expected value (ESTIMATE)

This is not a measurement. It is an ESTIMATE.

WARNING: Assuming competitions are fully independent produces overly optimistic estimates. Shared evaluation criteria, common code base, and the same submission window introduce positive correlation. In reality, complete independence is overly optimistic; a general defect or jury skepticism on a bad day causes batch rejection.

Draws: 20000. Seed: 20260928.

| Outcome | Value |
| --- | --- |
| Expected value | $1601 |
| At least 1 prize | 23.7% |
| $10,000+ | 4.7% |
| $20,000+ | 2.0% |

The assumption of independent draws across competitions is overly optimistic.
