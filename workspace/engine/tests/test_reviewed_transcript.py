from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from agentic_content_system.io import write_json
from agentic_content_system.project import ProjectContracts
from agentic_content_system.scaffold import default_brand, default_edit_plan, default_project
from agentic_content_system.transcript import (
    build_raw_record,
    build_reviewed_record,
    current_reviewed_segments,
    load_current_reviewed_transcript,
    normalize_json,
    plan_transcript_ranges,
)


class ReviewedTranscriptTests(unittest.TestCase):
    def make_contracts(self, root: Path) -> ProjectContracts:
        brand = default_brand("reviewed-test")
        project = default_project("reviewed-test", brand)
        plan = default_edit_plan("reviewed-test")
        source = root / "sources" / "source.mp4"
        source.parent.mkdir(parents=True)
        source.write_bytes(b"immutable source bytes")
        return ProjectContracts(root, brand, project, plan)

    def test_raw_words_survive_and_corrected_review_is_selected(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            contracts = self.make_contracts(root)
            normalized = normalize_json(
                {
                    "provider": "local-whisper",
                    "model": "tiny",
                    "segments": [
                        {
                            "start": 0,
                            "end": 1,
                            "text": "wrong raw wording",
                            "words": [
                                {"start": 0, "end": 0.4, "word": "wrong"},
                                {"start": 0.4, "end": 1, "word": "wording"},
                            ],
                        }
                    ],
                },
                "poor.json",
            )
            self.assertEqual("wrong", normalized["segments"][0]["words"][0]["text"])
            raw = build_raw_record(
                normalized,
                project_dir=root,
                project=contracts.project,
                input_path=root / "poor-whisper.json",
            )
            review_input = normalize_json(
                {"segments": [{"start": 0, "end": 1, "text": "correct reviewed wording"}]},
                "review.md",
            )
            reviewed = build_reviewed_record(
                review_input,
                raw_record=raw,
                project_dir=root,
                project=contracts.project,
                reviewer="owner",
                status="reviewed",
            )
            write_json(root / "transcripts" / "raw.json", raw)
            write_json(root / "transcripts" / "reviewed.json", reviewed)
            selected, _ = load_current_reviewed_transcript(contracts)
            self.assertEqual("correct reviewed wording", selected["segments"][0]["text"])
            self.assertNotIn("wrong raw wording", " ".join(item["text"] for item in selected["segments"]))

    def test_partial_coverage_stale_source_and_rejection_fail_closed(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            contracts = self.make_contracts(root)
            normalized = normalize_json(
                {"provider": "local-whisper", "segments": [{"start": 0, "end": 2, "text": "raw"}]},
                "raw.json",
            )
            raw = build_raw_record(
                normalized,
                project_dir=root,
                project=contracts.project,
                input_path=root / "raw-whisper.json",
            )
            write_json(root / "transcripts" / "raw.json", raw)
            partial = build_reviewed_record(
                normalize_json({"segments": [{"start": 0, "end": 1, "text": "corrected"}]}, "partial.json"),
                raw_record=raw,
                project_dir=root,
                project=contracts.project,
                reviewer="owner",
                status="partially_reviewed",
            )
            write_json(root / "transcripts" / "reviewed.json", partial)
            with self.assertRaises(Exception):
                current_reviewed_segments(
                    contracts,
                    [{"source": "sources/source.mp4", "start": 0, "end": 2}],
                )
            source = root / "sources" / "source.mp4"
            source.write_bytes(source.read_bytes() + b" changed")
            with self.assertRaises(Exception):
                load_current_reviewed_transcript(contracts)
            re_registered = build_reviewed_record(
                normalize_json({"segments": [{"start": 0, "end": 1, "text": "re-registered"}]}, "re-review.json"),
                raw_record=raw,
                project_dir=root,
                project=contracts.project,
                reviewer="owner",
                status="reviewed",
            )
            write_json(root / "transcripts" / "reviewed.json", re_registered)
            with self.assertRaises(Exception):
                load_current_reviewed_transcript(contracts)
            source.write_bytes(b"immutable source bytes")
            rejected = build_reviewed_record(
                normalize_json({"segments": [{"start": 0, "end": 1, "text": "ignored"}]}, "reject.json"),
                raw_record=raw,
                project_dir=root,
                project=contracts.project,
                reviewer="owner",
                status="rejected",
            )
            write_json(root / "transcripts" / "reviewed.json", rejected)
            with self.assertRaises(Exception):
                load_current_reviewed_transcript(contracts)

    def test_open_ended_edit_range_requires_full_raw_transcript_coverage(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            contracts = self.make_contracts(root)
            normalized = normalize_json(
                {"provider": "local-whisper", "segments": [{"start": 0, "end": 2, "text": "raw"}]},
                "raw.json",
            )
            raw = build_raw_record(
                normalized,
                project_dir=root,
                project=contracts.project,
                input_path=root / "raw-whisper.json",
            )
            write_json(root / "transcripts" / "raw.json", raw)
            contracts.edit_plan["short_form"]["segments"] = [
                {"source": "sources/source.mp4", "start": 0, "duration": 0}
            ]
            partial = build_reviewed_record(
                normalize_json({"segments": [{"start": 0, "end": 1, "text": "corrected"}]}, "partial.json"),
                raw_record=raw,
                project_dir=root,
                project=contracts.project,
                reviewer="owner",
                status="partially_reviewed",
            )
            write_json(root / "transcripts" / "reviewed.json", partial)
            with self.assertRaises(Exception):
                current_reviewed_segments(contracts, plan_transcript_ranges(contracts, "short"))
