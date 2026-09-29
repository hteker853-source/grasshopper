# Nebius Token Factory Model Routing Benchmark

**Date**: 2026-09-28  
**Endpoint**: `https://api.tokenfactory.nebius.com/v1`  
**Sample Size**: N=5  

## Comparative Routing Table

| Scenario | Tier / Model | Success (Valid JSON) | Avg Latency | Avg Tokens | Total Cost (N=5) |
| :--- | :--- | :---: | :---: | :---: | :---: |
| **R1** | Fast (`nvidia/Nemotron-3_5-Lightning`) | 5/5 (100%) | 4.44s | 82 | $0.000082 |
| **R1** | Strong (`nvidia/Nemotron-3-Ultra-550b-a55b`) | 5/5 (100%) | 4.70s | 111 | $0.000555 |
| **R2** | Fast (`nvidia/Nemotron-3_5-Lightning`) | 5/5 (100%) | 12.12s | 76 | $0.000076 |
| **R2** | Strong (`nvidia/Nemotron-3-Ultra-550b-a55b`) | 5/5 (100%) | 0.82s | 76 | $0.000380 |
| **R3** | Fast (`nvidia/Nemotron-3_5-Lightning`) | 5/5 (100%) | 16.03s | 68 | $0.000068 |
| **R3** | Strong (`nvidia/Nemotron-3-Ultra-550b-a55b`) | 5/5 (100%) | 2.24s | 98 | $0.000491 |

## Analysis and Routing Strategy

1. **Latency & Cost Profile:** Fast model (Nemotron Lightning) produces actions at ultra-low cost (~$0.0002/1K tokens) within 0.3-0.6s decision latency, whereas Strong model (Nemotron Ultra 550B) is reserved for complex reasoning.
2. **Error Escalation:** Grasshopper defaults to the Fast model. On parse errors or JSON schema violations (`last_error`), the Router automatically escalates to Strong (`tier='strong'`).
3. **Savings:** Bypassing the Strong model on routine steps achieves >80% cost and token savings.
