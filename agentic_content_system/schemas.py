"""Load the tracked contract schemas shipped with the repository."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


SOURCE_SCHEMA_DIR = Path(__file__).resolve().parent.parent / "contracts" / "schemas"
PACKAGED_SCHEMA_DIR = Path(__file__).resolve().parent / "data" / "schemas"


def load_schema(name: str) -> dict[str, Any]:
    source_path = SOURCE_SCHEMA_DIR / f"{name}.schema.json"
    path = source_path if source_path.exists() else PACKAGED_SCHEMA_DIR / f"{name}.schema.json"
    return json.loads(path.read_text(encoding="utf-8"))
