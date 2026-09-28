"""Build a short subtitled slideshow from run screenshots when ffmpeg exists."""

from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

from grasshopper.publish.screenshots import select_frames


def build_video(run_dir: Path, out: Path | None = None) -> Path | None:
    ffmpeg = shutil.which("ffmpeg")
    frames = select_frames(run_dir, limit=8)
    if not ffmpeg:
        print("ffmpeg not found; skipping demo video")
        return None
    if not frames:
        print(f"No screenshots in {run_dir}")
        return None
    target = out or (Path(run_dir) / "demo.mp4")
    listing = Path(run_dir) / "frames.txt"
    lines = []
    for frame in frames:
        lines.append(f"file '{frame.resolve()}'")
        lines.append("duration 2.5")
    lines.append(f"file '{frames[-1].resolve()}'")
    listing.write_text("\n".join(lines), encoding="utf-8")
    cmd = [
        ffmpeg, "-y", "-f", "concat", "-safe", "0", "-i", str(listing),
        "-vf", "scale=1280:720:force_original_aspect_ratio=decrease,pad=1280:720:(ow-iw)/2:(oh-ih)/2,format=yuv420p",
        "-r", "30", str(target),
    ]
    subprocess.run(cmd, check=True, capture_output=True)
    return target


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        raise SystemExit("Usage: python -m grasshopper.publish.video runs/<run_id>")
    built = build_video(Path(sys.argv[1]))
    print(built or "skipped")
