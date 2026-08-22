#!/usr/bin/env python3
"""Create a tiny deterministic local media source for CI and build proof.

The generated file is intentionally ignored by git. It is a test fixture, not
a content asset or a public reference video.
"""

from __future__ import annotations

import argparse
import shutil
import subprocess
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser(description="Create a small deterministic FFmpeg fixture video.")
    parser.add_argument("output", type=Path)
    parser.add_argument("--duration", type=float, default=4.0)
    args = parser.parse_args()
    ffmpeg = shutil.which("ffmpeg")
    if not ffmpeg:
        parser.error("ffmpeg is required")
    output = args.output.expanduser().resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    command = [
        ffmpeg,
        "-hide_banner",
        "-loglevel",
        "error",
        "-y",
        "-f",
        "lavfi",
        "-i",
        "color=c=0x0A0D10:s=640x360:r=24",
        "-f",
        "lavfi",
        "-i",
        "sine=frequency=440:sample_rate=48000",
        "-t",
        f"{args.duration:.3f}",
        "-map",
        "0:v:0",
        "-map",
        "1:a:0",
        "-c:v",
        "libx264",
        "-preset",
        "medium",
        "-crf",
        "23",
        "-pix_fmt",
        "yuv420p",
        "-c:a",
        "aac",
        "-ar",
        "48000",
        "-threads",
        "1",
        "-movflags",
        "+faststart",
        str(output),
    ]
    result = subprocess.run(command, check=False)
    if result.returncode:
        return result.returncode
    print(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
