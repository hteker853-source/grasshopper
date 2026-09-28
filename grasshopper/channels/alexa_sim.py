"""Alexa+ simulator page. The page talks to /mcp like an external MCP client."""

from __future__ import annotations

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse

router = APIRouter()


@router.get("/alexa", response_class=HTMLResponse)
def alexa_page(request: Request):
    template = request.app.state.templates.get_template("alexa.html")
    return HTMLResponse(template.render())
