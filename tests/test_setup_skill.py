from __future__ import annotations

import shutil
import subprocess
import sys
import unittest
from pathlib import Path

from agentic_content_system.io import read_json, write_json


REPO_ROOT = Path(__file__).resolve().parents[1]
SKILL_ROOT = REPO_ROOT / ".agents" / "skills" / "setup-content-system"


class SetupSkillTests(unittest.TestCase):
    def setUp(self) -> None:
        self.root = REPO_ROOT / "footage" / "test-runs" / "setup-skill"
        if self.root.exists():
            shutil.rmtree(self.root)
        self.root.mkdir(parents=True)

    def tearDown(self) -> None:
        if self.root.exists():
            shutil.rmtree(self.root)

    def run_cli(self, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, "-m", "agentic_content_system", *args],
            cwd=REPO_ROOT,
            text=True,
            capture_output=True,
        )

    def test_profile_copy_is_exact_and_routes_follow_enabled_policy(self) -> None:
        profile = REPO_ROOT / "channel" / "brand.json"
        result = self.run_cli("validate-profile", str(profile))
        self.assertEqual(result.returncode, 0, result.stderr)

        workspace = self.root / "generic-business"
        result = self.run_cli("init", str(workspace), "--brand", str(profile))
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(read_json(profile), read_json(workspace / "brand.json"))

        brand = read_json(workspace / "brand.json")
        project = read_json(workspace / "project.json")
        enabled = {channel["id"] for channel in brand["channels"] if channel["enabled"]}
        routes = {route["channel"] for route in project["delivery_intent"]["routes"]}
        self.assertEqual(enabled, routes)
        self.assertNotIn(
            "tiktok",
            {route["channel"] for route in project["delivery_intent"]["routes"]},
        )

    def test_disabled_delivery_default_is_rejected_before_workspace_write(self) -> None:
        profile = read_json(REPO_ROOT / "channel" / "brand.json")
        profile["delivery_defaults"]["routes"].append(
            {"channel": "tiktok", "delivery_mode": "manual"}
        )
        bad_profile = self.root / "bad-brand.json"
        write_json(bad_profile, profile)
        workspace = self.root / "must-not-be-created"

        result = self.run_cli("init", str(workspace), "--brand", str(bad_profile))
        self.assertEqual(result.returncode, 2)
        self.assertIn("disabled", result.stderr.lower())
        self.assertFalse(workspace.exists())

    def test_setup_skill_is_concise_and_metadata_is_invocable(self) -> None:
        files = {
            path.relative_to(SKILL_ROOT).as_posix()
            for path in SKILL_ROOT.rglob("*")
            if path.is_file()
        }
        self.assertEqual({"SKILL.md", "agents/openai.yaml"}, files)
        skill = (SKILL_ROOT / "SKILL.md").read_text(encoding="utf-8")
        self.assertTrue(skill.startswith("---\n"))
        self.assertIn("name: setup-content-system", skill)
        self.assertIn("validate-profile channel/brand.json", skill)
        self.assertIn("without creating a content workspace", skill)
        self.assertNotIn("TODO", skill)
        metadata = (SKILL_ROOT / "agents" / "openai.yaml").read_text(encoding="utf-8")
        self.assertIn('display_name: "Setup Content System"', metadata)
        self.assertIn('short_description: "Configure ACS before the first real video"', metadata)
        self.assertIn('Use $setup-content-system', metadata)


if __name__ == "__main__":
    unittest.main()
