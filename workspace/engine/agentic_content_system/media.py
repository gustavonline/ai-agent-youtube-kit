"""Controlled FFmpeg/ffprobe boundary."""

from __future__ import annotations

import json
import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import Any

from .errors import ACSCommandError, ACSUserError


def binary_path(name: str) -> str | None:
    return shutil.which(name)


def require_media_tools() -> tuple[str, str]:
    ffmpeg = binary_path("ffmpeg")
    ffprobe = binary_path("ffprobe")
    missing = [name for name, path in (("ffmpeg", ffmpeg), ("ffprobe", ffprobe)) if path is None]
    if missing:
        raise ACSUserError(
            "Missing required media tool(s): " + ", ".join(missing) + ". "
            "Install FFmpeg and ensure ffmpeg/ffprobe are on PATH."
        )
    return ffmpeg, ffprobe


def run_media_command(command: list[str]) -> subprocess.CompletedProcess[str]:
    try:
        result = subprocess.run(command, check=False, text=True, capture_output=True)
    except FileNotFoundError as exc:
        raise ACSUserError(f"Missing media command: {command[0]}") from exc
    if result.returncode != 0:
        detail = (result.stderr or result.stdout or "media command failed").strip()
        raise ACSCommandError(f"Media command failed ({result.returncode}): {detail}")
    return result


def probe(path: Path) -> dict[str, Any]:
    _, ffprobe = require_media_tools()
    result = run_media_command(
        [
            ffprobe,
            "-v",
            "error",
            "-print_format",
            "json",
            "-show_format",
            "-show_streams",
            str(path),
        ]
    )
    try:
        data = json.loads(result.stdout or "{}")
    except json.JSONDecodeError as exc:
        raise ACSUserError(f"ffprobe returned invalid JSON for {path}") from exc
    streams = data.get("streams", [])
    video = next((item for item in streams if item.get("codec_type") == "video"), {})
    audio = next((item for item in streams if item.get("codec_type") == "audio"), None)
    fmt = data.get("format", {})
    return {
        "duration_seconds": round(float(fmt.get("duration") or video.get("duration") or 0), 3),
        "width": video.get("width"),
        "height": video.get("height"),
        "video_codec": video.get("codec_name"),
        "audio_codec": audio.get("codec_name") if audio else None,
        "has_audio": audio is not None,
        "format": fmt.get("format_name"),
        "size_bytes": int(fmt.get("size") or path.stat().st_size),
    }


def render_media(
    *,
    source: Path,
    output: Path,
    kind: str,
    start: float = 0.0,
    duration: float | None = None,
    normalize_long: bool = False,
) -> dict[str, Any]:
    ffmpeg, _ = require_media_tools()
    output.parent.mkdir(parents=True, exist_ok=True)
    command = [
        ffmpeg,
        "-hide_banner",
        "-loglevel",
        "error",
        "-y",
        "-threads",
        "1",
        "-ss",
        f"{max(0.0, start):.3f}",
        "-i",
        str(source),
    ]
    if duration is not None:
        command.extend(["-t", f"{duration:.3f}"])
    if kind == "long":
        if normalize_long:
            command.extend(
                [
                    "-vf",
                    "scale=1280:720:force_original_aspect_ratio=decrease,pad=1280:720:(ow-iw)/2:(oh-ih)/2,setsar=1",
                ]
            )
        command.extend(
            [
                "-map",
                "0:v:0",
                "-map",
                "0:a:0?",
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
                "-movflags",
                "+faststart",
                str(output),
            ]
        )
    elif kind == "short":
        command.extend(
            [
                "-map",
                "0:v:0",
                "-map",
                "0:a:0?",
                "-vf",
                "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,setsar=1",
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
                "-movflags",
                "+faststart",
                str(output),
            ]
        )
    else:
        raise ACSUserError(f"Unsupported render kind: {kind}")
    run_media_command(command)
    return probe(output)


def render_segments(
    *,
    segments: list[dict[str, Any]],
    output: Path,
    kind: str,
    work_dir: Path,
) -> dict[str, Any]:
    """Render ordered source windows and concatenate them deterministically."""

    if not segments:
        raise ACSUserError(f"{kind} render requires at least one segment")
    if len(segments) == 1:
        segment = segments[0]
        duration = float(segment.get("duration") or 0) or None
        return render_media(
            source=Path(segment["resolved_source"]),
            output=output,
            kind=kind,
            start=float(segment.get("start") or 0),
            duration=duration,
        )

    output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix=".acs-segments-", dir=str(work_dir)) as temp_name:
        temp_dir = Path(temp_name)
        clips: list[Path] = []
        for index, segment in enumerate(segments):
            clip = temp_dir / f"segment-{index:04d}.mp4"
            duration = float(segment.get("duration") or 0) or None
            render_media(
                source=Path(segment["resolved_source"]),
                output=clip,
                kind=kind,
                start=float(segment.get("start") or 0),
                duration=duration,
                normalize_long=kind == "long",
            )
            clips.append(clip)
        concat_file = temp_dir / "concat.txt"
        lines: list[str] = []
        for clip in clips:
            path_text = str(clip.resolve()).replace("\\", "/")
            if "\n" in path_text or "\r" in path_text:
                raise ACSUserError("Media paths may not contain newlines")
            escaped = path_text.replace("'", "'\\''")
            lines.append(f"file '{escaped}'")
        concat_file.write_text("\n".join(lines) + "\n", encoding="utf-8")
        ffmpeg, _ = require_media_tools()
        run_media_command(
            [
                ffmpeg,
                "-hide_banner",
                "-loglevel",
                "error",
                "-y",
                "-threads",
                "1",
                "-f",
                "concat",
                "-safe",
                "0",
                "-i",
                str(concat_file),
                "-c",
                "copy",
                "-movflags",
                "+faststart",
                str(output),
            ]
        )
    return probe(output)
