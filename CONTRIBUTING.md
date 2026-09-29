# Contributing to Grasshopper

Thank you for your interest in contributing to Grasshopper! Grasshopper is an open-source (MIT) autonomous multi-step browser agent built for safety, determinism, and minimal inference cost.

---

## Quick Start (Three Commands)

```bash
git clone https://github.com/hteker853-source/grasshopper.git && cd grasshopper
bash scripts/setup.sh
make test
```

---

## Core Guidelines & Safety Rules

1. **`make test` Must Always Be Green:**
   - Every commit must pass all pytest unit and integration tests.
   - **Never delete, weaken, or skip tests.**
   - No placeholder or no-op tests; every assertion must verify authentic behavior.
2. **Deterministic Mock Mode by Default:**
   - The test suite and default runtime run in mock mode without requiring API keys or external network calls.
   - Real providers are only enabled via `.env` without modifying core code.
3. **Strict Secrets Policy:**
   - Never commit `.env` or any credentials to git.
   - Never print or leak API keys in logs or transcripts.
4. **Safety & Containment:**
   - Only allowlisted domains may be visited by default.
   - Sensitive operations (payments, external notifications, irreversible actions) must go through the human approval gate.
   - Budget ceilings (`BudgetLedger`) must be respected before calling external models.
5. **Human-in-the-Loop Submissions:**
   - Grasshopper generates submission kits and documentation drafts under `submissions/`.
   - The agent never auto-submits to competitions. The final submission is always made manually by a human.

---

## Pull Request Checklist

Before submitting a pull request, ensure:
- [ ] `make test` passes (100% green).
- [ ] `make audit` reports 0 failures (0 ❌).
- [ ] Any new feature includes dedicated unit/integration tests.
- [ ] New architectural decisions are logged in [docs/DECISIONS.md](docs/DECISIONS.md).
- [ ] No secrets or unverified external dependencies are introduced.

---

## Reporting Issues

Use our issue templates for structured feedback:
- [Bug Report](.github/ISSUE_TEMPLATE/bug_report.md)
- [Feature Request](.github/ISSUE_TEMPLATE/feature_request.md)
