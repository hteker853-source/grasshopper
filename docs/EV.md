# Earnings Model and Expected Value (EV) Report

> [!IMPORTANT]
> This is not a guaranteed income commitment. It is an ESTIMATE based on AI jury scores and Monte Carlo simulation.

WARNING: Assuming competitions are fully independent produces overly optimistic estimates. Shared evaluation criteria, common code base, and the same submission window introduce positive correlation. In reality, complete independence is overly optimistic; a general defect or jury skepticism on a bad day causes batch rejection.

## 1. Three Scenario Analysis (Correlated Model)

| Metric | Bear | Base | Bull |
| --- | --- | --- | --- |
| **Expected Value (EV)** | **$903** | **$1601** | **$2290** |
| **At Least 1 Prize Probability** | 14.0% | 23.7% | 33.1% |
| **$10,000+ Earnings Probability** | 2.6% | 4.7% | 6.9% |
| **$20,000+ Earnings Probability** | 1.1% | 2.0% | 2.8% |

## 2. Reality Check on the '$20,000 Average' Premise

- **$20,000 average across 19 competitions:** That would mean $380,000 in cash prizes. This premise is **IMPOSSIBLE**; the entire first-place cash prize pool of all 19 competitions combined is only ~$180,000, and several contests (ING, Kestra, Arbiter, Nordic) award credits or certificates rather than cash.
- **Probability of winning $20,000+ total:**
  - In the Base scenario, the probability of total income reaching $20,000 or more is **2.0%**, and in the Bull scenario it is **2.8%**.
- **Which competitions are critical for $20,000?**
  - **Amazon (Alexa+ 1st: $25,000)** and **Nebius (1st: $20,000)** form the backbone of this goal. Without these two competitions, even winning all other contests in the portfolio makes reaching $20,000 in cash virtually impossible (Vultr 9K + Open Agent 8K = 17K).

## 3. Assumptions and Notes
- The simulation runs 20,000 draws for each scenario.
- Placement outcomes within the same competition are mutually exclusive (one cannot place 1st and 2nd simultaneously).
- A latent quality correlation shock (±0.35) models co-dependent success/failure tendencies across contests.
