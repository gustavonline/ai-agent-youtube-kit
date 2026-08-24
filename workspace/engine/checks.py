#!/usr/bin/env python3
"""Validate the canonical ACS shell, stale paths, and local proof contracts."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

from tracer import validate_ledger

ROOT = Path(__file__).resolve().parents[2]
CANONICAL_REPOSITORY = "onlinesourdough/Agentic-Content-System"
CANONICAL_REPOSITORY_URL = f"https://github.com/{CANONICAL_REPOSITORY}"

ALLOWED_ROOT_ENTRIES = {
    ".agents",
    ".github",
    ".gitignore",
    "AGENTS.md",
    "README.md",
    "docs",
    "examples",
    "pyproject.toml",
    "workspace",
}
IGNORED_ROOT_ARTIFACTS = {
    ".DS_Store",
    ".coverage",
    ".pytest_cache",
    "__pycache__",
    "build",
    "dist",
    "node_modules",
}
REQUIRED = (
    "AGENTS.md",
    "README.md",
    ".agents/skills/agentic-content-system/SKILL.md",
    ".agents/skills/setup-content-system/SKILL.md",
    ".agents/skills/setup-content-system/agents/openai.yaml",
    ".agents/skills/audit-content-system/SKILL.md",
    ".agents/skills/audit-content-system/agents/openai.yaml",
    "docs",
    "workspace/README.md",
    "workspace/channel/PROFILE.md",
    "workspace/channel/DESIGN.md",
    "workspace/channel/STYLE_GUIDE.md",
    "workspace/channel/brand.json",
    "workspace/content-formats/formats.json",
    "workspace/content-pipeline/ideas.md",
    "workspace/productions",
    "workspace/references/REFERENCES.md",
    "workspace/learning/PROJECT_MEMORY.md",
    "workspace/learning/MOTION_PHILOSOPHY.md",
    "workspace/history/runs.jsonl",
    "workspace/runs",
    "workspace/engine/README.md",
    "workspace/engine/checks.py",
    "workspace/engine/tracer.py",
    "workspace/engine/agentic_content_system",
    "workspace/engine/contracts/schemas",
    "workspace/engine/scripts",
    "workspace/engine/templates",
    "workspace/engine/tests",
    "workspace/engine/motion-adapters",
    "examples/README.md",
    "pyproject.toml",
    ".gitignore",
    ".github/workflows/ci.yml",
)
REQUIRED_PLACEHOLDERS = (
    "workspace/history/runs.jsonl",
    "workspace/runs/.gitkeep",
    "workspace/learning/.gitkeep",
    "workspace/references/.gitkeep",
    "workspace/productions/.gitkeep",
    "workspace/content-pipeline/selected/.gitkeep",
    "workspace/content-pipeline/published/.gitkeep",
)
FORBIDDEN_PRODUCT_LANGUAGE = (
    re.compile(r"aios[-_]handoff", re.IGNORECASE),
    re.compile(r"init[-_]from[-_]handoff", re.IGNORECASE),
    re.compile(r"agentic-videoeditor", re.IGNORECASE),
    re.compile(r"ai-agent-youtube-kit", re.IGNORECASE),
    re.compile(r"\bvideo[- ]editor\b", re.IGNORECASE),
    re.compile(r"\bACS(?: content)? project\b", re.IGNORECASE),
    re.compile(r"\bAgentic Content System project\b", re.IGNORECASE),
    re.compile(r"\bscaffold(?:s|ed|ing)?\s+(?:a|the)\s+project\b", re.IGNORECASE),
    re.compile(r"Project directory not found", re.IGNORECASE),
    re.compile(r"Validate all project contracts", re.IGNORECASE),
    re.compile(r"Generic standalone projects", re.IGNORECASE),
    re.compile(r"without a project", re.IGNORECASE),
    re.compile(r"Plan a project", re.IGNORECASE),
    re.compile(r"\bon this project\b", re.IGNORECASE),
    re.compile(r"project-local run interface", re.IGNORECASE),
)
STALE_PATH_PATTERNS = (
    re.compile(r"(?<![A-Za-z0-9_/])(?:agentic_content_system|contracts|engine|scripts|tests|templates|channel|content-formats|content-pipeline|assets|requirements|video-projects|footage)/"),
    re.compile(r"scripts/check-system-shell\\.py"),
    re.compile(r"workspace/workspace"),
    re.compile(r"tranworkspace"),
)
EXCLUDED_TEXT_PATHS = {
    Path("docs/SYSTEM_TEMPLATE_MAPPING.md"),
    Path("docs/REPOSITORY_IDENTITY.md"),
    Path("workspace/engine/checks.py"),
}
BINARY_SUFFIXES = {".aac", ".gif", ".jpeg", ".jpg", ".m4a", ".mkv", ".mov", ".mp3", ".mp4", ".png", ".pyc", ".wav", ".webm"}


def iter_text_files():
    for path in ROOT.rglob("*"):
        if not path.is_file():
            continue
        relative = path.relative_to(ROOT)
        if any(part in {".git", ".venv", "node_modules", "__pycache__", "build", "dist"} for part in relative.parts):
            continue
        if path.suffix.lower() in BINARY_SUFFIXES:
            continue
        yield path, relative


def _record_failure(failures: list[str], message: str) -> None:
    failures.append(message)


def check_shell(failures: list[str]) -> None:
    for entry in sorted(set(ALLOWED_ROOT_ENTRIES) - {path.name for path in ROOT.iterdir()}):
        _record_failure(failures, f"missing canonical root entry: {entry}")
    for path in ROOT.iterdir():
        if path.name in IGNORED_ROOT_ARTIFACTS or path.name.endswith(".egg-info") or path.name.startswith(".venv") or path.name == ".git":
            continue
        if path.name not in ALLOWED_ROOT_ENTRIES:
            _record_failure(failures, f"visible root entry is outside canonical shell: {path.name}")

    for relative in REQUIRED:
        if not (ROOT / relative).exists():
            _record_failure(failures, f"missing required System surface: {relative}")
    for relative in REQUIRED_PLACEHOLDERS:
        if not (ROOT / relative).exists():
            _record_failure(failures, f"missing required placeholder: {relative}")

    history = ROOT / "workspace/history/runs.jsonl"
    if history.exists() and not history.is_file():
        _record_failure(failures, "workspace/history/runs.jsonl must be a regular file")
    for child in (ROOT / "examples").iterdir():
        if child.is_dir():
            allowed = {"README.md", "proof.json"}
            actual = {item.name for item in child.iterdir()}
            if not actual.issubset(allowed):
                _record_failure(failures, f"curated example contains operational/generated files: {child.relative_to(ROOT)}")
            if actual != allowed:
                _record_failure(failures, f"curated example must contain README.md and proof.json: {child.relative_to(ROOT)}")
            proof = child / "proof.json"
            if proof.is_file():
                try:
                    data = json.loads(proof.read_text(encoding="utf-8"))
                except json.JSONDecodeError:
                    _record_failure(failures, f"curated example proof is invalid JSON: {child.relative_to(ROOT)}")
                else:
                    if data.get("curated") is not True:
                        _record_failure(failures, f"curated example proof must be deliberate: {child.relative_to(ROOT)}")


def check_identity_and_package(failures: list[str]) -> None:
    identity = ROOT / "docs/REPOSITORY_IDENTITY.md"
    metadata = ROOT / "pyproject.toml"
    identity_text = identity.read_text(encoding="utf-8") if identity.exists() else ""
    metadata_text = metadata.read_text(encoding="utf-8") if metadata.exists() else ""
    if CANONICAL_REPOSITORY not in identity_text:
        _record_failure(failures, "repository identity must name the canonical ACS repository")
    if CANONICAL_REPOSITORY_URL not in metadata_text:
        _record_failure(failures, "package metadata must use the canonical ACS repository URL")
    if f"{CANONICAL_REPOSITORY_URL}/issues" not in metadata_text:
        _record_failure(failures, "package metadata must use the canonical ACS issue URL")
    if not re.search(r"historical.*redirect", identity_text, re.IGNORECASE | re.DOTALL):
        _record_failure(failures, "historical repository paths must be clearly marked as redirects")
    if 'where = ["workspace/engine"]' not in metadata_text:
        _record_failure(failures, "package discovery must target workspace/engine")
    if 'dependencies = []' not in metadata_text:
        _record_failure(failures, "the standalone package must declare no runtime dependency")
    for script in ("acs = \"agentic_content_system.cli:main\"", "agentic-content-system = \"agentic_content_system.cli:main\""):
        if script not in metadata_text:
            _record_failure(failures, f"missing public console script: {script}")


def check_skills(failures: list[str]) -> None:
    checks = (
        ("agentic-content-system", "name: agentic-content-system", "init <workspace>"),
        ("setup-content-system", "name: setup-content-system", "validate-profile"),
        ("audit-content-system", "name: audit-content-system", "strictly read-only"),
    )
    for name, marker, required_text in checks:
        path = ROOT / ".agents/skills" / name / "SKILL.md"
        text = path.read_text(encoding="utf-8") if path.exists() else ""
        if not text.startswith("---\n") or f"\n{marker}\n" not in text:
            _record_failure(failures, f"{name} skill has invalid frontmatter")
        if required_text not in text:
            _record_failure(failures, f"{name} skill lacks required contract text")
    primary = (ROOT / ".agents/skills/agentic-content-system/SKILL.md").read_text(encoding="utf-8")
    normalized_primary = " ".join(primary.split())
    workflow = (ROOT / "docs/WORKFLOW.md").read_text(encoding="utf-8")
    primary_obligations = (
        "Before planning an ordinary repeat or explicit recovery",
        "workspace/history/runs.jsonl",
        "workspace/runs/<run-id>/run.json",
        "Choose `predecessor` for an ordinary repeat",
        "one explicit `--recover <run-id>`",
        "promote-example",
        "optional and",
        "Never promote automatically",
    )
    missing = [marker for marker in primary_obligations if marker not in normalized_primary]
    if missing:
        _record_failure(failures, f"primary ACS skill lacks lifecycle obligations: {', '.join(missing)}")
    if "one success or failure" not in workflow or "promote-example" not in workflow:
        _record_failure(failures, "workflow must describe the local run relation and deliberate example promotion")


def check_text(failures: list[str]) -> None:
    for path, relative in iter_text_files():
        if relative in EXCLUDED_TEXT_PATHS:
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        for pattern in STALE_PATH_PATTERNS:
            if pattern.search(text):
                _record_failure(failures, f"stale path {pattern.pattern!r} in {relative}")
        product_surface = relative == Path("AGENTS.md") or relative == Path("README.md") or relative.parts[:1] in {
            ("docs",), (".agents",), ("examples",)
        }
        if product_surface and relative != Path("docs/EDITOR_ENGINE_DECISION.md"):
            for pattern in FORBIDDEN_PRODUCT_LANGUAGE:
                if pattern.search(text):
                    _record_failure(failures, f"stale product language {pattern.pattern!r} in {relative}")


def check_runtime_dependency(failures: list[str]) -> None:
    for path, relative in iter_text_files():
        if path.suffix.lower() not in {".py", ".ps1", ".sh", ".toml", ".yml", ".yaml"}:
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        if re.search(r"(?im)^\s*(?:from|import)\s+(?:aios|system_template)(?:\b|\\.)", text):
            _record_failure(failures, f"AIOS/System Template runtime import in {relative}")
    tracer_text = (ROOT / "workspace/engine/tracer.py").read_text(encoding="utf-8")
    if re.search(r"(?i)(?:import|from|pip install|dependencies).*(?:aios|system-template|system_template)", tracer_text):
        _record_failure(failures, "tracer has an AIOS/System Template runtime dependency")


def check_ledger(failures: list[str]) -> None:
    for message in validate_ledger(ROOT):
        _record_failure(failures, message)


def main() -> int:
    failures: list[str] = []
    check_shell(failures)
    check_identity_and_package(failures)
    check_skills(failures)
    check_text(failures)
    check_runtime_dependency(failures)
    check_ledger(failures)
    if failures:
        for failure in failures:
            print(f"FAIL: {failure}", file=sys.stderr)
        return 1
    print("ACS System shell, stale-path, ledger, and no-runtime-dependency checks: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
