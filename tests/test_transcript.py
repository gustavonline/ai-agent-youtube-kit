from __future__ import annotations

import json
import unittest
from pathlib import Path

from agentic_content_system.transcript import load_and_normalize


class TranscriptTests(unittest.TestCase):
    def test_whisper_word_json_is_accepted(self) -> None:
        path = Path(__file__).parent / "fixtures" / "whisper.json"
        path.write_text(
            json.dumps(
                {
                    "text": "hello world",
                    "words": [
                        {"text": "hello", "start": 0, "end": 0.5},
                        {"text": "world", "start": 0.5, "end": 1},
                    ],
                }
            ),
            encoding="utf-8",
        )
        try:
            normalized = load_and_normalize(path)
        finally:
            path.unlink(missing_ok=True)
        self.assertEqual("1.0", normalized["schema_version"])
        self.assertEqual("hello world", normalized["segments"][0]["text"])

    def test_timestamped_markdown_is_accepted(self) -> None:
        path = Path(__file__).parent / "fixtures" / "transcript.md"
        path.write_text("00:00-00:02: Promise and proof\n", encoding="utf-8")
        try:
            normalized = load_and_normalize(path)
        finally:
            path.unlink(missing_ok=True)
        self.assertEqual(2.0, normalized["segments"][0]["end"])

    def test_standard_srt_timestamps_are_preserved(self) -> None:
        normalized = load_and_normalize(Path(__file__).parent / "fixtures" / "transcript.srt")
        self.assertEqual(0.0, normalized["segments"][0]["start"])
        self.assertEqual(1.5, normalized["segments"][0]["end"])
        self.assertEqual(3.0, normalized["segments"][1]["end"])

    def test_standard_vtt_timestamps_and_settings_are_preserved(self) -> None:
        normalized = load_and_normalize(Path(__file__).parent / "fixtures" / "transcript.vtt")
        self.assertEqual(1.25, normalized["segments"][0]["end"])
        self.assertEqual(2.5, normalized["segments"][1]["end"])

    def test_malformed_subtitle_does_not_fallback_to_untimed_text(self) -> None:
        path = Path(__file__).parent / "fixtures" / "malformed.srt"
        path.write_text("1\nnot a timing line\ntext\n", encoding="utf-8")
        try:
            with self.assertRaises(Exception):
                load_and_normalize(path)
        finally:
            path.unlink(missing_ok=True)
