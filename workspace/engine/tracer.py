#!/usr/bin/env python3
"""Record deliberate ACS production-route proof without adding a runtime service."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

ROOT = Path(__file__).resolve().parents[2]
HISTORY_RELATIVE = Path("workspace/history/runs.jsonl")
RUNS_RELATIVE = Path("workspace/runs")
PRODUCTIONS_RELATIVE = Path("workspace/productions")
RUN_ID_PATTERN = re.compile(r"^run-[A-Za-z0-9][A-Za-z0-9._-]*$")
SLUG_PATTERN = re.compile(r"^[a-z0-9][a-z0-9-]*$")
FACT_PATTERN = re.compile(r"^[A-Za-z0-9_.:-]{1,80}$")
FORBIDDEN_FIELDS = {"prompt", "request", "raw_request", "raw_prompt", "context", "transcript", "credentials"}
STATUSES = {"succeeded", "failed"}
SEMANTIC_FAILURE_CODE = "semantic_eval_failed"
SEMANTIC_CHECK_IDS = ("promise_delivery", "proof_delivery", "audience_relevance")
LEGACY_RECORD_FIELDS = frozenset(
    {
        "run_id", "started_at", "finished_at", "status", "input_ref",
        "output_ref", "proof_ref", "previous_run_id",
        "previous_run_relation", "failure", "recovery",
    }
)
EVALUATED_RECORD_FIELDS = LEGACY_RECORD_FIELDS | {"evaluation"}


class TraceError(ValueError):
    """A caller supplied an invalid or unsafe tracing request."""


def _root(root: str | Path | None) -> Path:
    return Path(root or ROOT).expanduser().resolve()


def _safe_relative(value: str | Path, *, label: str) -> Path:
    raw = Path(value)
    if raw.is_absolute():
        raise TraceError(f"{label} must be relative to the repository root")
    normalized = Path(str(raw).replace("\\", "/"))
    if not normalized.parts or normalized == Path(".") or any(part in {"", ".."} for part in normalized.parts):
        raise TraceError(f"{label} must be a normalized relative path")
    return normalized


def _relative_to_root(root: Path, value: str | Path, *, label: str) -> Path:
    candidate = Path(value).expanduser()
    if candidate.is_absolute():
        resolved = candidate.resolve()
        try:
            return resolved.relative_to(root)
        except ValueError as exc:
            raise TraceError(f"{label} must stay inside the repository root") from exc
    return _safe_relative(candidate, label=label)


def _iso_timestamp(value: str | None) -> str:
    if value is None:
        return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise TraceError(f"timestamp is not ISO-8601: {value!r}") from exc
    if parsed.tzinfo is None:
        raise TraceError("timestamp must include a timezone")
    return value


def _timestamp_key(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def _validate_fact(value: str, *, label: str) -> str:
    if not isinstance(value, str) or not FACT_PATTERN.fullmatch(value):
        raise TraceError(f"{label} must be a short machine-readable fact")
    return value


def _failure_fact(failure: dict[str, Any] | None) -> dict[str, Any] | None:
    if failure is None:
        return None
    if not isinstance(failure, dict):
        raise TraceError("failure must be a small object of machine-readable facts")
    unexpected = set(failure) - {"code", "step", "retriable"}
    if unexpected:
        raise TraceError(f"failure contains unsupported fields: {sorted(unexpected)}")
    if "code" not in failure:
        raise TraceError("failure.code is required for a failed route")
    result: dict[str, Any] = {"code": _validate_fact(failure["code"], label="failure.code")}
    if "step" in failure:
        result["step"] = _validate_fact(failure["step"], label="failure.step")
    if "retriable" in failure:
        if not isinstance(failure["retriable"], bool):
            raise TraceError("failure.retriable must be boolean")
        result["retriable"] = failure["retriable"]
    return result


def _load_records(history_path: Path) -> list[dict[str, Any]]:
    if not history_path.exists():
        return []
    if not history_path.is_file():
        raise TraceError(f"history path is not a regular file: {history_path}")
    records: list[dict[str, Any]] = []
    for line_number, line in enumerate(history_path.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            continue
        try:
            value = json.loads(line)
        except json.JSONDecodeError as exc:
            raise TraceError(f"invalid JSON in history line {line_number}") from exc
        if not isinstance(value, dict):
            raise TraceError(f"history line {line_number} is not an object")
        records.append(value)
    return records


def _json_has_forbidden_field(value: Any) -> str | None:
    if isinstance(value, dict):
        for key, child in value.items():
            if key.lower() in FORBIDDEN_FIELDS:
                return key
            found = _json_has_forbidden_field(child)
            if found:
                return found
    elif isinstance(value, list):
        for child in value:
            found = _json_has_forbidden_field(child)
            if found:
                return found
    return None


def _owned_production_file(production_dir: Path, relative: str, *, label: str) -> Path:
    path = _safe_relative(relative, label=label)
    candidate = production_dir / path
    try:
        candidate.resolve().relative_to(production_dir.resolve())
    except ValueError as exc:
        raise TraceError(f"{label} escapes production") from exc
    if not candidate.is_file() or candidate.is_symlink():
        raise TraceError(f"{label} must be a regular local file")
    return candidate


def _validate_semantic_evaluation(
    evaluation: dict[str, Any],
    production_dir: Path,
    *,
    expected_result_sha256: str | None = None,
    expected_outcome: str | None = None,
) -> None:
    result = evaluation.get("result")
    if not isinstance(result, dict) or set(result) != {"path", "sha256"}:
        raise TraceError("semantic evaluation has invalid result snapshot facts")
    result_ref = result.get("path")
    result_sha256 = result.get("sha256")
    if not isinstance(result_ref, str) or not result_ref.startswith("evaluations/candidate-result-"):
        raise TraceError("semantic evaluation result reference is invalid")
    if not isinstance(result_sha256, str) or not re.fullmatch(r"[a-f0-9]{64}", result_sha256):
        raise TraceError("semantic evaluation result hash is invalid")
    if expected_result_sha256 is not None and result_sha256 != expected_result_sha256:
        raise TraceError("semantic evaluation is not bound to the current result")
    snapshot = _owned_production_file(production_dir, result_ref, label="semantic result snapshot")
    if sha256_file(snapshot) != result_sha256:
        raise TraceError("semantic evaluation result snapshot is stale or unreadable")

    checks = evaluation.get("observable_checks")
    if not isinstance(checks, list) or [item.get("id") if isinstance(item, dict) else None for item in checks] != list(SEMANTIC_CHECK_IDS):
        raise TraceError("semantic evaluation must retain exactly one promise, proof, and audience check")
    if any(
        not isinstance(item.get("passed"), bool)
        or not isinstance(item.get("observation"), str)
        or not item["observation"].strip()
        for item in checks
    ):
        raise TraceError("semantic evaluation checks must have observed boolean outcomes")
    derived_outcome = "passed" if all(item["passed"] for item in checks) else "failed"
    if evaluation.get("outcome") != derived_outcome:
        raise TraceError("semantic evaluation outcome contradicts its checks")
    if expected_outcome is not None and derived_outcome != expected_outcome:
        raise TraceError(f"current semantic evaluation must be {expected_outcome}")

    evidence_items = evaluation.get("required_evidence")
    if not isinstance(evidence_items, list) or not evidence_items:
        raise TraceError("semantic evaluation requires retained local evidence")
    for item in evidence_items:
        if not isinstance(item, dict) or set(item) != {"path", "sha256"}:
            raise TraceError("semantic evaluation has invalid required evidence")
        evidence_ref = item.get("path")
        evidence_sha256 = item.get("sha256")
        if not isinstance(evidence_ref, str) or not isinstance(evidence_sha256, str):
            raise TraceError("semantic evaluation has invalid required evidence")
        evidence = _owned_production_file(production_dir, evidence_ref, label="semantic evidence path")
        if sha256_file(evidence) != evidence_sha256:
            raise TraceError("semantic evaluation evidence is stale or unreadable")


def _require_current_semantic_decision(evaluation: dict[str, Any], project: dict[str, Any], edit_plan: dict[str, Any]) -> None:
    approval = edit_plan.get("approval")
    if not isinstance(approval, dict):
        raise TraceError("production edit-plan.json must contain approval facts")
    expected = {
        "promise": project.get("promise"),
        "audience": project.get("audience"),
        "required_proof": edit_plan.get("proof"),
        "approval_hash": approval.get("approval_hash"),
        "approval_revision": approval.get("approval_revision"),
    }
    if evaluation.get("decision") != expected:
        raise TraceError("semantic evaluation is bound to an older ACS content decision")


def _validate_record_shape(records: Iterable[dict[str, Any]], root: Path) -> list[str]:
    failures: list[str] = []
    seen: set[str] = set()
    recovery_sources: set[str] = set()
    prior_ids: set[str] = set()

    for index, record in enumerate(records, start=1):
        prefix = f"history record {index}"
        fields = set(record)
        legacy = fields == LEGACY_RECORD_FIELDS
        if fields not in {LEGACY_RECORD_FIELDS, EVALUATED_RECORD_FIELDS}:
            missing = LEGACY_RECORD_FIELDS - fields
            unsupported = fields - EVALUATED_RECORD_FIELDS
            if missing:
                failures.append(f"{prefix} missing fields: {sorted(missing)}")
            elif unsupported:
                failures.append(f"{prefix} has unsupported fields: {sorted(unsupported)}")
            else:
                failures.append(f"{prefix} must include evaluation or use the exact legacy record shape")
            continue
        run_id = record["run_id"]
        if not isinstance(run_id, str) or not RUN_ID_PATTERN.fullmatch(run_id):
            failures.append(f"{prefix} has invalid run_id")
        elif run_id in seen:
            failures.append(f"{prefix} duplicates run_id {run_id}")
        else:
            seen.add(run_id)

        status = record["status"]
        if status not in STATUSES:
            failures.append(f"{prefix} has invalid status")
        for field in ("started_at", "finished_at"):
            if not isinstance(record[field], str):
                failures.append(f"{prefix}.{field} must be a timestamp")
            else:
                try:
                    _timestamp_key(record[field])
                except ValueError:
                    failures.append(f"{prefix}.{field} is not ISO-8601")
        if isinstance(record.get("started_at"), str) and isinstance(record.get("finished_at"), str):
            try:
                if _timestamp_key(record["finished_at"]) < _timestamp_key(record["started_at"]):
                    failures.append(f"{prefix} finishes before it starts")
            except ValueError:
                pass

        for field in ("input_ref", "output_ref", "proof_ref"):
            try:
                relative = _safe_relative(record[field], label=f"{prefix}.{field}")
                (root / relative).resolve().relative_to(root)
            except (TraceError, ValueError):
                failures.append(f"{prefix}.{field} escapes the repository")

        previous_id = record["previous_run_id"]
        relation = record["previous_run_relation"]
        if previous_id is None:
            if relation is not None:
                failures.append(f"{prefix} has a relation without previous_run_id")
        elif not isinstance(previous_id, str) or previous_id not in prior_ids:
            failures.append(f"{prefix} points to a missing or future previous run")
        elif relation not in {"predecessor", "recovery"}:
            failures.append(f"{prefix} has an invalid previous_run_relation")

        if status == "succeeded" and record["failure"] is not None:
            failures.append(f"{prefix} succeeded with failure facts")
        if status == "failed":
            try:
                _failure_fact(record["failure"])
            except TraceError as exc:
                failures.append(f"{prefix}: {exc}")
        evaluation = None if legacy else record["evaluation"]
        failure_code = record.get("failure", {}).get("code") if isinstance(record.get("failure"), dict) else None
        if not legacy and status == "succeeded" and evaluation is None:
            failures.append(f"{prefix} succeeded without passed semantic evaluation")
        if not legacy and failure_code == SEMANTIC_FAILURE_CODE and evaluation is None:
            failures.append(f"{prefix} semantic failure lacks semantic evaluation")
        if evaluation is not None:
            if not isinstance(evaluation, dict) or set(evaluation) != {"path", "sha256", "outcome"}:
                failures.append(f"{prefix} has invalid semantic evaluation facts")
            else:
                try:
                    evaluation_path = _safe_relative(evaluation["path"], label=f"{prefix}.evaluation.path")
                    production_root = _safe_relative(record["input_ref"], label=f"{prefix}.input_ref").parent
                    evaluation_path.relative_to(production_root / "evaluations")
                    absolute_evaluation = (root / evaluation_path).resolve()
                    absolute_evaluation.relative_to((root / production_root).resolve())
                    if not absolute_evaluation.is_file() or sha256_file(absolute_evaluation) != evaluation["sha256"]:
                        raise TraceError("evaluation evidence is stale or missing")
                    value = json.loads(absolute_evaluation.read_text(encoding="utf-8"))
                    if not isinstance(value, dict) or value.get("outcome") != evaluation["outcome"]:
                        raise TraceError("evaluation evidence contradicts ledger facts")
                    _validate_semantic_evaluation(value, (root / production_root).resolve())
                except (OSError, ValueError, json.JSONDecodeError, TraceError, KeyError):
                    failures.append(f"{prefix} has escaping, unreadable, or inconsistent semantic evaluation evidence")
            if isinstance(evaluation, dict):
                if status == "succeeded" and evaluation.get("outcome") != "passed":
                    failures.append(f"{prefix} succeeded without a passed semantic evaluation")
                if failure_code == SEMANTIC_FAILURE_CODE and evaluation.get("outcome") != "failed":
                    failures.append(f"{prefix} semantic failure lacks failed semantic evaluation")
        recovery = record["recovery"]
        if relation == "recovery":
            if not isinstance(recovery, dict) or recovery.get("recovered_run_id") != previous_id:
                failures.append(f"{prefix} recovery must identify its failed previous run")
            elif previous_id in recovery_sources:
                failures.append(f"{prefix} consumes failed run {previous_id} more than once")
            else:
                recovery_sources.add(previous_id)
        elif recovery is not None:
            failures.append(f"{prefix} has recovery facts without a recovery relation")
        forbidden = _json_has_forbidden_field(record)
        if forbidden:
            failures.append(f"{prefix} contains forbidden raw field {forbidden!r}")
        evidence = root / RUNS_RELATIVE / str(run_id) / "run.json"
        if not evidence.is_file():
            failures.append(f"{prefix} is missing evidence file {evidence.relative_to(root)}")
        else:
            try:
                if json.loads(evidence.read_text(encoding="utf-8")) != record:
                    failures.append(f"{prefix} evidence does not match the append-only ledger record")
            except (OSError, json.JSONDecodeError):
                failures.append(f"{prefix} evidence is unreadable")
        prior_ids.add(run_id)

    return failures


def validate_ledger(root: str | Path | None = None) -> list[str]:
    """Return structural ledger failures without changing any file."""

    repo_root = _root(root)
    try:
        records = _load_records(repo_root / HISTORY_RELATIVE)
    except TraceError as exc:
        return [str(exc)]
    return _validate_record_shape(records, repo_root)


def load_ledger(root: str | Path | None = None) -> list[dict[str, Any]]:
    """Load and validate the append-only local run relation."""

    repo_root = _root(root)
    records = _load_records(repo_root / HISTORY_RELATIVE)
    failures = _validate_record_shape(records, repo_root)
    if failures:
        raise TraceError("; ".join(failures))
    return records


def _next_run_id(records: list[dict[str, Any]]) -> str:
    numbers = [
        int(match.group(1))
        for record in records
        if isinstance(record.get("run_id"), str)
        for match in [re.fullmatch(r"run-(\d+)", record["run_id"])]
        if match
    ]
    return f"run-{max(numbers, default=0) + 1:04d}"


def _write_evidence(path: Path, record: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=False)
    with path.open("x", encoding="utf-8") as handle:
        json.dump(record, handle, indent=2, sort_keys=True)
        handle.write("\n")


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _semantic_evaluation(production_dir: Path, project_id: str, *, outcome: str) -> tuple[Path, dict[str, Any]]:
    result_path = production_dir / "results" / "run-result.json"
    if not result_path.is_file():
        raise TraceError("semantic evaluation requires results/run-result.json")
    result_sha256 = sha256_file(result_path)
    directory = production_dir / "evaluations"
    candidates: list[tuple[Path, dict[str, Any]]] = []
    if directory.exists() and not directory.is_dir():
        raise TraceError("evaluations path must be a directory")
    for path in sorted(directory.glob("semantic-evaluation-*.json")) if directory.exists() else []:
        if not path.is_file() or path.is_symlink():
            raise TraceError("semantic evaluation evidence must be a regular file")
        try:
            value = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            raise TraceError(f"cannot read semantic evaluation evidence: {exc}") from exc
        if not isinstance(value, dict):
            raise TraceError("semantic evaluation evidence must be an object")
        if value.get("project_id") == project_id and value.get("result", {}).get("sha256") == result_sha256:
            candidates.append((path, value))
    if len(candidates) != 1:
        raise TraceError("exactly one semantic evaluation must bind the current result")
    path, evaluation = candidates[0]
    _validate_semantic_evaluation(
        evaluation,
        production_dir,
        expected_result_sha256=result_sha256,
        expected_outcome=outcome,
    )
    return path, evaluation


def _append_record(history_path: Path, record: dict[str, Any]) -> None:
    history_path.parent.mkdir(parents=True, exist_ok=True)
    with history_path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(record, sort_keys=True, separators=(",", ":")) + "\n")
        handle.flush()
        os.fsync(handle.fileno())


def record_run(
    production: str | Path,
    status: str,
    *,
    root: str | Path | None = None,
    run_id: str | None = None,
    started_at: str | None = None,
    finished_at: str | None = None,
    failure: dict[str, Any] | None = None,
    recover_run_id: str | None = None,
) -> dict[str, Any]:
    """Append one deliberate full-route attempt and create its evidence file."""

    repo_root = _root(root)
    if status not in STATUSES:
        raise TraceError("status must be 'succeeded' or 'failed'")
    production_relative = _relative_to_root(repo_root, production, label="production")
    try:
        production_relative.relative_to(PRODUCTIONS_RELATIVE)
    except ValueError as exc:
        raise TraceError("production must be under workspace/productions/") from exc
    production_dir = repo_root / production_relative
    if not production_dir.is_dir():
        raise TraceError(f"production directory does not exist: {production_dir}")
    project_path = production_dir / "project.json"
    if not project_path.is_file():
        raise TraceError(f"production is missing project.json: {project_path}")
    try:
        project = json.loads(project_path.read_text(encoding="utf-8"))
        if not isinstance(project, dict):
            raise TypeError("project must be an object")
        project_id = project["project_id"]
        edit_plan = json.loads((production_dir / "edit-plan.json").read_text(encoding="utf-8"))
        if not isinstance(edit_plan, dict):
            raise TypeError("edit plan must be an object")
    except (OSError, json.JSONDecodeError, KeyError, TypeError) as exc:
        raise TraceError("production project.json and edit-plan.json must name the current content decision") from exc

    records = load_ledger(repo_root)
    existing_ids = {record["run_id"] for record in records}
    chosen_id = run_id or _next_run_id(records)
    if not RUN_ID_PATTERN.fullmatch(chosen_id):
        raise TraceError("run_id must match run-<safe-id>")
    if chosen_id in existing_ids:
        raise TraceError(f"run_id already exists: {chosen_id}")

    started = _iso_timestamp(started_at)
    finished = _iso_timestamp(finished_at) if finished_at is not None else started
    if _timestamp_key(finished) < _timestamp_key(started):
        raise TraceError("finished_at cannot precede started_at")
    failure_fact = _failure_fact(failure)
    if status == "failed" and failure_fact is None:
        raise TraceError("failed routes require bounded failure facts")
    if status == "succeeded" and failure_fact is not None:
        raise TraceError("succeeded routes cannot include failure facts")

    evaluation_path: Path | None = None
    evaluation: dict[str, Any] | None = None
    if status == "succeeded":
        evaluation_path, evaluation = _semantic_evaluation(production_dir, project_id, outcome="passed")
    elif failure_fact and failure_fact["code"] == SEMANTIC_FAILURE_CODE:
        evaluation_path, evaluation = _semantic_evaluation(production_dir, project_id, outcome="failed")
    if evaluation is not None:
        _require_current_semantic_decision(evaluation, project, edit_plan)

    previous_id: str | None = None
    relation: str | None = None
    recovery: dict[str, Any] | None = None
    if recover_run_id is not None:
        if recover_run_id not in existing_ids:
            raise TraceError(f"recovery source does not exist: {recover_run_id}")
        source = next(record for record in records if record["run_id"] == recover_run_id)
        if source.get("status") != "failed":
            raise TraceError("only a failed run can be explicitly recovered")
        if any(
            record.get("previous_run_relation") == "recovery"
            and record.get("previous_run_id") == recover_run_id
            for record in records
        ):
            raise TraceError(f"failed run already consumed by recovery: {recover_run_id}")
        previous_id = recover_run_id
        relation = "recovery"
        recovery = {"mode": "explicit", "recovered_run_id": recover_run_id}
    elif records:
        previous_id = records[-1]["run_id"]
        relation = "predecessor"

    production_text = production_relative.as_posix()
    record: dict[str, Any] = {
        "run_id": chosen_id,
        "started_at": started,
        "finished_at": finished,
        "status": status,
        "input_ref": f"{production_text}/project.json",
        "output_ref": f"{production_text}/results/run-result.json",
        "proof_ref": f"{production_text}/reports/review.json",
        "previous_run_id": previous_id,
        "previous_run_relation": relation,
        "failure": failure_fact,
        "recovery": recovery,
        "evaluation": (
            {
                "path": f"{production_text}/{evaluation_path.relative_to(production_dir).as_posix()}",
                "sha256": sha256_file(evaluation_path),
                "outcome": evaluation["outcome"],
            }
            if evaluation_path is not None and evaluation is not None
            else None
        ),
    }
    forbidden = _json_has_forbidden_field(record)
    if forbidden:
        raise TraceError(f"record contains forbidden raw field {forbidden!r}")

    if status == "succeeded":
        for field in ("output_ref", "proof_ref"):
            if not (repo_root / record[field]).is_file():
                raise TraceError(f"succeeded route is missing production proof: {record[field]}")

    evidence_path = repo_root / RUNS_RELATIVE / chosen_id / "run.json"
    _write_evidence(evidence_path, record)
    try:
        _append_record(repo_root / HISTORY_RELATIVE, record)
    except Exception:
        evidence_path.unlink(missing_ok=True)
        evidence_path.parent.rmdir()
        raise
    return record


def _find_record(root: Path, run_id: str) -> dict[str, Any]:
    records = load_ledger(root)
    for record in records:
        if record["run_id"] == run_id:
            return record
    raise TraceError(f"run_id does not exist: {run_id}")


def promote_example(
    run_id: str,
    slug: str,
    *,
    root: str | Path | None = None,
) -> Path:
    """Deliberately promote a successful run to a small reviewable example."""

    repo_root = _root(root)
    record = _find_record(repo_root, run_id)
    if record["status"] != "succeeded":
        raise TraceError("only a succeeded run can be promoted")
    if not isinstance(record.get("evaluation"), dict) or record["evaluation"].get("outcome") != "passed":
        raise TraceError("only a semantically passed run can be promoted")
    if not SLUG_PATTERN.fullmatch(slug):
        raise TraceError("example slug must be lowercase kebab-case")
    destination = repo_root / "examples" / slug
    if destination.exists():
        raise TraceError(f"example already exists: {destination}")
    destination.mkdir(parents=True)
    proof = {
        "schema_version": "1.0",
        "curated": True,
        "run_id": record["run_id"],
        "status": record["status"],
        "production_ref": record["input_ref"].removesuffix("/project.json"),
        "input_ref": record["input_ref"],
        "output_ref": record["output_ref"],
        "proof_ref": record["proof_ref"],
        "semantic_evaluation": record["evaluation"],
    }
    with (destination / "proof.json").open("x", encoding="utf-8") as handle:
        json.dump(proof, handle, indent=2, sort_keys=True)
        handle.write("\n")
    with (destination / "README.md").open("x", encoding="utf-8") as handle:
        handle.write(
            f"# Curated ACS example: {slug}\n\n"
            "This is a deliberately promoted, reviewable proof pointer. "
            "Operational production state remains under workspace/productions/.\n\n"
            f"- run: {record['run_id']}\n"
            f"- production: {proof['production_ref']}\n"
            f"- result: {record['output_ref']}\n"
            f"- review proof: {record['proof_ref']}\n"
        )
    return destination


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Record local ACS production-route proof.")
    parser.add_argument("--root", default=str(ROOT), help="Repository root for local history and evidence.")
    sub = parser.add_subparsers(dest="command", required=True)

    record = sub.add_parser("record", help="Append one deliberate full production-route attempt.")
    record.add_argument("production", help="Production under workspace/productions/.")
    record.add_argument("--status", choices=sorted(STATUSES), required=True)
    record.add_argument("--run-id")
    record.add_argument("--started-at")
    record.add_argument("--finished-at")
    record.add_argument("--recover", dest="recover_run_id", help="Explicitly consume one unresolved failed run.")
    record.add_argument("--failure-code")
    record.add_argument("--failure-step")
    record.add_argument("--retriable", action="store_true")
    promote = sub.add_parser("promote-example", help="Deliberately promote a successful run to examples/.")
    promote.add_argument("--run-id", required=True)
    promote.add_argument("--slug", required=True)
    sub.add_parser("check", help="Validate the append-only relation without changing it.")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    repo_root = _root(args.root)
    try:
        if args.command == "record":
            failure = None
            if args.failure_code is not None or args.failure_step is not None or args.retriable:
                failure = {
                    "code": args.failure_code or "route_failed",
                    **({"step": args.failure_step} if args.failure_step is not None else {}),
                    **({"retriable": True} if args.retriable else {}),
                }
            record = record_run(
                args.production,
                args.status,
                root=repo_root,
                run_id=args.run_id,
                started_at=args.started_at,
                finished_at=args.finished_at,
                failure=failure,
                recover_run_id=args.recover_run_id,
            )
            print(json.dumps(record, indent=2, sort_keys=True))
            return 0
        if args.command == "promote-example":
            destination = promote_example(args.run_id, args.slug, root=repo_root)
            print(f"Curated example: {destination.relative_to(repo_root)}")
            return 0
        failures = validate_ledger(repo_root)
        if failures:
            for failure in failures:
                print(f"FAIL: {failure}", file=sys.stderr)
            return 1
        print("ACS run ledger: PASS")
        return 0
    except (OSError, TraceError) as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
