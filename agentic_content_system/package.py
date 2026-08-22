"""Build and verify clean publish-ready packages for enabled channels only."""

from __future__ import annotations

import os
import shutil
import tempfile
from pathlib import Path
from typing import Any

from .derive import prune_disabled_derivatives, require_current_linkedin_derivative
from .delivery import current_delivery_intent_hash
from .errors import ACSUserError
from .inspect import require_current_inspection
from .io import canonical_hash, copy_file, read_json, sha256_file, write_json
from .paths import inside_project
from .publisher import build_publisher_handoff, verify_publisher_handoff
from .project import (
    ProjectContracts,
    channels_by_id,
    current_policy_hash,
    current_provenance_hash,
    disabled_channels,
    enabled_channels,
    require_cleared_rights,
    require_current_approval,
)
from .report import invalidate_active_handoff
from .render import prune_disabled_render_outputs, require_current_render_outputs
from .schemas import load_schema
from .validation import require_valid


def _enabled_media_kinds(contracts: ProjectContracts) -> set[str]:
    return {
        kind
        for channel in enabled_channels(contracts.brand)
        for kind in ("long", "short")
        if kind in channel.get("allowed_asset_types", [])
    }


def _asset_record(kind: str, source: Path, destination: Path, path_text: str) -> dict[str, Any]:
    copy_file(source, destination)
    return {
        "kind": kind,
        "path": path_text,
        "sha256": sha256_file(destination),
        "bytes": destination.stat().st_size,
    }


def _expected_routes(
    contracts: ProjectContracts,
    *,
    asset_paths: dict[str, str],
    post_path: str,
) -> list[dict[str, Any]]:
    routes: list[dict[str, Any]] = []
    for channel in enabled_channels(contracts.brand):
        channel_id = channel["id"]
        allowed = set(channel.get("allowed_asset_types", []))
        route_assets: list[str] = []
        if "long" in allowed and "long" in asset_paths:
            route_assets.append(asset_paths["long"])
        if "short" in allowed and "short" in asset_paths:
            route_assets.append(asset_paths["short"])
        route_post = post_path if channel_id == "linkedin" and "text" in allowed else ""
        if not route_assets and not route_post:
            raise ACSUserError(f"Enabled channel {channel_id!r} has no enabled asset route in this edit plan.")
        routes.append({"channel": channel_id, "assets": route_assets, "post_path": route_post})
    return routes


def _expected_provenance(contracts: ProjectContracts) -> list[dict[str, Any]]:
    return [
        {
            "path": source["path"],
            "rights_status": source["rights"]["status"],
            "owner": source["rights"]["owner"],
            "license": source["rights"]["license"],
            "source_url": source["rights"]["source_url"],
            "attribution": source["rights"]["attribution"],
        }
        for source in contracts.project["sources"]
    ]


def package_project(contracts: ProjectContracts) -> Path:
    """Stage a fresh package and replace the old handoff only after success."""

    require_current_approval(contracts)
    # Keep disabled routes out of the active derivative state even when the
    # caller goes straight from policy change to package without a separate
    # `acs derive` invocation.
    prune_disabled_derivatives(contracts)
    prune_disabled_render_outputs(contracts)
    require_cleared_rights(contracts)
    enabled = _enabled_media_kinds(contracts)
    render_kinds = [kind for kind in ("long", "short") if kind in enabled and contracts.edit_plan[f"{kind}_form"].get("enabled")]
    renders = require_current_render_outputs(contracts, render_kinds)
    channels = channels_by_id(contracts.brand)

    staging_dir: Path | None = Path(
        tempfile.mkdtemp(prefix=".publish-staging-", dir=str(contracts.directory))
    )
    publish_dir = contracts.directory / "publish"
    backup_parent: Path | None = None
    backup_path: Path | None = None
    installed = False
    try:
        assert staging_dir is not None
        assets_dir = staging_dir / "assets"
        posts_dir = staging_dir / "posts"
        assets_dir.mkdir(parents=True, exist_ok=True)
        posts_dir.mkdir(parents=True, exist_ok=True)
        assets: list[dict[str, Any]] = []
        asset_paths: dict[str, str] = {}
        for kind, source in renders.items():
            destination = assets_dir / ("long.mp4" if kind == "long" else "short-vertical.mp4")
            path_text = f"publish/assets/{destination.name}"
            assets.append(_asset_record(kind, source, destination, path_text))
            asset_paths[kind] = path_text

        post_path = ""
        if channels.get("linkedin", {}).get("enabled"):
            if "text" not in channels["linkedin"].get("allowed_asset_types", []):
                raise ACSUserError("LinkedIn is enabled but text is not an allowed asset type in brand.json")
            linkedin_source = require_current_linkedin_derivative(contracts)
            linkedin_destination = posts_dir / "linkedin.md"
            post_path = "publish/posts/linkedin.md"
            assets.append(_asset_record("text", linkedin_source, linkedin_destination, post_path))

        routes = _expected_routes(contracts, asset_paths=asset_paths, post_path=post_path)
        manifest_basis = {
            "project_id": contracts.project["project_id"],
            "plan_id": contracts.edit_plan["plan_id"],
            "approval_hash": contracts.edit_plan["approval"]["approval_hash"],
            "approval_revision": contracts.edit_plan["approval"]["approval_revision"],
            "policy_hash": current_policy_hash(contracts),
            "provenance_hash": current_provenance_hash(contracts),
            "delivery_intent_hash": current_delivery_intent_hash(contracts),
            "assets": assets,
            "routes": routes,
        }
        manifest = {
            "schema_version": "1.0",
            "manifest_id": f"{contracts.project['project_id']}-{canonical_hash(manifest_basis)[:12]}",
            "project_id": contracts.project["project_id"],
            "status": "publish_ready",
            "approval": {
                "status": "approved",
                "approved_by": contracts.edit_plan["approval"]["approved_by"],
                "approved_at": contracts.edit_plan["approval"]["approved_at"],
                "approval_hash": contracts.edit_plan["approval"]["approval_hash"],
                "approval_revision": contracts.edit_plan["approval"]["approval_revision"],
            },
            "policy_hash": current_policy_hash(contracts),
            "provenance_hash": current_provenance_hash(contracts),
            "delivery_intent_hash": current_delivery_intent_hash(contracts),
            "publisher_handoff_path": "publish/publisher-handoff.json",
            "routes": routes,
            "assets": assets,
            "disabled_channels": [
                {"channel": channel["id"], "reason": channel["reason"]}
                for channel in disabled_channels(contracts.brand)
            ],
            "provenance": _expected_provenance(contracts),
            "verification": {"status": "not_run", "external_posting": False},
        }
        require_valid(manifest, load_schema("publish-manifest"), "publish manifest")
        write_json(staging_dir / "manifest.json", manifest)
        publisher_handoff = build_publisher_handoff(
            contracts,
            manifest,
            staging_dir / "manifest.json",
        )
        require_valid(publisher_handoff, load_schema("publisher-handoff"), "publisher handoff")
        write_json(staging_dir / "publisher-handoff.json", publisher_handoff)
        # Keep the old package reachable until the new directory is fully
        # staged. Both temporary directories live under the project, so the
        # two renames stay on one filesystem and the active handoff changes in
        # one directory rename rather than a delete-then-create window.
        if publish_dir.exists():
            backup_parent = Path(
                tempfile.mkdtemp(prefix=".publish-old-", dir=str(contracts.directory))
            )
            backup_path = backup_parent / "publish"
            os.replace(publish_dir, backup_path)
        os.replace(staging_dir, publish_dir)
        staging_dir = None
        installed = True
        # A new manifest invalidates claims made about the previous package.
        # This happens only after the active publish directory is installed;
        # replacement failures therefore preserve the prior report/result.
        invalidate_active_handoff(contracts)
        if backup_parent is not None:
            shutil.rmtree(backup_parent, ignore_errors=True)
        return publish_dir / "manifest.json"
    except Exception:
        if staging_dir is not None and staging_dir.exists():
            shutil.rmtree(staging_dir)
        if backup_path is not None and backup_path.exists():
            # Final replacement failures must leave the prior valid handoff
            # active. The generated publish tree is safe to remove here; it
            # is never an owner source or contract.
            if publish_dir.exists():
                shutil.rmtree(publish_dir)
            os.replace(backup_path, publish_dir)
        elif installed and publish_dir.exists():
            # There was no prior package to restore. Do not leave a partially
            # installed package active if post-install invalidation failed.
            shutil.rmtree(publish_dir)
        if backup_parent is not None and backup_parent.exists():
            shutil.rmtree(backup_parent, ignore_errors=True)
        raise


def validate_current_package(contracts: ProjectContracts) -> dict[str, Any]:
    """Validate the complete current package without changing its state.

    This is shared by ``verify`` and ``review-report``.  A report may describe
    a current package whose verification is still ``not_run``, but it may not
    combine current source/inspection data with an older package, handoff,
    render, derivative, or passed-verification claim.
    """

    require_current_approval(contracts)
    require_cleared_rights(contracts)
    require_current_inspection(contracts)
    manifest_path = contracts.directory / "publish" / "manifest.json"
    manifest = read_json(manifest_path)
    require_valid(manifest, load_schema("publish-manifest"), "publish manifest")
    if manifest.get("project_id") != contracts.project.get("project_id"):
        raise ACSUserError("Publish manifest project_id does not match project.json")
    if manifest.get("verification", {}).get("external_posting") is not False:
        raise ACSUserError("Verification failed: external_posting must remain false in v0.1")
    approval = contracts.edit_plan["approval"]
    if manifest.get("approval", {}).get("approval_hash") != approval.get("approval_hash"):
        raise ACSUserError("Publish manifest approval hash is stale; repackage after current approval.")
    if manifest.get("approval", {}).get("approval_revision") != approval.get("approval_revision"):
        raise ACSUserError("Publish manifest approval revision is stale; repackage after current approval.")
    if manifest.get("policy_hash") != current_policy_hash(contracts):
        raise ACSUserError("Publish manifest channel policy is stale; repackage after policy review.")
    if manifest.get("provenance_hash") != current_provenance_hash(contracts):
        raise ACSUserError("Publish manifest provenance is stale; repackage after source review.")
    if manifest.get("delivery_intent_hash") != current_delivery_intent_hash(contracts):
        raise ACSUserError("Publish manifest delivery intent is stale; repackage after scheduling review.")
    expected_disabled = [
        {"channel": channel["id"], "reason": channel["reason"]}
        for channel in disabled_channels(contracts.brand)
    ]
    if manifest.get("disabled_channels") != expected_disabled:
        raise ACSUserError("Publish manifest disabled-channel policy is stale; repackage.")

    asset_map = {asset["path"]: asset for asset in manifest.get("assets", [])}
    expected_asset_paths = {
        f"publish/assets/{kind}.mp4" if kind == "long" else "publish/assets/short-vertical.mp4"
        for kind in _enabled_media_kinds(contracts)
        if contracts.edit_plan[f"{kind}_form"].get("enabled")
    }
    if channels_by_id(contracts.brand).get("linkedin", {}).get("enabled"):
        expected_asset_paths.add("publish/posts/linkedin.md")
    if set(asset_map) != expected_asset_paths:
        raise ACSUserError("Publish manifest assets do not exactly match current enabled policy and plan.")
    expected_routes = _expected_routes(
        contracts,
        asset_paths={
            kind: (
                "publish/assets/long.mp4"
                if kind == "long"
                else "publish/assets/short-vertical.mp4"
            )
            for kind in ("long", "short")
            if f"publish/assets/{kind}.mp4" in asset_map or kind == "short" and "publish/assets/short-vertical.mp4" in asset_map
        },
        post_path="publish/posts/linkedin.md" if "publish/posts/linkedin.md" in asset_map else "",
    )
    if manifest.get("routes") != expected_routes:
        raise ACSUserError("Publish manifest routes do not exactly match current channel policy.")
    if manifest.get("provenance") != _expected_provenance(contracts):
        raise ACSUserError("Publish manifest provenance entries do not match project.json.")

    render_kinds = [
        kind
        for kind in ("long", "short")
        if kind in _enabled_media_kinds(contracts)
        and contracts.edit_plan[f"{kind}_form"].get("enabled")
    ]
    require_current_render_outputs(contracts, render_kinds)
    if channels_by_id(contracts.brand).get("linkedin", {}).get("enabled"):
        if "text" not in channels_by_id(contracts.brand)["linkedin"].get("allowed_asset_types", []):
            raise ACSUserError("LinkedIn is enabled but text is not an allowed asset type in brand.json")
        require_current_linkedin_derivative(contracts)

    checked: list[str] = []
    for asset in manifest.get("assets", []):
        path = inside_project(contracts.directory, asset["path"], label="manifest asset")
        if not path.exists():
            raise ACSUserError(f"Publish asset is missing: {asset['path']}")
        digest = sha256_file(path)
        if digest != asset["sha256"]:
            raise ACSUserError(f"Publish asset hash mismatch: {asset['path']}")
        if path.stat().st_size != asset["bytes"]:
            raise ACSUserError(f"Publish asset byte count mismatch: {asset['path']}")
        checked.append(asset["path"])
    for route in manifest.get("routes", []):
        for asset_path in route.get("assets", []):
            if asset_path not in asset_map:
                raise ACSUserError(f"Route references an unknown asset: {asset_path}")
        if route.get("post_path") and route["post_path"] not in asset_map:
            raise ACSUserError(f"Route references an unknown post: {route['post_path']}")
    publisher_handoff_path, publisher_handoff = verify_publisher_handoff(
        contracts,
        manifest,
        manifest_path,
    )

    verification_path = contracts.directory / "publish" / "verification.json"
    verification_status = manifest.get("verification", {}).get("status")
    verification: dict[str, Any] = {}
    if verification_status == "not_run":
        if verification_path.exists():
            raise ACSUserError(
                "Publish package has not_run status but contains a stale verification record; repackage."
            )
    elif verification_status == "passed":
        if not verification_path.exists():
            raise ACSUserError("Publish package claims passed verification but verification.json is missing.")
        verification = read_json(verification_path)
        if verification.get("status") != "passed" or verification.get("external_posting") is not False:
            raise ACSUserError("Publish verification record is stale or contradicts the current manifest.")
        if verification.get("checked_assets") != checked:
            raise ACSUserError("Publish verification checked-assets binding is stale; rerun `acs verify`.")
        if verification.get("manifest_id") != manifest.get("manifest_id"):
            raise ACSUserError("Publish verification manifest binding is stale; rerun `acs verify`.")
        if verification.get("manifest_sha256") != sha256_file(manifest_path):
            raise ACSUserError("Publish verification manifest bytes are stale; rerun `acs verify`.")
        if verification.get("publisher_handoff_path") != manifest.get("publisher_handoff_path"):
            raise ACSUserError("Publish verification handoff path is stale; rerun `acs verify`.")
        if verification.get("publisher_handoff_sha256") != sha256_file(publisher_handoff_path):
            raise ACSUserError("Publish verification handoff bytes are stale; rerun `acs verify`.")
        if verification.get("publisher_handoff_status") != publisher_handoff.get("status"):
            raise ACSUserError("Publish verification handoff status is stale; rerun `acs verify`.")
        if verification.get("delivery_intent_hash") != manifest.get("delivery_intent_hash"):
            raise ACSUserError("Publish verification delivery intent binding is stale; rerun `acs verify`.")

    return {
        "manifest_path": manifest_path,
        "manifest": manifest,
        "publisher_handoff_path": publisher_handoff_path,
        "publisher_handoff": publisher_handoff,
        "verification_path": verification_path,
        "verification": verification,
        "checked_assets": checked,
    }


def verify_package(contracts: ProjectContracts) -> list[str]:
    state = validate_current_package(contracts)
    manifest_path = state["manifest_path"]
    manifest = state["manifest"]
    publisher_handoff_path = state["publisher_handoff_path"]
    publisher_handoff = state["publisher_handoff"]
    checked = state["checked_assets"]
    manifest["verification"] = {"status": "passed", "external_posting": False}
    write_json(manifest_path, manifest)
    write_json(
        contracts.directory / "publish" / "verification.json",
        {
            "status": "passed",
            "external_posting": False,
            "checked_assets": checked,
            "manifest_id": manifest["manifest_id"],
            "manifest_sha256": sha256_file(manifest_path),
            "publisher_handoff_path": manifest["publisher_handoff_path"],
            "publisher_handoff_sha256": sha256_file(publisher_handoff_path),
            "publisher_handoff_status": publisher_handoff["status"],
            "delivery_intent_hash": manifest["delivery_intent_hash"],
        },
    )
    return checked
