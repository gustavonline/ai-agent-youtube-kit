from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from tracer import TraceError, load_ledger, promote_example, record_run, validate_ledger


REPO_ROOT = Path(__file__).resolve().parents[3]
FIXED_START = "2026-01-01T00:00:00Z"
FIXED_FINISH = "2026-01-01T00:00:01Z"


def make_root() -> tuple[tempfile.TemporaryDirectory[str], Path, Path]:
    temporary = tempfile.TemporaryDirectory()
    root = Path(temporary.name)
    production = root / "workspace/productions/demo"
    (production / "results").mkdir(parents=True)
    (production / "reports").mkdir()
    (root / "workspace/history").mkdir(parents=True)
    (root / "workspace/runs").mkdir(parents=True)
    (root / "examples").mkdir()
    (root / "workspace/history/runs.jsonl").write_text("\n", encoding="utf-8")
    (production / "project.json").write_text('{"project_id":"demo"}\n', encoding="utf-8")
    (production / "results/run-result.json").write_text('{"status":"passed"}\n', encoding="utf-8")
    (production / "reports/review.json").write_text('{"status":"passed"}\n', encoding="utf-8")
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
