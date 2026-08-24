from __future__ import annotations

import importlib.util
import os
import unittest
from pathlib import Path
from unittest.mock import patch


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "transcribe-local-whisper.py"


def load_script():
    spec = importlib.util.spec_from_file_location("acs_local_whisper", SCRIPT)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot load {SCRIPT}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class WhisperCacheTests(unittest.TestCase):
    def test_default_cache_is_below_engine_and_override_is_respected(self) -> None:
        module = load_script()
        self.assertEqual(
            module.REPO_ROOT / "workspace" / "engine" / ".cache" / "whisper",
            module.default_model_cache_dir(),
        )
        with patch.dict(os.environ, {"ACS_WHISPER_CACHE_DIR": "~/acs-test-whisper"}, clear=False):
            self.assertEqual(Path.home() / "acs-test-whisper", module.default_model_cache_dir())

