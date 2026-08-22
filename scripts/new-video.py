#!/usr/bin/env python3
"""Compatibility wrapper for the canonical ACS content-example scaffold.

Use ``scripts/new-content-example.py`` or ``acs init`` for new work. The old
filename remains so existing local instructions fail safely into the current
Agentic Content System boundary instead of creating a second legacy layout.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from agentic_content_system.scaffold import scaffold_project  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Compatibility wrapper: scaffold an ACS example under examples/<slug>."
    )
    parser.add_argument("slug", help="Content example/workspace slug")
    parser.add_argument("--brand", help="Copy and validate a brand profile into the workspace")
    parser.add_argument("--force", action="store_true", help="Replace existing contract files")
    args = parser.parse_args()

    from agentic_content_system.scaffold import load_brand_profile

    workspace = scaffold_project(
        REPO_ROOT / "examples" / args.slug,
        brand=None if not args.brand else load_brand_profile(args.brand),
        force=args.force,
    )
    print(f"Scaffolded ACS example: {workspace}")
    print("Canonical helper: scripts/new-content-example.py")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
