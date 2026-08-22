"""Project loading, contract validation, and channel-policy helpers."""

from __future__ import annotations

from dataclasses import dataclass
from copy import deepcopy
from datetime import datetime
from pathlib import Path
from typing import Any

from .errors import ACSUserError
from .io import canonical_hash, read_json, sha256_file
from .paths import inside_project, project_file
from .schemas import load_schema
from .validation import ValidationIssue, validate_json, require_valid


CLEARED_RIGHTS_STATUSES = frozenset({"owned", "licensed", "public-domain", "cc0", "cc-by"})


@dataclass
class ProjectContracts:
    directory: Path
    brand: dict[str, Any]
    project: dict[str, Any]
    edit_plan: dict[str, Any]


def normalize_edit_plan(plan: dict[str, Any]) -> dict[str, Any]:
    """Upgrade the original one-window plan in memory to the segment shape."""

    normalized = deepcopy(plan)
    approval = normalized.setdefault("approval", {})
    approval.setdefault("approval_hash", "")
    approval.setdefault("approval_revision", 0)
    source = normalized.get("source", "")
    for kind in ("long", "short"):
        section = normalized.get(f"{kind}_form")
        if not isinstance(section, dict):
            continue
        if "segments" not in section:
            section["segments"] = [
                {
                    "source": source,
                    "start": float(section.get("start") or 0),
                    "duration": float(section.get("duration") or 0),
                }
            ]
    return normalized


def load_contracts(project_dir: Path, *, require_plan: bool = True) -> ProjectContracts:
    brand = read_json(project_file(project_dir, "brand"))
    project = read_json(project_file(project_dir, "project"))
    plan = normalize_edit_plan(read_json(project_file(project_dir, "edit_plan"))) if require_plan else {}
    return ProjectContracts(project_dir, brand, project, plan)


def edit_plan_intent(plan: dict[str, Any]) -> dict[str, Any]:
    return {key: value for key, value in plan.items() if key != "approval"}


def source_fingerprints(contracts: ProjectContracts) -> list[dict[str, Any]]:
    fingerprints: list[dict[str, Any]] = []
    for source in contracts.project.get("sources", []):
        path = inside_project(contracts.directory, source["path"], label="project source")
        if not path.exists():
            raise ACSUserError(f"Cannot fingerprint missing source: {source['path']}")
        fingerprints.append(
            {
                "path": source["path"],
                "sha256": sha256_file(path),
                "bytes": path.stat().st_size,
            }
        )
    return fingerprints


def approval_payload(contracts: ProjectContracts) -> dict[str, Any]:
    # ACS-owned delivery intent is included in the same approval hash as the
    # policy, project, edit intent, and source bytes. Import lazily to keep the
    # contract helper cycle-free.
    from .delivery import current_delivery_intent

    return {
        "brand": contracts.brand,
        "project": contracts.project,
        "edit_plan_intent": edit_plan_intent(contracts.edit_plan),
        "source_fingerprints": source_fingerprints(contracts),
        "delivery_intent": current_delivery_intent(contracts),
    }


def current_approval_hash(contracts: ProjectContracts) -> str:
    return canonical_hash(approval_payload(contracts))


def current_intent_hash(contracts: ProjectContracts) -> str:
    return canonical_hash(edit_plan_intent(contracts.edit_plan))


def current_policy_hash(contracts: ProjectContracts) -> str:
    return canonical_hash(contracts.brand)


def current_provenance_hash(contracts: ProjectContracts) -> str:
    return canonical_hash(contracts.project.get("sources", []))


def require_current_approval(contracts: ProjectContracts) -> None:
    require_valid_project(contracts, require_sources=True)
    approval = contracts.edit_plan.get("approval", {})
    if approval.get("status") != "approved" or not approval.get("approved_by"):
        raise ACSUserError(
            "This command is blocked until edit-plan.json has an explicit approval. "
            "Run `acs plan --approve --by <name>` after review."
        )
    expected = current_approval_hash(contracts)
    if approval.get("approval_hash") != expected:
        raise ACSUserError(
            "Approval is stale: a consequential brand, project, source, or edit-plan input changed. "
            "Run `acs plan --approve --by <name>` again after review."
        )


def require_cleared_rights(contracts: ProjectContracts) -> None:
    """Block publish-ready work until every declared source has cleared rights."""

    uncleared = [
        f"{source.get('path', '<missing path>')} ({source.get('rights', {}).get('status', 'unknown')})"
        for source in contracts.project.get("sources", [])
        if source.get("rights", {}).get("status") not in CLEARED_RIGHTS_STATUSES
    ]
    if uncleared:
        statuses = ", ".join(sorted(CLEARED_RIGHTS_STATUSES))
        raise ACSUserError(
            "Publish-ready packaging and verification are blocked until every source has a cleared rights "
            f"status ({statuses}). Uncleared source(s): " + ", ".join(uncleared)
        )


def contract_issues(contracts: ProjectContracts, *, require_sources: bool = True) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []
    for name, value in (
        ("brand", contracts.brand),
        ("project", contracts.project),
        ("edit-plan", contracts.edit_plan),
    ):
        schema_name = "edit-plan" if name == "edit-plan" else ("content-project" if name == "project" else name)
        issues.extend(validate_json(value, load_schema(schema_name), f"{name}"))
    project = contracts.project
    plan = contracts.edit_plan
    if project.get("project_id") != plan.get("project_id"):
        issues.append(ValidationIssue("edit-plan.project_id", "must match project.project_id"))
    source_paths = {source.get("path") for source in project.get("sources", [])}
    if plan.get("source") and plan.get("source") not in source_paths:
        issues.append(ValidationIssue("edit-plan.source", "must reference one of project.sources"))
    if plan.get("source"):
        try:
            source_path = inside_project(contracts.directory, plan["source"], label="edit-plan.source")
            if require_sources and not source_path.exists():
                issues.append(ValidationIssue("edit-plan.source", f"file does not exist: {plan['source']}"))
        except ACSUserError as exc:
            issues.append(ValidationIssue("edit-plan.source", str(exc)))
    declared_sources = set(source_paths)
    for kind in ("long", "short"):
        section = plan.get(f"{kind}_form", {})
        for index, segment in enumerate(section.get("segments", [])):
            source = segment.get("source")
            if source not in declared_sources:
                issues.append(ValidationIssue(f"edit-plan.{kind}_form.segments[{index}].source", "must reference project.sources"))
                continue
            try:
                segment_path = inside_project(contracts.directory, source, label=f"{kind} segment source")
                if require_sources and not segment_path.exists():
                    issues.append(ValidationIssue(f"edit-plan.{kind}_form.segments[{index}].source", f"file does not exist: {source}"))
            except ACSUserError as exc:
                issues.append(ValidationIssue(f"edit-plan.{kind}_form.segments[{index}].source", str(exc)))
    transcript_ref = project.get("transcript", {}).get("path")
    if transcript_ref and plan.get("transcript_ref") != transcript_ref:
        issues.append(ValidationIssue("edit-plan.transcript_ref", "must match project.transcript.path"))
    for label, value in (
        ("project.transcript.path", transcript_ref),
        ("edit-plan.transcript_ref", plan.get("transcript_ref")),
        ("edit-plan.long_form.output", plan.get("long_form", {}).get("output")),
        ("edit-plan.short_form.output", plan.get("short_form", {}).get("output")),
    ):
        if value:
            try:
                inside_project(contracts.directory, value, label=label)
            except ACSUserError as exc:
                issues.append(ValidationIssue(label, str(exc)))
    if require_sources:
        for index, source in enumerate(project.get("sources", [])):
            try:
                source_path = inside_project(contracts.directory, source.get("path", ""), label=f"sources[{index}].path")
                if not source_path.exists():
                    issues.append(ValidationIssue(f"project.sources[{index}].path", f"file does not exist: {source.get('path')}"))
            except ACSUserError as exc:
                issues.append(ValidationIssue(f"project.sources[{index}].path", str(exc)))
    channels = contracts.brand.get("channels", [])
    channel_ids = [channel.get("id") for channel in channels]
    if len(channel_ids) != len(set(channel_ids)):
        issues.append(ValidationIssue("brand.channels", "channel ids must be unique"))
    for index, channel in enumerate(channels):
        if not channel.get("enabled") and not channel.get("reason", "").strip():
            issues.append(ValidationIssue(f"brand.channels[{index}].reason", "disabled channels require a reason"))
    try:
        from .delivery import current_delivery_intent

        current_delivery_intent(contracts)
    except ACSUserError as exc:
        issues.append(ValidationIssue("project.delivery_intent", str(exc)))
    return issues


def require_valid_project(contracts: ProjectContracts, *, require_sources: bool = True) -> None:
    issues = contract_issues(contracts, require_sources=require_sources)
    if issues:
        rendered = "\n".join(f"- {issue}" for issue in issues)
        raise ACSUserError(f"Workspace validation failed:\n{rendered}")


def channels_by_id(brand: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {channel["id"]: channel for channel in brand.get("channels", [])}


def brand_profile_issues(brand: dict[str, Any]) -> list[ValidationIssue]:
    """Return schema and policy issues for a clone-owned channel profile."""

    issues = validate_json(brand, load_schema("brand"), "brand")
    if not isinstance(brand, dict):
        return issues
    channels = brand.get("channels", [])
    if not isinstance(channels, list):
        return issues
    channel_ids = [
        channel.get("id")
        for channel in channels
        if isinstance(channel, dict) and isinstance(channel.get("id"), str)
    ]
    if len(channel_ids) != len(set(channel_ids)):
        issues.append(ValidationIssue("brand.channels", "channel ids must be unique"))
    for index, channel in enumerate(channels):
        if isinstance(channel, dict) and not channel.get("enabled") and not channel.get("reason", "").strip():
            issues.append(ValidationIssue(f"brand.channels[{index}].reason", "disabled channels require a reason"))

    defaults = brand.get("delivery_defaults")
    if not isinstance(defaults, dict):
        return issues
    routes = defaults.get("routes", [])
    known = {
        channel["id"]: channel
        for channel in channels
        if isinstance(channel, dict) and isinstance(channel.get("id"), str)
    }
    enabled_ids = [channel_id for channel_id, channel in known.items() if channel.get("enabled")]
    seen: set[str] = set()
    for index, route in enumerate(routes if isinstance(routes, list) else []):
        if not isinstance(route, dict):
            continue
        channel_id = route.get("channel")
        if not isinstance(channel_id, str):
            continue
        if channel_id in seen:
            issues.append(ValidationIssue(f"brand.delivery_defaults.routes[{index}].channel", "duplicate channel"))
        seen.add(channel_id)
        policy = known.get(channel_id)
        if policy is None:
            issues.append(ValidationIssue(f"brand.delivery_defaults.routes[{index}].channel", "must reference a declared channel"))
        elif not policy.get("enabled"):
            issues.append(
                ValidationIssue(
                    f"brand.delivery_defaults.routes[{index}].channel",
                    "disabled channels cannot be delivery defaults",
                )
            )
        elif route.get("delivery_mode") == "scheduled":
            scheduled_at = route.get("scheduled_at", "")
            if not isinstance(scheduled_at, str) or ("T" not in scheduled_at and " " not in scheduled_at):
                issues.append(
                    ValidationIssue(
                        f"brand.delivery_defaults.routes[{index}].scheduled_at",
                        "scheduled delivery requires a date and time",
                    )
                )
            else:
                try:
                    datetime.fromisoformat(scheduled_at.replace("Z", "+00:00"))
                except (AttributeError, ValueError):
                    issues.append(
                        ValidationIssue(
                            f"brand.delivery_defaults.routes[{index}].scheduled_at",
                            "scheduled delivery requires an ISO date/time",
                        )
                    )
    missing = [channel_id for channel_id in enabled_ids if channel_id not in seen]
    if missing:
        issues.append(
            ValidationIssue(
                "brand.delivery_defaults.routes",
                "must specify every enabled channel: " + ", ".join(missing),
            )
        )
    return issues


def require_valid_brand_profile(brand: dict[str, Any]) -> None:
    issues = brand_profile_issues(brand)
    if issues:
        rendered = "\n".join(f"- {issue}" for issue in issues)
        raise ACSUserError(f"Brand profile validation failed:\n{rendered}")


def enabled_channels(brand: dict[str, Any]) -> list[dict[str, Any]]:
    return [channel for channel in brand.get("channels", []) if channel.get("enabled")]


def disabled_channels(brand: dict[str, Any]) -> list[dict[str, Any]]:
    return [channel for channel in brand.get("channels", []) if not channel.get("enabled")]
