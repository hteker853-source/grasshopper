"""OpenCV preprocessing: clickable regions, annotated frames, and page-change ratio.

When VISION_SERVICE_URL is set, detect and change calls go to that HTTP service.
An empty URL keeps the work in this process.
"""

from __future__ import annotations

import base64
import os
from pathlib import Path

import cv2
import httpx
import numpy as np


def read_bgr(path: str | Path) -> np.ndarray:
    image = cv2.imread(str(path))
    if image is None:
        raise FileNotFoundError(path)
    return image


def preprocess(path: str | Path) -> np.ndarray:
    """Gray + blur. Returned for callers that want the pixels the detector sees."""
    image = read_bgr(path)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    return cv2.GaussianBlur(gray, (5, 5), 0)


def _contours(edges: np.ndarray):
    found = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if len(found) == 3:
        return found[1]
    return found[0]


def _service_url() -> str:
    return os.environ.get("VISION_SERVICE_URL", "").strip().rstrip("/")


def detect_regions(image_path: str | Path, annotated_path: str | Path, *, min_area: int = 400) -> list[dict]:
    """Find rectangular click targets and write a numbered annotated.png."""
    url = _service_url()
    if url:
        return _detect_remote(url, image_path, annotated_path, min_area)
    return _detect_local(image_path, annotated_path, min_area=min_area)


def _detect_local(image_path: str | Path, annotated_path: str | Path, *, min_area: int = 400) -> list[dict]:
    image = read_bgr(image_path)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (5, 5), 0)
    edges = cv2.Canny(blur, 40, 140)
    boxes: list[tuple[int, int, int, int]] = []
    for contour in _contours(edges):
        x, y, width, height = cv2.boundingRect(contour)
        if width < 24 or height < 12:
            continue
        if width * height < min_area:
            continue
        if width > image.shape[1] * 0.95 and height > image.shape[0] * 0.95:
            continue
        boxes.append((x, y, width, height))
    boxes = _dedupe(boxes)
    annotated = image.copy()
    regions = []
    for index, (x, y, width, height) in enumerate(boxes, start=1):
        cv2.rectangle(annotated, (x, y), (x + width, y + height), (80, 220, 60), 2)
        cv2.putText(
            annotated,
            str(index),
            (x + 4, y + 18),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            (80, 220, 60),
            2,
        )
        regions.append({"n": index, "x": int(x), "y": int(y), "w": int(width), "h": int(height)})
    Path(annotated_path).parent.mkdir(parents=True, exist_ok=True)
    cv2.imwrite(str(annotated_path), annotated)
    return regions


def _dedupe(boxes: list[tuple[int, int, int, int]]) -> list[tuple[int, int, int, int]]:
    kept: list[tuple[int, int, int, int]] = []
    for box in sorted(boxes, key=lambda item: item[2] * item[3], reverse=True):
        cx = box[0] + box[2] / 2
        cy = box[1] + box[3] / 2
        if any(abs(cx - (other[0] + other[2] / 2)) < 12 and abs(cy - (other[1] + other[3] / 2)) < 12 for other in kept):
            continue
        kept.append(box)
    return kept[:25]


def change_percent(before: str | Path, after: str | Path, *, threshold: int = 25) -> float:
    """Percent of pixels whose absdiff exceeds `threshold`. Sizes are aligned first."""
    url = _service_url()
    if url:
        return _change_remote(url, before, after, threshold)
    return _change_local(before, after, threshold=threshold)


def _change_local(before: str | Path, after: str | Path, *, threshold: int = 25) -> float:
    left = read_bgr(before)
    right = read_bgr(after)
    if left.shape != right.shape:
        right = cv2.resize(right, (left.shape[1], left.shape[0]))
    diff = cv2.absdiff(left, right)
    gray = cv2.cvtColor(diff, cv2.COLOR_BGR2GRAY)
    changed = int(np.count_nonzero(gray > threshold))
    total = int(gray.size) or 1
    return 100.0 * changed / total


def _detect_remote(url: str, image_path: str | Path, annotated_path: str | Path, min_area: int) -> list[dict]:
    raw = Path(image_path).read_bytes()
    with httpx.Client(timeout=30) as client:
        response = client.post(f"{url}/detect", files={"image": raw}, data={"min_area": str(min_area)})
    response.raise_for_status()
    body = response.json()
    encoded = body.get("annotated_png") or ""
    if encoded:
        Path(annotated_path).parent.mkdir(parents=True, exist_ok=True)
        Path(annotated_path).write_bytes(base64.b64decode(encoded))
    return list(body.get("regions") or [])


def _change_remote(url: str, before: str | Path, after: str | Path, threshold: int) -> float:
    with httpx.Client(timeout=30) as client:
        response = client.post(
            f"{url}/change",
            files={"before": Path(before).read_bytes(), "after": Path(after).read_bytes()},
            data={"threshold": str(threshold)},
        )
    response.raise_for_status()
    return float(response.json()["change_percent"])
