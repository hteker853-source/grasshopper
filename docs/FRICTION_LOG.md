# Friction log

Template for the Amazon open-source friction bonus. One row per real snag. Do not invent entries after the fact.

| Date | Tool | Problem | Fix |
| --- | --- | --- | --- |
| 2026-09-27 | MCP Python SDK 2.x | `FastMCP` was renamed to `MCPServer`. Mounting the Starlette app did not start the session task group, so the first client call returned "Task group is not initialized". | Call `mcp_server.session_manager.run()` from the FastAPI lifespan and mount the app at `/mcp` with `streamable_http_path="/"`. Clients use `/mcp/`. |
| 2026-09-27 | Playwright | The sandbox image already had Chromium under `/opt/pw-browsers`, but a missing browser must not take the demos down. | `BROWSER_DRIVER=auto` tries Playwright and falls back to the HTTP sandbox driver. |
| 2026-09-28 | HTTP browser driver | `text=Continue` matched the `<body>` element, whose visible text was only that word, so the repair click raised "element is not clickable". Seen while running the REC fixture in `tests/test_realweb.py`. | Skip `html/body/head` and prefer an `a` or `button` with that exact text. |
| 2026-09-28 | arXiv API | `export.arxiv.org` returned HTTP 406 Not Acceptable to default HTTP clients without custom identification. | Configured an informative `User-Agent` containing repository contact details in `grasshopper/browser/controller.py`. |
| 2026-09-28 | arXiv robots.txt | `export.arxiv.org/robots.txt` specifies `Disallow: /`, but official API guidelines designate `/api/query` for automated access with a 3-second delay. | Updated `grasshopper/realweb/policy.py` to allow `/api/` on `export.arxiv.org` while strictly enforcing a 3.0-second delay between requests. |
| 2026-09-28 | HTTP client headers | Setting an empty `Authorization: Bearer ` header when an API key was empty caused `httpcore.LocalProtocolError: Illegal header value`. | Conditionally omit the `Authorization` header when `api_key` is empty in `grasshopper/sandbox_runner/vultr.py`. |
| 2026-09-28 | Nebius Nemotron Ultra (550B) | High reasoning token generation (1000+ tokens) consumed the completion limit when `max_tokens` was set to 1000, leaving final JSON content empty. | Increased `max_tokens` to 2500 and implemented regex-based JSON block extraction with graceful retry in `scripts/independent_jury.py`. |
