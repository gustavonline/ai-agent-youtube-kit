"""Controlled FFmpeg/ffprobe boundary."""

from __future__ import annotations

import json
import re
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


def _supports_ffmpeg_filter(filter_name: str) -> bool:
    ffmpeg, _ = require_media_tools()
    result = subprocess.run(
        [ffmpeg, "-hide_banner", "-filters"],
        check=False,
        text=True,
        capture_output=True,
    )
    return result.returncode == 0 and re.search(rf"\b{re.escape(filter_name)}\b", result.stdout or "") is not None


def require_lut3d_filter() -> None:
    if not _supports_ffmpeg_filter("lut3d"):
        raise ACSUserError(
            "This FFmpeg build lacks the lut3d filter required by the approved LUT. "
            "Use a supervised editor adapter that can apply the LUT and import its proved output."
        )


def _ffmpeg_filter_path(path: Path) -> str:
    """Escape a local path for an FFmpeg filter option on all supported OSes."""

    value = str(path.resolve()).replace("\\", "/")
    return value.replace("\\", "\\\\").replace(":", "\\:").replace("'", "\\'")


def _lut_filter(lut_source: Path) -> str:
    if not lut_source.is_file():
        raise ACSUserError(f"Approved LUT does not exist: {lut_source}")
    require_lut3d_filter()
    return f"lut3d=file='{_ffmpeg_filter_path(lut_source)}'"


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
    frame: dict[str, Any] | None = None,
    overlay_source: Path | None = None,
    audio_mode: str = "source",
    primary_audio_source: Path | None = None,
    audio_start: float | None = None,
    lut_source: Path | None = None,
    audio_fade: bool = False,
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
    audio_input_index = 0
    if audio_mode == "primary":
        if primary_audio_source is None or not primary_audio_source.exists():
            raise ACSUserError("A segment using primary audio requires an existing project primary source.")
        primary_start = start if audio_start is None else audio_start
        command.extend(["-ss", f"{max(0.0, primary_start):.3f}", "-i", str(primary_audio_source)])
        audio_input_index = 1
    if overlay_source is not None:
        command.extend(["-loop", "1", "-i", str(overlay_source)])
    overlay_input_index = 1 + (1 if audio_mode == "primary" else 0)
    if duration is not None:
        command.extend(["-t", f"{duration:.3f}"])
    video_filter = _frame_filter(kind, frame)
    lut_filter = _lut_filter(lut_source) if lut_source is not None else ""
    if kind == "long":
        if normalize_long and not video_filter:
            video_filter = "scale=1280:720:force_original_aspect_ratio=decrease,pad=1280:720:(ow-iw)/2:(oh-ih)/2,setsar=1"
        video_filter = ",".join(filter_part for filter_part in (video_filter, lut_filter) if filter_part)
        if overlay_source is not None:
            video_filter = video_filter or "null"
            video_filter = f"[0:v]{video_filter}[base];[{overlay_input_index}:v]format=rgba[overlay];[base][overlay]overlay=0:0:shortest=1[vout]"
            command.extend(["-filter_complex", video_filter, "-map", "[vout]"])
        elif video_filter:
            command.extend(["-vf", video_filter])
        command.extend(
            [
                *([] if overlay_source is not None else ["-map", "0:v:0"]),
                "-map",
                f"{audio_input_index}:a:0?",
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
                "-af",
                _audio_filter(audio_mode, duration, audio_fade),
                "-shortest",
                str(output),
            ]
        )
    elif kind == "short":
        if not video_filter:
            video_filter = "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920:(iw-ow)/2:(ih-oh)/2,setsar=1"
        video_filter = ",".join(filter_part for filter_part in (video_filter, lut_filter) if filter_part)
        if overlay_source is not None:
            video_filter = f"[0:v]{video_filter}[base];[{overlay_input_index}:v]format=rgba[overlay];[base][overlay]overlay=0:0:shortest=1[vout]"
            command.extend(["-filter_complex", video_filter, "-map", "[vout]"])
        else:
            command.extend(["-vf", video_filter])
        command.extend(
            [
                *([] if overlay_source is not None else ["-map", "0:v:0"]),
                "-map",
                f"{audio_input_index}:a:0?",
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
                "-af",
                _audio_filter(audio_mode, duration, audio_fade),
                "-shortest",
                str(output),
            ]
        )
    else:
        raise ACSUserError(f"Unsupported render kind: {kind}")
    run_media_command(command)
    return probe(output)


def _audio_filter(audio_mode: str, duration: float | None, audio_fade: bool) -> str:
    filters = ["volume=0" if audio_mode == "mute" else "anull"]
    if audio_fade and duration is not None and duration > 0:
        fade = min(0.03, duration / 2)
        filters.extend(
            [
                f"afade=t=in:st=0:d={fade:.3f}",
                f"afade=t=out:st={max(0.0, duration - fade):.3f}:d={fade:.3f}",
            ]
        )
    return ",".join(filters)


def _frame_filter(kind: str, frame: dict[str, Any] | None) -> str:
    if not frame:
        return ""
    if kind == "long":
        width, height = 1280, 720
    elif kind == "short":
        width, height = 1080, 1920
    else:
        raise ACSUserError(f"Unsupported render kind: {kind}")
    fit = str(frame.get("fit") or "cover")
    anchor = frame.get("anchor") or frame.get("focal_point") or {}
    x = min(1.0, max(0.0, float(anchor.get("x", 0.5))))
    y = min(1.0, max(0.0, float(anchor.get("y", 0.5))))
    if fit == "contain":
        return (
            f"scale={width}:{height}:force_original_aspect_ratio=decrease,"
            f"pad={width}:{height}:(ow-iw)*{x:.4f}:(oh-ih)*{y:.4f},setsar=1"
        )
    if fit != "cover":
        raise ACSUserError("Frame fit must be cover or contain.")
    return (
        f"scale={width}:{height}:force_original_aspect_ratio=increase,"
        f"crop={width}:{height}:(iw-ow)*{x:.4f}:(ih-oh)*{y:.4f},setsar=1"
    )


def render_segments(
    *,
    segments: list[dict[str, Any]],
    output: Path,
    kind: str,
    work_dir: Path,
    frame: dict[str, Any] | None = None,
    primary_audio_source: Path | None = None,
    lut_source: Path | None = None,
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
            frame=frame,
            overlay_source=Path(segment["resolved_overlay_source"]) if segment.get("resolved_overlay_source") else None,
            audio_mode=str(segment.get("audio") or "source"),
            primary_audio_source=primary_audio_source,
            audio_start=float(segment["audio_start"]) if segment.get("audio_start") is not None else None,
            lut_source=lut_source,
        )

    output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix=".acs-segments-", dir=str(work_dir)) as temp_name:
        temp_dir = Path(temp_name)
        clips: list[Path] = []
        for index, segment in enumerate(segments):
            clip = temp_dir / f"segment-{index:04d}.mp4"
            duration = _segment_duration(segment)
            render_media(
                source=Path(segment["resolved_source"]),
                output=clip,
                kind=kind,
                start=float(segment.get("start") or 0),
                duration=duration,
                normalize_long=kind == "long",
                frame=frame,
                overlay_source=Path(segment["resolved_overlay_source"]) if segment.get("resolved_overlay_source") else None,
                audio_mode=str(segment.get("audio") or "source"),
                primary_audio_source=primary_audio_source,
                audio_start=float(segment["audio_start"]) if segment.get("audio_start") is not None else None,
                lut_source=lut_source,
                audio_fade=True,
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


def _segment_duration(segment: dict[str, Any]) -> float | None:
    """Resolve an open-ended segment so multi-clip joins can be faded safely."""

    explicit = float(segment.get("duration") or 0)
    if explicit > 0:
        return explicit
    source = Path(segment["resolved_source"])
    start = max(0.0, float(segment.get("start") or 0))
    metadata = probe(source)
    available = float(metadata.get("duration_seconds") or 0) - start
    return available if available > 0 else None
