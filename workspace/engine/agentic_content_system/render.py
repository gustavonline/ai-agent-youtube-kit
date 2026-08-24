"""Approved-plan deterministic long-form and vertical-short rendering."""

from __future__ import annotations

from pathlib import Path
from typing import Any

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
        segments.append(resolved)
    if section.get("enabled") and not segments:
        raise ACSUserError(f"{kind}_form requires at least one segment")
    return section, segments, output


def _load_record(record_path: Path) -> dict[str, Any]:
    if not record_path.exists():
        return {"schema_version": "2.0", "renders": {}}
    return read_json(record_path)


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
        if source in seen:
            continue
        path = Path(segment["resolved_source"])
        fingerprints.append({"path": source, "sha256": sha256_file(path), "bytes": path.stat().st_size})
        seen.add(source)
    return fingerprints


def render_project(contracts: ProjectContracts, kinds: list[str], *, force: bool = False) -> list[dict[str, Any]]:
    require_current_approval(contracts)
    record_path = contracts.directory / "renders" / "render-record.json"
    record = prune_disabled_render_outputs(contracts)
    results: list[dict[str, Any]] = []
    intent_hash = current_intent_hash(contracts)
    approval_hash = current_approval_hash(contracts)
    approval_revision = contracts.edit_plan["approval"]["approval_revision"]
    for kind in kinds:
        section, segments, output = _render_spec(contracts, kind)
        if not section.get("enabled"):
            results.append({"kind": kind, "status": "disabled"})
            continue
        source_fingerprints = _used_source_fingerprints(segments)
        previous = record.get("renders", {}).get(kind, {})
        if (
            not force
            and output.exists()
            and previous.get("plan_hash") == intent_hash
            and previous.get("approval_hash") == approval_hash
            and previous.get("approval_revision") == approval_revision
            and previous.get("source_fingerprints") == source_fingerprints
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
        metadata = render_segments(
            segments=segments,
            output=output,
            kind="long" if kind == "long" else "short",
            work_dir=contracts.directory / "renders",
        )
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
        outputs[kind] = output
    return outputs
