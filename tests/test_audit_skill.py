from __future__ import annotations

import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SKILL_ROOT = REPO_ROOT / ".agents" / "skills" / "audit-content-system"


class AuditSkillTests(unittest.TestCase):
    def test_skill_has_only_the_required_files(self) -> None:
        files = {
            path.relative_to(SKILL_ROOT).as_posix()
            for path in SKILL_ROOT.rglob("*")
            if path.is_file()
        }
        self.assertEqual({"SKILL.md", "agents/openai.yaml"}, files)

    def test_skill_frontmatter_and_contract_are_complete(self) -> None:
        text = (SKILL_ROOT / "SKILL.md").read_text(encoding="utf-8")
        self.assertTrue(text.startswith("---\n"))
        _, frontmatter, body = text.split("---\n", 2)
        keys = {
            line.split(":", 1)[0]
            for line in frontmatter.splitlines()
            if line.strip()
        }
        self.assertEqual({"name", "description"}, keys)
        self.assertIn("name: audit-content-system", frontmatter)
        for trigger in ("audit", "health-check", "reconcile", "drift", "readiness"):
            self.assertIn(trigger, frontmatter)
        for required in (
            "strictly read-only",
            "repository",
            "one named workspace",
            "Never silently scan every client or workspace",
            "acs verify",
            "acs review-report",
            "acs export-result",
            "not audit-safe",
            "external_posting: false",
            "not_posted: true",
            "Result: PASS | FAIL | BLOCKED",
            "missing authority, access, or required input is `BLOCKED`",
        ):
            self.assertIn(required, body)
        self.assertNotIn("TODO", text)
        self.assertNotIn("file:" + "///", text)
        self.assertNotIn("private/tmp", text)

    def test_openai_metadata_is_exact_and_invocable(self) -> None:
        metadata = (SKILL_ROOT / "agents" / "openai.yaml").read_text(encoding="utf-8")
        self.assertEqual(
            """interface:
  display_name: "Audit Content System"
  short_description: "Audit ACS health, truth, and workspace proof"
  default_prompt: "Use $audit-content-system to audit this Agentic Content System and report evidence, gaps, and the smallest next action."
""",
            metadata,
        )

    def test_repository_discovery_and_identity_route_are_present(self) -> None:
        agents = (REPO_ROOT / "AGENTS.md").read_text(encoding="utf-8")
        readme = (REPO_ROOT / "README.md").read_text(encoding="utf-8")
        identity = (REPO_ROOT / "docs" / "REPOSITORY_IDENTITY.md").read_text(encoding="utf-8")
        pyproject = (REPO_ROOT / "pyproject.toml").read_text(encoding="utf-8")
        for text in (agents, readme):
            self.assertIn(".agents/skills/audit-content-system/SKILL.md", text)
        self.assertIn("read-only", agents.lower())
        self.assertIn("onlinesourdough/Agentic-Content-System", identity)
        self.assertIn("https://github.com/onlinesourdough/Agentic-Content-System", pyproject)
        self.assertIn("https://github.com/onlinesourdough/Agentic-Content-System/issues", pyproject)
        self.assertIn("historical", identity.lower())
        self.assertIn("redirect", identity.lower())
        self.assertNotIn("intended canonical", identity.lower())
        historical_editor_slug = "Agentic-" + "videoeditor"
        self.assertNotIn("https://github.com/onlinesourdough/" + historical_editor_slug, pyproject)
        self.assertNotIn("https://github.com/gustavonline/" + historical_editor_slug, pyproject)
        self.assertIn("onlinesourdough/" + historical_editor_slug, identity)
        self.assertIn("gustavonline/" + historical_editor_slug, identity)

    def test_audit_instructions_prohibit_mutating_lifecycle_commands(self) -> None:
        text = (SKILL_ROOT / "SKILL.md").read_text(encoding="utf-8")
        lower = text.lower()
        for operation in (
            "repair",
            "edit",
            "render",
            "derive",
            "package",
            "verify",
            "create a review report",
            "export a result",
            "clean",
            "publish",
            "transfer",
        ):
            self.assertIn(operation, lower)
        self.assertIn("do not", lower)
        self.assertIn("leave all inputs and generated artifacts", lower)
        self.assertIn("unchanged", lower)


if __name__ == "__main__":
    unittest.main()
