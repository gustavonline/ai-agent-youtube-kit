"""Optional human creative direction and resolved render choices."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from .errors import ACSUserError
from .io import canonical_hash, sha256_file
from .paths import display_path, inside_project


CHOICE_KEYS = (
    "caption_choice",
    "framing_choice",
    "grade_choice",
    "callout_choice",
    "thumbnail_choice",
    "motion_choice",
)


def _lut_value(direction: dict[str, Any]) -> dict[str, Any] | None:
    value = direction.get("lut")
    if isinstance(value, str) and value.strip():
        return {"path": value}
    return value if isinstance(value, dict) and value.get("path") else None


def require_creative_direction(contracts: Any) -> dict[str, Any]:
    direction = contracts.edit_plan.get("creative_direction") or {}
    if not isinstance(direction, dict):
        raise ACSUserError("creative_direction must be an object when supplied.")
    result: dict[str, Any] = {key: str(direction.get(key, "")) for key in CHOICE_KEYS if direction.get(key) is not None}
    references = direction.get("references")
    if isinstance(references, list):
        result["references"] = [str(item) for item in references]
    if direction.get("rights_notes") is not None:
        result["rights_notes"] = str(direction["rights_notes"])
    lut = _lut_value(direction)
    if lut:
        lut_path = inside_project(contracts.directory, str(lut["path"]), label="creative LUT")
        preview_value = lut.get("preview_path") or lut.get("preview")
        if not preview_value:
            raise ACSUserError("A supplied LUT requires a representative preview_path before render.")
        preview_path = inside_project(contracts.directory, str(preview_value), label="creative LUT preview")
        if not lut_path.exists() or not preview_path.exists():
            raise ACSUserError("A supplied LUT and its representative preview must both exist inside the production.")
        if not lut.get("approved") or not str(lut.get("approved_by") or "").strip():
            raise ACSUserError("A supplied LUT requires explicit approved: true and approved_by before render.")
        preview_hash = sha256_file(preview_path)
        if lut.get("preview_sha256") and lut["preview_sha256"] != preview_hash:
            raise ACSUserError("Creative LUT preview hash is stale; update the preview proof and reapprove.")
        result["lut"] = {
            "path": display_path(contracts.directory, lut_path),
            "sha256": sha256_file(lut_path),
            "preview_path": display_path(contracts.directory, preview_path),
            "preview_sha256": preview_hash,
            "approved": True,
            "approved_by": str(lut["approved_by"]),
        }
    result["direction_hash"] = canonical_hash(result)
    return result


def creative_direction_fingerprints(contracts: Any) -> list[dict[str, Any]]:
    direction = contracts.edit_plan.get("creative_direction") or {}
    lut = _lut_value(direction) if isinstance(direction, dict) else None
    if not lut:
        return []
    proof = require_creative_direction(contracts)
    return [
        {"path": proof["lut"]["path"], "sha256": proof["lut"]["sha256"], "bytes": inside_project(contracts.directory, proof["lut"]["path"], label="creative LUT").stat().st_size},
        {"path": proof["lut"]["preview_path"], "sha256": proof["lut"]["preview_sha256"], "bytes": inside_project(contracts.directory, proof["lut"]["preview_path"], label="creative LUT preview").stat().st_size},
    ]
