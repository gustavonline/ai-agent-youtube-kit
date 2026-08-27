from __future__ import annotations

import json
import hashlib
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from tracer import TraceError, load_ledger, promote_example, record_run, validate_ledger


REPO_ROOT = Path(__file__).resolve().parents[3]
FIXED_START = "2026-01-01T00:00:00Z"
FIXED_FINISH = "2026-01-01T00:00:01Z"


def make_root(*, semantic_outcome: str = "passed") -> tuple[tempfile.TemporaryDirectory[str], Path, Path]:
    temporary = tempfile.TemporaryDirectory()
    root = Path(temporary.name)
    production = root / "workspace/productions/demo"
    (production / "results").mkdir(parents=True)
    (production / "reports").mkdir()
    (root / "workspace/history").mkdir(parents=True)
    (root / "workspace/runs").mkdir(parents=True)
    (root / "examples").mkdir()
    (root / "workspace/history/runs.jsonl").write_text("\n", encoding="utf-8")
    (production / "project.json").write_text('{"project_id":"demo","title":"Demo","promise":"Promise","audience":"Audience"}\n', encoding="utf-8")
    (production / "edit-plan.json").write_text(
        '{"proof":["Proof"],"approval":{"approval_hash":"' + "a" * 64 + '","approval_revision":1}}\n',
        encoding="utf-8",
    )
    (production / "results/run-result.json").write_text('{"status":"passed"}\n', encoding="utf-8")
    (production / "reports/review.json").write_text('{"status":"passed"}\n', encoding="utf-8")
    result_path = production / "results/run-result.json"
    (production / "evaluations").mkdir()
    snapshot = production / "evaluations" / "candidate-result-seed.json"
    snapshot.write_bytes(result_path.read_bytes())
    (production / "evaluations" / "semantic-evaluation-seed.json").write_text(
        json.dumps(
            {
                "schema_version": "1.0",
                "evaluation_id": "seed",
                "project_id": "demo",
                "subject": "Demo",
                "checkpoint": "candidate result checkpoint",
                "result": {"path": "evaluations/candidate-result-seed.json", "sha256": hashlib.sha256(result_path.read_bytes()).hexdigest()},
                "decision": {"promise": "Promise", "audience": "Audience", "required_proof": ["Proof"], "approval_hash": "a" * 64, "approval_revision": 1},
                "observable_checks": [
                    {"id": "promise_delivery", "passed": semantic_outcome == "passed", "observation": "Promise observation."},
                    {"id": "proof_delivery", "passed": semantic_outcome == "passed", "observation": "Proof observation."},
                    {"id": "audience_relevance", "passed": semantic_outcome == "passed", "observation": "Audience observation."},
                ],
                "required_evidence": [{"path": "evaluations/candidate-result-seed.json", "sha256": hashlib.sha256(snapshot.read_bytes()).hexdigest()}],
                "outcome": semantic_outcome,
                "failure_action": "Retain the local candidate.",
                "evaluated_by": "reviewer",
                "evaluated_at": "2026-01-01T00:00:00Z",
            }
        )
        + "\n",
        encoding="utf-8",
    )
    return temporary, root, production


class SystemProofTests(unittest.TestCase):
    def test_canonical_shell_guard_passes(self) -> None:
        result = subprocess.run(
            [sys.executable, str(REPO_ROOT / "workspace/engine/checks.py")],
            cwd=REPO_ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(0, result.returncode, result.stderr)

    def test_success_record_has_production_proof_and_evidence(self) -> None:
        temporary, root, production = make_root()
        try:
            record = record_run(
                production,
                "succeeded",
                root=root,
                started_at=FIXED_START,
                finished_at=FIXED_FINISH,
            )
            self.assertEqual("run-0001", record["run_id"])
            self.assertIsNone(record["previous_run_id"])
            self.assertEqual("workspace/productions/demo/project.json", record["input_ref"])
            self.assertTrue((root / "workspace/runs/run-0001/run.json").is_file())
            self.assertEqual([], validate_ledger(root))
            self.assertEqual(1, len(load_ledger(root)))
            self.assertNotIn("prompt", (root / "workspace/history/runs.jsonl").read_text(encoding="utf-8"))
        finally:
            temporary.cleanup()

    def test_mixed_legacy_and_evaluated_ledger_records_remain_valid(self) -> None:
        temporary, root, production = make_root()
        try:
            legacy = {
                "run_id": "run-0001",
                "started_at": FIXED_START,
                "finished_at": FIXED_FINISH,
                "status": "succeeded",
                "input_ref": "workspace/productions/demo/project.json",
                "output_ref": "workspace/productions/demo/results/run-result.json",
                "proof_ref": "workspace/productions/demo/reports/review.json",
                "previous_run_id": None,
                "previous_run_relation": None,
                "failure": None,
                "recovery": None,
            }
            history_path = root / "workspace/history/runs.jsonl"
            history_path.write_text(json.dumps(legacy, sort_keys=True) + "\n", encoding="utf-8")
            legacy_evidence = root / "workspace/runs/run-0001"
            legacy_evidence.mkdir()
            (legacy_evidence / "run.json").write_text(json.dumps(legacy, sort_keys=True) + "\n", encoding="utf-8")
            self.assertEqual([], validate_ledger(root))

            evaluated = record_run(
                production,
                "succeeded",
                root=root,
                started_at="2026-01-01T00:02:00Z",
            )
            self.assertEqual("run-0001", evaluated["previous_run_id"])
            self.assertEqual("predecessor", evaluated["previous_run_relation"])
            self.assertIn("evaluation", evaluated)
            self.assertEqual("passed", evaluated["evaluation"]["outcome"])
            self.assertEqual([], validate_ledger(root))
            self.assertEqual(["run-0001", "run-0002"], [record["run_id"] for record in load_ledger(root)])
        finally:
            temporary.cleanup()

    def test_failure_can_be_recovered_only_once(self) -> None:
        temporary, root, production = make_root()
        try:
            failed = record_run(
                production,
                "failed",
                root=root,
                failure={"code": "render_failed", "step": "render", "retriable": True},
                started_at=FIXED_START,
            )
            recovered = record_run(
                production,
                "succeeded",
                root=root,
                recover_run_id=failed["run_id"],
                started_at="2026-01-01T00:01:00Z",
            )
            self.assertEqual("recovery", recovered["previous_run_relation"])
            self.assertEqual(failed["run_id"], recovered["recovery"]["recovered_run_id"])
            with self.assertRaises(TraceError):
                record_run(
                    production,
                    "succeeded",
                    root=root,
                    recover_run_id=failed["run_id"],
                    started_at="2026-01-01T00:02:00Z",
                )
            self.assertEqual(2, len(load_ledger(root)))
            self.assertEqual([], validate_ledger(root))
        finally:
            temporary.cleanup()

    def test_semantic_failure_is_retained_and_recovered_from_a_new_result(self) -> None:
        temporary, root, production = make_root(semantic_outcome="failed")
        try:
            failed = record_run(
                production,
                "failed",
                root=root,
                failure={"code": "semantic_eval_failed", "step": "semantic-eval", "retriable": True},
                started_at=FIXED_START,
            )
            retained_evaluation = root / failed["evaluation"]["path"]
            retained_bytes = retained_evaluation.read_bytes()
            result_path = production / "results/run-result.json"
            result_path.write_text('{"status":"corrected"}\n', encoding="utf-8")
            snapshot = production / "evaluations" / "candidate-result-recovery.json"
            snapshot.write_bytes(result_path.read_bytes())
            (production / "evaluations" / "semantic-evaluation-recovery.json").write_text(
                json.dumps(
                    {
                        "schema_version": "1.0",
                        "evaluation_id": "recovery",
                        "project_id": "demo",
                        "subject": "Demo",
                        "checkpoint": "candidate result checkpoint",
                        "result": {"path": "evaluations/candidate-result-recovery.json", "sha256": hashlib.sha256(result_path.read_bytes()).hexdigest()},
                        "decision": {"promise": "Promise", "audience": "Audience", "required_proof": ["Proof"], "approval_hash": "a" * 64, "approval_revision": 1},
                        "observable_checks": [
                            {"id": "promise_delivery", "passed": True, "observation": "Promise observation."},
                            {"id": "proof_delivery", "passed": True, "observation": "Proof observation."},
                            {"id": "audience_relevance", "passed": True, "observation": "Audience observation."},
                        ],
                        "required_evidence": [{"path": "evaluations/candidate-result-recovery.json", "sha256": hashlib.sha256(snapshot.read_bytes()).hexdigest()}],
                        "outcome": "passed",
                        "failure_action": "No correction is required.",
                        "evaluated_by": "reviewer",
                        "evaluated_at": "2026-01-01T00:01:00Z",
                    }
                )
                + "\n",
                encoding="utf-8",
            )
            recovered = record_run(
                production,
                "succeeded",
                root=root,
                recover_run_id=failed["run_id"],
                started_at="2026-01-01T00:01:00Z",
            )
            self.assertEqual("recovery", recovered["previous_run_relation"])
            self.assertEqual(retained_bytes, retained_evaluation.read_bytes())
            self.assertEqual("failed", failed["evaluation"]["outcome"])
            self.assertEqual("passed", recovered["evaluation"]["outcome"])
            self.assertEqual([], validate_ledger(root))
        finally:
            temporary.cleanup()

    def test_semantic_evaluation_references_cannot_escape_owning_production(self) -> None:
        temporary, root, production = make_root()
        try:
            evaluation_path = production / "evaluations" / "semantic-evaluation-seed.json"
            evaluation = json.loads(evaluation_path.read_text(encoding="utf-8"))
            evaluation["required_evidence"] = [{"path": "../outside.json", "sha256": "0" * 64}]
            evaluation_path.write_text(json.dumps(evaluation) + "\n", encoding="utf-8")
            with self.assertRaisesRegex(TraceError, "semantic evidence path"):
                record_run(production, "succeeded", root=root, started_at=FIXED_START)
            self.assertEqual([], [line for line in (root / "workspace/history/runs.jsonl").read_text().splitlines() if line])
        finally:
            temporary.cleanup()

    def test_ledger_rejects_deleted_retained_semantic_evidence(self) -> None:
        temporary, root, production = make_root()
        try:
            record_run(production, "succeeded", root=root, started_at=FIXED_START)
            snapshot = production / "evaluations" / "candidate-result-seed.json"
            snapshot.unlink()
            failures = validate_ledger(root)
            self.assertTrue(failures)
            self.assertIn("semantic evaluation evidence", " ".join(failures))
        finally:
            temporary.cleanup()

    def test_record_rejects_evaluation_when_current_promise_changes(self) -> None:
        temporary, root, production = make_root()
        try:
            project_path = production / "project.json"
            project = json.loads(project_path.read_text(encoding="utf-8"))
            project["promise"] = "A materially different promise"
            project_path.write_text(json.dumps(project) + "\n", encoding="utf-8")
            with self.assertRaisesRegex(TraceError, "older ACS content decision"):
                record_run(production, "succeeded", root=root, started_at=FIXED_START)
            self.assertEqual([], [line for line in (root / "workspace/history/runs.jsonl").read_text().splitlines() if line])
        finally:
            temporary.cleanup()

    def test_ledger_keeps_validating_retained_evidence_after_live_decision_changes(self) -> None:
        temporary, root, production = make_root()
        try:
            record_run(production, "succeeded", root=root, started_at=FIXED_START)
            project_path = production / "project.json"
            project = json.loads(project_path.read_text(encoding="utf-8"))
            project["promise"] = "A later decision outside the retained run evidence"
            project_path.write_text(json.dumps(project) + "\n", encoding="utf-8")
            self.assertEqual([], validate_ledger(root))
        finally:
            temporary.cleanup()

    def test_record_rejects_duplicate_semantic_check(self) -> None:
        temporary, root, production = make_root()
        try:
            evaluation_path = production / "evaluations" / "semantic-evaluation-seed.json"
            evaluation = json.loads(evaluation_path.read_text(encoding="utf-8"))
            evaluation["observable_checks"].append(
                {"id": "promise_delivery", "passed": True, "observation": "Duplicate observation."}
            )
            evaluation_path.write_text(json.dumps(evaluation) + "\n", encoding="utf-8")
            with self.assertRaisesRegex(TraceError, "exactly one promise, proof, and audience check"):
                record_run(production, "succeeded", root=root, started_at=FIXED_START)
        finally:
            temporary.cleanup()

    def test_ordinary_repeat_uses_predecessor_and_history_is_append_only(self) -> None:
        temporary, root, production = make_root()
        try:
            first = record_run(production, "succeeded", root=root, started_at=FIXED_START)
            history_path = root / "workspace/history/runs.jsonl"
            first_line = [line for line in history_path.read_text(encoding="utf-8").splitlines() if line][0]
            second = record_run(
                production,
                "succeeded",
                root=root,
                started_at="2026-01-01T00:02:00Z",
            )
            lines = [line for line in history_path.read_text(encoding="utf-8").splitlines() if line]
            self.assertEqual(first["run_id"], second["previous_run_id"])
            self.assertEqual("predecessor", second["previous_run_relation"])
            self.assertEqual(first_line, lines[0])
            self.assertEqual(2, len(lines))
            self.assertEqual([], validate_ledger(root))
        finally:
            temporary.cleanup()

    def test_example_promotion_is_explicit_and_curated(self) -> None:
        temporary, root, production = make_root()
        try:
            record = record_run(production, "succeeded", root=root, started_at=FIXED_START)
            self.assertEqual([], list((root / "examples").iterdir()))
            destination = promote_example(record["run_id"], "demo-proof", root=root)
            self.assertEqual({"README.md", "proof.json"}, {path.name for path in destination.iterdir()})
            proof = json.loads((destination / "proof.json").read_text(encoding="utf-8"))
            self.assertTrue(proof["curated"])
            self.assertEqual(record["run_id"], proof["run_id"])
            self.assertEqual([], validate_ledger(root))
        finally:
            temporary.cleanup()

    def test_repeatability_and_post_use_validation_are_byte_stable(self) -> None:
        snapshots: list[tuple[bytes, bytes, bytes]] = []
        source_history = (REPO_ROOT / "workspace/history/runs.jsonl").read_bytes()
        for _ in range(2):
            temporary, root, production = make_root()
            try:
                failed = record_run(
                    production,
                    "failed",
                    root=root,
                    failure={"code": "package_failed", "step": "package"},
                    started_at=FIXED_START,
                )
                record_run(
                    production,
                    "succeeded",
                    root=root,
                    recover_run_id=failed["run_id"],
                    started_at="2026-01-01T00:01:00Z",
                )
                promote_example("run-0002", "repeatable-proof", root=root)
                self.assertEqual([], validate_ledger(root))
                snapshots.append(
                    (
                        (root / "workspace/history/runs.jsonl").read_bytes(),
                        (root / "workspace/runs/run-0002/run.json").read_bytes(),
                        (root / "examples/repeatable-proof/proof.json").read_bytes(),
                    )
                )
            finally:
                temporary.cleanup()
        self.assertEqual(snapshots[0], snapshots[1])
        self.assertEqual(source_history, (REPO_ROOT / "workspace/history/runs.jsonl").read_bytes())


if __name__ == "__main__":
    unittest.main()
