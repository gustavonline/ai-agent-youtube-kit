"""Policy-aware, approval-bound text derivatives."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from .errors import ACSUserError
from .io import read_json, sha256_file, write_json
from .paths import display_path, inside_project
from .project import (
    ProjectContracts,
    channels_by_id,
    current_approval_hash,
    current_intent_hash,
    require_current_approval,
)
from .transcript import (
    current_reviewed_segments,
    load_current_reviewed_transcript,
    plan_transcript_ranges,
    reviewed_transcript_proof,
    transcript_text,
)


def _active_transcript_path(contracts: ProjectContracts) -> Path:
    relative = str(
        contracts.project.get("transcript", {}).get("path")
        or "transcripts/active.json"
    )
    return inside_project(contracts.directory, relative, label="project.transcript.path")


def _linkedin_enabled(contracts: ProjectContracts) -> bool:
    policy = channels_by_id(contracts.brand).get("linkedin", {})
    return bool(policy.get("enabled") and "text" in policy.get("allowed_asset_types", []))


def _load_active_transcript(contracts: ProjectContracts) -> tuple[dict[str, Any], Path]:
    reviewed, reviewed_path = load_current_reviewed_transcript(contracts)
    ranges = plan_transcript_ranges(contracts)
    segments = current_reviewed_segments(contracts, ranges if ranges else None)
    if not segments:
        raise ACSUserError("Reviewed transcript has no text in the selected edit ranges.")
    selected = dict(reviewed)
    selected["segments"] = segments
    return selected, reviewed_path


def _draft_linkedin(contracts: ProjectContracts, source_text: str) -> str:
    points = contracts.edit_plan["points"]
    title = contracts.project["title"]
    promise = contracts.project["promise"]
    cta = contracts.edit_plan["cta"]
    return (
        f"# {title}\n\n"
        f"{promise}\n\n"
        "A useful content system starts with the buyer's real question, not a platform trend. "
        "This walkthrough turns one piece of source material into an approved long-form edit, "
        "a focused short derivative, and a publish-ready handoff.\n\n"
        "## The three useful beats\n\n"
        + "\n".join(f"{index}. {point}" for index, point in enumerate(points, start=1))
        + "\n\n## What the source says\n\n"
        + (source_text or "Transcript text is not available yet.")
        + f"\n\n## Next step\n\n{cta}\n"
    )


def _record_entry(record: dict[str, Any], path: Path, contracts: ProjectContracts) -> dict[str, Any] | None:
    for item in record.get("derivatives", []):
        if item.get("path") == display_path(contracts.directory, path):
            return item
    return None


def prune_disabled_derivatives(contracts: ProjectContracts) -> None:
    """Remove disabled-route files from the active derivative state.

    A derivative under ``derived/`` is an active input to the local handoff.
    Keeping a LinkedIn draft there after policy disables LinkedIn makes the
    project look runnable for a route that is no longer allowed. Preserve the
    bytes, when present, in a clearly named recovery area outside active
    ``derived/``; package and result discovery never read that area.
    """

    if _linkedin_enabled(contracts):
        return

    output_path = contracts.directory / "derived" / "linkedin.md"
    record_path = contracts.directory / "derived" / "derivative-record.json"
    record: dict[str, Any] | None = None
    if record_path.exists():
        record = read_json(record_path)
    entry = _record_entry(record or {}, output_path, contracts)

    if output_path.exists():
        content_hash = sha256_file(output_path)
        archive_dir = contracts.directory / "recovery" / "disabled-derivatives"
        archive_dir.mkdir(parents=True, exist_ok=True)
        archive_path = archive_dir / f"linkedin-{content_hash[:16]}.md"
        if archive_path.exists():
            output_path.unlink()
        else:
            output_path.replace(archive_path)
        write_json(
            archive_path.with_suffix(".json"),
            {
                "schema_version": "1.0",
                "route": "linkedin",
                "source_path": display_path(contracts.directory, output_path),
                "archived_path": display_path(contracts.directory, archive_path),
                "content_sha256": content_hash,
                "disabled_reason": channels_by_id(contracts.brand)
                .get("linkedin", {})
                .get("reason", "LinkedIn is not enabled by current channel policy."),
                "previous_record": entry,
            },
        )

    if not record_path.exists():
        return
    remaining = [
        item
        for item in (record or {}).get("derivatives", [])
        if item.get("route") != "linkedin" and item.get("path") != "derived/linkedin.md"
    ]
    if remaining:
        record = dict(record or {})
        record["derivatives"] = remaining
        write_json(record_path, record)
    else:
        record_path.unlink()


def derive_project(contracts: ProjectContracts) -> list[Path]:
    """Create an allowed draft, or register/refine an existing human draft.

    Existing derivative contents are never overwritten. A changed plan or
    approval requires the human/agent to review the derivative before it can be
    registered for the new revision.
    """

    require_current_approval(contracts)
    prune_disabled_derivatives(contracts)
    if not _linkedin_enabled(contracts):
        # Disabled routes have no active derivative state. Any prior bytes
        # were moved to recovery/disabled-derivatives above.
        return []

    transcript, transcript_path = _load_active_transcript(contracts)
    output_dir = contracts.directory / "derived"
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / "linkedin.md"
    record_path = output_dir / "derivative-record.json"
    record = read_json(record_path) if record_path.exists() else {"schema_version": "1.0", "derivatives": []}
    current_plan_hash = current_intent_hash(contracts)
    current_approval = current_approval_hash(contracts)
    current_revision = contracts.edit_plan["approval"]["approval_revision"]
    previous_plan_hash = record.get("plan_hash")
    previous_approval_hash = record.get("approval_hash")
    if output_path.exists() and record.get("derivatives") and (
        previous_plan_hash != current_plan_hash
        or previous_approval_hash != current_approval
    ):
        raise ACSUserError(
            "LinkedIn derivative belongs to an older approved revision. Review it and remove or replace "
            "the old derivative explicitly before running `acs derive` for this revision."
        )

    if not output_path.exists():
        output_path.write_text(
            _draft_linkedin(contracts, transcript_text(transcript)),
            encoding="utf-8",
        )
        status = "draft"
    else:
        status = "agent-authored"

    content_hash = sha256_file(output_path)
    existing = _record_entry(record, output_path, contracts)
    if existing and existing.get("content_sha256") != content_hash:
        status = "agent-authored"
    registered_status = status
    if existing and existing.get("content_sha256") == content_hash:
        registered_status = existing.get("status", status)
    active_path = _active_transcript_path(contracts)
    active_hash = sha256_file(active_path) if active_path.exists() else sha256_file(transcript_path)
    reviewed_proof = reviewed_transcript_proof(contracts)
    entry = {
        "route": "linkedin",
        "kind": "text",
        "path": display_path(contracts.directory, output_path),
        "status": registered_status,
        "content_sha256": content_hash,
        # Keep the long-standing field bound to the active transcript view so
        # older workspaces still fail closed when that compatibility input is
        # edited. The reviewed record is the publish-ready source of truth.
        "transcript_sha256": active_hash,
        "active_transcript_sha256": active_hash,
        "reviewed_transcript_revision": reviewed_proof["revision"],
        "reviewed_transcript_sha256": reviewed_proof["sha256"],
    }
    record = {
        "schema_version": "1.0",
        "plan_hash": current_plan_hash,
        "approval_hash": current_approval,
        "approval_revision": current_revision,
        "derivatives": [entry],
    }
    write_json(record_path, record)
    return [output_path]


def require_current_linkedin_derivative(contracts: ProjectContracts) -> Path:
    if not _linkedin_enabled(contracts):
        raise ACSUserError("LinkedIn derivative requested while LinkedIn is disabled by brand policy.")
    output_path = contracts.directory / "derived" / "linkedin.md"
    record_path = contracts.directory / "derived" / "derivative-record.json"
    if not output_path.exists() or not record_path.exists():
        raise ACSUserError("LinkedIn derivative is missing; run `acs derive` after reviewing the approved plan.")
    record = read_json(record_path)
    if record.get("plan_hash") != current_intent_hash(contracts):
        raise ACSUserError("LinkedIn derivative is stale for the current edit plan; review and run `acs derive`.")
    if record.get("approval_hash") != current_approval_hash(contracts):
        raise ACSUserError("LinkedIn derivative approval is stale; review and run `acs derive`.")
    if record.get("approval_revision") != contracts.edit_plan["approval"]["approval_revision"]:
        raise ACSUserError("LinkedIn derivative revision is stale; review and run `acs derive`.")
    entry = _record_entry(record, output_path, contracts)
    reviewed, reviewed_path = load_current_reviewed_transcript(contracts)
    active_path = _active_transcript_path(contracts)
    if active_path.exists() and entry and entry.get("transcript_sha256") != sha256_file(active_path):
        raise ACSUserError(
            "LinkedIn derivative active transcript is stale; review the current transcript and run `acs derive` to "
            "regenerate or re-register the post."
        )
    if not entry or entry.get("reviewed_transcript_sha256") != sha256_file(reviewed_path):
        raise ACSUserError(
            "LinkedIn derivative reviewed transcript is stale; review the current transcript and run `acs derive` to "
            "regenerate or re-register the post."
        )
    if entry.get("reviewed_transcript_revision") != reviewed.get("revision"):
        raise ACSUserError("LinkedIn derivative reviewed revision is stale; run `acs derive` again.")
    if not entry or entry.get("content_sha256") != sha256_file(output_path):
        raise ACSUserError("LinkedIn derivative changed after registration; run `acs derive` to register the reviewed text.")
    return output_path
