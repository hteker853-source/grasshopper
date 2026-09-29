# Amazon Build, Ship, Shape — Open Source Mini Checklist

> **Important Note**: This file is intended for human review (Halil must review). No submissions are performed automatically.
> Selected Mini: **Open Source Mini** ($5,000 cash + $5,000 AWS credits). No Bedrock calls made (`ALLOW_BEDROCK=0`), runs entirely with open-source components.

## 1. Participation and Eligibility Criteria

- [x] **Open Source License**: MIT License is present at the repository root (`LICENSE`).
- [x] **Public Repository**: Code prepared as a public GitHub repository or reviewable local git repo.
- [x] **Hackathon Time Window**: All developments, friction log entries, and benchmark measurements generated within the hackathon window.
- [x] **Autonomous Keyless Execution (0 API Keys)**: Grasshopper runs in `mock` mode by default (`MODE=mock`, `LLM_FAST_PROVIDER=mock`). `make test` and `make judge` execute with zero spend and zero external dependencies.
- [x] **Bedrock Separation**: Because the Open Source mini track is selected, Bedrock is not used (`ALLOW_BEDROCK=0`). Open model weights (Ollama, HuggingFace, or OpenAI-compatible local/open models) are supported.

## 2. Technical Requirements (Alexa+ MCP and Open Architecture)

- [x] **Official MCP Python SDK Integration**: Streamable HTTP endpoint implemented via `mcp.server.mcpserver.MCPServer` on Starlette/FastAPI at `/mcp`.
- [x] **Voice-Driven Hero Flow (`/alexa`)**:
  1. Voice command or natural-language input (`orb` / `btn-listen` / text prompt)
  2. MCP Tool call (`start_task` / `get_task_status`)
  3. Live browser preview (1 FPS `/live/frame.png`)
  4. Visual and audible human approval card (`approval-card` / `list_pending_approvals` / `approve`)
  5. Speech summary and blast radius feedback (`speech` and `blast_radius.json`)
- [x] **Trust & Safety Layer**:
  - Historical auditing via `get_audit_log` MCP tool.
  - Blast radius summary: number of modified files, visited domains, and USD cost.
  - Approval Gate: human sign-off requested prior to external API calls, file edits, or sensitive button clicks.
  - Hard Budget Ceiling: daily $0.50 and per-run $0.05 caps enforced by `BudgetLedger`.
- [x] **Single-Command Reproducibility**:
  - `make judge`: Deterministic 60-second jury demonstration.
  - `make test`: Unit and integration test suite passing green (111+ tests).
  - `make audit`: Policy and security audit passing green.

## 3. Submission Assets

- [x] **Project Description**: `submissions/amazon/DESCRIPTION.md` (English, architectural specifics, verified run IDs).
- [x] **Video Script**: `submissions/amazon/VIDEO_SCRIPT.md` (under 180 seconds, timestamped timeline: 0:00–0:20 intro, 2:45–3:00 outro).
- [x] **Friction Log**: `submissions/amazon/FRICTION_LOG.md` (authentic development friction: MCP SDK 2.x session task groups, Playwright Chromium headless separation, DOM selector healing `run_9f24d8fa5fad`, arXiv API rate limiting and token boundaries).
- [x] **Static Replay Page**: `site/index.html` (Jury playback and step-by-step screenshots).

## 4. Human Submission Procedure (Action items for Halil)

1. Sign in to the Devpost portal (`https://amazonappdev2026.devpost.com/`).
2. Primary category: **Alexa+ Track**, Mini category: select **Open Source Mini**.
3. Paste text from `submissions/amazon/DESCRIPTION.md`.
4. Upload recorded video (`videos/main_demo.mp4`) to YouTube/Vimeo/Loom and enter URL.
5. Provide GitHub repo link (`https://github.com/hteker853-source/grasshopper`).
6. Give final human approval and submit.
