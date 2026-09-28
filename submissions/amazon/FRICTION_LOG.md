# Friction Log Draft

**Halil should review - Draft only. Do not submit.** Compiled from actual build snags and errors recorded during Grasshopper development and `runs/demo-record`.

| Date | Source | What the log actually says | What we did |
| --- | --- | --- | --- |
| 2026-09-27 | `docs/FRICTION_LOG.md` | MCP Python SDK 2.x renamed `FastMCP` to `MCPServer`. Mounting the Starlette app did not start the session task group, so the first client call returned "Task group is not initialized". | The FastAPI lifespan calls `mcp_server.session_manager.run()` and mounts the app at `/mcp`. Clients use `/mcp/`. |
| 2026-09-27 | `docs/FRICTION_LOG.md` | Chromium lived under `/opt/pw-browsers` in one image, and a missing browser must not take the demos down. | `BROWSER_DRIVER=auto` tries Playwright and falls back to the HTTP sandbox driver. |
| 2026-09-28 | `runs/demo-record` & `run_9f24d8fa5fad/result.json` | "Stuck on Click the export button. The broken sandbox renamed the control to data-testid=export-btn-renamed. Retrying the old selector cannot succeed." Status `waiting_approval`. Temp check of the patch passed. The patch was not applied to the tree. | No code change during recording. The run stops for a person, which is what S7 is for. |
| 2026-09-28 | `tests/test_realweb.py` | `text=Continue` matched `<body>` element when text was identical, throwing "element is not clickable". | Skipped `html/body/head` and preferred an `a` or `button` with exact text in `grasshopper/realweb/driver.py`. |
| 2026-09-28 | `grasshopper/browser/controller.py` | `export.arxiv.org` returned HTTP 406 Not Acceptable to default HTTP clients without custom identification. | Configured an informative `User-Agent` containing repository contact details in `grasshopper/browser/controller.py`. |
| 2026-09-28 | `grasshopper/realweb/policy.py` | `export.arxiv.org/robots.txt` specifies `Disallow: /`, but official API guidelines designate `/api/query` for automated access with a 3-second delay. | Updated `grasshopper/realweb/policy.py` to allow `/api/` on `export.arxiv.org` while strictly enforcing a 3.0-second delay between requests. |
| 2026-09-28 | `grasshopper/sandbox_runner/vultr.py` | Setting an empty `Authorization: Bearer ` header when an API key was empty caused `httpcore.LocalProtocolError: Illegal header value`. | Conditionally omit the `Authorization` header when `api_key` is empty in `grasshopper/sandbox_runner/vultr.py`. |
| 2026-09-28 | `scripts/independent_jury.py` | High reasoning token generation (1000+ tokens) consumed the completion limit when `max_tokens` was set to 1000, leaving final JSON content empty. | Increased `max_tokens` to 2500 and implemented regex-based JSON block extraction with graceful retry in `scripts/independent_jury.py`. |
