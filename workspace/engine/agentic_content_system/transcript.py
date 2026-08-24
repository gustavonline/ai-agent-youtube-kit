"""Open transcript ingestion and normalization.

The canonical interchange is a small JSON document with timestamped segments.
The adapter also accepts common Whisper JSON and timestamped Markdown/SRT/VTT so
local tools can feed the same downstream contract.
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from .errors import ACSUserError
from .validation import require_valid
from .schemas import load_schema


TIMESTAMP = re.compile(r"(?P<minutes>\d{1,3}):(?P<seconds>\d{2}(?:\.\d+)?)")
SUBTITLE_TIMESTAMP = re.compile(
    r"^(?P<value>\d{1,3}:\d{2}(?::\d{2})?[\.,]\d{3}|\d{1,3}:\d{2}(?::\d{2})?)$"
)
RANGE_LINE = re.compile(
    r"^\s*(?P<start>\d{1,3}:\d{2}(?:\.\d+)?)\s*(?:-|–|—|to)\s*"
    r"(?P<end>\d{1,3}:\d{2}(?:\.\d+)?)\s*[:|]\s*(?P<text>.+?)\s*$",
    re.IGNORECASE,
)


def parse_clock(value: str) -> float:
    match = TIMESTAMP.search(value.strip())
    if not match:
        raise ACSUserError(f"Invalid transcript timestamp: {value!r}")
    return int(match.group("minutes")) * 60 + float(match.group("seconds"))


def _segment(start: float, end: float, text: str, speaker: str | None = None) -> dict[str, Any]:
    item: dict[str, Any] = {"start": round(max(0.0, start), 3), "end": round(max(start, end), 3), "text": text.strip()}
    if speaker:
        item["speaker"] = speaker
    return item


def normalize_json(raw: dict[str, Any], source_name: str) -> dict[str, Any]:
    if raw.get("schema_version") == "1.0" and isinstance(raw.get("segments"), list):
        segments = raw["segments"]
        source = str(raw.get("source") or source_name)
        language = raw.get("language")
    elif isinstance(raw.get("segments"), list):
        segments = []
        for item in raw["segments"]:
            if not isinstance(item, dict):
                continue
            text = str(item.get("text") or "").strip()
            if not text:
                continue
            segments.append(
                _segment(
                    float(item.get("start") or 0),
                    float(item.get("end") or item.get("start") or 0),
                    text,
                    str(item.get("speaker") or item.get("speaker_id") or "") or None,
                )
            )
        source = str(raw.get("source") or raw.get("metadata", {}).get("source") or source_name)
        language = raw.get("language")
    elif isinstance(raw.get("words"), list):
        words = [item for item in raw["words"] if isinstance(item, dict) and item.get("text")]
        if not words:
            raise ACSUserError(f"Transcript JSON contains no usable words: {source_name}")
        segments = [
            _segment(
                float(words[0].get("start") or 0),
                float(words[-1].get("end") or words[-1].get("start") or 0),
                " ".join(str(item["text"]).strip() for item in words),
            )
        ]
        source = str(raw.get("source") or raw.get("metadata", {}).get("source") or source_name)
        language = raw.get("language")
    elif raw.get("text"):
        segments = [_segment(0, 1, str(raw["text"]))]
        source = str(raw.get("source") or source_name)
        language = raw.get("language")
    else:
        raise ACSUserError(f"Transcript JSON has no segments, words, or text: {source_name}")

    normalized = {"schema_version": "1.0", "source": source, "segments": segments}
    if language:
        normalized["language"] = str(language)
    require_valid(normalized, load_schema("transcript"), "transcript")
    return normalized


def parse_timestamped_text(text: str, source_name: str) -> dict[str, Any]:
    segments: list[dict[str, Any]] = []
    pending: list[str] = []
    pending_start: float | None = None
    pending_end: float | None = None

    def flush() -> None:
        nonlocal pending, pending_start, pending_end
        joined = " ".join(line.strip() for line in pending if line.strip()).strip()
        if joined and pending_start is not None:
            segments.append(_segment(pending_start, pending_end or pending_start + 1, joined))
        pending = []
        pending_start = None
        pending_end = None

    lines = [line.strip() for line in text.splitlines()]
    for line in lines:
        if not line or line.upper() == "WEBVTT" or line.isdigit():
            continue
        range_match = re.search(
            r"(?P<start>\d{1,2}:\d{2}(?::\d{2})?(?:\.\d+)?)\s*-->\s*"
            r"(?P<end>\d{1,2}:\d{2}(?::\d{2})?(?:\.\d+)?)",
            line,
        )
        markdown_match = RANGE_LINE.match(line)
        if range_match:
            flush()
            pending_start = _parse_flexible_clock(range_match.group("start"))
            pending_end = _parse_flexible_clock(range_match.group("end"))
        elif markdown_match:
            flush()
            pending_start = parse_clock(markdown_match.group("start"))
            pending_end = parse_clock(markdown_match.group("end"))
            pending.append(markdown_match.group("text"))
            flush()
        elif pending_start is not None:
            pending.append(line)
    flush()

    if not segments:
        meaningful = [line for line in lines if line]
        if meaningful:
            segments = [_segment(0, 1, " ".join(meaningful))]
    if not segments:
        raise ACSUserError(f"Transcript text contains no usable content: {source_name}")
    normalized = {"schema_version": "1.0", "source": source_name, "segments": segments}
    require_valid(normalized, load_schema("transcript"), "transcript")
    return normalized


def parse_subtitle_text(text: str, source_name: str) -> dict[str, Any]:
    """Parse strict SRT/VTT cues; never downgrade malformed subtitles to plain text."""

    lines = [line.lstrip("\ufeff").rstrip() for line in text.splitlines()]
    segments: list[dict[str, Any]] = []
    index = 0
    while index < len(lines):
        line = lines[index].strip()
        if not line or line.upper().startswith("WEBVTT"):
            index += 1
            continue
        if line.upper() in {"NOTE", "STYLE", "REGION"}:
            index += 1
            while index < len(lines) and lines[index].strip():
                index += 1
            continue
        if line.isdigit():
            index += 1
            if index >= len(lines):
                raise ACSUserError(f"Malformed subtitle cue without timing: {source_name}")
            line = lines[index].strip()
        if "-->" not in line:
            raise ACSUserError(
                f"Malformed {Path(source_name).suffix.lower().lstrip('.') or 'subtitle'} timing line in {source_name}: {line!r}"
            )
        parts = [part.strip() for part in line.split("-->", 1)]
        if len(parts) != 2:
            raise ACSUserError(f"Malformed subtitle timing line in {source_name}: {line!r}")
        start_token = parts[0]
        end_token = parts[1].split()[0] if parts[1].split() else ""
        if not SUBTITLE_TIMESTAMP.match(start_token) or not SUBTITLE_TIMESTAMP.match(end_token):
            raise ACSUserError(f"Malformed subtitle timestamp in {source_name}: {line!r}")
        start = _parse_flexible_clock(start_token)
        end = _parse_flexible_clock(end_token)
        index += 1
        cue_lines: list[str] = []
        while index < len(lines) and lines[index].strip():
            if "-->" in lines[index]:
                raise ACSUserError(f"Malformed subtitle cue text in {source_name}")
            cue_lines.append(lines[index].strip())
            index += 1
        cue_text = " ".join(cue_lines).strip()
        if not cue_text:
            raise ACSUserError(f"Subtitle cue has no text in {source_name}")
        segments.append(_segment(start, end, cue_text))

    if not segments:
        raise ACSUserError(f"Subtitle file contains no valid cues: {source_name}")
    normalized = {"schema_version": "1.0", "source": source_name, "segments": segments}
    require_valid(normalized, load_schema("transcript"), "transcript")
    return normalized


def _parse_flexible_clock(value: str) -> float:
    value = value.replace(",", ".")
    parts = value.split(":")
    if len(parts) == 1:
        return float(parts[0])
    if len(parts) == 2:
        return int(parts[0]) * 60 + float(parts[1])
    if len(parts) == 3:
        return int(parts[0]) * 3600 + int(parts[1]) * 60 + float(parts[2])
    raise ACSUserError(f"Invalid transcript timestamp: {value!r}")


def load_and_normalize(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise ACSUserError(f"Transcript input not found: {path}")
    suffix = path.suffix.lower()
    if suffix == ".json":
        try:
            raw = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            raise ACSUserError(f"Invalid transcript JSON in {path}: {exc}") from exc
        if not isinstance(raw, dict):
            raise ACSUserError(f"Transcript JSON must be an object: {path}")
        return normalize_json(raw, path.name)
    if suffix in {".srt", ".vtt"}:
        return parse_subtitle_text(path.read_text(encoding="utf-8"), path.name)
    if suffix in {".md", ".txt"}:
        return parse_timestamped_text(path.read_text(encoding="utf-8"), path.name)
    raise ACSUserError("Supported transcript inputs are .json, .md, .txt, .srt, and .vtt")


def transcript_text(transcript: dict[str, Any]) -> str:
    return " ".join(str(item["text"]).strip() for item in transcript.get("segments", []) if item.get("text")).strip()
