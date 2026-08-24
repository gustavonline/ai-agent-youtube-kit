"""Supervised import seam for independently rendered adapter outputs."""

from __future__ import annotations

import json
import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .errors import ACSUserError
from .io import copy_file, read_json, sha256_file, write_json
from .media import probe
from .paths import display_path, inside_project
from .project import ProjectContracts, current_approval_hash, require_current_approval
from .schemas import load_schema
from .validation import require_valid


ADAPTER_IMPORT_RELATIVE = "adapters/import.json"
DEFAULT_ADAPTER_PROVENANCE = "Supervised local adapter output; source rights remain owned by the ACS production."


def _copy_if_distinct(source: Path, destination: Path) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    if source.resolve() != destination.resolve():
        shutil.copy2(source, destination)


def import_adapter_output(
    contracts: ProjectContracts,
    output_path: Path,
    manifest_path: Path,
    *,
    adapter: str,
    reviewer: str,
    provenance: str = DEFAULT_ADAPTER_PROVENANCE,
    adapter_version: str = "",
) -> Path:
    """Copy, inspect, and approve an adapter result inside the production."""

    require_current_approval(contracts)
    if not reviewer.strip():
        raise ACSUserError("Adapter import requires --by <reviewer>.")
    if not adapter.strip():
        raise ACSUserError("Adapter import requires a named adapter.")
    if not provenance.strip():
        raise ACSUserError("Adapter import requires a provenance note.")
    output = output_path.expanduser().resolve()
    manifest = manifest_path.expanduser().resolve()
    if not output.is_file():
        raise ACSUserError(f"Adapter output not found: {output}")
    if not manifest.is_file():
        raise ACSUserError(f"Adapter plan/manifest not found: {manifest}")
    try:
        manifest_value = json.loads(manifest.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ACSUserError(f"Adapter plan/manifest is not valid JSON: {manifest}") from exc
    if not isinstance(manifest_value, dict):
        raise ACSUserError("Adapter plan/manifest must be a JSON object.")

    adapter_dir = contracts.directory / "adapters"
    stored_output = adapter_dir / "imported-output" / output.name
    stored_manifest = adapter_dir / "imported-manifest.json"
    _copy_if_distinct(output, stored_output)
    _copy_if_distinct(manifest, stored_manifest)
    media = probe(stored_output)
    record = {
        "schema_version": "1.0",
        "project_id": contracts.project["project_id"],
        "adapter": adapter.strip(),
        "adapter_version": adapter_version.strip(),
        "status": "approved",
        "reviewer": reviewer.strip(),
        "approval_hash": current_approval_hash(contracts),
        "approval_revision": contracts.edit_plan["approval"]["approval_revision"],
        "output": {
            "path": display_path(contracts.directory, stored_output),
            "sha256": sha256_file(stored_output),
            "bytes": stored_output.stat().st_size,
            "media": media,
        },
        "manifest": {
            "path": display_path(contracts.directory, stored_manifest),
            "sha256": sha256_file(stored_manifest),
            "bytes": stored_manifest.stat().st_size,
        },
        "provenance": provenance.strip(),
        "imported_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
    }
    require_valid(record, load_schema("adapter-import"), "adapter import")
    record_path = contracts.directory / ADAPTER_IMPORT_RELATIVE
    write_json(record_path, record)
    return record_path


def load_current_adapter_import(contracts: ProjectContracts) -> tuple[dict[str, Any], Path] | None:
    record_path = contracts.directory / ADAPTER_IMPORT_RELATIVE
    if not record_path.exists():
        return None
    require_current_approval(contracts)
    record = read_json(record_path)
    require_valid(record, load_schema("adapter-import"), "adapter import")
    if record.get("project_id") != contracts.project["project_id"]:
        raise ACSUserError("Adapter import belongs to another production.")
    if record.get("approval_hash") != current_approval_hash(contracts) or record.get("approval_revision") != contracts.edit_plan["approval"]["approval_revision"]:
        raise ACSUserError("Adapter import approval is stale; re-import and approve it after the current plan approval.")
    output_path = inside_project(contracts.directory, record["output"]["path"], label="adapter output")
    manifest_path = inside_project(contracts.directory, record["manifest"]["path"], label="adapter manifest")
    if not output_path.exists() or sha256_file(output_path) != record["output"]["sha256"] or output_path.stat().st_size != record["output"]["bytes"]:
        raise ACSUserError("Adapter output is missing or hash-tampered; restore or re-import it.")
    if not manifest_path.exists() or sha256_file(manifest_path) != record["manifest"]["sha256"] or manifest_path.stat().st_size != record["manifest"]["bytes"]:
        raise ACSUserError("Adapter plan/manifest is missing or hash-tampered; restore or re-import it.")
    if probe(output_path) != record["output"]["media"]:
        raise ACSUserError("Adapter output media metadata changed; re-import and approve the current output.")
    return record, record_path
