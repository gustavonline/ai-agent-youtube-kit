"""Export a hashed, caller-agnostic ACS proof and learning result."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from .errors import ACSUserError
from .adapters import ADAPTER_IMPORT_RELATIVE, load_current_adapter_import
from .inspect import require_current_inspection
from .io import canonical_hash, read_json, sha256_file, write_json
from .package import verify_package
from .paths import display_path, inside_project
from .project import ProjectContracts, require_current_approval
from .publisher import PUBLISHER_HANDOFF_RELATIVE
from .report import qa_review_proof, render_review_proof
from .schemas import load_schema
from .validation import require_valid


def archive_active_result(contracts: ProjectContracts) -> None:
    """Move an old result out of active state before a new export attempt."""

    result_path = contracts.directory / "results" / "run-result.json"
    if not result_path.exists():
        return
    if not result_path.is_file():
        raise ACSUserError("Active run-result path is not a file.")
    archive_dir = contracts.directory / "recovery" / "stale-results"
    archive_dir.mkdir(parents=True, exist_ok=True)
    digest = sha256_file(result_path)
    archive_path = archive_dir / f"run-result-{digest[:16]}.json"
    if archive_path.exists():
        result_path.unlink()
    else:
        result_path.replace(archive_path)
    index_path = contracts.directory / "results" / "index.md"
    if index_path.exists():
        index_archive = contracts.directory / "recovery" / "stale-results" / f"index-{digest[:16]}.md"
        if index_archive.exists():
            index_path.unlink()
        else:
            index_path.replace(index_archive)


def _write_result_index(contracts: ProjectContracts, manifest: dict[str, Any]) -> Path:
    lines = [
        f"# Result index: {contracts.project['title']}",
        "",
        "This is a human-facing pointer into the canonical production workspace. The workspace remains the source of truth; no external post was made.",
        "",
        "## Finished files",
        "",
    ]
    labels = {
        "long": "Long video",
        "short": "9:16 short video",
        "caption": "Caption sidecar",
        "text": "Text post",
        "adapter": "Imported adapter output",
        "adapter-manifest": "Adapter plan/manifest",
    }
    for asset in manifest.get("assets", []):
        label = labels.get(asset.get("kind"), asset.get("kind", "Asset"))
        path = asset.get("path", "")
        lines.append(f"- {label}: [`{path}`](../{path})")
    lines.extend(
        [
            "",
            "## Proof and handoff",
            "",
            "- [Static review report](../reports/review.html)",
            "- [Review record](../reports/review.json)",
            "- [Verified run result](run-result.json)",
            "- [Publisher handoff](../publish/publisher-handoff.json)",
        ]
    )
    qa_paths = [item["path"] for item in qa_review_proof(contracts)]
    if qa_paths:
        lines.append("")
        lines.append("## Visual QA")
        lines.append("")
        for path in qa_paths:
            lines.append(f"- Visual QA proof: [`{path}`](../{path})")
    lines.extend(
        [
            "",
            "Status: verified locally; publisher handoff remains awaiting separate authorization.",
            "",
        ]
    )
    path = contracts.directory / "results" / "index.md"
    path.write_text("\n".join(lines), encoding="utf-8")
    return path


def _require_current_review(
    contracts: ProjectContracts,
    *,
    manifest_path: Path,
    verification_path: Path,
    report_path: Path,
    review_record_path: Path,
    manifest: dict[str, Any],
) -> dict[str, Any]:
    if not report_path.exists() or not review_record_path.exists():
        raise ACSUserError("Result export requires a current review-report; rerun `acs review-report`.")
    review = read_json(review_record_path)
    require_valid(review, load_schema("review-record"), "review record")
    inspection_path = require_current_inspection(contracts)
    approval = contracts.edit_plan["approval"]
    if review.get("project_id") != contracts.project["project_id"]:
        raise ACSUserError("Review record project_id is stale; rerun `acs review-report`.")
    if review.get("html") != "reports/review.html" or review.get("html_sha256") != sha256_file(report_path):
        raise ACSUserError("Review report bytes are stale or changed; rerun `acs review-report`.")
    if review.get("inspection_sha256") != sha256_file(inspection_path):
        raise ACSUserError("Review report source inspection binding is stale; rerun `acs review-report`.")
    if review.get("manifest_id") != manifest.get("manifest_id"):
        raise ACSUserError("Review report is bound to an older publish manifest; rerun `acs review-report`.")
    if review.get("manifest_sha256") != sha256_file(manifest_path):
        raise ACSUserError("Review report manifest binding is stale; rerun `acs review-report`.")
    if review.get("manifest_approval_hash") != manifest.get("approval", {}).get("approval_hash"):
        raise ACSUserError("Review report approval binding is stale; rerun `acs review-report`.")
    if review.get("manifest_approval_revision") != manifest.get("approval", {}).get("approval_revision"):
        raise ACSUserError("Review report approval revision is stale; rerun `acs review-report`.")
    if review.get("approval_hash") != approval.get("approval_hash") or review.get("approval_revision") != approval.get("approval_revision"):
        raise ACSUserError("Review report is not bound to the current approval; rerun `acs review-report`.")
    if review.get("policy_hash") != manifest.get("policy_hash") or review.get("provenance_hash") != manifest.get("provenance_hash"):
        raise ACSUserError("Review report policy/provenance binding is stale; rerun `acs review-report`.")
    if review.get("delivery_intent_hash") != manifest.get("delivery_intent_hash"):
        raise ACSUserError("Review report delivery intent binding is stale; rerun `acs review-report`.")
    if review.get("publisher_handoff_path") != manifest.get("publisher_handoff_path"):
        raise ACSUserError("Review report publisher handoff path is stale; rerun `acs review-report`.")
    publisher_handoff_path = inside_project(
        contracts.directory,
        manifest["publisher_handoff_path"],
        label="publisher handoff path",
    )
    if review.get("publisher_handoff_sha256") != sha256_file(publisher_handoff_path):
        raise ACSUserError("Review report publisher handoff binding is stale; rerun `acs review-report`.")
    if review.get("verification_status") != "passed" or review.get("verification_sha256") != sha256_file(verification_path):
        raise ACSUserError("Review report is not bound to current passed verification; rerun `acs review-report`.")
    render_record_path = contracts.directory / "renders" / "render-record.json"
    render_record = read_json(render_record_path) if render_record_path.exists() else {}
    expected_render_proof = render_review_proof(contracts, render_record)
    if review.get("render_proof", []) != expected_render_proof:
        raise ACSUserError("Review report render/caption proof is stale; rerun `acs review-report`.")
    expected_qa_proof = qa_review_proof(contracts)
    if review.get("qa_proof", []) != expected_qa_proof:
        raise ACSUserError("Review report visual-QA proof is stale; rerun `acs review-report`.")
    return review


def export_result(contracts: ProjectContracts) -> Path:
    # A failed attempt must not leave an older verified result discoverable as
    # the current caller result. Preserve it for recovery, outside results/.
    archive_active_result(contracts)
    require_current_approval(contracts)
    require_current_inspection(contracts)
    manifest_path = contracts.directory / "publish" / "manifest.json"
    verification_path = contracts.directory / "publish" / "verification.json"
    report_path = contracts.directory / "reports" / "review.html"
    review_record_path = contracts.directory / "reports" / "review.json"
    if not manifest_path.exists() or not verification_path.exists():
        raise ACSUserError("Result export requires package, verify, and review-report outputs.")

    # Verification is a point-in-time claim about generated bytes. Re-run the
    # complete package verifier immediately before exporting so a replaced or
    # mutated asset cannot inherit an old `verification.json` and produce a
    # false verified result.
    verify_package(contracts)
    manifest = read_json(manifest_path)
    verification = read_json(verification_path)
    if manifest.get("verification", {}).get("status") != "passed" or verification.get("status") != "passed":
        raise ACSUserError("Result export requires passed package verification.")
    _require_current_review(
        contracts,
        manifest_path=manifest_path,
        verification_path=verification_path,
        report_path=report_path,
        review_record_path=review_record_path,
        manifest=manifest,
    )
    _write_result_index(contracts, manifest)

    proof_candidates = [
        ("inspection", "inspection.json"),
        ("raw-transcript", "transcripts/raw.json"),
        ("reviewed-transcript", "transcripts/reviewed.json"),
        ("approved-plan", "edit-plan.json"),
        ("render-record", "renders/render-record.json"),
        ("publish-manifest", "publish/manifest.json"),
        ("publisher-handoff", PUBLISHER_HANDOFF_RELATIVE),
        ("publish-verification", "publish/verification.json"),
        ("review-report", "reports/review.html"),
        ("review-record", "reports/review.json"),
        ("result-index", "results/index.md"),
    ]
    creative_note = contracts.directory / "creative-direction.md"
    if creative_note.exists():
        proof_candidates.insert(3, ("creative-direction", "creative-direction.md"))
    derivative_record = contracts.directory / "derived" / "derivative-record.json"
    if derivative_record.exists():
        proof_candidates.insert(3, ("derivative-record", "derived/derivative-record.json"))
    render_record_path = contracts.directory / "renders" / "render-record.json"
    if render_record_path.exists():
        render_record = read_json(render_record_path)
        for kind, render in render_record.get("renders", {}).items():
            captions = render.get("captions") or {}
            sidecar_path = captions.get("sidecar_path")
            if captions.get("sidecar") and sidecar_path:
                proof_candidates.append((f"{kind}-caption-sidecar", str(sidecar_path)))
    for item in qa_review_proof(contracts):
        proof_candidates.append(("visual-qa", item["path"]))
    adapter_state = load_current_adapter_import(contracts)
    if adapter_state is not None:
        adapter_record, _ = adapter_state
        proof_candidates.extend(
            [
                ("adapter-import", ADAPTER_IMPORT_RELATIVE),
                ("adapter-output", adapter_record["output"]["path"]),
                ("adapter-manifest", adapter_record["manifest"]["path"]),
            ]
        )
    proof: list[dict[str, str]] = []
    for kind, relative in proof_candidates:
        path = inside_project(contracts.directory, relative, label="proof path")
        if not path.exists():
            raise ACSUserError(f"Missing required proof artifact: {relative}")
        proof.append(
            {
                "kind": kind,
                "path": relative,
                "sha256": sha256_file(path),
            }
        )

    publisher_handoff_path = inside_project(
        contracts.directory,
        PUBLISHER_HANDOFF_RELATIVE,
        label="publisher handoff path",
    )
    publisher_handoff = read_json(publisher_handoff_path)
    learning_path = contracts.directory / "learning.json"
    learning: dict[str, Any] = {"what_worked": "", "what_to_change": "", "next_experiment": ""}
    if learning_path.exists():
        raw_learning = read_json(learning_path)
        for key in learning:
            learning[key] = str(raw_learning.get(key, ""))

    result = {
        "schema_version": "1.0",
        "result_id": f"{contracts.project['project_id']}-{canonical_hash(proof)[:12]}",
        "project_id": contracts.project["project_id"],
        "status": "verified",
        "proof": proof,
        "enabled_routes": [route["channel"] for route in manifest.get("routes", [])],
        "disabled_routes": manifest.get("disabled_channels", []),
        "review": {"status": "available", "report_path": "reports/review.html"},
        "publisher_handoff": {
            "path": PUBLISHER_HANDOFF_RELATIVE,
            "sha256": sha256_file(publisher_handoff_path),
            "status": publisher_handoff["status"],
            "external_posting": publisher_handoff["external_posting"],
        },
        "verification": {"status": "passed", "external_posting": False},
        "learning": learning,
    }
    require_valid(result, load_schema("run-result"), "run result")
    result_path = contracts.directory / "results" / "run-result.json"
    write_json(result_path, result)
    return result_path
