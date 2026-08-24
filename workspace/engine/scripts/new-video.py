#!/usr/bin/env python3
"""Compatibility wrapper for the canonical ACS content-example scaffold.

Use ``workspace/engine/scripts/new-content-example.py`` or ``acs init`` for new work. The old
filename remains so existing local instructions fail safely into the current
Agentic Content System boundary instead of creating a second legacy layout.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[3]
ENGINE_ROOT = Path(__file__).resolve().parents[1]
if str(ENGINE_ROOT) not in sys.path:
    sys.path.insert(0, str(ENGINE_ROOT))

from agentic_content_system.scaffold import load_brand_profile, scaffold_project  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Compatibility wrapper: scaffold an ACS production under workspace/productions/<slug>."
    )
    parser.add_argument("slug", help="Content production/workspace slug")
    parser.add_argument("--brand", help="Copy and validate a brand profile into the workspace")
    parser.add_argument("--force", action="store_true", help="Replace existing contract files")
    args = parser.parse_args()

    workspace = scaffold_project(
        REPO_ROOT / "workspace" / "productions" / args.slug,
        brand=None if not args.brand else load_brand_profile(args.brand),
        force=args.force,
    )
    print(f"Scaffolded ACS production: {workspace}")
    print("Canonical helper: workspace/engine/scripts/new-content-example.py")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
