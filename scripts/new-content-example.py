#!/usr/bin/env python3
"""Scaffold an ACS content example/workspace under examples/<slug>."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from agentic_content_system.scaffold import scaffold_project


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Scaffold a local Agentic Content System example under examples/<slug>."
    )
    parser.add_argument("slug", help="Example/workspace slug")
    parser.add_argument("--example", choices=["gustav"], help="Apply an explicit channel example")
    parser.add_argument("--force", action="store_true", help="Replace existing contract files")
    args = parser.parse_args()
    project = scaffold_project(REPO_ROOT / "examples" / args.slug, example=args.example, force=args.force)
    print(f"Scaffolded ACS example: {project}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
