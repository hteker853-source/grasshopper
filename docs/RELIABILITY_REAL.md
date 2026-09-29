# Real site reliability

N=3. Provider: nebius (nvidia/Nemotron-3_5-Lightning). Delay: 0.35s.
Run 1 generates decisions with live LLM and records trace; Run 2 replays learned playbook with 0 model calls.

## Reliability Table

| Scenario | Goal | Runs | Success Rate | Avg Steps | Run 1 LLM | Run 1 Tokens | Run 1 $ | Run 1 Duration | Run 2 (Playbook) | Notes / Error |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| **R1** | books.toscrape cheapest 4-star book | 3 | 0/3 (0.0%) | 20.3 | 22 | 19272 | $0.003814 | 230.2s | 20 calls | stuck; time budget |
| **R2** | saucedemo login, add two items, checkout | 3 | 0/3 (0.0%) | 3.0 | 3 | 702 | $0.000140 | 10.9s | 3 calls | stuck |
| **R3** | Hacker News top three headlines summary | 3 | 0/3 (0.0%) | 3.7 | 2 | 2220 | $0.000444 | 40.7s | 3 calls | stuck; time budget |
| **R4** | arXiv 'browser agents' search 3 papers | 3 | 0/3 (0.0%) | 4.0 | 6 | 2941 | $0.000588 | 39.2s | 3 calls | stuck |
| **R5** | the-internet dynamic loading, dropdown, upload | 3 | 0/3 (0.0%) | 2.0 | 5 | 1834 | $0.000108 | 41.6s | 5 calls | stuck |

## Broken Page Recovery Table

| Test Metric | Trials | Successful Recovery | Percentage |
| :--- | :---: | :---: | :---: |
| Controlled image set (change detection) | 20 | 20 | 100% |
| Continue selection on control with stripped DOM id | 20 | 20 | 100% |
| Deliberate HTML mutation on live site | - | - | unmeasured (third-party page not mutated) |
| REC scenario (local broken page recovery) | 1 | 1 | 100% |

## Scenario Details

## R1

- Runs: 3
- Success: 0/3 (0.0%)
- Average steps: 20.3
- Average tokens: 24247
- Total actual spend: $0.013914
- Run 1 LLM calls: 22
- Run 1 tokens: 19272
- Run 1 $: $0.003814
- Run 1 duration: 230.2s
- Run 2 (playbook) LLM calls: 20
- Errors: stuck; time budget

## R2

- Runs: 3
- Success: 0/3 (0.0%)
- Average steps: 3.0
- Average tokens: 702
- Total actual spend: $0.000421
- Run 1 LLM calls: 3
- Run 1 tokens: 702
- Run 1 $: $0.000140
- Run 1 duration: 10.9s
- Run 2 (playbook) LLM calls: 3
- Errors: stuck

## R3

- Runs: 3
- Success: 0/3 (0.0%)
- Average steps: 3.7
- Average tokens: 3280
- Total actual spend: $0.001968
- Run 1 LLM calls: 2
- Run 1 tokens: 2220
- Run 1 $: $0.000444
- Run 1 duration: 40.7s
- Run 2 (playbook) LLM calls: 3
- Errors: stuck; time budget

## R4

- Runs: 3
- Success: 0/3 (0.0%)
- Average steps: 4.0
- Average tokens: 1840
- Total actual spend: $0.001104
- Run 1 LLM calls: 6
- Run 1 tokens: 2941
- Run 1 $: $0.000588
- Run 1 duration: 39.2s
- Run 2 (playbook) LLM calls: 3
- Errors: stuck

## R5

- Runs: 3
- Success: 0/3 (0.0%)
- Average steps: 2.0
- Average tokens: 1831
- Total actual spend: $0.000323
- Run 1 LLM calls: 5
- Run 1 tokens: 1834
- Run 1 $: $0.000108
- Run 1 duration: 41.6s
- Run 2 (playbook) LLM calls: 5
- Errors: stuck

## Reading

0 of 15 measured runs succeeded: 0%. Provider: nebius (nvidia/Nemotron-3_5-Lightning). Across Run 1 executions, 38 live LLM calls were made and spend was measured at $0.017731 via BudgetLedger. In live LLM calls, loop stuck detection and time budget were triggered; because successful traces could not be completed, playbooks could not replay on Run 2.

## Spend

Total actual `cost_usd` for this bench: $0.017731.
Live Nebius Nemotron calls were accurately billed through BudgetLedger. Non-zero spend was verified for real calls while remaining $0 for mock.
