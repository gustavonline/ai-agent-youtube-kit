from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from agentic_content_system import adapters, captions, media
from agentic_content_system.creative import require_creative_direction
from agentic_content_system.derive import derive_project
from agentic_content_system.errors import ACSUserError
from agentic_content_system.io import read_json, sha256_file, write_json
from agentic_content_system.project import ProjectContracts, current_approval_hash
from agentic_content_system.scaffold import default_brand, default_edit_plan, default_project
from agentic_content_system.transcript import (
    build_raw_record,
    build_reviewed_record,
    normalize_json,
    plan_transcript_ranges,
)


FIXTURE_ADAPTER_MANIFEST = Path(__file__).resolve().parent / "fixtures" / "adapter-manifest.json"


class ProductionLoopTests(unittest.TestCase):
    def make_contracts(self, root: Path) -> ProjectContracts:
        brand = default_brand("production-loop-test")
        project = default_project("production-loop-test", brand)
        plan = default_edit_plan("production-loop-test")
        source = root / "sources" / "source.mp4"
        source.parent.mkdir(parents=True, exist_ok=True)
        source.write_bytes(b"source bytes")
        return ProjectContracts(root, brand, project, plan)

    def add_reviewed_transcript(
        self,
        contracts: ProjectContracts,
        *,
        raw_segments: list[dict],
        reviewed_segments: list[dict],
    ) -> None:
        raw = build_raw_record(
            normalize_json(
                {"provider": "local-whisper", "model": "tiny", "segments": raw_segments},
                "raw-whisper.json",
            ),
            project_dir=contracts.directory,
            project=contracts.project,
            input_path=contracts.directory / "raw-whisper.json",
        )
        reviewed = build_reviewed_record(
            normalize_json({"segments": reviewed_segments}, "reviewed.json"),
            raw_record=raw,
            project_dir=contracts.directory,
            project=contracts.project,
            reviewer="owner",
            status="reviewed",
        )
        write_json(contracts.directory / "transcripts" / "raw.json", raw)
        write_json(contracts.directory / "transcripts" / "reviewed.json", reviewed)

    def approve(self, contracts: ProjectContracts) -> None:
        contracts.edit_plan["approval"].update(
            {
                "status": "approved",
                "approved_by": "owner",
                "approved_at": "2026-08-24T00:00:00+00:00",
                "approval_revision": 1,
                "approval_hash": "",
            }
        )
        contracts.edit_plan["approval"]["approval_hash"] = current_approval_hash(contracts)

    def test_caption_cues_map_ordered_segments_to_output_time(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            contracts = self.make_contracts(root)
            contracts.edit_plan["long_form"]["segments"] = [
                {"source": "sources/source.mp4", "start": 1, "duration": 2},
                {"source": "sources/source.mp4", "start": 10, "duration": 2},
            ]
            contracts.edit_plan["captions"] = {
                "long": {"enabled": True, "format": "srt", "max_words": 20}
            }
            self.add_reviewed_transcript(
                contracts,
                raw_segments=[
                    {
                        "start": 1,
                        "end": 3,
                        "text": "raw first phrase",
                        "words": [
                            {"start": 1.1, "end": 1.4, "text": "raw"},
                            {"start": 1.5, "end": 1.8, "text": "first"},
                        ],
                    },
                    {
                        "start": 10,
                        "end": 12,
                        "text": "raw second phrase",
                        "words": [
                            {"start": 10.2, "end": 10.5, "text": "second"},
                            {"start": 10.6, "end": 10.9, "text": "phrase"},
                        ],
                    },
                ],
                reviewed_segments=[
                    {
                        "start": 1,
                        "end": 3,
                        "text": "corrected first phrase",
                        "words": [
                            {"start": 1.1, "end": 1.4, "text": "corrected"},
                            {"start": 1.5, "end": 1.8, "text": "first"},
                        ],
                    },
                    {
                        "start": 10,
                        "end": 12,
                        "text": "corrected second phrase",
                        "words": [
                            {"start": 10.2, "end": 10.5, "text": "corrected"},
                            {"start": 10.6, "end": 10.9, "text": "second"},
                        ],
                    },
                ],
            )
            resolved = [
                {**segment, "resolved_source": str(root / segment["source"])}
                for segment in contracts.edit_plan["long_form"]["segments"]
            ]
            with patch.object(captions, "_source_duration", side_effect=lambda segment: float(segment["duration"])):
                cues = captions.build_caption_cues(contracts, "long", resolved)
            self.assertEqual([0.1, 2.2], [cue["start"] for cue in cues])
            self.assertEqual([0.8, 2.9], [cue["end"] for cue in cues])
            self.assertEqual(["corrected first", "corrected second"], [cue["text"] for cue in cues])
            subtitle = captions.caption_text(cues, "srt")
            self.assertIn("00:00:02,200 --> 00:00:02,900", subtitle)
            self.assertNotIn("raw", subtitle)

    def test_burn_fallback_builds_overlay_graph_without_text_filter(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            base = root / "base.mp4"
            final = root / "final.mp4"
            base.write_bytes(b"base")
            cues = [
                {"start": 0.0, "end": 0.8, "text": "Hej"},
                {"start": 1.2, "end": 1.8, "text": "åre"},
            ]
            with (
                patch.object(captions, "probe", return_value={"width": 320, "height": 180}),
                patch.object(captions, "require_media_tools", return_value=("ffmpeg", "ffprobe")),
                patch.object(captions, "_caption_image"),
                patch.object(captions, "run_media_command") as run_command,
            ):
                renderer = captions.burn_captions(base, final, cues, {}, root)
            self.assertEqual("pillow-overlay", renderer)
            command = run_command.call_args.args[0]
            filter_graph = command[command.index("-filter_complex") + 1]
            self.assertIn("overlay=0:0", filter_graph)
            self.assertNotIn("subtitles", filter_graph)
            self.assertNotIn("drawtext", filter_graph)
            self.assertNotIn("ass", filter_graph)
            self.assertFalse(final.exists())  # the media command was intentionally mocked

    def test_adapter_import_is_hash_bound_and_tamper_evident(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            contracts = self.make_contracts(root)
            self.approve(contracts)
            output = root / "adapter-output.mp4"
            output.write_bytes(b"adapter bytes")
            media_metadata = {"duration_seconds": 1.0, "width": 320, "height": 180}
            approval_hash = "a" * 64
            with (
                patch.object(adapters, "require_current_approval"),
                patch.object(adapters, "current_approval_hash", return_value=approval_hash),
                patch.object(adapters, "probe", return_value=media_metadata),
            ):
                record_path = adapters.import_adapter_output(
                    contracts,
                    output,
                    FIXTURE_ADAPTER_MANIFEST,
                    adapter="test-adapter",
                    reviewer="owner",
                    adapter_version="test-1",
                    provenance="Local independent render for supervised import test.",
                )
            record = read_json(record_path)
            stored_output = root / record["output"]["path"]
            self.assertEqual(sha256_file(stored_output), record["output"]["sha256"])
            self.assertEqual(approval_hash, record["approval_hash"])
            stored_output.write_bytes(b"tampered")
            with (
                patch.object(adapters, "require_current_approval"),
                patch.object(adapters, "current_approval_hash", return_value=approval_hash),
                patch.object(adapters, "probe", return_value=media_metadata),
            ):
                with self.assertRaises(ACSUserError):
                    adapters.load_current_adapter_import(contracts)

    def test_lut_requires_preview_hash_and_explicit_approval(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            contracts = self.make_contracts(root)
            lut = root / "creative" / "archive.cube"
            preview = root / "qa" / "lut-preview.png"
            lut.parent.mkdir(parents=True)
            preview.parent.mkdir(parents=True)
            lut.write_text("LUT_3D_SIZE 2\n", encoding="utf-8")
            preview.write_bytes(b"preview")
            contracts.edit_plan["creative_direction"] = {
                "grade_choice": "Archive LUT",
                "lut": {
                    "path": "creative/archive.cube",
                    "preview_path": "qa/lut-preview.png",
                    "approved": False,
                    "approved_by": "owner",
                },
            }
            with self.assertRaises(ACSUserError):
                require_creative_direction(contracts)
            contracts.edit_plan["creative_direction"]["lut"]["approved"] = True
            contracts.edit_plan["creative_direction"]["lut"]["preview_sha256"] = sha256_file(preview)
            proof = require_creative_direction(contracts)
            self.assertEqual(sha256_file(lut), proof["lut"]["sha256"])
            self.assertEqual(sha256_file(preview), proof["lut"]["preview_sha256"])
            preview.write_bytes(b"changed preview")
            with self.assertRaises(ACSUserError):
                require_creative_direction(contracts)

    def test_derived_text_uses_reviewed_truth_only(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            contracts = self.make_contracts(root)
            for kind in ("long", "short"):
                contracts.edit_plan[f"{kind}_form"]["segments"] = [
                    {"source": "sources/source.mp4", "start": 0, "duration": 1}
                ]
            self.add_reviewed_transcript(
                contracts,
                raw_segments=[{"start": 0, "end": 1, "text": "wrong raw wording"}],
                reviewed_segments=[{"start": 0, "end": 1, "text": "correct reviewed wording"}],
            )
            self.approve(contracts)
            derive_project(contracts)
            text = (root / "derived" / "linkedin.md").read_text(encoding="utf-8")
            self.assertIn("correct reviewed wording", text)
            self.assertNotIn("wrong raw wording", text)
            record = read_json(root / "derived" / "derivative-record.json")
            self.assertEqual(1, record["derivatives"][0]["reviewed_transcript_revision"])

    def test_muted_ranges_do_not_require_review_coverage(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            contracts = self.make_contracts(root)
            broll = root / "sources" / "broll.mp4"
            broll.write_bytes(b"b-roll bytes")
            contracts.project["sources"].append(
                {
                    "path": "sources/broll.mp4",
                    "kind": "camera",
                    "role": "b-roll",
                    "rights": {
                        "status": "owned",
                        "owner": "owner",
                        "license": "owner-provided-original",
                        "source_url": "",
                        "attribution": "",
                    },
                }
            )
            contracts.edit_plan["long_form"]["segments"] = [
                {"source": "sources/broll.mp4", "start": 0, "duration": 4, "audio": "mute"},
                {"source": "sources/source.mp4", "start": 0, "duration": 1},
            ]
            self.add_reviewed_transcript(
                contracts,
                raw_segments=[{"start": 0, "end": 1, "text": "spoken"}],
                reviewed_segments=[{"start": 0, "end": 1, "text": "spoken"}],
            )
            ranges = plan_transcript_ranges(contracts, "long")
            self.assertEqual([{"source": "sources/source.mp4", "start": 0.0, "end": 1.0}], ranges)

    def test_open_ended_multi_segment_render_resolves_duration_for_fades(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            work = root / "renders"
            work.mkdir()
            segments = [
                {"resolved_source": str(root / "a.mp4"), "source": "a.mp4", "start": 1, "duration": 0},
                {"resolved_source": str(root / "b.mp4"), "source": "b.mp4", "start": 2, "duration": 0},
            ]
            with (
                patch.object(media, "probe", return_value={"duration_seconds": 5.0}),
                patch.object(media, "render_media") as render_media,
                patch.object(media, "run_media_command"),
            ):
                media.render_segments(segments=segments, output=root / "out.mp4", kind="long", work_dir=work)
            self.assertEqual([4.0, 3.0], [call.kwargs["duration"] for call in render_media.call_args_list])
            self.assertTrue(all(call.kwargs["audio_fade"] for call in render_media.call_args_list))


if __name__ == "__main__":
    unittest.main()
