"""Bounded, reviewer-owned semantic evaluation of an exported ACS result."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .errors import ACSUserError
from .io import canonical_hash, read_json, sha256_file, write_json
from .paths import display_path, inside_project
from .project import ProjectContracts, require_current_approval
from .schemas import load_schema
from .validation import require_valid


CHECKPOINT = "candidate result is judged against the approved ACS content decision before deliberate attempt acceptance"
CHECKS = (
    ("promise_delivery", "approved promise"),
    ("proof_delivery", "approved proof"),
    ("audience_relevance", "approved audience"),
)


def _require_exact_checks(evaluation: dict[str, Any]) -> None:
    checks = evaluation.get("observable_checks")
    expected_ids = [item[0] for item in CHECKS]
    if not isinstance(checks, list) or [item.get("id") if isinstance(item, dict) else None for item in checks] != expected_ids:
        raise ACSUserError("Semantic evaluation must retain exactly one promise, proof, and audience observation in ACS order.")
    expected_outcome = "passed" if all(item.get("passed") is True for item in checks) else "failed"
    if evaluation.get("outcome") != expected_outcome:
        raise ACSUserError("Semantic evaluation outcome contradicts its observations.")


def _require_current_decision(contracts: ProjectContracts, evaluation: dict[str, Any]) -> None:
    decision = evaluation.get("decision")
    approval = contracts.edit_plan.get("approval", {})
    expected = {
        "promise": contracts.project.get("promise"),
        "audience": contracts.project.get("audience"),
        "required_proof": contracts.edit_plan.get("proof"),
        "approval_hash": approval.get("approval_hash"),
        "approval_revision": approval.get("approval_revision"),
    }
    if decision != expected:
        raise ACSUserError("Semantic evaluation is bound to an older ACS content decision; export and evaluate the current candidate result.")


def _bound_file(project_dir: Path, relative: str) -> dict[str, str]:
    path = inside_project(project_dir, relative, label="semantic evaluation evidence")
    if not path.is_file():
        raise ACSUserError(f"Semantic evaluation requires readable local evidence: {relative}")
    return {"path": relative, "sha256": sha256_file(path)}


def _snapshot_file(project_dir: Path, relative: str, *, label: str) -> dict[str, str]:
    source = inside_project(project_dir, relative, label=label)
    if not source.is_file() or source.is_symlink():
        raise ACSUserError(f"Semantic evaluation requires a regular local file: {relative}")
    digest = sha256_file(source)
    destination = project_dir / "evaluations" / f"{label}-{digest[:16]}-{source.name}"
    if destination.exists():
        if not destination.is_file() or destination.is_symlink() or sha256_file(destination) != digest:
            raise ACSUserError(f"Semantic evaluation snapshot is unsafe or contradictory: {destination.name}")
    else:
        destination.parent.mkdir(parents=True, exist_ok=True)
        with source.open("rb") as input_handle, destination.open("xb") as output_handle:
            output_handle.write(input_handle.read())
    return {"path": display_path(project_dir, destination), "sha256": digest}


def _result_evidence(contracts: ProjectContracts, result: dict[str, Any]) -> list[dict[str, str]]:
    evidence = [
        _snapshot_file(contracts.directory, "project.json", label="evidence"),
        _snapshot_file(contracts.directory, "edit-plan.json", label="evidence"),
        _snapshot_file(contracts.directory, "reports/review.json", label="evidence"),
        _snapshot_file(contracts.directory, "results/run-result.json", label="candidate-result"),
    ]
    for item in result.get("proof", []):
        relative = item.get("path")
        if not isinstance(relative, str):
            raise ACSUserError("Run result has an invalid proof path; export it again before semantic evaluation.")
        bound = _bound_file(contracts.directory, relative)
        if bound["sha256"] != item.get("sha256"):
            raise ACSUserError(f"Run result proof is stale or changed: {relative}; export it again before semantic evaluation.")
        snapshot = _snapshot_file(contracts.directory, relative, label="evidence")
        if snapshot not in evidence:
            evidence.append(snapshot)
    return evidence


def evaluate_content_result(
    contracts: ProjectContracts,
    assessment_path: str | Path,
    *,
    reviewer: str,
) -> tuple[Path, dict[str, Any]]:
    """Write immutable local evaluation evidence without changing the candidate result."""

    if not reviewer.strip():
        raise ACSUserError("Semantic evaluation requires --by <reviewer>.")
    require_current_approval(contracts)
    result_path = contracts.directory / "results" / "run-result.json"
    if not result_path.is_file():
        raise ACSUserError("Semantic evaluation requires an exported result; run `acs export-result` first.")
    result = read_json(result_path)
    require_valid(result, load_schema("run-result"), "run result")

    source = Path(assessment_path).expanduser().resolve()
    if not source.is_file():
        raise ACSUserError(f"Semantic assessment file not found: {source}")
    assessment = read_json(source)
    require_valid(assessment, load_schema("semantic-assessment"), "semantic assessment")

    checks: list[dict[str, Any]] = []
    for check_id, label in CHECKS:
        item = assessment[check_id]
        if check_id == "promise_delivery":
            subject = contracts.project["promise"]
        elif check_id == "proof_delivery":
            subject = "; ".join(contracts.edit_plan["proof"])
        else:
            subject = contracts.project["audience"]
        checks.append({"id": check_id, "subject": subject, "passed": item["passed"], "observation": item["observation"]})
    outcome = "passed" if all(item["passed"] for item in checks) else "failed"
    approval = contracts.edit_plan["approval"]
    result_evidence = _result_evidence(contracts, result)
    identity = canonical_hash(
        {
            "result_sha256": sha256_file(result_path),
            "assessment": assessment,
            "reviewer": reviewer.strip(),
            "approval_hash": approval["approval_hash"],
        }
    )[:16]
    evaluation = {
        "schema_version": "1.0",
        "evaluation_id": f"{contracts.project['project_id']}-semantic-{identity}",
        "project_id": contracts.project["project_id"],
        "subject": contracts.project["title"],
        "checkpoint": CHECKPOINT,
        "result": _snapshot_file(contracts.directory, "results/run-result.json", label="candidate-result"),
        "decision": {
            "promise": contracts.project["promise"],
            "audience": contracts.project["audience"],
            "required_proof": contracts.edit_plan["proof"],
            "approval_hash": approval["approval_hash"],
            "approval_revision": approval["approval_revision"],
        },
        "observable_checks": checks,
        "required_evidence": result_evidence,
        "outcome": outcome,
        "failure_action": assessment["failure_action"],
        "evaluated_by": reviewer.strip(),
        "evaluated_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
    }
    require_valid(evaluation, load_schema("semantic-evaluation"), "semantic evaluation")
    evaluation_path = contracts.directory / "evaluations" / f"semantic-evaluation-{identity}.json"
    if evaluation_path.exists():
        raise ACSUserError(f"Semantic evaluation already exists and is immutable: {display_path(contracts.directory, evaluation_path)}")
    write_json(evaluation_path, evaluation)
    return evaluation_path, evaluation


def current_semantic_evaluation(contracts: ProjectContracts) -> tuple[Path, dict[str, Any]]:
    """Return exactly one evaluation bound to the current exported result."""

    result_path = contracts.directory / "results" / "run-result.json"
    if not result_path.is_file():
        raise ACSUserError("Semantic evaluation requires an exported result.")
    result_sha256 = sha256_file(result_path)
    candidates: list[tuple[Path, dict[str, Any]]] = []
    directory = contracts.directory / "evaluations"
    if directory.exists() and not directory.is_dir():
        raise ACSUserError("Semantic evaluations path must be a directory.")
    for path in sorted(directory.glob("semantic-evaluation-*.json")) if directory.exists() else []:
        if not path.is_file() or path.is_symlink():
            raise ACSUserError("Semantic evaluation evidence must be a regular local file.")
        evaluation = read_json(path)
        require_valid(evaluation, load_schema("semantic-evaluation"), "semantic evaluation")
        _require_exact_checks(evaluation)
        if evaluation.get("project_id") == contracts.project["project_id"] and evaluation.get("result", {}).get("sha256") == result_sha256:
            candidates.append((path, evaluation))
    if not candidates:
        raise ACSUserError("No semantic evaluation is bound to the current result; run `acs semantic-eval <workspace> <assessment> --by <reviewer>`.")
    if len(candidates) != 1:
        raise ACSUserError("More than one semantic evaluation is bound to the current result; export a fresh result before reevaluating.")
    path, evaluation = candidates[0]
    if not evaluation["result"]["path"].startswith("evaluations/candidate-result-"):
        raise ACSUserError("Semantic evaluation result snapshot must stay in the workspace evaluations boundary.")
    _require_current_decision(contracts, evaluation)
    for item in evaluation["required_evidence"]:
        current = _bound_file(contracts.directory, item["path"])
        if current["sha256"] != item["sha256"]:
            raise ACSUserError(f"Semantic evaluation evidence is stale or changed: {item['path']}")
    return path, evaluation
