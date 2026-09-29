# Grasshopper — ASUS UGen AI League, Stage I

20 slides. Markdown presentation. YouTube upload not performed. UGen300 not present on this machine. Hardware integration unmeasured.

<!-- slide 1 -->
## 1. Cover

Grasshopper is an open-source browser worker that breaks a natural-language goal into steps, validates each step, and stops before spending funds. MIT licensed. This presentation is for Stage I. Not submitted. Halil will review.

<!-- slide 2 -->
## 2. One sentence

A browser worker that replays tasks on modified web pages with zero model cost on second execution, capped by strict budget limits.

<!-- slide 3 -->
## 3. Target User

An individual running repetitive tasks on their own web properties: stale listings, forms, checklists. No enterprise customer base claimed. User count is unmeasured.

<!-- slide 4 -->
## 4. Problem

Browser agents are expensive on their first attempt, incur the exact same cost on repeat runs, and silently misclick when a selector shifts. Grasshopper replays cached execution traces and falls back to computer vision when selectors break.

<!-- slide 5 -->
## 5. Product

Dashboard, human-in-the-loop approval gate, Alexa-style voice interface via MCP, local sandbox sites, and allowlist for real sites. Default mode is mock. `make test` passes without API keys.

<!-- slide 6 -->
## 6. Three commands

`bash scripts/setup.sh`, copy `.env.example` to `.env`, then `make test`. Details in CONTRIBUTING.md and README.md.

<!-- slide 7 -->
## 7. Architecture

Inbound channels feed the task queue. Router checks playbooks, falling back to LLM. Driver executes browser actions. Verifier validates outcomes. Explainer writes trace logs. Documented in docs/ARCHITECTURE.md with Mermaid diagrams.

<!-- slide 8 -->
## 8. Learning

Initial run calls LLM and saves action trace. Second run on same workflow targets 0 model calls. Proven in fixture suite via `tests/test_realweb.py`. Live site benchmarks unmeasured until full test pass completes.

<!-- slide 9 -->
## 9. Cost

Hard limits: $0.50 daily cap, $0.05 per-run cap. Router estimates token pricing before each call. Task halts and notifies user if limit is reached. Mock invoice is $0. Real spend documented in docs/COST.md.

<!-- slide 10 -->
## 10. Vision

OpenCV identifies diffs and visual bounding regions. On controlled fixture sets, modified elements are differentiated and unmodified elements remain stable. Continue button without DOM id is clicked via vision fallback. Accuracy outside fixture set is unmeasured. See docs/AGENTIC_VISION.md.

<!-- slide 11 -->
## 11. Safety

Allowlist hardcoded in policy. Retail checkouts, social media feeds, third-party logins, and payment endpoints are denied. Strict robots.txt adherence and request rate limiting. Mainnet crypto addresses refused.

<!-- slide 12 -->
## 12. Approval

Financial transfers, outbound shares, and data exports require explicit human approval. Workflow halts if rejected. Mock bank enforces limit, approval, and audit trail.

<!-- slide 13 -->
## 13. Blast Radius

Each run outputs `blast_radius.json` recording touched files, visited domains, duration, and financial spend. Docker runner is optional; falls back to local sandbox with warning if absent.

<!-- slide 14 -->
## 14. Demo

`videos/demo.mp4` under 180 seconds, 1280x720. Halil handles YouTube upload. File existence is not proof of submission.

<!-- slide 15 -->
## 15. Testing

Clean test suite: `make test` green, `make audit` passes without missing deliverables. Verified in docs/HANDOFF.md and docs/AUDIT.md. No placeholder assertions.

<!-- slide 16 -->
## 16. Edge Device

UGen300 hardware not physically attached. Model executes locally on host, not connected to edge NPU. Latency unmeasured. If Stage II hardware is granted, observation loop will be benchmarked on device.

<!-- slide 17 -->
## 17. What Was Not Measured

Live cloud Bedrock calls, remote AWS vision service, UGen300 NPU latency, real commercial users, YouTube view count. None of these are fabricated.

<!-- slide 18 -->
## 18. Risks

Local sandbox may appear synthetic to evaluators. Real site benchmark runs must be cited honestly. Hardware qualification cannot be met without device delivery.

<!-- slide 19 -->
## 19. Requested Decision

Presentation and video demo are sufficient for Stage I evaluation. No device presence claimed. Judged on reproducible test suite and hard budget caps.

<!-- slide 20 -->
## 20. Conclusion

Grasshopper is MIT licensed. Final submission is handled by Halil. Task timeline tracked in docs/INSAN_ISLERI.md.
