#!/usr/bin/env python3
"""Validate the canonical ACS shell, stale paths, and local proof contracts."""

from __future__ import annotations

import json
import os
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
    ".agents/skills/README.md",
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
ACTIVE_VIDEO_ROUTE_SURFACES = (
    Path("docs/WORKFLOW.md"),
    Path("docs/PROMPTS.md"),
    Path("docs/CODEX_PLUGIN_SETUP.md"),
    Path("docs/ADAPTERS.md"),
    Path("docs/BRANDING.md"),
    Path("docs/LEARNING.md"),
    Path("docs/CLI.md"),
    Path("docs/ARCHITECTURE.md"),
    Path("docs/EDITOR_ENGINE_DECISION.md"),
    Path("workspace/engine/README.md"),
    Path("workspace/engine/motion-adapters/README.md"),
    Path("workspace/learning/MOTION_PHILOSOPHY.md"),
    Path("workspace/content-formats/formats.json"),
    Path("workspace/engine/templates/video-brief.md"),
    Path("workspace/channel/assets/README.md"),
)
ACTIVE_VIDEO_ROUTE_MARKERS = ("FreeCut", "one normal", "migration/recovery")
FREECUT_RETURN_SURFACES = (
    Path(".agents/skills/agentic-content-system/SKILL.md"),
    Path(".agents/skills/freecut-studio/SKILL.md"),
    Path("README.md"),
    Path("docs/WORKFLOW.md"),
    Path("docs/QUICKSTART.md"),
    Path("docs/CLI.md"),
    Path("docs/ADAPTERS.md"),
)
FREECUT_RETURN_MARKERS = (
    "sources/",
    "project.json",
    "edit-plan.json",
    "acs inspect",
    "acs render",
    "acs derive",
    "acs package",
    "acs verify",
    "acs review-report",
    "acs export-result",
    "acs semantic-eval",
    "acs import-adapter",
    "must never use",
    "a FreeCut manifest, reference JSON, schema, bridge",
)
FORBIDDEN_ACTIVE_VIDEO_ROUTE_PATTERNS = (
    re.compile(r"##\s+Optional motion adapter", re.IGNORECASE),
    re.compile(r"HyperFrames can supply", re.IGNORECASE),
    re.compile(r"HyperFrames is an optional motion adapter", re.IGNORECASE),
    re.compile(r"existing HyperFrames projects remain useful", re.IGNORECASE),
    re.compile(r"Full editors,\s*HyperFrames.*optional\s+adapters", re.IGNORECASE | re.DOTALL),
    re.compile(r"^\s*-\s*HyperFrames:\s*$", re.IGNORECASE | re.MULTILINE),
    re.compile(r"Timeline Studio,\s*OpenReelio.*documented seams", re.IGNORECASE | re.DOTALL),
    re.compile(r"fonts for deterministic HyperFrames renders", re.IGNORECASE),
)


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


def _skill_frontmatter_name(path: Path) -> str | None:
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        return None
    sections = text.split("---\n", 2)
    if len(sections) != 3:
        return None
    names = re.findall(r"(?m)^name:\s*([a-z0-9][a-z0-9-]*)\s*$", sections[1])
    return names[0] if len(names) == 1 else None


def check_skill_shelf(failures: list[str], root: Path = ROOT) -> None:
    skills_root = root / ".agents/skills"
    if skills_root.is_symlink():
        _record_failure(failures, "repository-local skill shelf must not be a symlink")
        return
    if not skills_root.is_dir():
        _record_failure(failures, "missing repository-local skill shelf: .agents/skills")
        return

    for current, directory_names, file_names in os.walk(skills_root, followlinks=False):
        current_path = Path(current)
        for name in [*directory_names, *file_names]:
            path = current_path / name
            if path.is_symlink():
                relative = path.relative_to(root).as_posix()
                _record_failure(failures, f"skill-tree symlink is not allowed: {relative}")
        for name in file_names:
            if name != "SKILL.md":
                continue
            relative = (current_path / name).relative_to(skills_root)
            if len(relative.parts) != 2:
                _record_failure(
                    failures,
                    f"nested SKILL.md is not allowed: {(skills_root / relative).relative_to(root).as_posix()}",
                )

    skill_names: list[str] = []
    for entry in sorted(skills_root.iterdir(), key=lambda path: path.name):
        if entry.name == "README.md":
            continue
        if entry.is_symlink():
            continue
        if not entry.is_dir():
            _record_failure(failures, f"unexpected file in repository-local skill shelf: {entry.name}")
            continue
        skill_path = entry / "SKILL.md"
        if skill_path.is_symlink() or not skill_path.is_file():
            _record_failure(failures, f"skill folder lacks a direct regular SKILL.md: {entry.name}")
            continue
        skill_names.append(entry.name)
        frontmatter_name = _skill_frontmatter_name(skill_path)
        if frontmatter_name is None:
            _record_failure(failures, f"{entry.name} skill has invalid name frontmatter")
        elif frontmatter_name != entry.name:
            _record_failure(
                failures,
                f"skill folder/frontmatter name mismatch: {entry.name} != {frontmatter_name}",
            )

    index_path = skills_root / "README.md"
    if index_path.is_symlink() or not index_path.is_file():
        _record_failure(failures, "missing regular repository-local skill index: .agents/skills/README.md")
        return
    index_text = index_path.read_text(encoding="utf-8")
    documented_names: list[str] = []
    for target in re.findall(r"\]\(([^)]+)\)", index_text):
        target = target.split("#", 1)[0]
        if target.startswith(".agents/skills/"):
            target = target.removeprefix(".agents/skills/")
        parts = target.split("/")
        if len(parts) == 2 and parts[1] == "SKILL.md":
            documented_names.append(parts[0])

    for name in skill_names:
        count = documented_names.count(name)
        if count != 1:
            _record_failure(failures, f"skill index must document {name}/SKILL.md exactly once")
    for name in sorted(set(documented_names) - set(skill_names)):
        _record_failure(failures, f"skill index documents unknown direct skill: {name}/SKILL.md")


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
    allowed_dependency_declarations = (
        'dependencies = []',
        'dependencies = [\n  "Pillow>=10.0",\n]',
    )
    if not any(declaration in metadata_text for declaration in allowed_dependency_declarations):
        _record_failure(failures, "the standalone package may declare only the justified Pillow caption fallback dependency")
    for script in ("acs = \"agentic_content_system.cli:main\"", "agentic-content-system = \"agentic_content_system.cli:main\""):
        if script not in metadata_text:
            _record_failure(failures, f"missing public console script: {script}")


def check_skills(failures: list[str]) -> None:
    check_skill_shelf(failures)
    checks = (
        ("agentic-content-system", "init <workspace>"),
        ("setup-content-system", "validate-profile"),
        ("audit-content-system", "strictly read-only"),
    )
    for name, required_text in checks:
        path = ROOT / ".agents/skills" / name / "SKILL.md"
        text = path.read_text(encoding="utf-8") if path.exists() else ""
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

    freecut = (ROOT / ".agents/skills/freecut-studio/SKILL.md").read_text(encoding="utf-8")
    normalized_freecut = " ".join(freecut.split())
    freecut_truth_markers = (
        "current owner-facing agent session",
        "AIOS may be that session when present",
        "independently invocable",
        "Physical Linux/amd64",
        "remain unverified",
        "current eight public findings",
        "claim of zero vulnerabilities",
    )
    missing = [marker for marker in freecut_truth_markers if marker not in normalized_freecut]
    if missing:
        _record_failure(failures, f"FreeCut skill lacks caller/evidence truth: {', '.join(missing)}")
    for stale_claim in (
        "AIOS remains the owner-facing session",
        "Node 22.23.2 on Linux/amd64",
        "Both safe installs",
    ):
        if stale_claim in normalized_freecut:
            _record_failure(failures, f"FreeCut skill retains stale caller/Linux claim: {stale_claim}")


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


def check_active_video_route(failures: list[str]) -> None:
    for relative in ACTIVE_VIDEO_ROUTE_SURFACES:
        path = ROOT / relative
        if not path.is_file():
            _record_failure(failures, f"missing active video-route surface: {relative}")
            continue
        text = path.read_text(encoding="utf-8")
        for marker in ACTIVE_VIDEO_ROUTE_MARKERS:
            if marker not in text:
                _record_failure(failures, f"active video-route surface lacks {marker!r}: {relative}")
        if relative == Path("docs/EDITOR_ENGINE_DECISION.md"):
            for marker in (
                "## Historical adapter seams (not active routing)",
                "## Historical revisit triggers (not active routing)",
            ):
                if marker not in text:
                    _record_failure(failures, f"editor decision lacks historical routing label: {marker}")
            continue
        for pattern in FORBIDDEN_ACTIVE_VIDEO_ROUTE_PATTERNS:
            if pattern.search(text):
                _record_failure(failures, f"parallel video-route language {pattern.pattern!r} in {relative}")

    for relative in FREECUT_RETURN_SURFACES:
        path = ROOT / relative
        if not path.is_file():
            _record_failure(failures, f"missing normal FreeCut-return surface: {relative}")
            continue
        text = " ".join(path.read_text(encoding="utf-8").split())
        for marker in FREECUT_RETURN_MARKERS:
            if marker not in text:
                _record_failure(failures, f"FreeCut-return surface lacks {marker!r}: {relative}")

    scaffold = (ROOT / "workspace/engine/agentic_content_system/scaffold.py").read_text(encoding="utf-8")
    for marker in (
        "Legacy migration/recovery adapter imports",
        "must never be used for a ",
        "normal FreeCut export",
        "`sources/`",
        "`project.json`",
    ):
        if marker not in scaffold:
            _record_failure(failures, f"scaffold adapter note lacks FreeCut-return boundary: {marker!r}")


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
    check_active_video_route(failures)
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
