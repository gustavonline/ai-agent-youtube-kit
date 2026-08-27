from __future__ import annotations

import copy
import json
import shutil
import subprocess
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

import agentic_content_system.package as package_module
from agentic_content_system.io import read_json, sha256_file, write_json
from agentic_content_system.package import package_project
from agentic_content_system.project import load_contracts
from agentic_content_system.semantic import current_semantic_evaluation
from agentic_content_system.schemas import load_schema
from agentic_content_system.validation import validate_json
from agentic_content_system.errors import ACSUserError


REPO_ROOT = Path(__file__).resolve().parents[3]
FIXTURE_TRANSCRIPT = REPO_ROOT / "workspace" / "engine" / "tests" / "fixtures" / "transcript.json"
SEMANTIC_PASS = REPO_ROOT / "workspace" / "engine" / "tests" / "fixtures" / "semantic-assessment-passed.json"
SEMANTIC_FAIL = REPO_ROOT / "workspace" / "engine" / "tests" / "fixtures" / "semantic-assessment-failed.json"


class CLITests(unittest.TestCase):
    def setUp(self) -> None:
        self.runs_root = REPO_ROOT / "workspace" / "productions" / "test-runs"
        self.runs_root.mkdir(parents=True, exist_ok=True)
        self.project = self.runs_root / self._testMethodName
        if self.project.exists():
            shutil.rmtree(self.project)

    def tearDown(self) -> None:
        if self.project.exists():
            shutil.rmtree(self.project)

    def run_cli(self, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, "-m", "agentic_content_system", *args],
            cwd=REPO_ROOT,
            text=True,
            capture_output=True,
        )

    def create_project_and_source(self) -> None:
        result = self.run_cli("init", str(self.project))
        self.assertEqual(result.returncode, 0, result.stderr)
        fixture_script = REPO_ROOT / "workspace" / "engine" / "scripts" / "create-fixture-media.py"
        result = subprocess.run(
            [sys.executable, str(fixture_script), str(self.project / "sources" / "source.mp4"), "--duration", "2"],
            cwd=REPO_ROOT,
            text=True,
            capture_output=True,
        )
        if result.returncode != 0 and "ffmpeg" in result.stderr.lower():
            self.skipTest("ffmpeg is not installed")
        self.assertEqual(result.returncode, 0, result.stderr)

    def prepare_approved_project(self) -> None:
        self.create_project_and_source()
        for command in (
            ("inspect", str(self.project)),
            ("ingest-transcript", str(self.project), str(FIXTURE_TRANSCRIPT)),
            ("plan", str(self.project), "--approve", "--by", "reviewer"),
        ):
            result = self.run_cli(*command)
            self.assertEqual(result.returncode, 0, f"{command}: {result.stderr}")

    def prepare_exported_project(self) -> None:
        self.prepare_approved_project()
        for command in (
            ("render", str(self.project), "--kind", "all"),
            ("derive", str(self.project)),
            ("package", str(self.project)),
            ("verify", str(self.project)),
            ("review-report", str(self.project)),
            ("export-result", str(self.project)),
        ):
            result = self.run_cli(*command)
            self.assertEqual(result.returncode, 0, f"{command}: {result.stderr}")

    def create_color_source(self, path: Path, color: str, duration: float = 1.0) -> None:
        ffmpeg = shutil.which("ffmpeg")
        if not ffmpeg:
            self.skipTest("ffmpeg is not installed")
        result = subprocess.run(
            [
                ffmpeg,
                "-hide_banner",
                "-loglevel",
                "error",
                "-y",
                "-f",
                "lavfi",
                "-i",
                f"color=c={color}:s=160x90:r=24",
                "-t",
                str(duration),
                "-an",
                "-c:v",
                "libx264",
                "-preset",
                "medium",
                "-crf",
                "23",
                "-pix_fmt",
                "yuv420p",
                str(path),
            ],
            cwd=REPO_ROOT,
            text=True,
            capture_output=True,
        )
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_help_is_portable_and_stable(self) -> None:
        result = self.run_cli("--help")
        self.assertEqual(result.returncode, 0)
        self.assertIn("Agentic Content System", result.stdout)
        self.assertIn("review-report", result.stdout)
        self.assertNotIn("init-from-handoff", result.stdout)
        self.assertFalse((REPO_ROOT / "workspace" / "engine" / "agentic_content_system" / "handoff.py").exists())
        self.assertFalse((REPO_ROOT / "workspace" / "engine" / "contracts" / "schemas" / "aios-handoff.schema.json").exists())

        for command in ("derive", "package"):
            sub_help = self.run_cli(command, "--help")
            self.assertEqual(sub_help.returncode, 0, sub_help.stderr)
            self.assertNotIn("--force", sub_help.stdout)
        clean_help = self.run_cli("clean", "--help")
        self.assertEqual(clean_help.returncode, 0, clean_help.stderr)
        self.assertIn("results", clean_help.stdout)

    def test_end_to_end_fixture_and_idempotent_render(self) -> None:
        self.create_project_and_source()
        for command in (
            ("inspect", str(self.project)),
            ("validate", str(self.project)),
            ("ingest-transcript", str(self.project), str(FIXTURE_TRANSCRIPT)),
        ):
            result = self.run_cli(*command)
            self.assertEqual(result.returncode, 0, result.stderr)

        blocked = self.run_cli("render", str(self.project), "--kind", "all")
        self.assertEqual(blocked.returncode, 2)
        self.assertIn("approval", blocked.stderr.lower())

        commands = (
            ("plan", str(self.project), "--approve", "--by", "automated-test"),
            ("render", str(self.project), "--kind", "all"),
            ("derive", str(self.project)),
            ("package", str(self.project)),
            ("verify", str(self.project)),
            ("review-report", str(self.project)),
            ("export-result", str(self.project)),
        )
        for command in commands:
            result = self.run_cli(*command)
            self.assertEqual(result.returncode, 0, f"{command}: {result.stderr}")

        cached = self.run_cli("render", str(self.project), "--kind", "all")
        self.assertEqual(cached.returncode, 0, cached.stderr)
        self.assertIn('"status": "cached"', cached.stdout)

        manifest = read_json(self.project / "publish" / "manifest.json")
        route_ids = {route["channel"] for route in manifest["routes"]}
        self.assertEqual({"youtube", "linkedin"}, route_ids)
        self.assertNotIn("tiktok", route_ids)
        self.assertNotIn("instagram", route_ids)
        self.assertFalse(manifest["verification"]["external_posting"])
        self.assertEqual("passed", manifest["verification"]["status"])
        self.assertTrue((self.project / "reports" / "review.html").exists())
        self.assertEqual(1080, read_json(self.project / "renders" / "render-record.json")["renders"]["short"]["metadata"]["width"])
        publisher = read_json(self.project / "publish" / "publisher-handoff.json")
        self.assertEqual({"youtube", "linkedin"}, {route["channel"] for route in publisher["routes"]})
        youtube_route = next(route for route in publisher["routes"] if route["channel"] == "youtube")
        linkedin_route = next(route for route in publisher["routes"] if route["channel"] == "linkedin")
        self.assertEqual("manual", youtube_route["delivery_mode"])
        self.assertNotIn("scheduled_at", youtube_route)
        self.assertNotIn("timezone", youtube_route)
        self.assertEqual("manual", linkedin_route["delivery_mode"])
        self.assertNotIn("scheduled_at", linkedin_route)
        self.assertNotIn("timezone", linkedin_route)
        self.assertEqual("awaiting-separate-authorization", publisher["status"])
        self.assertTrue(publisher["not_posted"])
        self.assertFalse(publisher["external_posting"])

        result = read_json(self.project / "results" / "run-result.json")
        self.assertEqual("publish/publisher-handoff.json", result["publisher_handoff"]["path"])
        self.assertEqual(
            sha256_file(self.project / "publish" / "publisher-handoff.json"),
            result["publisher_handoff"]["sha256"],
        )
        self.assertEqual("awaiting-separate-authorization", result["publisher_handoff"]["status"])
        self.assertFalse(result["publisher_handoff"]["external_posting"])

    def test_disabled_channel_policy_is_enforced(self) -> None:
        self.create_project_and_source()
        brand_path = self.project / "brand.json"
        brand = read_json(brand_path)
        brand["channels"][3]["reason"] = ""
        write_json(brand_path, brand)
        result = self.run_cli("validate", str(self.project))
        self.assertEqual(result.returncode, 2)
        self.assertIn("reason", result.stderr.lower())

    def test_semantic_eval_rejects_valid_but_irrelevant_candidate_without_changing_result(self) -> None:
        self.prepare_exported_project()
        result_path = self.project / "results" / "run-result.json"
        result_before = result_path.read_bytes()
        valid = self.run_cli("validate", str(self.project))
        self.assertEqual(valid.returncode, 0, valid.stderr)

        failed = self.run_cli("semantic-eval", str(self.project), str(SEMANTIC_FAIL), "--by", "content-reviewer")
        self.assertEqual(failed.returncode, 2)
        self.assertIn("semantic evaluation failed", failed.stderr.lower())
        self.assertEqual(result_before, result_path.read_bytes())
        evaluations = list((self.project / "evaluations").glob("semantic-evaluation-*.json"))
        self.assertEqual(1, len(evaluations))
        evaluation = read_json(evaluations[0])
        self.assertEqual("failed", evaluation["outcome"])
        self.assertTrue(evaluation["result"]["path"].startswith("evaluations/candidate-result-"))
        self.assertTrue(all(not item["passed"] for item in evaluation["observable_checks"]))

    def test_current_semantic_evaluation_rejects_duplicate_check_rows(self) -> None:
        self.prepare_exported_project()
        passed = self.run_cli("semantic-eval", str(self.project), str(SEMANTIC_PASS), "--by", "content-reviewer")
        self.assertEqual(passed.returncode, 0, passed.stderr)
        evaluation_path = next((self.project / "evaluations").glob("semantic-evaluation-*.json"))
        evaluation = read_json(evaluation_path)
        evaluation["observable_checks"].append(
            {"id": "promise_delivery", "subject": "duplicate", "passed": True, "observation": "Duplicate row."}
        )
        write_json(evaluation_path, evaluation)
        with self.assertRaises(ACSUserError):
            current_semantic_evaluation(load_contracts(self.project))

    def test_semantic_evaluation_schema_uses_uniform_full_rows_without_prefix_items(self) -> None:
        self.prepare_exported_project()
        passed = self.run_cli("semantic-eval", str(self.project), str(SEMANTIC_PASS), "--by", "content-reviewer")
        self.assertEqual(passed.returncode, 0, passed.stderr)
        evaluation = read_json(next((self.project / "evaluations").glob("semantic-evaluation-*.json")))
        schema = load_schema("semantic-evaluation")
        checks_schema = schema["properties"]["observable_checks"]
        self.assertNotIn("prefixItems", checks_schema)
        self.assertEqual(3, checks_schema["minItems"])
        self.assertEqual(3, checks_schema["maxItems"])
        self.assertEqual(
            {"id", "subject", "passed", "observation"},
            set(checks_schema["items"]["required"]),
        )
        self.assertFalse(checks_schema["items"]["additionalProperties"])

        missing_passed = copy.deepcopy(evaluation)
        del missing_passed["observable_checks"][0]["passed"]
        self.assertTrue(validate_json(missing_passed, schema))
        unexpected_check_field = copy.deepcopy(evaluation)
        unexpected_check_field["observable_checks"][0]["unexpected"] = True
        self.assertTrue(validate_json(unexpected_check_field, schema))
        fourth_check = copy.deepcopy(evaluation)
        fourth_check["observable_checks"].append(copy.deepcopy(fourth_check["observable_checks"][0]))
        self.assertTrue(validate_json(fourth_check, schema))

    def test_validator_does_not_apply_nonstandard_prefix_items_to_uniform_items(self) -> None:
        issues = validate_json(
            [{"id": "not-positional", "passed": True}],
            {
                "type": "array",
                "prefixItems": [{"type": "object", "properties": {"id": {"const": "first"}}}],
                "items": {
                    "type": "object",
                    "required": ["id", "passed"],
                    "properties": {"id": {"type": "string"}, "passed": {"type": "boolean"}},
                },
            },
        )
        self.assertEqual([], issues)

    def test_approval_drift_blocks_every_gated_command_until_reapproval(self) -> None:
        self.prepare_approved_project()
        plan_path = self.project / "edit-plan.json"
        plan = read_json(plan_path)
        plan["long_form"]["segments"][0]["duration"] = 1
        write_json(plan_path, plan)
        for command in ("render", "derive", "package"):
            result = self.run_cli(command, str(self.project), "--kind", "long") if command == "render" else self.run_cli(command, str(self.project))
            self.assertEqual(result.returncode, 2, f"{command} unexpectedly passed")
            self.assertTrue(
                "stale" in result.stderr.lower() or "approval" in result.stderr.lower(),
                result.stderr,
            )

        result = self.run_cli("plan", str(self.project), "--approve", "--by", "reviewer")
        self.assertEqual(result.returncode, 0, result.stderr)
        result = self.run_cli("render", str(self.project), "--kind", "long")
        self.assertEqual(result.returncode, 0, result.stderr)

        brand_path = self.project / "brand.json"
        brand = read_json(brand_path)
        brand["channels"][0]["reason"] = "Updated policy reason requiring review."
        write_json(brand_path, brand)
        result = self.run_cli("render", str(self.project), "--kind", "long")
        self.assertEqual(result.returncode, 2)
        self.assertIn("approval", result.stderr.lower())

        result = self.run_cli("plan", str(self.project), "--approve", "--by", "reviewer")
        self.assertEqual(result.returncode, 0, result.stderr)

        project_path = self.project / "project.json"
        project = read_json(project_path)
        project["sources"][0]["rights"]["license"] = "owner-provided-original-v2"
        write_json(project_path, project)
        result = self.run_cli("render", str(self.project), "--kind", "long")
        self.assertEqual(result.returncode, 2)
        self.assertIn("approval", result.stderr.lower())

        source_path = self.project / "sources" / "source.mp4"
        with source_path.open("ab") as handle:
            handle.write(b"source drift")
        result = self.run_cli("render", str(self.project), "--kind", "long")
        self.assertEqual(result.returncode, 2)
        self.assertIn("approval", result.stderr.lower())

    def test_stale_inspection_blocks_verification_and_review_proof(self) -> None:
        self.prepare_approved_project()
        project_path = self.project / "project.json"
        project = read_json(project_path)
        project["sources"][0]["rights"]["license"] = "changed-without-reinspection"
        write_json(project_path, project)

        for command in (
            ("plan", str(self.project), "--approve", "--by", "reviewer"),
            ("render", str(self.project), "--kind", "all"),
            ("derive", str(self.project)),
            ("package", str(self.project)),
        ):
            result = self.run_cli(*command)
            self.assertEqual(result.returncode, 0, f"{command}: {result.stderr}")

        for command in ("verify", "review-report", "export-result"):
            result = self.run_cli(command, str(self.project))
            self.assertEqual(result.returncode, 2, f"{command} unexpectedly passed")
            self.assertIn("inspection", result.stderr.lower(), result.stderr)

    def test_review_report_rejects_stale_package_epoch_before_writing(self) -> None:
        self.prepare_exported_project()
        report_path = self.project / "reports" / "review.html"
        review_record_path = self.project / "reports" / "review.json"
        old_report = report_path.read_bytes()
        old_review_record = review_record_path.read_bytes()

        project_path = self.project / "project.json"
        project = read_json(project_path)
        project["sources"][0]["rights"]["license"] = "changed-after-publish"
        write_json(project_path, project)
        result = self.run_cli("inspect", str(self.project))
        self.assertEqual(result.returncode, 0, result.stderr)

        result = self.run_cli("review-report", str(self.project))
        self.assertEqual(result.returncode, 2)
        self.assertTrue("approval" in result.stderr.lower() or "stale" in result.stderr.lower(), result.stderr)
        self.assertEqual(old_report, report_path.read_bytes())
        self.assertEqual(old_review_record, review_record_path.read_bytes())

        result = self.run_cli("plan", str(self.project), "--approve", "--by", "reviewer")
        self.assertEqual(result.returncode, 0, result.stderr)
        result = self.run_cli("review-report", str(self.project))
        self.assertEqual(result.returncode, 2)
        self.assertIn("stale", result.stderr.lower())
        self.assertEqual(old_report, report_path.read_bytes())
        self.assertEqual(old_review_record, review_record_path.read_bytes())

        result = self.run_cli("render", str(self.project), "--kind", "all")
        self.assertEqual(result.returncode, 0, result.stderr)
        for stale_path in (
            self.project / "derived" / "linkedin.md",
            self.project / "derived" / "derivative-record.json",
        ):
            stale_path.unlink(missing_ok=True)
        for command in (
            ("derive", str(self.project)),
            ("package", str(self.project)),
            ("verify", str(self.project)),
            ("review-report", str(self.project)),
        ):
            result = self.run_cli(*command)
            self.assertEqual(result.returncode, 0, f"{command}: {result.stderr}")
        review_record = read_json(review_record_path)
        self.assertEqual("passed", review_record["verification_status"])
        self.assertIn("changed-after-publish", report_path.read_text(encoding="utf-8"))

    def test_disabled_render_output_cannot_prune_owner_source(self) -> None:
        self.prepare_approved_project()
        source_path = self.project / "sources" / "source.mp4"
        original_hash = sha256_file(source_path)
        plan_path = self.project / "edit-plan.json"
        plan = read_json(plan_path)
        plan["short_form"]["enabled"] = False
        plan["short_form"]["output"] = "sources/source.mp4"
        write_json(plan_path, plan)
        result = self.run_cli("plan", str(self.project), "--approve", "--by", "reviewer")
        self.assertEqual(result.returncode, 0, result.stderr)

        for command in (
            ("render", str(self.project), "--kind", "all"),
            ("review-report", str(self.project)),
            ("package", str(self.project)),
        ):
            result = self.run_cli(*command)
            self.assertEqual(result.returncode, 2, f"{command} unexpectedly passed")
            self.assertIn("renders", result.stderr.lower(), result.stderr)
        self.assertTrue(source_path.exists())
        self.assertEqual(original_hash, sha256_file(source_path))
        archive_dir = self.project / "recovery" / "disabled-renders"
        self.assertFalse(archive_dir.exists() and any(archive_dir.iterdir()))

    def test_prepackage_review_report_uses_canonical_not_packaged_status(self) -> None:
        self.prepare_approved_project()
        result = self.run_cli("review-report", str(self.project))
        self.assertEqual(result.returncode, 0, result.stderr)
        review_record = read_json(self.project / "reports" / "review.json")
        self.assertEqual("not_packaged", review_record["verification_status"])
        self.assertEqual("", review_record["manifest_id"])
        self.assertEqual("", review_record["verification_sha256"])

    def test_uncleared_rights_block_package_and_verification(self) -> None:
        self.prepare_exported_project()
        project_path = self.project / "project.json"
        project = read_json(project_path)
        for status in ("permission-pending", "unknown"):
            project["sources"][0]["rights"]["status"] = status
            write_json(project_path, project)
            inspect = self.run_cli("inspect", str(self.project))
            self.assertEqual(inspect.returncode, 0, inspect.stderr)
            approve = self.run_cli("plan", str(self.project), "--approve", "--by", "reviewer")
            self.assertEqual(approve.returncode, 0, approve.stderr)
            for command in ("package", "verify"):
                result = self.run_cli(command, str(self.project))
                self.assertEqual(result.returncode, 2, f"{status} allowed {command}")
                self.assertIn("cleared rights", result.stderr.lower(), result.stderr)

    def test_linkedin_derivative_denies_stale_transcript_until_reregistered(self) -> None:
        self.prepare_approved_project()
        for command in (
            ("render", str(self.project), "--kind", "all"),
            ("derive", str(self.project)),
        ):
            result = self.run_cli(*command)
            self.assertEqual(result.returncode, 0, f"{command}: {result.stderr}")

        transcript_path = self.project / "transcripts" / "active.json"
        transcript = read_json(transcript_path)
        transcript["segments"][0]["text"] += " Transcript revision."
        write_json(transcript_path, transcript)
        result = self.run_cli("package", str(self.project))
        self.assertEqual(result.returncode, 2)
        self.assertIn("transcript", result.stderr.lower())

        result = self.run_cli("derive", str(self.project))
        self.assertEqual(result.returncode, 0, result.stderr)
        result = self.run_cli("package", str(self.project))
        self.assertEqual(result.returncode, 0, result.stderr)
        derivative_record = read_json(self.project / "derived" / "derivative-record.json")
        self.assertEqual(
            sha256_file(transcript_path),
            derivative_record["derivatives"][0]["transcript_sha256"],
        )

    def test_package_rejects_stale_render_and_cleans_disabled_route_state(self) -> None:
        self.prepare_approved_project()
        for command in (
            ("render", str(self.project), "--kind", "all"),
            ("derive", str(self.project)),
            ("package", str(self.project)),
            ("verify", str(self.project)),
        ):
            result = self.run_cli(*command)
            self.assertEqual(result.returncode, 0, f"{command}: {result.stderr}")
        self.assertTrue((self.project / "publish" / "verification.json").exists())

        plan_path = self.project / "edit-plan.json"
        plan = read_json(plan_path)
        plan["long_form"]["segments"][0]["duration"] = 1.25
        write_json(plan_path, plan)
        result = self.run_cli("plan", str(self.project), "--approve", "--by", "reviewer")
        self.assertEqual(result.returncode, 0, result.stderr)
        result = self.run_cli("package", str(self.project))
        self.assertEqual(result.returncode, 2)
        self.assertIn("stale", result.stderr.lower())

        result = self.run_cli("render", str(self.project), "--kind", "all")
        self.assertEqual(result.returncode, 0, result.stderr)
        brand_path = self.project / "brand.json"
        brand = read_json(brand_path)
        brand["channels"][1]["enabled"] = False
        brand["channels"][1]["reason"] = "Disabled for this project; keep the proof on YouTube only."
        write_json(brand_path, brand)
        result = self.run_cli("plan", str(self.project), "--approve", "--by", "reviewer")
        self.assertEqual(result.returncode, 0, result.stderr)
        result = self.run_cli("render", str(self.project), "--kind", "all")
        self.assertEqual(result.returncode, 0, result.stderr)
        result = self.run_cli("derive", str(self.project))
        self.assertEqual(result.returncode, 0, result.stderr)
        result = self.run_cli("package", str(self.project))
        self.assertEqual(result.returncode, 0, result.stderr)
        manifest = read_json(self.project / "publish" / "manifest.json")
        self.assertEqual(["youtube"], [route["channel"] for route in manifest["routes"]])
        self.assertEqual("not_run", manifest["verification"]["status"])
        self.assertFalse((self.project / "publish" / "posts" / "linkedin.md").exists())
        self.assertFalse((self.project / "publish" / "verification.json").exists())
        self.assertFalse((self.project / "derived" / "linkedin.md").exists())
        self.assertFalse((self.project / "derived" / "derivative-record.json").exists())
        archive = list((self.project / "recovery" / "disabled-derivatives").glob("linkedin-*.md"))
        self.assertEqual(1, len(archive))

        for command in (
            ("verify", str(self.project)),
            ("review-report", str(self.project)),
            ("export-result", str(self.project)),
        ):
            result = self.run_cli(*command)
            self.assertEqual(result.returncode, 0, f"{command}: {result.stderr}")
        run_result = read_json(self.project / "results" / "run-result.json")
        self.assertEqual(["youtube"], run_result["enabled_routes"])
        self.assertNotIn("linkedin", run_result["enabled_routes"])
        self.assertNotIn(
            "derived/derivative-record.json",
            {item["path"] for item in run_result["proof"]},
        )

    def test_export_result_rejects_mutated_asset_after_verify(self) -> None:
        self.prepare_approved_project()
        for command in (
            ("render", str(self.project), "--kind", "all"),
            ("derive", str(self.project)),
            ("package", str(self.project)),
            ("verify", str(self.project)),
            ("review-report", str(self.project)),
        ):
            result = self.run_cli(*command)
            self.assertEqual(result.returncode, 0, f"{command}: {result.stderr}")

        asset = self.project / "publish" / "assets" / "long.mp4"
        with asset.open("ab") as handle:
            handle.write(b"tampered after verify")
        result = self.run_cli("export-result", str(self.project))
        self.assertEqual(result.returncode, 2)
        self.assertIn("hash mismatch", result.stderr.lower())
        self.assertFalse((self.project / "results" / "run-result.json").exists())

    def test_publisher_handoff_tamper_and_missing_file_are_denied(self) -> None:
        self.prepare_approved_project()
        for command in (
            ("render", str(self.project), "--kind", "all"),
            ("derive", str(self.project)),
            ("package", str(self.project)),
        ):
            result = self.run_cli(*command)
            self.assertEqual(result.returncode, 0, f"{command}: {result.stderr}")

        handoff_path = self.project / "publish" / "publisher-handoff.json"
        original = handoff_path.read_text(encoding="utf-8")
        handoff = read_json(handoff_path)
        handoff["routes"][0]["channel"] = "tiktok"
        write_json(handoff_path, handoff)
        result = self.run_cli("verify", str(self.project))
        self.assertEqual(result.returncode, 2)
        self.assertIn("publisher handoff", result.stderr.lower())

        handoff_path.write_text(original, encoding="utf-8")
        handoff_path.unlink()
        result = self.run_cli("verify", str(self.project))
        self.assertEqual(result.returncode, 2)
        self.assertIn("handoff", result.stderr.lower())

    def test_package_invalidates_review_and_result_until_current_report_is_rebuilt(self) -> None:
        self.prepare_exported_project()
        old_report = (self.project / "reports" / "review.html").read_text(encoding="utf-8")
        old_review_record = (self.project / "reports" / "review.json").read_text(encoding="utf-8")
        old_result = (self.project / "results" / "run-result.json").read_text(encoding="utf-8")

        brand_path = self.project / "brand.json"
        brand = read_json(brand_path)
        brand["channels"][1]["enabled"] = False
        brand["channels"][1]["reason"] = "Disabled for this run; keep the current proof on YouTube only."
        write_json(brand_path, brand)
        for command in (
            ("plan", str(self.project), "--approve", "--by", "reviewer"),
            ("render", str(self.project), "--kind", "all"),
            ("derive", str(self.project)),
            ("package", str(self.project)),
            ("verify", str(self.project)),
        ):
            result = self.run_cli(*command)
            self.assertEqual(result.returncode, 0, f"{command}: {result.stderr}")

        self.assertFalse((self.project / "reports" / "review.html").exists())
        self.assertFalse((self.project / "reports" / "review.json").exists())
        self.assertFalse((self.project / "results" / "run-result.json").exists())
        result = self.run_cli("export-result", str(self.project))
        self.assertEqual(result.returncode, 2)
        self.assertIn("review-report", result.stderr.lower())
        self.assertFalse((self.project / "results" / "run-result.json").exists())
        self.assertNotEqual(old_report, "")
        self.assertNotEqual(old_review_record, "")
        self.assertNotEqual(old_result, "")

        # Even if a stale report is manually restored, its old manifest
        # binding must not be accepted for the new package.
        reports_dir = self.project / "reports"
        reports_dir.mkdir(parents=True, exist_ok=True)
        (reports_dir / "review.html").write_text(old_report, encoding="utf-8")
        (reports_dir / "review.json").write_text(old_review_record, encoding="utf-8")
        result = self.run_cli("export-result", str(self.project))
        self.assertEqual(result.returncode, 2)
        self.assertIn("older publish manifest", result.stderr.lower())
        self.assertFalse((self.project / "results" / "run-result.json").exists())

        for command in (
            ("review-report", str(self.project)),
            ("export-result", str(self.project)),
        ):
            result = self.run_cli(*command)
            self.assertEqual(result.returncode, 0, f"{command}: {result.stderr}")
        manifest = read_json(self.project / "publish" / "manifest.json")
        run_result = read_json(self.project / "results" / "run-result.json")
        review_record = read_json(self.project / "reports" / "review.json")
        self.assertEqual(["youtube"], run_result["enabled_routes"])
        self.assertEqual(manifest["manifest_id"], review_record["manifest_id"])
        self.assertIn(
            "publish/manifest.json",
            {item["path"] for item in run_result["proof"]},
        )
        self.assertEqual("passed", review_record["verification_status"])
        self.assertNotIn("linkedin", run_result["enabled_routes"])

    def test_failed_export_archives_prior_result_and_leaves_no_active_stale_result(self) -> None:
        self.prepare_exported_project()
        result_path = self.project / "results" / "run-result.json"
        old_result = result_path.read_text(encoding="utf-8")
        asset = self.project / "publish" / "assets" / "long.mp4"
        with asset.open("ab") as handle:
            handle.write(b"tampered after successful export")

        result = self.run_cli("export-result", str(self.project))
        self.assertEqual(result.returncode, 2)
        self.assertIn("hash mismatch", result.stderr.lower())
        self.assertFalse(result_path.exists())
        archived = list((self.project / "recovery" / "stale-results").glob("run-result-*.json"))
        self.assertEqual(1, len(archived))
        self.assertEqual(old_result, archived[0].read_text(encoding="utf-8"))

    def test_package_failure_restores_prior_valid_publish_atomically(self) -> None:
        self.prepare_exported_project()
        old_manifest = (self.project / "publish" / "manifest.json").read_text(encoding="utf-8")
        old_publisher_handoff = (self.project / "publish" / "publisher-handoff.json").read_text(encoding="utf-8")
        old_verification = (self.project / "publish" / "verification.json").read_text(encoding="utf-8")
        old_report = (self.project / "reports" / "review.html").read_text(encoding="utf-8")
        old_review_record = (self.project / "reports" / "review.json").read_text(encoding="utf-8")
        old_result = (self.project / "results" / "run-result.json").read_text(encoding="utf-8")
        real_replace = package_module.os.replace
        calls = 0

        def fail_final_replace(source: str | bytes | Path, destination: str | bytes | Path) -> None:
            nonlocal calls
            calls += 1
            if calls == 2:
                raise OSError("injected final publish replacement failure")
            real_replace(source, destination)

        contracts = load_contracts(self.project)
        with patch.object(package_module.os, "replace", side_effect=fail_final_replace):
            with self.assertRaises(OSError):
                package_project(contracts)

        self.assertEqual(3, calls)  # move old, failed final move, restore old
        self.assertEqual(old_manifest, (self.project / "publish" / "manifest.json").read_text(encoding="utf-8"))
        self.assertEqual(old_publisher_handoff, (self.project / "publish" / "publisher-handoff.json").read_text(encoding="utf-8"))
        self.assertEqual(old_verification, (self.project / "publish" / "verification.json").read_text(encoding="utf-8"))
        self.assertEqual(old_report, (self.project / "reports" / "review.html").read_text(encoding="utf-8"))
        self.assertEqual(old_review_record, (self.project / "reports" / "review.json").read_text(encoding="utf-8"))
        self.assertEqual(old_result, (self.project / "results" / "run-result.json").read_text(encoding="utf-8"))
        self.assertFalse(any(self.project.glob(".publish-staging-*")))
        self.assertFalse(any(self.project.glob(".publish-old-*")))

    def test_refined_linkedin_post_is_preserved_and_registered_explicitly(self) -> None:
        self.prepare_approved_project()
        for command in (
            ("render", str(self.project), "--kind", "all"),
            ("derive", str(self.project)),
        ):
            result = self.run_cli(*command)
            self.assertEqual(result.returncode, 0, result.stderr)
        post = self.project / "derived" / "linkedin.md"
        refined = "# Human-refined post\n\nKeep this exact buyer-relevant language.\n"
        post.write_text(refined, encoding="utf-8")
        result = self.run_cli("package", str(self.project))
        self.assertEqual(result.returncode, 2)
        self.assertIn("changed", result.stderr.lower())
        self.assertEqual(refined, post.read_text(encoding="utf-8"))
        result = self.run_cli("derive", str(self.project))
        self.assertEqual(result.returncode, 0, result.stderr)
        result = self.run_cli("package", str(self.project))
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(refined, (self.project / "publish" / "posts" / "linkedin.md").read_text(encoding="utf-8"))

    def test_non_contiguous_multi_source_segments_preserve_order_and_duration(self) -> None:
        self.create_project_and_source()
        self.create_color_source(self.project / "sources" / "source.mp4", "red", 1.0)
        self.create_color_source(self.project / "sources" / "blue.mp4", "blue", 1.0)
        project_path = self.project / "project.json"
        project = read_json(project_path)
        project["sources"].append(
            {
                "path": "sources/blue.mp4",
                "kind": "camera",
                "role": "supporting",
                "rights": {
                    "status": "owned",
                    "owner": "Test",
                    "license": "fixture",
                    "source_url": "",
                    "attribution": "",
                },
            }
        )
        write_json(project_path, project)
        plan_path = self.project / "edit-plan.json"
        plan = read_json(plan_path)
        plan["long_form"]["segments"] = [
            {"source": "sources/source.mp4", "start": 0, "duration": 0.8},
            {"source": "sources/blue.mp4", "start": 0.1, "duration": 0.8},
        ]
        plan["short_form"]["enabled"] = False
        write_json(plan_path, plan)
        result = self.run_cli("plan", str(self.project), "--approve", "--by", "segment-test")
        self.assertEqual(result.returncode, 0, result.stderr)
        result = self.run_cli("render", str(self.project), "--kind", "long")
        self.assertEqual(result.returncode, 0, result.stderr)
        record = read_json(self.project / "renders" / "render-record.json")["renders"]["long"]
        self.assertEqual([segment["source"] for segment in record["segments"]], ["sources/source.mp4", "sources/blue.mp4"])
        self.assertGreater(record["metadata"]["duration_seconds"], 1.3)
        self.assertLess(record["metadata"]["duration_seconds"], 1.9)

        ffmpeg = shutil.which("ffmpeg")
        output = self.project / "renders" / "long.mp4"
        def mean_rgb(at: float) -> tuple[float, float, float]:
            frame = subprocess.run(
                [ffmpeg, "-hide_banner", "-loglevel", "error", "-ss", str(at), "-i", str(output), "-frames:v", "1", "-f", "rawvideo", "-pix_fmt", "rgb24", "-"],
                capture_output=True,
                check=True,
            ).stdout
            return tuple(sum(frame[index::3]) / max(1, len(frame[index::3])) for index in range(3))

        first = mean_rgb(0.2)
        second = mean_rgb(1.0)
        self.assertGreater(first[0], first[2] * 1.5)
        self.assertGreater(second[2], second[0] * 1.5)

    def test_disabled_edit_output_is_pruned_from_active_record_and_review(self) -> None:
        self.prepare_exported_project()
        plan_path = self.project / "edit-plan.json"
        plan = read_json(plan_path)
        plan["short_form"]["enabled"] = False
        write_json(plan_path, plan)
        result = self.run_cli("plan", str(self.project), "--approve", "--by", "reviewer")
        self.assertEqual(result.returncode, 0, result.stderr)
        result = self.run_cli("render", str(self.project), "--kind", "all")
        self.assertEqual(result.returncode, 0, result.stderr)

        record = read_json(self.project / "renders" / "render-record.json")
        self.assertNotIn("short", record["renders"])
        self.assertFalse((self.project / "renders" / "short-vertical.mp4").exists())
        self.assertTrue(any((self.project / "recovery" / "disabled-renders").glob("short-*.mp4")))

        # The approval revision makes the prior derivative intentionally stale;
        # removing it models an explicit review/replacement before packaging.
        (self.project / "derived" / "linkedin.md").unlink()
        (self.project / "derived" / "derivative-record.json").unlink()
        for command in (
            ("derive", str(self.project)),
            ("package", str(self.project)),
            ("verify", str(self.project)),
            ("review-report", str(self.project)),
            ("export-result", str(self.project)),
        ):
            result = self.run_cli(*command)
            self.assertEqual(result.returncode, 0, f"{command}: {result.stderr}")
        html = (self.project / "reports" / "review.html").read_text(encoding="utf-8")
        self.assertNotIn("renders/short-vertical.mp4", html)
        run_result = read_json(self.project / "results" / "run-result.json")
        self.assertEqual("verified", run_result["status"])

    def test_standalone_init_ignores_optional_caller_notes_and_exports_generic_result(self) -> None:
        result = self.run_cli("init", str(self.project))
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("buyer problem", (self.project / "content-brief.md").read_text(encoding="utf-8").lower())
        self.assertTrue((self.project / "recording-plan.md").exists())
        self.assertTrue((self.project / "context" / "README.md").exists())
        (self.project / "context" / "source-notes.json").write_text(
            json.dumps(
                {
                    "source_system": "AIOS",
                    "space_ref": "caller://not-a-runtime-dependency",
                    "handoff_id": "caller-owned-note",
                    "unrelated": "ignored by ACS",
                }
            ),
            encoding="utf-8",
        )
        self.assertFalse((self.project / "context" / "inbound-handoff.json").exists())
        self.assertEqual(
            "manual",
            next(
                route for route in read_json(self.project / "project.json")["delivery_intent"]["routes"]
                if route["channel"] == "youtube"
            )["delivery_mode"],
        )
        fixture_script = REPO_ROOT / "workspace" / "engine" / "scripts" / "create-fixture-media.py"
        result = subprocess.run(
            [sys.executable, str(fixture_script), str(self.project / "sources" / "source.mp4"), "--duration", "2"],
            cwd=REPO_ROOT,
            text=True,
            capture_output=True,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        commands = (
            ("inspect", str(self.project)),
            ("ingest-transcript", str(self.project), str(FIXTURE_TRANSCRIPT)),
            ("plan", str(self.project), "--approve", "--by", "automated-test"),
            ("render", str(self.project), "--kind", "all"),
            ("derive", str(self.project)),
            ("package", str(self.project)),
            ("verify", str(self.project)),
            ("review-report", str(self.project)),
            ("export-result", str(self.project)),
        )
        for command in commands:
            result = self.run_cli(*command)
            self.assertEqual(result.returncode, 0, f"{command}: {result.stderr}")
        run_result = read_json(self.project / "results" / "run-result.json")
        self.assertNotIn("handoff_id", run_result)
        self.assertNotIn("source_system", run_result)
        self.assertNotIn("space_ref", run_result)
        self.assertEqual({"youtube", "linkedin"}, set(run_result["enabled_routes"]))
        self.assertIn("tiktok", {item["channel"] for item in run_result["disabled_routes"]})
        self.assertTrue(all(len(item["sha256"]) == 64 for item in run_result["proof"]))
        publisher = read_json(self.project / "publish" / "publisher-handoff.json")
        manifest = read_json(self.project / "publish" / "manifest.json")
        self.assertEqual(manifest["manifest_id"], publisher["manifest_id"])
        self.assertEqual({"youtube", "linkedin"}, {route["channel"] for route in publisher["routes"]})
        youtube = next(route for route in publisher["routes"] if route["channel"] == "youtube")
        linkedin = next(route for route in publisher["routes"] if route["channel"] == "linkedin")
        self.assertEqual("manual", youtube["delivery_mode"])
        self.assertNotIn("scheduled_at", youtube)
        self.assertNotIn("timezone", youtube)
        self.assertEqual("manual", linkedin["delivery_mode"])
        self.assertNotIn("scheduled_at", linkedin)
        self.assertNotIn("timezone", linkedin)
        self.assertEqual("awaiting-separate-authorization", publisher["status"])
        self.assertTrue(publisher["not_posted"])
        self.assertFalse(publisher["external_posting"])
        self.assertEqual("publish/publisher-handoff.json", run_result["publisher_handoff"]["path"])
        self.assertEqual(
            sha256_file(self.project / "publish" / "publisher-handoff.json"),
            run_result["publisher_handoff"]["sha256"],
        )
        self.assertEqual("awaiting-separate-authorization", run_result["publisher_handoff"]["status"])
        self.assertFalse(run_result["publisher_handoff"]["external_posting"])

        publisher_path = self.project / "publish" / "publisher-handoff.json"
        original_publisher = publisher_path.read_text(encoding="utf-8")
        publisher["routes"][0]["scheduled_at"] = "2026-09-04T09:00:00"
        write_json(publisher_path, publisher)
        result = self.run_cli("verify", str(self.project))
        self.assertEqual(result.returncode, 2)
        self.assertIn("publisher handoff", result.stderr.lower())
        publisher_path.write_text(original_publisher, encoding="utf-8")

        project_path = self.project / "project.json"
        project = read_json(project_path)
        project["delivery_intent"]["routes"][0].update(
            {
                "delivery_mode": "scheduled",
                "scheduled_at": "2026-09-02T09:00:00",
                "timezone": "Europe/Copenhagen",
            }
        )
        write_json(project_path, project)
        result = self.run_cli("plan", str(self.project), "--approve", "--by", "automated-test")
        self.assertEqual(result.returncode, 0, result.stderr)
        result = self.run_cli("verify", str(self.project))
        self.assertEqual(result.returncode, 2)
        self.assertTrue(
            "approval" in result.stderr.lower() or "delivery intent" in result.stderr.lower(),
            result.stderr,
        )

        project["delivery_intent"]["routes"].append(
            {"channel": "tiktok", "delivery_mode": "scheduled", "scheduled_at": "2026-09-03T09:00:00", "timezone": "Europe/Copenhagen"}
        )
        write_json(project_path, project)
        result = self.run_cli("plan", str(self.project), "--approve", "--by", "automated-test")
        self.assertEqual(result.returncode, 0, result.stderr)
        for stale_derivative in (
            self.project / "derived" / "linkedin.md",
            self.project / "derived" / "derivative-record.json",
        ):
            stale_derivative.unlink(missing_ok=True)
        for command in (
            ("render", str(self.project), "--kind", "all"),
            ("derive", str(self.project)),
            ("package", str(self.project)),
        ):
            result = self.run_cli(*command)
            self.assertEqual(result.returncode, 0, f"{command}: {result.stderr}")
        manifest = read_json(self.project / "publish" / "manifest.json")
        self.assertNotIn("tiktok", {route["channel"] for route in manifest["routes"]})
