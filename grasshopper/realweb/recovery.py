"""Measured vision checks. Numbers come from the pixels this process draws."""

from __future__ import annotations

from pathlib import Path

import cv2
import numpy as np

from grasshopper.browser.vision import change_percent, detect_regions


def _blank() -> np.ndarray:
    return np.full((420, 640, 3), 245, dtype=np.uint8)


def measure_change_accuracy(directory: Path, n_each: int = 10) -> dict:
    """Identical cards must score as unchanged. A moved block must score as changed."""
    directory.mkdir(parents=True, exist_ok=True)
    correct = 0
    total = n_each * 2
    for index in range(n_each):
        image = _blank()
        cv2.rectangle(image, (40, 40), (180, 100), (40, 140, 40), -1)
        left = directory / f"same-{index}-a.png"
        right = directory / f"same-{index}-b.png"
        cv2.imwrite(str(left), image)
        cv2.imwrite(str(right), image.copy())
        if change_percent(left, right) < 0.5:
            correct += 1
        moved = image.copy()
        cv2.rectangle(moved, (40, 40), (180, 100), (245, 245, 245), -1)
        cv2.rectangle(moved, (300, 200), (460, 280), (40, 140, 40), -1)
        dest = directory / f"moved-{index}.png"
        cv2.imwrite(str(dest), moved)
        if change_percent(left, dest) > 5:
            correct += 1
    return {"correct": correct, "total": total, "accuracy": correct / total if total else 0.0}


def _overlaps(box: tuple[int, int, int, int], region: dict) -> bool:
    x, y, width, height = box
    rx, ry, rw, rh = region["x"], region["y"], region["w"], region["h"]
    return not (x + width < rx or rx + rw < x or y + height < ry or ry + rh < y)


def pick_by_vision(elements: list[dict], regions: list[dict], goal_word: str) -> str:
    for element in elements:
        if goal_word.lower() not in element.get("text", "").lower():
            continue
        if any(_overlaps(element["box"], region) for region in regions):
            return element["selector"]
    return ""


def measure_dom_recovery(directory: Path, n: int = 20) -> dict:
    """The id is gone. Vision has to land on the Continue block, not the undrawn Cancel label."""
    directory.mkdir(parents=True, exist_ok=True)
    hits = 0
    for index in range(n):
        x = 30 + (index * 41) % 360
        y = 30 + (index * 23) % 240
        image = _blank()
        cv2.rectangle(image, (x, y), (x + 130, y + 46), (60, 170, 70), -1)
        path = directory / f"recover-{index}.png"
        annotated = directory / f"recover-{index}-ann.png"
        cv2.imwrite(str(path), image)
        regions = detect_regions(path, annotated, min_area=200)
        elements = [
            {"text": "Continue", "box": (x, y, 130, 46), "selector": "text=Continue"},
            {"text": "Cancel", "box": (x, min(y + 80, 360), 130, 46), "selector": "text=Cancel"},
        ]
        if pick_by_vision(elements, regions, "Continue") == "text=Continue":
            hits += 1
    return {"hits": hits, "n": n, "rate": hits / n if n else 0.0}
