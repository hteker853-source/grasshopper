# Alexa+ Developer Console MCP Integration Guide

This document outlines the setup steps, manifest schema, and conversational flows for connecting Grasshopper's Model Context Protocol (MCP) Streamable HTTP server to the Amazon Alexa+ developer console.

---

## 1. Developer Console Configuration Steps

### Step 1: Sign in to Alexa Developer Console
1. Navigate to [developer.amazon.com/alexa/console/ask](https://developer.amazon.com/alexa/console/ask).
2. Click **Create Skill**.
3. Skill Name: `Grasshopper Worker`.
4. Model Selection: **Alexa+ AI Assistant / Tool Calling** or **Custom**.

### Step 2: Connect MCP Endpoint
1. In the sidebar, navigate to **Tools & Integrations** > **Model Context Protocol (MCP)**.
2. **Endpoint Type**: Select `Streamable HTTP`.
3. **Endpoint URL**:
   - For Local Testing / Demo: Cloudflare tunnel generated via `make share-mcp` (e.g., `https://xyz.trycloudflare.com/mcp/`).
   - For Production: AWS App Runner HTTPS endpoint (e.g., `https://grasshopper.us-east-1.awsapprunner.com/mcp/`).
4. **Authentication**: Select `Bearer Token`.
   - Header: `Authorization: Bearer <MCP_BEARER_TOKEN>`
5. **Allowed Origins**: `https://alexa.amazon.com`.

### Step 3: Tool Discovery
1. Click **Discover Tools**.
2. The console issues a `tools/list` request against `/mcp/`, enumerating Grasshopper's 8 registered tools:
   - `start_task(text)`
   - `get_task_status(task_id)`
   - `get_task_result(task_id)`
   - `run_task(text)`
   - `list_pending_approvals()`
   - `approve(approval_id, decision)`
   - `store_check_old_listings(months)`
   - `council_ask(question)`

---

## 2. Developer Verification (cURL Commands)

Verify endpoint connectivity prior to linking in Alexa Developer Console:

### A. Handshake and Initialization
```bash
curl -X POST https://your-domain.com/mcp/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_MCP_TOKEN" \
  -d '{
    "jsonrpc": "2.0",
    "id": 1,
    "method": "initialize",
    "params": {
      "protocolVersion": "2025-11-25",
      "capabilities": {},
      "clientInfo": {"name": "alexa-plus-tester", "version": "1.0.0"}
    }
  }'
```

### B. Tool Enumeration (tools/list)
```bash
curl -X POST https://your-domain.com/mcp/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_MCP_TOKEN" \
  -d '{
    "jsonrpc": "2.0",
    "id": 2,
    "method": "tools/list",
    "params": {}
  }'
```

### C. Task Dispatch (start_task)
```bash
curl -X POST https://your-domain.com/mcp/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_MCP_TOKEN" \
  -d '{
    "jsonrpc": "2.0",
    "id": 3,
    "method": "tools/call",
    "params": {
      "name": "start_task",
      "arguments": {
        "text": "Find cheapest 4-star book on books.toscrape.com"
      }
    }
  }'
```
*Sample Response:*
```json
{
  "jsonrpc": "2.0",
  "id": 3,
  "result": {
    "content": [
      {
        "type": "text",
        "text": "{\"task_id\": \"task_01j...\", \"status\": \"queued\", \"speech\": \"Task received: Finding cheapest 4-star book on books.toscrape.com. Launching browser.\"}"
      }
    ]
  }
}
```

---

## 3. Skill Manifest Template (`skill.json`)

```json
{
  "manifest": {
    "publishingInformation": {
      "locales": {
        "en-US": {
          "name": "Grasshopper Browser Worker",
          "summary": "Autonomous web browser agent connected via MCP",
          "description": "Multi-step web automation, price checking, and shop administration with risk-gated human approvals."
        }
      }
    },
    "apis": {
      "custom": {
        "endpoint": {
          "uri": "https://your-domain.com/mcp/",
          "sslCertificateType": "Wildcard"
        },
        "interfaces": [
          {
            "type": "MODEL_CONTEXT_PROTOCOL",
            "version": "2025-11-25"
          }
        ]
      }
    }
  }
}
```

---

## 4. Sample Conversational Flows

### Scenario 1: E-Commerce Store Listing Audit
> **User:** "Alexa, tell Grasshopper to check my stale store listings."
>
> **Alexa (MCP -> `store_check_old_listings(months=4)`):** "Task received. Logging into store dashboard and scanning listings older than 4 months."
>
> *(Agent executes in background, detects 3 stale items)*
>
> **User:** "Alexa, what is Grasshopper's status?"
>
> **Alexa (MCP -> `get_task_status(task_id)`):** "Task complete. Found 3 inactive listings older than 4 months; price adjustment suggestions are ready on your dashboard."

### Scenario 2: Price Comparison & Multi-Step Research
> **User:** "Alexa, ask Grasshopper to find the cheapest 4-star book and summarize the author."
>
> **Alexa (MCP -> `start_task(...)`):** "Task received: Finding cheapest 4-star book and fetching author bio from Wikipedia."
>
> **Alexa (Upon completion):** "Research complete. Identified 'A Light in the Attic' at 51.77 GBP. Author is Shel Silverstein, American poet and cartoonist."

### Scenario 3: Human Approval Gate on Sensitive Operations
> **Alexa:** "Alert from Grasshopper: Human approval required to execute a 0.50 SOL subscription payment. Do you approve?"
>
> **User:** "Yes, I approve."
>
> **Alexa (MCP -> `approve(approval_id, 'approved')`):** "Action approved. Payment completed within safety boundaries on Solana devnet."
