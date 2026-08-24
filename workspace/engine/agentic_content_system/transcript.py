"""Open transcript adapters and explicit reviewed-transcript truth.

The input adapter accepts common local transcript shapes.  A production
workspace keeps the immutable raw input in ``transcripts/raw.json`` and a
separate, reviewer-owned bounded truth in ``transcripts/reviewed.json``.
``active.json`` remains a compatibility view of the raw input for older
workspaces and tools; publish-ready consumers must use the reviewed record.
"""

from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .errors import ACSUserError
from .io import canonical_hash, read_json, sha256_file
from .paths import display_path, inside_project
from .schemas import load_schema
from .validation import require_valid


TIMESTAMP = re.compile(r"(?P<minutes>\d{1,3}):(?P<seconds>\d{2}(?:\.\d+)?)")
SUBTITLE_TIMESTAMP = re.compile(
    r"^(?P<value>\d{1,3}:\d{2}(?::\d{2})?[\.,]\d{3}|\d{1,3}:\d{2}(?::\d{2})?)$"
)
RANGE_LINE = re.compile(
    r"^\s*(?P<start>\d{1,3}:\d{2}(?:\.\d+)?)\s*(?:-|–|—|to)\s*"
    r"(?P<end>\d{1,3}:\d{2}(?:\.\d+)?)\s*[:|]\s*(?P<text>.+?)\s*$",
    re.IGNORECASE,
)

RAW_TRANSCRIPT_RELATIVE = "transcripts/raw.json"
REVIEWED_TRANSCRIPT_RELATIVE = "transcripts/reviewed.json"
ACTIVE_TRANSCRIPT_RELATIVE = "transcripts/active.json"
REVIEWED_STATUSES = frozenset({"reviewed", "partially_reviewed"})


def parse_clock(value: str) -> float:
    match = TIMESTAMP.search(value.strip())
    if not match:
        raise ACSUserError(f"Invalid transcript timestamp: {value!r}")
    return int(match.group("minutes")) * 60 + float(match.group("seconds"))


def _word(item: dict[str, Any]) -> dict[str, Any] | None:
    text = str(item.get("text") or item.get("word") or "").strip()
    if not text or item.get("start") is None or item.get("end") is None:
        return None
    return {
        "start": round(max(0.0, float(item["start"])), 3),
        "end": round(max(float(item["start"]), float(item["end"])), 3),
        "text": text,
    }


def _segment(
    start: float,
    end: float,
    text: str,
    speaker: str | None = None,
    *,
    source: str | None = None,
    words: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    item: dict[str, Any] = {
        "start": round(max(0.0, start), 3),
        "end": round(max(start, end), 3),
        "text": text.strip(),
    }
    if speaker:
        item["speaker"] = speaker
    if source:
        item["source"] = source
    if words:
        item["words"] = words
    return item


def _normalized_words(items: Any) -> list[dict[str, Any]]:
    if not isinstance(items, list):
        return []
    words: list[dict[str, Any]] = []
    for item in items:
        if isinstance(item, dict):
            normalized = _word(item)
            if normalized:
                words.append(normalized)
    return words


def _normalized_segment(item: dict[str, Any], *, default_source: str | None = None) -> dict[str, Any] | None:
    text = str(item.get("text") or "").strip()
    words = _normalized_words(item.get("words"))
    if not text and words:
        text = " ".join(word["text"] for word in words)
    if not text:
        return None
    start = float(item.get("start") or (words[0]["start"] if words else 0))
    end = float(item.get("end") or (words[-1]["end"] if words else start + 1))
    return _segment(
        start,
        end,
        text,
        str(item.get("speaker") or item.get("speaker_id") or "") or None,
        source=str(item.get("source") or default_source or "") or None,
        words=words or None,
    )


def normalize_json(raw: dict[str, Any], source_name: str) -> dict[str, Any]:
    metadata = raw.get("metadata") if isinstance(raw.get("metadata"), dict) else {}
    raw_segments = raw.get("segments")
    if isinstance(raw_segments, list):
        segments = [
            normalized
            for item in raw_segments
            if isinstance(item, dict)
            for normalized in [_normalized_segment(item)]
            if normalized is not None
        ]
        source = str(raw.get("source") or metadata.get("source") or source_name)
    elif isinstance(raw.get("words"), list):
        words = _normalized_words(raw["words"])
        if not words:
            raise ACSUserError(f"Transcript JSON contains no usable words: {source_name}")
        segments = [
            _segment(
                words[0]["start"],
                words[-1]["end"],
                " ".join(word["text"] for word in words),
                words=words,
            )
        ]
        source = str(raw.get("source") or metadata.get("source") or source_name)
    elif raw.get("text"):
        segments = [_segment(0, 1, str(raw["text"]))]
        source = str(raw.get("source") or metadata.get("source") or source_name)
    else:
        raise ACSUserError(f"Transcript JSON has no segments, words, or text: {source_name}")

    if not segments:
        raise ACSUserError(f"Transcript JSON contains no usable segments: {source_name}")
    normalized: dict[str, Any] = {"schema_version": "1.0", "source": source, "segments": segments}
    language = raw.get("language") or metadata.get("language")
    provider = raw.get("provider") or metadata.get("provider") or metadata.get("engine")
    model = raw.get("model") or metadata.get("model")
    if language:
        normalized["language"] = str(language)
    if provider:
        normalized["provider"] = str(provider)
    if model:
        normalized["model"] = str(model)
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
    """Parse strict SRT/VTT cues; never downgrade malformed subtitles to text."""

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
        start_token = parts[0]
        end_token = parts[1].split()[0] if len(parts) > 1 and parts[1].split() else ""
        if len(parts) != 2 or not SUBTITLE_TIMESTAMP.match(start_token) or not SUBTITLE_TIMESTAMP.match(end_token):
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


def is_asr_transcript(normalized: dict[str, Any], source_path: Path) -> bool:
    provider = str(normalized.get("provider") or "").lower()
    return provider in {"local-whisper", "openai-whisper", "whisper", "asr"} or "whisper" in source_path.name.lower()


def _source_binding(project_dir: Path, project: dict[str, Any]) -> dict[str, Any]:
    sources: list[dict[str, Any]] = []
    for source in project.get("sources", []):
        path = inside_project(project_dir, source["path"], label="project source")
        if not path.exists():
            raise ACSUserError(f"Cannot bind transcript to missing source: {source['path']}")
        sources.append(
            {
                "path": source["path"],
                "sha256": sha256_file(path),
                "bytes": path.stat().st_size,
            }
        )
    return {"project_id": project["project_id"], "sources": sources}


def _content_hash(record: dict[str, Any]) -> str:
    return canonical_hash({key: value for key, value in record.items() if key != "content_hash"})


def transcript_content_hash(record: dict[str, Any]) -> str:
    return str(record.get("content_hash") or _content_hash(record))


def build_raw_record(
    normalized: dict[str, Any],
    *,
    project_dir: Path,
    project: dict[str, Any],
    input_path: Path,
) -> dict[str, Any]:
    record: dict[str, Any] = dict(normalized)
    record.update(
        {
            "schema_version": "1.1",
            "record_type": "raw_asr" if is_asr_transcript(normalized, input_path) else "raw_transcript",
            "status": "raw",
            "revision": 1,
            "input_name": input_path.name,
            "source_binding": _source_binding(project_dir, project),
        }
    )
    record["content_hash"] = _content_hash(record)
    require_valid(record, load_schema("transcript"), "raw transcript")
    return record


def _default_source(project: dict[str, Any]) -> str:
    for source in project.get("sources", []):
        if source.get("role") == "primary":
            return str(source["path"])
    return str(project.get("sources", [{}])[0].get("path", ""))


def _review_segments(normalized: dict[str, Any], default_source: str) -> list[dict[str, Any]]:
    result: list[dict[str, Any]] = []
    for item in normalized.get("segments", []):
        if not isinstance(item, dict):
            continue
        segment = _normalized_segment(item, default_source=default_source)
        if segment:
            result.append(segment)
    return result


def build_reviewed_record(
    normalized: dict[str, Any],
    *,
    raw_record: dict[str, Any],
    project_dir: Path,
    project: dict[str, Any],
    reviewer: str,
    status: str = "reviewed",
    note: str = "",
    revision: int | None = None,
) -> dict[str, Any]:
    selected_status = "partially_reviewed" if status in {"partial", "partially-reviewed"} else status
    if selected_status not in {"reviewed", "partially_reviewed", "rejected"}:
        raise ACSUserError("Reviewed transcript status must be reviewed, partially_reviewed, or rejected.")
    source_binding = _source_binding(project_dir, project)
    default_source = _default_source(project)
    segments = [] if selected_status == "rejected" else _review_segments(normalized, default_source)
    if selected_status != "rejected" and not segments:
        raise ACSUserError("Reviewed transcript must contain at least one corrected/timestamped segment.")
    coverage = [
        {
            "source": str(segment.get("source") or default_source),
            "start": segment["start"],
            "end": segment["end"],
            "status": "covered",
        }
        for segment in segments
    ]
    record: dict[str, Any] = {
        "schema_version": "1.0",
        "record_type": "reviewed_truth",
        "project_id": project["project_id"],
        "source": normalized.get("source", "reviewed-input"),
        "status": selected_status,
        "reviewer": reviewer.strip(),
        "revision": int(revision or 1),
        "reviewed_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "raw_transcript_sha256": transcript_content_hash(raw_record),
        "source_binding": source_binding,
        "coverage": coverage,
        "segments": segments,
        "note": note.strip(),
    }
    record["content_hash"] = _content_hash(record)
    require_valid(record, load_schema("transcript-review"), "reviewed transcript")
    return record


def source_binding_current(contracts: Any, binding: dict[str, Any]) -> bool:
    try:
        return binding == _source_binding(contracts.directory, contracts.project)
    except (ACSUserError, KeyError, TypeError):
        return False


def _load_raw_record(contracts: Any) -> tuple[dict[str, Any], Path]:
    path = contracts.directory / RAW_TRANSCRIPT_RELATIVE
    if not path.exists():
        raise ACSUserError("Immutable raw transcript is missing; run `acs ingest-transcript` first.")
    record = read_json(path)
    require_valid(record, load_schema("transcript"), "raw transcript")
    if record.get("status") != "raw":
        raise ACSUserError("Raw transcript record is not marked raw.")
    if record.get("content_hash") != _content_hash(record):
        raise ACSUserError("Raw transcript content hash is invalid; restore the immutable raw record.")
    if not source_binding_current(contracts, record.get("source_binding", {})):
        raise ACSUserError("Raw transcript is stale after a source-byte or provenance change; ingest the current source again.")
    return record, path


def load_current_reviewed_transcript(contracts: Any) -> tuple[dict[str, Any], Path]:
    """Load reviewed truth and fail closed on rejection or stale evidence."""

    reviewed_path = contracts.directory / REVIEWED_TRANSCRIPT_RELATIVE
    if not reviewed_path.exists():
        raise ACSUserError(
            "Reviewed transcript truth is missing. Review raw ASR with `acs review-transcript` before derive, captions, or packaging."
        )
    reviewed = read_json(reviewed_path)
    require_valid(reviewed, load_schema("transcript-review"), "reviewed transcript")
    raw, _ = _load_raw_record(contracts)
    if reviewed.get("status") == "rejected":
        raise ACSUserError("Reviewed transcript is rejected; publish-ready text and captions are blocked.")
    if reviewed.get("status") not in REVIEWED_STATUSES:
        raise ACSUserError("Reviewed transcript is not approved for publish-ready use.")
    if reviewed.get("raw_transcript_sha256") != transcript_content_hash(raw):
        raise ACSUserError("Reviewed transcript is stale for the current raw ASR; review the current raw record again.")
    if not source_binding_current(contracts, reviewed.get("source_binding", {})):
        raise ACSUserError("Reviewed transcript is stale after a source-byte or provenance change; review it again.")
    if reviewed.get("content_hash") != _content_hash(reviewed):
        raise ACSUserError("Reviewed transcript content hash is invalid; restore or re-register the reviewed revision.")
    return reviewed, reviewed_path


def current_reviewed_segments(contracts: Any, ranges: list[dict[str, Any]] | None = None) -> list[dict[str, Any]]:
    reviewed, _ = load_current_reviewed_transcript(contracts)
    if ranges is None:
        return list(reviewed.get("segments", []))
    _require_coverage(reviewed, ranges)
    selected: list[dict[str, Any]] = []
    for segment in reviewed.get("segments", []):
        source = str(segment.get("source") or _default_source(contracts.project))
        if any(
            source == str(item.get("source") or source)
            and float(segment.get("end", 0)) > float(item.get("start", 0))
            and (item.get("end") is None or float(segment.get("start", 0)) < float(item["end"]))
            for item in ranges
        ):
            selected.append(segment)
    return selected


def _require_coverage(reviewed: dict[str, Any], ranges: list[dict[str, Any]]) -> None:
    coverage = reviewed.get("coverage", [])
    for requested in ranges:
        source = str(requested.get("source") or "")
        start = float(requested.get("start") or 0)
        end_value = requested.get("end")
        end = float(end_value) if end_value is not None else start + 0.001
        intervals = sorted(
            (
                float(item.get("start", 0)),
                float(item.get("end", 0)),
            )
            for item in coverage
            if str(item.get("source") or "") == source and item.get("status", "covered") == "covered"
        )
        cursor = start
        for interval_start, interval_end in intervals:
            if interval_end <= cursor:
                continue
            if interval_start > cursor + 0.001:
                break
            cursor = max(cursor, interval_end)
            if cursor >= end - 0.001:
                break
        if cursor < end - 0.001:
            label = f"{source} {start:.3f}-{end:.3f}s" if source else f"{start:.3f}-{end:.3f}s"
            raise ACSUserError(f"Reviewed transcript coverage does not cover selected source range: {label}")


def plan_transcript_ranges(contracts: Any, kind: str | None = None) -> list[dict[str, Any]]:
    kinds = [kind] if kind else ["long", "short"]
    raw_ends: dict[str, float] = {}
    media_ends: dict[str, float] = {}
    raw_path = contracts.directory / RAW_TRANSCRIPT_RELATIVE
    if raw_path.exists():
        try:
            raw = read_json(raw_path)
            default_source = _default_source(contracts.project)
            for item in raw.get("segments", []):
                source = str(item.get("source") or default_source)
                raw_ends[source] = max(raw_ends.get(source, 0.0), float(item.get("end") or 0))
        except (ACSUserError, TypeError, ValueError):
            raw_ends = {}
    inspection_path = contracts.directory / "inspection.json"
    if inspection_path.exists():
        try:
            inspection = read_json(inspection_path)
            for item in inspection.get("sources", []):
                if not isinstance(item, dict) or not isinstance(item.get("path"), str):
                    continue
                duration = float((item.get("media") or {}).get("duration_seconds") or 0)
                if duration > 0:
                    media_ends[item["path"]] = duration
        except (ACSUserError, TypeError, ValueError):
            media_ends = {}
    ranges: list[dict[str, Any]] = []
    for selected_kind in kinds:
        section = contracts.edit_plan.get(f"{selected_kind}_form", {})
        if not section.get("enabled"):
            continue
        for segment in section.get("segments", []):
            start = float(segment.get("start") or 0)
            duration = float(segment.get("duration") or 0)
            source = str(segment.get("source") or _default_source(contracts.project))
            if str(segment.get("audio") or "source") == "primary":
                # Primary audio is read from the project's primary source, not
                # from the visual B-roll source. Keep the old aligned behavior
                # when audio_start is omitted, while allowing independent
                # source timing for a primary-audio B-roll cut.
                source = _default_source(contracts.project)
                start = float(segment.get("audio_start") if segment.get("audio_start") is not None else start)
            # Muted B-roll is a visual-only edit input. It has no spoken
            # transcript range to review, while captions still account for
            # its duration when mapping the ordered edit segments.
            if str(segment.get("audio") or "") == "mute":
                continue
            media_end = media_ends.get(source)
            if duration > 0:
                planned_end = start + duration
                end = min(planned_end, media_end) if media_end is not None else planned_end
            else:
                # A zero-duration segment means "through the available source
                # transcript/media", not "check only the first millisecond".
                # This keeps partially reviewed truth from leaking into
                # captions or publish-ready derivatives for open-ended plans.
                end = raw_ends.get(source, media_end)
            ranges.append({"source": source, "start": start, "end": end})
    return ranges


def reviewed_transcript_proof(contracts: Any) -> dict[str, Any]:
    reviewed, path = load_current_reviewed_transcript(contracts)
    return {
        "path": display_path(contracts.directory, path),
        "sha256": sha256_file(path),
        "revision": reviewed["revision"],
        "status": reviewed["status"],
        "reviewer": reviewed["reviewer"],
        "raw_transcript_sha256": reviewed["raw_transcript_sha256"],
        "source_binding": reviewed["source_binding"],
    }
