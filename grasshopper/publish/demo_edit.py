"""Filters and limits for the side-by-side demo video."""

from __future__ import annotations

import subprocess
from pathlib import Path

TELEGRAM_VIDEO_LIMIT = 50 * 1024 * 1024
DEMO_LIMIT_SEC = 180.0


def find_font() -> str | None:
    for candidate in (
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
        "/usr/share/fonts/truetype/freefont/FreeSans.ttf",
    ):
        if Path(candidate).is_file():
            return candidate
    return None


def _escape_drawtext(value: str) -> str:
    return value.replace("\\", " ").replace(":", "\\:").replace("'", "")


def side_by_side_filter(
    title: str | None,
    font: str | None,
    *,
    left_pad: float = 0.0,
    right_pad: float = 0.0,
) -> tuple[str, str]:
    """Return a filter_complex and the label of the final video stream.

    A missing font drops the title instead of failing the encode.
    """
    left_hold = f"tpad=stop_mode=clone:stop_duration={left_pad:.3f}," if left_pad > 0 else ""
    right_hold = f"tpad=stop_mode=clone:stop_duration={right_pad:.3f}," if right_pad > 0 else ""
    graph = (
        f"[0:v]{left_hold}scale=640:720:force_original_aspect_ratio=decrease,"
        "pad=640:720:(ow-iw)/2:(oh-ih)/2,setsar=1[left];"
        f"[1:v]{right_hold}scale=640:720:force_original_aspect_ratio=decrease,"
        "pad=640:720:(ow-iw)/2:(oh-ih)/2,setsar=1[right];"
        "[left][right]hstack=inputs=2[stacked]"
    )
    if title and font:
        safe_title = _escape_drawtext(title)
        safe_font = _escape_drawtext(font)
        graph += (
            f";[stacked]drawtext=fontfile={safe_font}:text='{safe_title}':"
            "x=24:y=24:fontsize=32:fontcolor=white:box=1:boxcolor=black@0.45[vout]"
        )
        return graph, "vout"
    return graph, "stacked"


def speed_factor(duration_sec: float, limit_sec: float = DEMO_LIMIT_SEC) -> float | None:
    """How much to speed the timeline up so the result stays under the limit."""
    if duration_sec <= limit_sec:
        return None
    return duration_sec / (limit_sec - 1.0)


def under_telegram_limit(size_bytes: int, limit: int = TELEGRAM_VIDEO_LIMIT) -> bool:
    return size_bytes < limit


def probe_duration(path: Path) -> float:
    proc = subprocess.run(
        [
            "ffprobe", "-v", "error",
            "-show_entries", "format=duration",
            "-of", "default=nw=1:nk=1",
            str(path),
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    return float(proc.stdout.strip())
