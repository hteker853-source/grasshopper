"""Pick the frames that best explain a run: first, mid, last, plus any approval frame."""

from __future__ import annotations

from pathlib import Path


def select_frames(run_dir: Path, limit: int = 6) -> list[Path]:
    frames = sorted(path for path in Path(run_dir).glob("*.png") if path.name.endswith("_after.png"))
    if not frames:
        frames = sorted(Path(run_dir).glob("*.png"))
    if len(frames) <= limit:
        return frames
    indexes = {0, len(frames) // 2, len(frames) - 1}
    step = max(1, len(frames) // limit)
    for index in range(0, len(frames), step):
        indexes.add(index)
        if len(indexes) >= limit:
            break
    return [frames[index] for index in sorted(indexes)][:limit]
