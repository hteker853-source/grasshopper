"""WhatsApp Cloud API webhook. Returns 503 when WHATSAPP_TOKEN is empty."""

from __future__ import annotations

from fastapi import APIRouter, Request, Response

router = APIRouter()


def _token(request: Request) -> str:
    return request.app.state.ctx.settings.whatsapp_token


@router.get("/webhooks/whatsapp")
async def verify(request: Request):
    if not _token(request):
        return Response('{"status":"passive"}', status_code=503, media_type="application/json")
    params = request.query_params
    if (
        params.get("hub.mode") == "subscribe"
        and params.get("hub.verify_token") == request.app.state.ctx.settings.whatsapp_verify_token
    ):
        return Response(params.get("hub.challenge", ""), media_type="text/plain")
    return Response(status_code=403)


@router.post("/webhooks/whatsapp")
async def incoming(request: Request):
    if not _token(request):
        return Response('{"status":"passive"}', status_code=503, media_type="application/json")
    payload = await request.json()
    texts = []
    for entry in payload.get("entry", []):
        for change in entry.get("changes", []):
            value = change.get("value", {})
            for message in value.get("messages", []):
                if message.get("type") == "text":
                    texts.append(message.get("text", {}).get("body", ""))
    ctx = request.app.state.ctx
    ids = []
    for text in texts:
        if text.strip():
            task = ctx.orchestrator.accept(text, channel="whatsapp")
            ids.append(task.id)
    return {"queued": ids}
