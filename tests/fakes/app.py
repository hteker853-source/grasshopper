"""One process that speaks the provider HTTP shapes the real clients already use."""

from __future__ import annotations

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse


class Capture:
    def __init__(self):
        self.requests: list[dict] = []
        self.fail_chat = False
        self.fail_search = False

    def add(self, request: Request, body) -> None:
        self.requests.append({
            "method": request.method,
            "path": request.url.path,
            "query": request.url.query,
            "headers": {key.lower(): value for key, value in request.headers.items()},
            "body": body,
        })

    def paths(self) -> list[str]:
        return [item["path"] for item in self.requests]


def create_app(capture: Capture) -> FastAPI:
    app = FastAPI()
    app.state.capture = capture

    @app.post("/chat/completions")
    async def chat(request: Request):
        body = await request.json()
        capture.add(request, body)
        if capture.fail_chat:
            return JSONResponse({"error": "down"}, status_code=503)
        return {"choices": [{"message": {"content": "from-fake-llm"}}]}

    @app.post("/openai/deployments/{deployment}/chat/completions")
    async def azure_chat(deployment: str, request: Request):
        body = await request.json()
        capture.add(request, body)
        return {"choices": [{"message": {"content": f"azure:{deployment}"}}]}

    @app.post("/api/generate")
    async def ollama(request: Request):
        body = await request.json()
        capture.add(request, body)
        return {"response": "from-fake-ollama"}

    @app.post("/search")
    async def search(request: Request):
        body = await request.json()
        capture.add(request, body)
        if capture.fail_search:
            return JSONResponse({"error": "down"}, status_code=502)
        return {"results": [{"title": "Solar", "url": "https://example.test/solar", "content": "panels"}]}

    @app.post("/v2/upload")
    async def upload(request: Request):
        raw = await request.body()
        capture.add(request, {"bytes": len(raw)})
        return {"upload_url": "http://fake.local/audio"}

    @app.post("/v2/transcript")
    async def create_transcript(request: Request):
        body = await request.json()
        capture.add(request, body)
        return {"id": "tr_1"}

    @app.get("/v2/transcript/{transcript_id}")
    async def poll_transcript(transcript_id: str, request: Request):
        capture.add(request, {"id": transcript_id})
        return {"status": "completed", "text": "solar panels on the roof"}

    @app.post("/bot{token}/sendMessage")
    async def telegram_message(token: str, request: Request):
        body = await request.json()
        capture.add(request, {"token_len": len(token), "json": body})
        return {"ok": True, "result": {"message_id": 1}}

    @app.post("/v20.0/{phone_id}/messages")
    async def whatsapp(phone_id: str, request: Request):
        body = await request.json()
        capture.add(request, body)
        return {"messages": [{"id": "wamid"}]}

    @app.post("/speech")
    async def azure_speech(request: Request):
        raw = await request.body()
        capture.add(request, {"bytes": len(raw)})
        return {"DisplayText": "enable research mode"}

    return app
