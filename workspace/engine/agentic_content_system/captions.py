"""Reviewed-transcript captions and a portable Pillow overlay fallback."""

from __future__ import annotations

import re
import shutil
import tempfile
import textwrap
from pathlib import Path
from typing import Any

from .errors import ACSUserError
from .io import canonical_hash, sha256_file, write_json
from .media import probe, require_media_tools, run_media_command
from .paths import display_path
from .transcript import (
    current_reviewed_segments,
    plan_transcript_ranges,
    reviewed_transcript_proof,
)


DEFAULTS: dict[str, Any] = {
    "format": "srt",
    "sidecar": True,
    "burn": False,
    "max_chars": 76,
    "max_words": 10,
    "case": "preserve",
    "placement": "bottom",
    "font": "",
    "font_size": 42,
    "color": "#ffffff",
    "outline_color": "#000000",
    "outline_width": 3,
    "margin": 64,
}


def _merge_config(value: dict[str, Any]) -> dict[str, Any]:
    config = dict(DEFAULTS)
    style = value.get("style") if isinstance(value.get("style"), dict) else {}
    chunking = value.get("chunking") if isinstance(value.get("chunking"), dict) else {}
    config.update(style)
    config.update(chunking)
    config.update({key: val for key, val in value.items() if key not in {"style", "chunking"}})
    return config


def caption_intent(plan: dict[str, Any], kind: str) -> dict[str, Any] | None:
    """Resolve the canonical per-output caption intent and small aliases."""

    candidates: list[Any] = []
    for key in ("captions", "caption_intent"):
        container = plan.get(key)
        if isinstance(container, dict):
            candidates.extend([container.get(kind), container.get(f"{kind}_form"), container])
    section = plan.get(f"{kind}_form")
    if isinstance(section, dict):
        candidates.extend([section.get("captions"), section.get("caption_intent")])
    selected = next((item for item in candidates if isinstance(item, dict)), None)
    if selected is None:
        return None
    config = _merge_config(selected)
    if not bool(config.get("enabled", False)):
        return None
    config["enabled"] = True
    return config


def _case(text: str, mode: str) -> str:
    if mode == "upper":
        return text.upper()
    if mode == "lower":
        return text.lower()
    if mode == "title":
        return text.title()
    return text


def _chunks(text: str, start: float, end: float, words: list[dict[str, Any]], config: dict[str, Any]) -> list[dict[str, Any]]:
    max_chars = max(1, int(config.get("max_chars", DEFAULTS["max_chars"])))
    max_words = max(1, int(config.get("max_words", DEFAULTS["max_words"])))
    if words:
        groups: list[list[dict[str, Any]]] = []
        current: list[dict[str, Any]] = []
        for word in words:
            proposed = " ".join(item["text"] for item in current + [word])
            if current and (len(proposed) > max_chars or len(current) >= max_words):
                groups.append(current)
                current = []
            current.append(word)
        if current:
            groups.append(current)
        return [
            {
                "start": float(group[0]["start"]),
                "end": float(group[-1]["end"]),
                "text": _case(" ".join(item["text"] for item in group).strip(), str(config.get("case", "preserve"))),
            }
            for group in groups
        ]

    text = _case(text.strip(), str(config.get("case", "preserve")))
    if len(text) <= max_chars:
        return [{"start": start, "end": max(end, start + 0.05), "text": text}]
    pieces = textwrap.wrap(text, width=max_chars, break_long_words=False, break_on_hyphens=False)
    if not pieces:
        return []
    span = max(end - start, 0.05)
    step = span / len(pieces)
    return [
        {"start": start + index * step, "end": start + (index + 1) * step, "text": piece}
        for index, piece in enumerate(pieces)
    ]


def _source_duration(segment: dict[str, Any]) -> float:
    duration = float(segment.get("duration") or 0)
    metadata = probe(Path(segment["resolved_source"]))
    available = max(0.0, float(metadata.get("duration_seconds") or 0) - float(segment.get("start") or 0))
    if duration > 0:
        return min(duration, available) if available > 0 else duration
    return available


def build_caption_cues(contracts: Any, kind: str, edit_segments: list[dict[str, Any]]) -> list[dict[str, Any]]:
    config = caption_intent(contracts.edit_plan, kind)
    if config is None:
        return []
    ranges = plan_transcript_ranges(contracts, kind)
    reviewed_segments = current_reviewed_segments(contracts, ranges if ranges else None)
    if not reviewed_segments:
        raise ACSUserError(f"Captions for {kind} require reviewed transcript text in the selected ranges.")
    default_source = next(
        (str(source["path"]) for source in contracts.project.get("sources", []) if source.get("role") == "primary"),
        str(contracts.project["sources"][0]["path"]),
    )
    cues: list[dict[str, Any]] = []
    output_offset = 0.0
    for edit_segment in edit_segments:
        source = str(edit_segment.get("source") or default_source)
        source_start = float(edit_segment.get("start") or 0)
        source_duration = _source_duration(edit_segment)
        source_end = source_start + source_duration
        for reviewed in reviewed_segments:
            reviewed_source = str(reviewed.get("source") or default_source)
            if reviewed_source != source:
                continue
            overlap_start = max(float(reviewed.get("start") or 0), source_start)
            overlap_end = min(float(reviewed.get("end") or 0), source_end)
            if overlap_end <= overlap_start:
                continue
            for chunk in _chunks(
                str(reviewed.get("text") or ""),
                overlap_start,
                overlap_end,
                [word for word in reviewed.get("words", []) if isinstance(word, dict) and float(word.get("end", 0)) > overlap_start and float(word.get("start", 0)) < overlap_end],
                config,
            ):
                start = output_offset + max(0.0, chunk["start"] - source_start)
                end = output_offset + min(source_duration, chunk["end"] - source_start)
                if end > start:
                    cues.append(
                        {
                            "start": round(start, 3),
                            "end": round(end, 3),
                            "text": chunk["text"],
                            "source": source,
                            "source_start": round(chunk["start"], 3),
                            "source_end": round(chunk["end"], 3),
                        }
                    )
        output_offset += source_duration
    cues.sort(key=lambda item: (item["start"], item["end"], item["text"]))
    return cues


def _timestamp(seconds: float, *, vtt: bool = False) -> str:
    milliseconds = max(0, int(round(seconds * 1000)))
    hours, remainder = divmod(milliseconds, 3_600_000)
    minutes, remainder = divmod(remainder, 60_000)
    seconds_value, millis = divmod(remainder, 1000)
    separator = "." if vtt else ","
    return f"{hours:02d}:{minutes:02d}:{seconds_value:02d}{separator}{millis:03d}"


def caption_text(cues: list[dict[str, Any]], format_name: str) -> str:
    vtt = format_name == "vtt"
    lines = ["WEBVTT", ""] if vtt else []
    for index, cue in enumerate(cues, start=1):
        if not vtt:
            lines.append(str(index))
        lines.append(f"{_timestamp(cue['start'], vtt=vtt)} --> {_timestamp(cue['end'], vtt=vtt)}")
        lines.append(cue["text"])
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def _font_and_color(config: dict[str, Any], size: int):
    try:
        from PIL import ImageColor, ImageFont
    except ImportError as exc:
        raise ACSUserError(
            "Burned captions need the portable Pillow fallback. Install the ACS dependency with `python -m pip install -e .`."
        ) from exc
    font_value = str(config.get("font") or "")

    def portable_font():
        # Prefer a widely available Unicode font so reviewed text such as
        # Danish, German, or accented names does not become tofu glyphs. The
        # list is deliberately small and platform-neutral; an explicit font
        # in the caption intent still wins.
        candidates = (
            Path("/System/Library/Fonts/Supplemental/Arial.ttf"),
            Path("/Library/Fonts/Arial.ttf"),
            Path(r"C:\Windows\Fonts\arial.ttf"),
            Path(r"C:\Windows\Fonts\segoeui.ttf"),
            Path("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"),
            Path("/usr/share/fonts/truetype/liberation2/LiberationSans-Regular.ttf"),
        )
        for candidate in candidates:
            if candidate.exists():
                try:
                    return ImageFont.truetype(str(candidate), size)
                except OSError:
                    continue
        return None

    def default_font():
        # Pillow 10+ exposes a scalable default bitmap font. Keep a fallback
        # for older Pillow builds so the ACS dependency remains portable.
        selected = portable_font()
        if selected is not None:
            return selected
        try:
            return ImageFont.load_default(size=size)
        except TypeError:
            return ImageFont.load_default()

    try:
        font = ImageFont.truetype(font_value, size) if font_value else default_font()
    except OSError:
        font = default_font()
    try:
        color = ImageColor.getrgb(str(config.get("color", "#ffffff")))
        outline = ImageColor.getrgb(str(config.get("outline_color", "#000000")))
    except ValueError as exc:
        raise ACSUserError(f"Caption color must be a CSS/hex color: {exc}") from exc
    return font, (*color, 255), (*outline, 255)


def _caption_image(path: Path, width: int, height: int, text: str, config: dict[str, Any]) -> None:
    try:
        from PIL import Image, ImageDraw
    except ImportError as exc:
        raise ACSUserError(
            "Burned captions need the portable Pillow fallback. Install the ACS dependency with `python -m pip install -e .`."
        ) from exc
    font_size = max(1, int(config.get("font_size", DEFAULTS["font_size"])))
    font, color, outline = _font_and_color(config, font_size)
    image = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)
    max_width = max(80, width - 2 * int(config.get("margin", DEFAULTS["margin"])))
    wrapped: list[str] = []
    for paragraph in text.splitlines() or [text]:
        wrapped.extend(textwrap.wrap(paragraph, width=max(8, int(max_width / max(font_size * 0.55, 1))), break_long_words=False) or [""])
    rendered = "\n".join(wrapped)
    stroke_width = max(0, int(config.get("outline_width", DEFAULTS["outline_width"])))
    bbox = draw.multiline_textbbox((0, 0), rendered, font=font, stroke_width=stroke_width, spacing=4)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    margin = int(config.get("margin", DEFAULTS["margin"]))
    placement = str(config.get("placement", "bottom"))
    x = max(margin, (width - text_width) // 2)
    if placement == "top":
        y = margin
    elif placement == "center":
        y = max(margin, (height - text_height) // 2)
    else:
        y = max(margin, height - text_height - margin)
    draw.multiline_text(
        (x, y),
        rendered,
        font=font,
        fill=color,
        stroke_width=stroke_width,
        stroke_fill=outline,
        spacing=4,
        align="center",
    )
    image.save(path, format="PNG", optimize=True)


def burn_captions(base_output: Path, final_output: Path, cues: list[dict[str, Any]], config: dict[str, Any], work_dir: Path) -> str:
    if not cues:
        shutil.copy2(base_output, final_output)
        return "none"
    metadata = probe(base_output)
    width = int(metadata.get("width") or 0)
    height = int(metadata.get("height") or 0)
    if width <= 0 or height <= 0:
        raise ACSUserError("Cannot burn captions into an output without video dimensions.")
    ffmpeg, _ = require_media_tools()
    with tempfile.TemporaryDirectory(prefix=".acs-caption-", dir=str(work_dir)) as temp_name:
        temp_dir = Path(temp_name)
        images: list[Path] = []
        for index, cue in enumerate(cues):
            image_path = temp_dir / f"cue-{index:04d}.png"
            _caption_image(image_path, width, height, cue["text"], config)
            images.append(image_path)
        filter_parts: list[str] = []
        current = "[0:v]"
        for index, (image_path, cue) in enumerate(zip(images, cues), start=1):
            next_label = f"[caption{index}]"
            filter_parts.append(
                f"{current}[{index}:v]overlay=0:0:enable='between(t,{cue['start']:.3f},{cue['end']:.3f})'{next_label}"
            )
            current = next_label
        command = [ffmpeg, "-hide_banner", "-loglevel", "error", "-y", "-i", str(base_output)]
        for image_path in images:
            command.extend(["-loop", "1", "-i", str(image_path)])
        command.extend(
            [
                "-filter_complex",
                ";".join(filter_parts),
                "-map",
                current,
                "-map",
                "0:a?",
                "-c:v",
                "libx264",
                "-preset",
                "medium",
                "-crf",
                "23",
                "-pix_fmt",
                "yuv420p",
                "-c:a",
                "copy",
                "-shortest",
                "-movflags",
                "+faststart",
                str(final_output),
            ]
        )
        run_media_command(command)
    return "pillow-overlay"


def render_caption_assets(
    contracts: Any,
    kind: str,
    *,
    base_output: Path,
    final_output: Path,
    edit_segments: list[dict[str, Any]],
    work_dir: Path,
) -> dict[str, Any] | None:
    config = caption_intent(contracts.edit_plan, kind)
    if config is None:
        return None
    cues = build_caption_cues(contracts, kind, edit_segments)
    if not cues:
        raise ACSUserError(f"Caption intent for {kind} produced no cues.")
    caption_dir = contracts.directory / "renders" / "captions"
    caption_dir.mkdir(parents=True, exist_ok=True)
    format_name = str(config.get("format", "srt"))
    sidecar_path = caption_dir / f"{kind}.{format_name}"
    if bool(config.get("sidecar", True)):
        sidecar_path.write_text(caption_text(cues, format_name), encoding="utf-8")
    elif sidecar_path.exists():
        sidecar_path.unlink()
    renderer = "none"
    if bool(config.get("burn", False)):
        renderer = burn_captions(base_output, final_output, cues, config, work_dir)
    elif base_output != final_output:
        shutil.copy2(base_output, final_output)
    proof = reviewed_transcript_proof(contracts)
    result: dict[str, Any] = {
        "enabled": True,
        "format": format_name,
        "burn": bool(config.get("burn", False)),
        "sidecar": bool(config.get("sidecar", True)),
        "renderer": renderer,
        "text_filter": False,
        # Keep the resolved style decisions beside the hash so a reviewer can
        # inspect the exact choices that produced the sidecar/burned cues.
        "intent": config,
        "caption_intent_hash": canonical_hash(config),
        "reviewed_transcript_revision": proof["revision"],
        "reviewed_transcript_sha256": proof["sha256"],
        "cue_count": len(cues),
        "cues": cues,
    }
    if sidecar_path.exists():
        result["sidecar_path"] = display_path(contracts.directory, sidecar_path)
        result["sidecar_sha256"] = sha256_file(sidecar_path)
        result["sidecar_bytes"] = sidecar_path.stat().st_size
    return result
