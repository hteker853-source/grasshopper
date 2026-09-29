# Cost Ceiling and Policy

Date: 2026-09-28. Prices are catalog estimates. Mock calls incur $0 actual spend. Live provider bills are unmeasured in this file.

## Ceilings

| Gate | Value | Configuration Key |
| --- | --- | --- |
| Daily | $0.50 | `BUDGET_USD_DAILY` |
| Per Run | $0.05 | `BUDGET_USD_PER_RUN` |

Before every LLM invocation, the Router estimates token count from prompt length (`len/4`) and adds a response buffer (64 tokens). If estimated usage crosses the ceiling, the call is refused, the task transitions to `failed`, and a notification is dispatched with `kind=budget`. Telegram delivers this alert only if both token and allowed user ID are configured.

Mock calls also reserve against catalog pricing. Consequently, when live credentials are supplied later, workflows do not breach budget thresholds. The per-call `cost_usd` field remains 0 in mock mode. The daily "spend" report sums actual `cost_usd`.

## Catalog (per 1,000 tokens)

| Tier | $ |
| --- | --- |
| fast | 0.0002 |
| strong | 0.003 |
| vision | 0.004 |
| repair | 0.0004 |

Source: `grasshopper/core/budget.py` `PRICE_PER_1K`. Live Nebius invoice reconciliation unmeasured.

## Bedrock

Disabled by default. Even when keys are present, the client operates as a stub unless `ALLOW_BEDROCK=1`. Verified by: `test_bedrock_converse_is_stubbed`.

## Real Sites

Code allowlist in `grasshopper/realweb/policy.py` (`CODE_ALLOWLIST`): books.toscrape.com, quotes.toscrape.com, saucedemo.com, the-internet.herokuapp.com, webscraper.io, wikipedia.org, arxiv.org, news.ycombinator.com, github.com. Subdomains included. The environment variable `REAL_SITES_ALLOWLIST` can only restrict this set further.

Permanently refused: etsy.com, retail amazon.* domains, social networks, Google login, PayPal/Stripe, unlisted payment checkouts, github.com/login. `robots.txt` Disallow directives are strictly observed. A delay of `REAL_SITE_DELAY_SEC` (default 1s) is enforced between requests, or the site's Crawl-delay if larger. Localhost sandbox is isolated.

Verified by: `tests/test_budget_policy.py`.

## Out of Scope Domains and Safety Rationale

The following categories are strictly excluded from Grasshopper's autonomous execution:

1. **Live Financial Payments and Credit Card Processing:**
   - *Rationale:* Eliminate risk of unauthorized capital transfer, card charges, or wallet depletion. Funds movements are simulated solely in sandbox or Solana devnet; all actions require human approval via `ApprovalGate`.
2. **Authenticated Real User Accounts (Google Login, Personal Email, Banking):**
   - *Rationale:* Prevent leakage of credentials (passwords, 2FA tokens, session cookies) and maintain strict adherence to website Terms of Service regarding bot interactions.
3. **Social Media Platforms (Twitter/X, LinkedIn, Meta/Instagram):**
   - *Rationale:* Prevent automated spamming, unauthorized social posting, and anti-scraping blocks. The agent visits only public allowlisted resources (arXiv, Wikipedia, Hacker News, open book catalogs).
