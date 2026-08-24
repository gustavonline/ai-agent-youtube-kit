from __future__ import annotations

import importlib.util
import os
import sys
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
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

    def test_loader_creates_resolved_override_cache_path(self) -> None:
        module = load_script()
        with tempfile.TemporaryDirectory() as temp:
            cache = Path(temp) / "whisper-cache"
            fake_whisper = SimpleNamespace(load_model=lambda *args, **kwargs: (args, kwargs))
            with patch.dict(
                os.environ,
                {"ACS_WHISPER_CACHE_DIR": str(cache)},
                clear=False,
            ), patch.dict(sys.modules, {"whisper": fake_whisper}):
                result = module.load_whisper_model("tiny", "auto", module.default_model_cache_dir())
            self.assertEqual(("tiny",), result[0])
            self.assertEqual(str(cache), result[1]["download_root"])
            self.assertTrue(cache.is_dir())
