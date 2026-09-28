"""Small vision HTTP service. Deployable on its own. Do not set VISION_SERVICE_URL here."""

from __future__ import annotations

import base64
from pathlib import Path
from tempfile import TemporaryDirectory

from fastapi import FastAPI, File, Form, UploadFile

from grasshopper.browser.vision import _change_local, _detect_local

app = FastAPI(title="Grasshopper vision")


@app.get("/health")
def health():
    return {"ok": True, "service": "vision"}


@app.post("/detect")
async def detect(image: UploadFile = File(...), min_area: int = Form(400)):
    raw = await image.read()
    with TemporaryDirectory() as folder:
        source = Path(folder) / "frame.png"
        annotated = Path(folder) / "annotated.png"
        source.write_bytes(raw)
        regions = _detect_local(source, annotated, min_area=min_area)
        encoded = base64.b64encode(annotated.read_bytes()).decode("ascii") if annotated.exists() else ""
    return {"regions": regions, "annotated_png": encoded}


@app.post("/change")
async def change(
    before: UploadFile = File(...),
    after: UploadFile = File(...),
    threshold: int = Form(25),
):
    with TemporaryDirectory() as folder:
        left = Path(folder) / "before.png"
        right = Path(folder) / "after.png"
        left.write_bytes(await before.read())
        right.write_bytes(await after.read())
        percent = _change_local(left, right, threshold=threshold)
    return {"change_percent": percent}
