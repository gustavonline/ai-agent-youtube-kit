#!/usr/bin/env python3
"""Create the standard file scaffold for a new video project."""

from __future__ import annotations

import argparse
import re
import sys
from datetime import date
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent
TEMPLATE_MAP = {
    "video-brief.md": "video-brief.md",
    "cut-plan.md": "cut-plan.md",
    "packaging-review.md": "packaging-review.md",
    "final-review.md": "final-review.md",
    "project.md": "project.md",
}


def slugify(value: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return slug or "new-video"


def copy_template(template_name: str, out_path: Path, slug: str, force: bool) -> str:
    if out_path.exists() and not force:
        return "exists"
    text = (REPO_ROOT / "templates" / template_name).read_text(encoding="utf-8")
    text = text.replace("**Slug:** <fill>", f"**Slug:** {slug}")
    text = text.replace("**Video slug:** <fill>", f"**Video slug:** {slug}")
    text = text.replace("**Started:** <fill>", f"**Started:** {date.today().isoformat()}")
    text = text.replace("**Reviewed:** <fill>", f"**Reviewed:** {date.today().isoformat()}")
    out_path.write_text(text, encoding="utf-8")
    return "created"


def main() -> int:
    parser = argparse.ArgumentParser(description="Scaffold footage/<slug>/edit files.")
    parser.add_argument("slug", help="Video slug or title.")
    parser.add_argument("--force", action="store_true", help="Overwrite existing scaffold files.")
    args = parser.parse_args()

    slug = slugify(args.slug)
    footage_dir = REPO_ROOT / "footage" / slug
    edit_dir = footage_dir / "edit"
    edit_dir.mkdir(parents=True, exist_ok=True)
    (edit_dir / "animations").mkdir(exist_ok=True)

    statuses = {}
    for output_name, template_name in TEMPLATE_MAP.items():
        statuses[output_name] = copy_template(template_name, edit_dir / output_name, slug, args.force)

    print(f"Scaffolded: {footage_dir}")
    for name, status in statuses.items():
        print(f"- edit/{name}: {status}")
    print()
    print("Next steps:")
    print(f"1. Add source clips to footage/{slug}/")
    print(f"2. Fill footage/{slug}/edit/video-brief.md")
    print(f"3. Transcribe with: .venv/bin/python scripts/transcribe-local-whisper.py footage/{slug} --model large --pack")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
