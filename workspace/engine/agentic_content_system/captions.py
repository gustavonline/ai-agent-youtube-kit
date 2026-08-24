"""Reviewed-transcript captions and a portable Pillow overlay fallback."""

from __future__ import annotations

import shutil
import tempfile
import textwrap
from pathlib import Path
from typing import Any

from .errors import ACSUserError
from .io import canonical_hash, sha256_file
from .media import probe, require_media_tools, run_media_command
from .paths import display_path, inside_project
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


FONT_CANDIDATES = (
    Path("/System/Library/Fonts/Supplemental/Arial.ttf"),
    Path("/Library/Fonts/Arial.ttf"),
    Path(r"C:\Windows\Fonts\arial.ttf"),
    Path(r"C:\Windows\Fonts\segoeui.ttf"),
    Path("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"),
    Path("/usr/share/fonts/truetype/liberation2/LiberationSans-Regular.ttf"),
)
PILLOW_DEFAULT_FONT_HASH = canonical_hash({"font": "pillow-default-bitmap-v1"})


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
    if not text:
        return []
    tokens = text.split()
    groups: list[list[str]] = []
    current: list[str] = []
    for token in tokens:
        # A no-word transcript still honors both configured limits. A single
        # overlong token is the only unavoidable exception to the usual
        # word-boundary preference, so split that token deterministically.
        if len(token) > max_chars:
            if current:
                groups.append(current)
                current = []
            groups.extend(
                [
                    [piece]
                    for piece in textwrap.wrap(
                        token,
                        width=max_chars,
                        break_long_words=True,
                        break_on_hyphens=False,
                    )
                ]
            )
            continue
        proposed = " ".join(current + [token])
        if current and (len(proposed) > max_chars or len(current) >= max_words):
            groups.append(current)
            current = []
        current.append(token)
    if current:
        groups.append(current)
    pieces = [" ".join(group) for group in groups if group]
    if not pieces:
        return []
    timing_end = max(float(end), float(start) + 0.05)
    span = timing_end - float(start)
    total_weight = sum(max(1, len(piece)) for piece in pieces)
    cursor = start
    result: list[dict[str, Any]] = []
    for index, piece in enumerate(pieces):
        piece_end = timing_end if index == len(pieces) - 1 else cursor + span * max(1, len(piece)) / total_weight
        result.append({"start": cursor, "end": piece_end, "text": piece})
        cursor = piece_end
    return result


def _source_duration(segment: dict[str, Any]) -> float:
    duration = float(segment.get("duration") or 0)
    metadata = probe(Path(segment["resolved_source"]))
    available = max(0.0, float(metadata.get("duration_seconds") or 0) - float(segment.get("start") or 0))
    if duration > 0:
        return min(duration, available) if available > 0 else duration
    return available


def _font_candidate_is_loadable(path: Path, size: int) -> bool:
    try:
        from PIL import ImageFont

        ImageFont.truetype(str(path), size)
    except (ImportError, OSError):
        return False
    return True


def _resolve_font(
    config: dict[str, Any],
    project_dir: Path | None,
    *,
    size: int,
    validate: bool,
) -> tuple[dict[str, Any], Path | None]:
    """Resolve the exact font input used by Pillow and return public proof."""

    font_value = str(config.get("font") or "").strip()
    if font_value:
        if project_dir is None:
            raise ACSUserError("An explicit caption font must be a production-local relative path.")
        path = inside_project(project_dir, font_value, label="caption font")
        if not path.is_file():
            raise ACSUserError(f"Caption font does not exist: {display_path(project_dir, path)}")
        if validate and not _font_candidate_is_loadable(path, size):
            raise ACSUserError(f"Caption font cannot be loaded by Pillow: {display_path(project_dir, path)}")
        return (
            {
                "kind": "custom",
                "identity": path.name,
                "path": display_path(project_dir, path),
                "sha256": sha256_file(path),
                "bytes": path.stat().st_size,
            },
            path,
        )

    for candidate in FONT_CANDIDATES:
        if candidate.is_file() and (not validate or _font_candidate_is_loadable(candidate, size)):
            return (
                {
                    "kind": "system-fallback",
                    "identity": candidate.name,
                    "path": str(candidate),
                    "sha256": sha256_file(candidate),
                    "bytes": candidate.stat().st_size,
                },
                candidate,
            )
    return (
        {
            "kind": "pillow-default",
            "identity": "Pillow default bitmap font",
            "path": "Pillow default bitmap font",
            "sha256": PILLOW_DEFAULT_FONT_HASH,
            "bytes": 0,
        },
        None,
    )


def caption_font_proof(
    config: dict[str, Any],
    project_dir: Path,
    *,
    size: int | None = None,
    validate: bool = False,
) -> dict[str, Any]:
    """Return hash-bound proof for a custom or resolved fallback font."""

    proof, _ = _resolve_font(
        config,
        project_dir,
        size=max(1, int(size or config.get("font_size", DEFAULTS["font_size"]))),
        validate=validate,
    )
    return proof


def caption_render_fingerprint(contracts: Any, kind: str) -> dict[str, Any] | None:
    config = caption_intent(contracts.edit_plan, kind)
    if config is None:
        return None
    reviewed = reviewed_transcript_proof(contracts)
    return {
        "intent_hash": canonical_hash(config),
        "reviewed_transcript_revision": reviewed["revision"],
        "reviewed_transcript_sha256": reviewed["sha256"],
        "font_proof": caption_font_proof(
            config,
            contracts.directory,
            validate=bool(config.get("burn", False)),
        ),
    }


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
        if str(edit_segment.get("audio") or "source") == "mute":
            # Muted B-roll still occupies the ordered output timeline, but it
            # cannot contribute spoken text even when a reviewed transcript
            # happens to cover the same source bytes.
            output_offset += source_duration
            continue
        transcript_source = default_source if str(edit_segment.get("audio") or "source") == "primary" else source
        transcript_start = (
            float(edit_segment.get("audio_start"))
            if str(edit_segment.get("audio") or "source") == "primary" and edit_segment.get("audio_start") is not None
            else source_start
        )
        transcript_end = transcript_start + source_duration
        for reviewed in reviewed_segments:
            reviewed_source = str(reviewed.get("source") or default_source)
            if reviewed_source != transcript_source:
                continue
            overlap_start = max(float(reviewed.get("start") or 0), transcript_start)
            overlap_end = min(float(reviewed.get("end") or 0), transcript_end)
            if overlap_end <= overlap_start:
                continue
            for chunk in _chunks(
                str(reviewed.get("text") or ""),
                overlap_start,
                overlap_end,
                [word for word in reviewed.get("words", []) if isinstance(word, dict) and float(word.get("end", 0)) > overlap_start and float(word.get("start", 0)) < overlap_end],
                config,
            ):
                start = output_offset + max(0.0, chunk["start"] - transcript_start)
                end = output_offset + min(source_duration, chunk["end"] - transcript_start)
                if end > start:
                    cues.append(
                        {
                            "start": round(start, 3),
                            "end": round(end, 3),
                            "text": chunk["text"],
                            "source": transcript_source,
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


def _font_and_color(
    config: dict[str, Any],
    size: int,
    *,
    project_dir: Path | None = None,
    font_path: Path | None = None,
    font_proof: dict[str, Any] | None = None,
):
    try:
        from PIL import ImageColor, ImageFont
    except ImportError as exc:
        raise ACSUserError(
            "Burned captions need the portable Pillow fallback. Install the ACS dependency with `python -m pip install -e .`."
        ) from exc
    if font_proof is None:
        font_proof, font_path = _resolve_font(config, project_dir, size=size, validate=True)

    def default_font():
        # Pillow 10+ exposes a scalable default bitmap font. Keep a fallback
        # for older Pillow builds so the ACS dependency remains portable.
        try:
            return ImageFont.load_default(size=size)
        except TypeError:
            return ImageFont.load_default()

    if font_path is not None:
        try:
            font = ImageFont.truetype(str(font_path), size)
        except OSError as exc:
            raise ACSUserError(f"Caption font cannot be loaded: {font_proof.get('path', '')}") from exc
    else:
        font = default_font()
    try:
        color = ImageColor.getrgb(str(config.get("color", "#ffffff")))
        outline = ImageColor.getrgb(str(config.get("outline_color", "#000000")))
    except ValueError as exc:
        raise ACSUserError(f"Caption color must be a CSS/hex color: {exc}") from exc
    return font, (*color, 255), (*outline, 255)


def _caption_image(
    path: Path,
    width: int,
    height: int,
    text: str,
    config: dict[str, Any],
    *,
    project_dir: Path | None = None,
    font_path: Path | None = None,
    font_proof: dict[str, Any] | None = None,
) -> None:
    try:
        from PIL import Image, ImageDraw
    except ImportError as exc:
        raise ACSUserError(
            "Burned captions need the portable Pillow fallback. Install the ACS dependency with `python -m pip install -e .`."
        ) from exc
    font_size = max(1, int(config.get("font_size", DEFAULTS["font_size"])))
    font, color, outline = _font_and_color(
        config,
        font_size,
        project_dir=project_dir,
        font_path=font_path,
        font_proof=font_proof,
    )
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


def burn_captions(
    base_output: Path,
    final_output: Path,
    cues: list[dict[str, Any]],
    config: dict[str, Any],
    work_dir: Path,
    *,
    project_dir: Path | None = None,
    font_proof: dict[str, Any] | None = None,
) -> str:
    if not cues:
        shutil.copy2(base_output, final_output)
        return "none"
    metadata = probe(base_output)
    width = int(metadata.get("width") or 0)
    height = int(metadata.get("height") or 0)
    if width <= 0 or height <= 0:
        raise ACSUserError("Cannot burn captions into an output without video dimensions.")
    ffmpeg, _ = require_media_tools()
    font_size = max(1, int(config.get("font_size", DEFAULTS["font_size"])))
    resolved_font_proof, font_path = _resolve_font(
        config,
        project_dir,
        size=font_size,
        validate=True,
    )
    if font_proof is not None and resolved_font_proof != font_proof:
        raise ACSUserError("Caption font resolution changed between proof and burn; rerun the render.")
    with tempfile.TemporaryDirectory(prefix=".acs-caption-", dir=str(work_dir)) as temp_name:
        temp_dir = Path(temp_name)
        images: list[Path] = []
        for index, cue in enumerate(cues):
            image_path = temp_dir / f"cue-{index:04d}.png"
            _caption_image(
                image_path,
                width,
                height,
                cue["text"],
                config,
                project_dir=project_dir,
                font_path=font_path,
                font_proof=resolved_font_proof,
            )
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
    font_size = max(1, int(config.get("font_size", DEFAULTS["font_size"])))
    font_proof, _ = _resolve_font(
        config,
        contracts.directory,
        size=font_size,
        validate=bool(config.get("burn", False)),
    )
    sidecar_path = caption_dir / f"{kind}.{format_name}"
    if bool(config.get("sidecar", True)):
        sidecar_path.write_text(caption_text(cues, format_name), encoding="utf-8")
    elif sidecar_path.exists():
        sidecar_path.unlink()
    renderer = "none"
    if bool(config.get("burn", False)):
        renderer = burn_captions(
            base_output,
            final_output,
            cues,
            config,
            work_dir,
            project_dir=contracts.directory,
            font_proof=font_proof,
        )
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
        "font_proof": font_proof,
        "cue_count": len(cues),
        "cues": cues,
    }
    if sidecar_path.exists():
        result["sidecar_path"] = display_path(contracts.directory, sidecar_path)
        result["sidecar_sha256"] = sha256_file(sidecar_path)
        result["sidecar_bytes"] = sidecar_path.stat().st_size
    return result
