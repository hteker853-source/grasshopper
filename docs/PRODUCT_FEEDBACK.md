# Alexa+ & Model Context Protocol (MCP) Toolkit Product Feedback

> **Date**: 2026-09-28  
> **Topic**: Product feedback, architectural friction points, and recommendations gathered during the implementation of Grasshopper's Alexa+ simulator and official MCP Python SDK (`mcp.server.mcpserver`) integration.

---

## 1. Executive Summary

Grasshopper utilizes Anthropic and Amazon's Model Context Protocol (MCP) Streamable HTTP standard (`/mcp`) to expose browser automation and web workflows to external agent networks. This integration highlighted multiple developer experience strengths, as well as specific architectural gaps and friction points encountered when integrating voice-first assistants and human-in-the-loop validation flows.

---

## 2. Strengths (What Worked Well)

1. **Streamable HTTP Specification**: Exposing JSON-RPC 2.0 and SSE over standard HTTP POST rather than requiring raw WebSockets allowed seamless mounting within Starlette/FastAPI microservices (`streamable_http_app`).
2. **Decorator-Driven Tool Definitions**: Automatic translation of Python type hints to JSON schema via `@mcp_server.tool()` significantly reduced boilerplate.
3. **Protocol Transparency**: Dynamic capability discovery (`initialize`, `tools/list`) by external clients like Alexa+ or Claude functioned reliably out of the box.

---

## 3. Friction Points and Challenges

### 3.1. ASGI Lifespan and Session Manager Initialization
- **Issue**: Migrating to `MCPServer` in MCP Python SDK 2.x resulted in `RuntimeError: Task group is not initialized` on the initial client request because the internal background task group (`session_manager.run()`) was unstarted.
- **Solution**: Explicitly attached the session manager lifecycle to the FastAPI `lifespan` handler via `asyncio.create_task(mcp_server.session_manager.run())`.
- **Recommendation**: Provide an out-of-the-box lifespan context manager in `streamable_http_app` to handle this setup automatically.

### 3.2. Bidirectional Human Approval Flow (Elicitation)
- **Issue**: The MCP protocol adheres primarily to a client-to-server RPC paradigm. When an autonomous browser agent encounters a high-risk action (e.g., checkout submission, fund transfers), it must elicit confirmation from the human operator or voice client. The protocol lacks a standardized proactive server-to-client approval request mechanism.
- **Solution**: Defined bidirectional polling tools (`list_pending_approvals` and `approve`), polled by `/alexa` at 3-second intervals to render approval cards.
- **Recommendation**: Standardize a `notifications/request_approval` or `tools/elicit` schema enabling servers to request interactive user confirmation natively.

### 3.3. Speech Summaries and Blast Radius Standards
- **Issue**: Voice assistants require tool responses to include both machine-readable JSON payloads and concise, natural-language spoken text (`speech`).
- **Solution**: Combined `speech` alongside structured `blast_radius` metadata ("2 files, 1 domain, $0.00 cost") in tool return objects.
- **Recommendation**: Introduce optional `metadata.speech_summary` or `display_text` fields in the official MCP Tool specification.

---

## 4. Summary and Recommended Roadmap

| Priority | Recommendation | Impact |
| :---: | :--- | :--- |
| **High** | Single-line ASGI Lifespan binding helper | Prevents 100% of task group startup failures |
| **High** | Standard Human-in-the-Loop Approval / Elicitation specification | Enhances agent ecosystem safety |
| **Medium** | Voice `speech` summary template standard for tool responses | Accelerates Alexa+ and voice agent development |
