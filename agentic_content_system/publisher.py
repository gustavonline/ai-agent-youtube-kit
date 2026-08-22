"""Versioned, supervised-publisher handoff generation and verification."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from .delivery import current_delivery_intent, current_delivery_intent_hash
from .errors import ACSUserError
from .io import canonical_hash, read_json, sha256_file
from .paths import inside_project
from .project import ProjectContracts, disabled_channels
from .schemas import load_schema
from .validation import require_valid


PUBLISHER_HANDOFF_RELATIVE = "publish/publisher-handoff.json"


def manifest_binding_sha256(manifest: dict[str, Any]) -> str:
    """Hash the immutable package identity, excluding verify-time status bytes."""

    return canonical_hash({key: value for key, value in manifest.items() if key != "verification"})


def _asset_refs(manifest: dict[str, Any], route: dict[str, Any]) -> list[dict[str, Any]]:
    assets = {asset["path"]: asset for asset in manifest.get("assets", [])}
    paths = list(route.get("assets", []))
    post_path = route.get("post_path", "")
    if post_path:
        paths.append(post_path)
    refs: list[dict[str, Any]] = []
    for path in paths:
        asset = assets.get(path)
        if asset is None:
            raise ACSUserError(f"Publisher handoff route references an unknown asset: {path}")
        refs.append(
            {
                "path": asset["path"],
                "kind": asset["kind"],
                "sha256": asset["sha256"],
                "bytes": asset["bytes"],
            }
        )
    return refs


def build_publisher_handoff(
    contracts: ProjectContracts,
    manifest: dict[str, Any],
    manifest_path: Path,
) -> dict[str, Any]:
    intent = {route["channel"]: route for route in current_delivery_intent(contracts)["routes"]}
    if not manifest_path.exists():
        raise ACSUserError("Cannot bind publisher handoff to a missing publish manifest.")
    routes: list[dict[str, Any]] = []
    for route in manifest.get("routes", []):
        channel = route["channel"]
        delivery = intent.get(channel)
        if delivery is None:
            raise ACSUserError(f"Publisher handoff is missing delivery intent for enabled channel {channel!r}.")
        item: dict[str, Any] = {
            "channel": channel,
            "delivery_mode": delivery["delivery_mode"],
            "assets": _asset_refs(manifest, route),
            "post_path": route.get("post_path", ""),
        }
        if delivery["delivery_mode"] == "scheduled":
            item["scheduled_at"] = delivery["scheduled_at"]
            item["timezone"] = delivery["timezone"]
        routes.append(item)
    return {
        "schema_version": "1.1",
        "publisher_handoff_id": f"{manifest['manifest_id']}-publisher",
        "project_id": manifest["project_id"],
        "manifest_id": manifest["manifest_id"],
        "manifest_sha256": manifest_binding_sha256(manifest),
        "delivery_intent_hash": current_delivery_intent_hash(contracts),
        "status": "awaiting-separate-authorization",
        "not_posted": True,
        "external_posting": False,
        "routes": routes,
        "disabled_channels": [
            {"channel": channel["id"], "reason": channel["reason"]}
            for channel in disabled_channels(contracts.brand)
        ],
    }


def verify_publisher_handoff(
    contracts: ProjectContracts,
    manifest: dict[str, Any],
    manifest_path: Path,
) -> tuple[Path, dict[str, Any]]:
    handoff_relative = manifest.get("publisher_handoff_path")
    if handoff_relative != PUBLISHER_HANDOFF_RELATIVE:
        raise ACSUserError("Publish manifest publisher handoff path is missing or contradictory.")
    handoff_path = inside_project(contracts.directory, handoff_relative, label="publisher handoff path")
    if not handoff_path.exists():
        raise ACSUserError("Supervised publisher handoff is missing from the publish package.")
    handoff = read_json(handoff_path)
    require_valid(handoff, load_schema("publisher-handoff"), "publisher handoff")
    expected = build_publisher_handoff(contracts, manifest, manifest_path)
    if handoff != expected:
        raise ACSUserError(
            "Supervised publisher handoff is stale, tampered, or contradicts current policy, assets, or delivery intent."
        )
    return handoff_path, handoff
