"""Approved-plan deterministic long-form and vertical-short rendering."""

from __future__ import annotations

from pathlib import Path
from typing import Any
import tempfile

from .captions import caption_intent, render_caption_assets
from .creative import require_creative_direction
from .errors import ACSUserError
from .io import canonical_hash, read_json, sha256_file, write_json
from .media import probe, render_segments
from .paths import display_path, inside_project, render_output_path
from .project import (
    ProjectContracts,
    current_approval_hash,
    current_intent_hash,
    require_current_approval,
)
from .transcript import reviewed_transcript_proof


def _render_spec(contracts: ProjectContracts, kind: str) -> tuple[dict[str, Any], list[dict[str, Any]], Path]:
    section = contracts.edit_plan[f"{kind}_form"]
    output = render_output_path(contracts.directory, section["output"], label=f"{kind}_form.output")
    segments: list[dict[str, Any]] = []
    for segment in section.get("segments", []):
        source = inside_project(contracts.directory, segment["source"], label=f"{kind} segment source")
        if not source.exists():
            raise ACSUserError(f"Render source does not exist: {display_path(contracts.directory, source)}")
        resolved = dict(segment)
        resolved["resolved_source"] = str(source)
        overlay = segment.get("overlay")
        if overlay:
            overlay_path = inside_project(contracts.directory, overlay, label=f"{kind} segment overlay")
            if not overlay_path.exists():
                raise ACSUserError(f"Render overlay does not exist: {display_path(contracts.directory, overlay_path)}")
            resolved["resolved_overlay_source"] = str(overlay_path)
        segments.append(resolved)
    if section.get("enabled") and not segments:
        raise ACSUserError(f"{kind}_form requires at least one segment")
    return section, segments, output


def _load_record(record_path: Path) -> dict[str, Any]:
    if not record_path.exists():
        return {"schema_version": "2.0", "renders": {}}
    return read_json(record_path)


def _primary_audio_source(contracts: ProjectContracts) -> Path | None:
    primary = next(
        (source for source in contracts.project.get("sources", []) if source.get("role") == "primary"),
        None,
    )
    if primary is None:
        return None
    path = inside_project(contracts.directory, primary["path"], label="primary audio source")
    return path if path.exists() else None


def _archive_disabled_render(contracts: ProjectContracts, kind: str, output_value: str) -> None:
    output = render_output_path(contracts.directory, output_value, label=f"{kind}_form.output")
    if not output.exists():
        return
    if not output.is_file():
        raise ACSUserError(f"Disabled {kind} render path is not a file: {display_path(contracts.directory, output)}")
    archive_dir = contracts.directory / "recovery" / "disabled-renders"
    archive_dir.mkdir(parents=True, exist_ok=True)
    digest = sha256_file(output)
    archive_path = archive_dir / f"{kind}-{digest[:16]}{output.suffix or '.bin'}"
    if archive_path.exists():
        output.unlink()
    else:
        output.replace(archive_path)


def prune_disabled_render_outputs(contracts: ProjectContracts) -> dict[str, Any]:
    """Keep render records and active bytes limited to enabled edit outputs."""

    record_path = contracts.directory / "renders" / "render-record.json"
    record = _load_record(record_path)
    renders = record.setdefault("renders", {})
    changed = False
    for kind in ("long", "short"):
        section = contracts.edit_plan.get(f"{kind}_form", {})
        if section.get("enabled"):
            continue
        output_value = section.get("output")
        if output_value:
            output = render_output_path(contracts.directory, output_value, label=f"{kind}_form.output")
            if output.exists():
                _archive_disabled_render(contracts, kind, str(output_value))
        if kind in renders:
            renders.pop(kind, None)
            changed = True
    if record_path.exists() and changed:
        record["schema_version"] = "2.0"
        write_json(record_path, record)
    return record


def _used_source_fingerprints(segments: list[dict[str, Any]]) -> list[dict[str, Any]]:
    fingerprints: list[dict[str, Any]] = []
    seen: set[str] = set()
    for segment in segments:
        source = segment["source"]
        if source not in seen:
            path = Path(segment["resolved_source"])
            fingerprints.append({"path": source, "sha256": sha256_file(path), "bytes": path.stat().st_size})
            seen.add(source)
        overlay = segment.get("overlay")
        if overlay and overlay not in seen:
            overlay_path = Path(segment["resolved_overlay_source"])
            fingerprints.append({"path": overlay, "sha256": sha256_file(overlay_path), "bytes": overlay_path.stat().st_size})
            seen.add(overlay)
    return fingerprints


def render_project(contracts: ProjectContracts, kinds: list[str], *, force: bool = False) -> list[dict[str, Any]]:
    require_current_approval(contracts)
    creative_proof = require_creative_direction(contracts)
    record_path = contracts.directory / "renders" / "render-record.json"
    record = prune_disabled_render_outputs(contracts)
    results: list[dict[str, Any]] = []
    intent_hash = current_intent_hash(contracts)
    approval_hash = current_approval_hash(contracts)
    approval_revision = contracts.edit_plan["approval"]["approval_revision"]
    primary_audio_source = _primary_audio_source(contracts)
    for kind in kinds:
        section, segments, output = _render_spec(contracts, kind)
        if not section.get("enabled"):
            results.append({"kind": kind, "status": "disabled"})
            continue
        caption_config = caption_intent(contracts.edit_plan, kind)
        caption_fingerprint: dict[str, Any] | None = None
        if caption_config is not None:
            reviewed = reviewed_transcript_proof(contracts)
            caption_fingerprint = {
                "intent_hash": canonical_hash(caption_config),
                "reviewed_transcript_revision": reviewed["revision"],
                "reviewed_transcript_sha256": reviewed["sha256"],
            }
        source_fingerprints = _used_source_fingerprints(segments)
        previous = record.get("renders", {}).get(kind, {})
        if (
            not force
            and output.exists()
            and previous.get("plan_hash") == intent_hash
            and previous.get("approval_hash") == approval_hash
            and previous.get("approval_revision") == approval_revision
            and previous.get("source_fingerprints") == source_fingerprints
            and previous.get("caption_fingerprint") == caption_fingerprint
            and previous.get("output_sha256") == sha256_file(output)
        ):
            metadata = previous.get("metadata") or probe(output)
            results.append(
                {
                    "kind": kind,
                    "status": "cached",
                    "output": display_path(contracts.directory, output),
                    "metadata": metadata,
                }
            )
            continue
        caption_metadata: dict[str, Any] | None = None
        if caption_config is None:
            metadata = render_segments(
                segments=segments,
                output=output,
                kind="long" if kind == "long" else "short",
                work_dir=contracts.directory / "renders",
                frame=section.get("frame") or section.get("framing"),
                primary_audio_source=primary_audio_source,
            )
        else:
            with tempfile.TemporaryDirectory(prefix=".acs-caption-base-", dir=str(contracts.directory / "renders")) as temp_name:
                base_output = Path(temp_name) / "base.mp4"
                render_segments(
                    segments=segments,
                    output=base_output,
                    kind="long" if kind == "long" else "short",
                    work_dir=contracts.directory / "renders",
                    frame=section.get("frame") or section.get("framing"),
                    primary_audio_source=primary_audio_source,
                )
                caption_metadata = render_caption_assets(
                    contracts,
                    kind,
                    base_output=base_output,
                    final_output=output,
                    edit_segments=segments,
                    work_dir=contracts.directory / "renders",
                )
            metadata = probe(output)
            metadata["captions"] = caption_metadata
        metadata["framing"] = section.get("frame") or section.get("framing") or (
            {"fit": "cover", "anchor": {"x": 0.5, "y": 0.5}} if kind == "short" else {"fit": "native"}
        )
        metadata["audio_modes"] = sorted({str(segment.get("audio") or "source") for segment in segments})
        metadata["audio_boundary_fade_seconds"] = 0.03 if len(segments) > 1 else 0.0
        metadata["audio_boundary_fade_applied"] = len(segments) > 1
        metadata["audio_boundary_evidence"] = (
            "30ms per-segment fade-in/fade-out before ordered concat"
            if len(segments) > 1
            else "single ordered segment; no join boundary"
        )
        metadata["creative_direction"] = creative_proof
        output_hash = sha256_file(output)
        record.setdefault("renders", {})[kind] = {
            "kind": kind,
            "output": display_path(contracts.directory, output),
            "segments": [
                {key: value for key, value in segment.items() if key != "resolved_source"}
                for segment in segments
            ],
            "source_fingerprints": source_fingerprints,
            "plan_hash": intent_hash,
            "approval_hash": approval_hash,
            "approval_revision": approval_revision,
            "output_sha256": output_hash,
            "bytes": output.stat().st_size,
            "metadata": metadata,
            "caption_fingerprint": caption_fingerprint,
            "captions": caption_metadata,
        }
        results.append(
            {
                "kind": kind,
                "status": "rendered",
                "output": display_path(contracts.directory, output),
                "metadata": metadata,
            }
        )
    record["schema_version"] = "2.0"
    write_json(record_path, record)
    return results


def require_current_render_outputs(contracts: ProjectContracts, kinds: list[str]) -> dict[str, Path]:
    """Fail closed if a package would consume a stale or unapproved render."""

    require_current_approval(contracts)
    record_path = contracts.directory / "renders" / "render-record.json"
    record = _load_record(record_path)
    expected_intent_hash = current_intent_hash(contracts)
    expected_approval_hash = current_approval_hash(contracts)
    expected_revision = contracts.edit_plan["approval"]["approval_revision"]
    outputs: dict[str, Path] = {}
    for kind in kinds:
        section, segments, output = _render_spec(contracts, kind)
        if not section.get("enabled"):
            continue
        entry = record.get("renders", {}).get(kind)
        if not entry:
            raise ACSUserError(f"No render record for enabled {kind} output; run `acs render` first.")
        expected_sources = _used_source_fingerprints(segments)
        if entry.get("plan_hash") != expected_intent_hash:
            raise ACSUserError(f"Stale {kind} render: edit plan changed; run `acs render` after approval.")
        if entry.get("approval_hash") != expected_approval_hash or entry.get("approval_revision") != expected_revision:
            raise ACSUserError(f"Stale {kind} render approval: run `acs render` after the current approval.")
        if entry.get("source_fingerprints") != expected_sources:
            raise ACSUserError(f"Stale {kind} render source: a declared input changed; run `acs render` again.")
        if not output.exists():
            raise ACSUserError(f"Missing current {kind} render: {display_path(contracts.directory, output)}")
        if entry.get("output_sha256") != sha256_file(output):
            raise ACSUserError(f"Changed {kind} render output: restore or rerun `acs render`.")
        expected_captions = caption_intent(contracts.edit_plan, kind)
        caption_record = entry.get("captions") or {}
        if expected_captions is None:
            if caption_record.get("enabled"):
                raise ACSUserError(f"{kind} render caption record is stale; rerun `acs render`.")
        else:
            expected_review = reviewed_transcript_proof(contracts)
            if (
                not caption_record.get("enabled")
                or caption_record.get("caption_intent_hash") != canonical_hash(expected_captions)
                or caption_record.get("reviewed_transcript_revision") != expected_review["revision"]
                or caption_record.get("reviewed_transcript_sha256") != expected_review["sha256"]
            ):
                raise ACSUserError(f"{kind} render captions are stale; rerun `acs render`.")
            sidecar_path = caption_record.get("sidecar_path")
            if expected_captions.get("sidecar", True):
                if not sidecar_path:
                    raise ACSUserError(f"Missing current {kind} caption sidecar; rerun `acs render`.")
                sidecar = inside_project(contracts.directory, sidecar_path, label=f"{kind} caption sidecar")
                if not sidecar.exists() or caption_record.get("sidecar_sha256") != sha256_file(sidecar):
                    raise ACSUserError(f"Changed {kind} caption sidecar; rerun `acs render`.")
        outputs[kind] = output
    return outputs
