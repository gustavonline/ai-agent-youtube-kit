#!/usr/bin/env python3
"""Scaffold an ACS content production under workspace/productions/<slug>."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
ENGINE_ROOT = Path(__file__).resolve().parents[1]
if str(ENGINE_ROOT) not in sys.path:
    sys.path.insert(0, str(ENGINE_ROOT))

from agentic_content_system.scaffold import load_brand_profile, scaffold_project


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Scaffold a local Agentic Content System production under workspace/productions/<slug>."
    )
    parser.add_argument("slug", help="Production/workspace slug")
    parser.add_argument("--brand", help="Copy and validate a brand profile into the workspace")
    parser.add_argument("--force", action="store_true", help="Replace existing contract files")
    args = parser.parse_args()
    project = scaffold_project(
        REPO_ROOT / "workspace" / "productions" / args.slug,
        brand=None if not args.brand else load_brand_profile(args.brand),
        force=args.force,
    )
    print(f"Scaffolded ACS production: {project}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
