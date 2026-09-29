# Vultr Agent Rush Hackathon

Source: official rules and jury criteria, retrieved 2026-09-28 from lablab.ai.
https://lablab.ai/ai-hackathons/vultr-hackathon

This file is not the default rubric. It is the official jury evaluation table.

## Jury Criteria

| Criterion | Weight (%) | Official Definition |
| --- | --- | --- |
| Application of Technology | 25 | How effectively selected model(s) are integrated into the solution |
| Presentation | 25 | Clarity and persuasiveness of the presentation and demo video |
| Business Value | 25 | Alignment with business domains, practical utility and impact |
| Originality | 25 | Originality of the solution, creativity and agent behaviors |

## Technical Requirements and "Containment-First"

- Theme: "Blast Radius Zero" — web/code agents performing real work inside isolated sandbox environments on Vultr infrastructure.
- Mandatory deliverables:
  1. GitHub repo with setup instructions and documentation.
  2. Vultr VM backend deployment and LLM calls via Vultr Serverless Inference.
  3. Public demo URL and recorded demo video.
  4. A "containment moment" in the video: tangible proof that the sandbox safely isolates and halts an unsafe action (e.g. dangerous command, infinite loop, hostile webpage).

## Schedule and Prizes

- Date: Nov 3–8, 2026 (online build).
- Prizes: $9,000 cash + $5,000 credit.
  - 1st: $5,000 cash + $3,000 credit
  - 2nd: $3,000 cash + $1,000 credit
  - 3rd: $1,000 cash + $1,000 credit

## This Repository

- Every run writes `blast_radius.json` (touched files, domains, duration, spend).
- Vultr sandbox integration resides in `grasshopper/sandbox_runner/vultr.py`.
