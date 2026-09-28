"""Local stand-in for the Vultr instance API used by the runner tests."""

from __future__ import annotations

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse


def create_vultr_app(store: dict) -> FastAPI:
    app = FastAPI()

    @app.post("/v2/instances")
    async def create(request: Request):
        if not request.headers.get("authorization", "").startswith("Bearer "):
            return JSONResponse({"error": "unauthorized"}, status_code=401)
        store["created"] = store.get("created", 0) + 1
        instance_id = f"inst-{store['created']}"
        store["status"] = "active"
        store["alive"] = instance_id
        return {"instance": {"id": instance_id, "status": "active"}}

    @app.get("/v2/instances")
    async def list_inst():
        items = [{"id": store.get("alive"), "status": store.get("status", "active")}] if store.get("alive") else []
        return {"instances": items}

    @app.get("/v2/instances/{instance_id}")
    async def read(instance_id: str):
        return {"instance": {"id": instance_id, "status": store.get("status", "active")}}

    @app.delete("/v2/instances/{instance_id}")
    async def delete(instance_id: str):
        store.setdefault("deleted", []).append(instance_id)
        store["alive"] = ""
        return {"ok": True}

    return app
