"""Source inspection through ffprobe with rights/provenance carried forward."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from .errors import ACSUserError
from .io import read_json, sha256_file, write_json
from .media import probe
from .paths import display_path, inside_project
from .project import ProjectContracts, require_valid_project


def inspection_payload(contracts: ProjectContracts) -> dict[str, Any]:
    """Reconstruct the exact inspection claims from current local inputs.

    The static report consumes media and rights claims from inspection.json.
    Rebuilding the payload binds those claims to the current project id, source
    order, source bytes, provenance, kind/role, and ffprobe result instead of
    treating the inspection file as an unqualified cache.
    """

    require_valid_project(contracts, require_sources=True)
    sources: list[dict[str, Any]] = []
    for source in contracts.project["sources"]:
        path = inside_project(contracts.directory, source["path"], label="source.path")
        sources.append(
            {
                "path": display_path(contracts.directory, path),
                "sha256": sha256_file(path),
                "bytes": path.stat().st_size,
                "media": probe(path),
                "rights": source["rights"],
                "kind": source["kind"],
                "role": source["role"],
            }
        )
    return {
        "schema_version": "1.0",
        "project_id": contracts.project["project_id"],
        "sources": sources,
    }


def require_current_inspection(contracts: ProjectContracts) -> Path:
    """Require inspection claims to match the current authoritative inputs."""

    inspection_path = contracts.directory / "inspection.json"
    if not inspection_path.exists():
        raise ACSUserError("Current source inspection is required; run `acs inspect <workspace>` first.")
    actual = read_json(inspection_path)
    expected = inspection_payload(contracts)
    if actual != expected:
        raise ACSUserError(
            "Source inspection is stale for the current source set, bytes, rights, or media metadata; "
            "rerun `acs inspect <workspace>`."
        )
    return inspection_path


def inspect_project(contracts: ProjectContracts) -> Path:
    output = contracts.directory / "inspection.json"
    write_json(output, inspection_payload(contracts))
    return output
