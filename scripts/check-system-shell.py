#!/usr/bin/env python3
"""Validate the public ACS System shell and its naming guardrails."""

from __future__ import annotations

import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
REQUIRED = (
    "AGENTS.md",
    "README.md",
    ".agents/skills/agentic-content-system/SKILL.md",
    "docs",
    "engine",
    "examples",
    "scripts",
    "tests",
    ".github/workflows",
)
PUBLIC_SURFACES = (
    "AGENTS.md",
    "README.md",
    "SETUP.md",
    "DESIGN.md",
    "MOTION_PHILOSOPHY.md",
    ".agents/skills/agentic-content-system/SKILL.md",
    "docs",
    "engine",
    "examples",
    "pyproject.toml",
    ".github/workflows",
    "scripts/check-system-shell.py",
    "scripts/new-content-example.py",
    "agentic_content_system/cli.py",
)
FORBIDDEN = (
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
ALLOWLIST = {
    "pyproject.toml",  # canonical GitHub destination is metadata, not product identity
    "docs/REPOSITORY_IDENTITY.md",  # records the owner-authorized migration boundary
    "docs/EDITOR_ENGINE_DECISION.md",  # cites a dated external candidate repository
    "scripts/check-system-shell.py",  # the guard must contain its own patterns
}


def iter_text_files(surface: Path):
    if surface.is_file():
        yield surface
        return
    for path in surface.rglob("*"):
        if not path.is_file() or ".venv" in path.parts:
            continue
        if path.suffix.lower() in {".mp4", ".webm", ".wav", ".png", ".jpg", ".jpeg", ".gif", ".pyc"}:
            continue
        yield path


def main() -> int:
    failures: list[str] = []
    for relative in REQUIRED:
        if not (ROOT / relative).exists():
            failures.append(f"missing required System surface: {relative}")

    skill = ROOT / ".agents/skills/agentic-content-system/SKILL.md"
    skill_text = skill.read_text(encoding="utf-8") if skill.exists() else ""
    if not skill_text.startswith("---\n") or "\nname: agentic-content-system\n" not in skill_text:
        failures.append("project-local ACS skill must begin with valid YAML frontmatter")
    if not (ROOT / "examples/gustav/README.md").exists():
        failures.append("examples/gustav must provide a visible self-contained boundary")

    for relative in PUBLIC_SURFACES:
        surface = ROOT / relative
        for path in iter_text_files(surface):
            rel = path.relative_to(ROOT).as_posix()
            if rel in ALLOWLIST:
                continue
            text = path.read_text(encoding="utf-8", errors="replace")
            for pattern in FORBIDDEN:
                if pattern.search(text):
                    failures.append(f"stale product language {pattern.pattern!r} in {rel}")

    if failures:
        for failure in failures:
            print(f"FAIL: {failure}", file=sys.stderr)
        return 1
    print("ACS System shell and stale-name guard: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
