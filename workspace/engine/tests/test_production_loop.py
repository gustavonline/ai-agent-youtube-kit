from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from agentic_content_system import adapters, captions, media, render
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

    def test_overlay_render_record_strips_runtime_paths_and_stays_current(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            contracts = self.make_contracts(root)
            overlay = root / "overlays" / "card.mp4"
            overlay.parent.mkdir(parents=True)
            overlay.write_bytes(b"overlay bytes")
            contracts.project["sources"].append(
                {
                    "path": "overlays/card.mp4",
                    "kind": "video-overlay",
                    "role": "graphic",
                    "rights": {
                        "status": "owned",
                        "owner": "owner",
                        "license": "fixture",
                        "source_url": "",
                        "attribution": "",
                    },
                }
            )
            contracts.edit_plan["long_form"]["segments"] = [
                {
                    "source": "sources/source.mp4",
                    "start": 0,
                    "duration": 1,
                    "overlay": "overlays/card.mp4",
                }
            ]
            contracts.edit_plan["short_form"]["enabled"] = False
            self.approve(contracts)

            def fake_render_segments(**kwargs: object) -> dict[str, float | int]:
                output = kwargs["output"]
                assert isinstance(output, Path)
                output.parent.mkdir(parents=True, exist_ok=True)
                output.write_bytes(b"rendered overlay output")
                return {"duration_seconds": 1.0, "width": 1280, "height": 720}

            with patch.object(render, "render_segments", side_effect=fake_render_segments):
                render.render_project(contracts, ["long"])

            record = read_json(root / "renders" / "render-record.json")["renders"]["long"]
            persisted_segment = record["segments"][0]
            self.assertEqual("overlays/card.mp4", persisted_segment["overlay"])
            self.assertNotIn("resolved_source", persisted_segment)
            self.assertNotIn("resolved_overlay_source", persisted_segment)
            serialized_record = str(record)
            self.assertNotIn("resolved_source", serialized_record)
            self.assertNotIn("resolved_overlay_source", serialized_record)
            self.assertNotIn(str(root), serialized_record)
            self.assertEqual(
                (root / "renders" / "long.mp4").resolve(),
                render.require_current_render_outputs(contracts, ["long"])["long"],
            )

            overlay.write_bytes(b"changed overlay bytes")
            with self.assertRaisesRegex(ACSUserError, "stale"):
                render.require_current_render_outputs(contracts, ["long"])

    def test_no_word_caption_fallback_honors_word_char_limits_and_proportional_timing(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            contracts = self.make_contracts(root)
            contracts.edit_plan["long_form"]["segments"] = [
                {"source": "sources/source.mp4", "start": 0, "duration": 4}
            ]
            contracts.edit_plan["captions"] = {
                "long": {"enabled": True, "format": "srt", "max_words": 5, "max_chars": 20}
            }
            text = "One two three four five six seven eight nine ten eleven twelve."
            self.add_reviewed_transcript(
                contracts,
                raw_segments=[{"start": 0, "end": 4, "text": text}],
                reviewed_segments=[{"start": 0, "end": 4, "text": text}],
            )
            resolved = [{"source": "sources/source.mp4", "start": 0, "duration": 4, "resolved_source": str(root / "sources/source.mp4")}]
            with patch.object(captions, "_source_duration", return_value=4.0):
                cues = captions.build_caption_cues(contracts, "long", resolved)
            self.assertGreater(len(cues), 1)
            self.assertTrue(all(len(cue["text"].split()) <= 5 for cue in cues))
            self.assertTrue(all(len(cue["text"]) <= 20 for cue in cues))
            self.assertAlmostEqual(0.0, cues[0]["start"])
            self.assertAlmostEqual(4.0, cues[-1]["end"])
            self.assertNotEqual(cues[0]["end"] - cues[0]["start"], cues[-1]["end"] - cues[-1]["start"])

    def test_muted_segment_never_emits_reviewed_caption_and_still_advances_time(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            contracts = self.make_contracts(root)
            broll = root / "sources" / "broll.mp4"
            broll.write_bytes(b"b-roll bytes")
            contracts.edit_plan["long_form"]["segments"] = [
                {"source": "sources/broll.mp4", "start": 0, "duration": 2, "audio": "mute"}
            ]
            contracts.edit_plan["captions"] = {"long": {"enabled": True, "max_words": 5}}
            self.add_reviewed_transcript(
                contracts,
                raw_segments=[{"start": 0, "end": 2, "text": "Må ikke vises"}],
                reviewed_segments=[{"start": 0, "end": 2, "text": "Må ikke vises", "source": "sources/broll.mp4"}],
            )
            resolved = [{"source": "sources/broll.mp4", "start": 0, "duration": 2, "audio": "mute", "resolved_source": str(broll)}]
            with patch.object(captions, "_source_duration", return_value=2.0):
                cues = captions.build_caption_cues(contracts, "long", resolved)
            self.assertEqual([], cues)

    def test_primary_audio_broll_uses_independent_audio_start_for_ranges_captions_and_render(self) -> None:
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
                        "license": "fixture",
                        "source_url": "",
                        "attribution": "",
                    },
                }
            )
            segment = {
                "source": "sources/broll.mp4",
                "start": 20,
                "duration": 2,
                "audio": "primary",
                "audio_start": 7.5,
            }
            contracts.edit_plan["long_form"]["segments"] = [segment]
            contracts.edit_plan["captions"] = {"long": {"enabled": True, "max_words": 5}}
            self.add_reviewed_transcript(
                contracts,
                raw_segments=[{"start": 7.5, "end": 9.5, "text": "Primary voice"}],
                reviewed_segments=[{"start": 7.5, "end": 9.5, "text": "Primary voice"}],
            )
            self.assertEqual(
                [{"source": "sources/source.mp4", "start": 7.5, "end": 9.5}],
                plan_transcript_ranges(contracts, "long"),
            )
            resolved = [{**segment, "resolved_source": str(broll)}]
            with patch.object(captions, "_source_duration", return_value=2.0):
                cues = captions.build_caption_cues(contracts, "long", resolved)
            self.assertEqual(["Primary voice"], [cue["text"] for cue in cues])
            self.assertEqual("sources/source.mp4", cues[0]["source"])
            self.assertEqual(7.5, cues[0]["source_start"])
            work = root / "renders"
            work.mkdir()
            with patch.object(media, "render_media") as render_media, patch.object(media, "run_media_command"):
                media.render_segments(
                    segments=resolved,
                    output=root / "out.mp4",
                    kind="long",
                    work_dir=work,
                    primary_audio_source=root / "sources/source.mp4",
                )
            self.assertEqual(20.0, render_media.call_args.kwargs["start"])
            self.assertEqual(7.5, render_media.call_args.kwargs["audio_start"])

    def test_approved_lut_is_in_per_segment_filter_chain_before_concat(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            source = root / "source.mp4"
            source.write_bytes(b"source")
            lut = root / "creative" / "grade.cube"
            lut.parent.mkdir()
            lut.write_text("LUT_3D_SIZE 2\n", encoding="utf-8")
            output = root / "render.mp4"
            with (
                patch.object(media, "require_media_tools", return_value=("ffmpeg", "ffprobe")),
                patch.object(media, "require_lut3d_filter"),
                patch.object(media, "run_media_command") as run_command,
                patch.object(media, "probe", return_value={"duration_seconds": 1.0, "width": 1280, "height": 720}),
            ):
                media.render_media(
                    source=source,
                    output=output,
                    kind="long",
                    duration=1,
                    normalize_long=True,
                    lut_source=lut,
                )
            command = run_command.call_args.args[0]
            video_filter = command[command.index("-vf") + 1]
            self.assertIn("scale=1280:720", video_filter)
            self.assertIn("lut3d=file=", video_filter)

    def test_custom_caption_font_is_local_and_changes_render_fingerprint_when_tampered(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            contracts = self.make_contracts(root)
            contracts.edit_plan["long_form"]["segments"] = [
                {"source": "sources/source.mp4", "start": 0, "duration": 1}
            ]
            contracts.edit_plan["captions"] = {
                "long": {"enabled": True, "font": "creative/fonts/custom.ttf"}
            }
            font = root / "creative" / "fonts" / "custom.ttf"
            font.parent.mkdir(parents=True)
            font.write_bytes(b"font-v1")
            self.add_reviewed_transcript(
                contracts,
                raw_segments=[{"start": 0, "end": 1, "text": "spoken"}],
                reviewed_segments=[{"start": 0, "end": 1, "text": "spoken"}],
            )
            first = captions.caption_render_fingerprint(contracts, "long")
            self.assertEqual("custom", first["font_proof"]["kind"])
            self.assertEqual("creative/fonts/custom.ttf", first["font_proof"]["path"])
            font.write_bytes(b"font-v2")
            second = captions.caption_render_fingerprint(contracts, "long")
            self.assertNotEqual(first["font_proof"]["sha256"], second["font_proof"]["sha256"])
            contracts.edit_plan["captions"]["long"]["font"] = "../outside.ttf"
            with self.assertRaises(ACSUserError):
                captions.caption_render_fingerprint(contracts, "long")

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

    def test_primary_audio_start_is_separate_from_visual_start_in_ffmpeg_command(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            visual = root / "visual.mp4"
            primary = root / "primary.mp4"
            visual.write_bytes(b"visual")
            primary.write_bytes(b"primary")
            with (
                patch.object(media, "require_media_tools", return_value=("ffmpeg", "ffprobe")),
                patch.object(media, "probe", return_value={"duration_seconds": 1.0}),
                patch.object(media, "run_media_command") as run_command,
            ):
                media.render_media(
                    source=visual,
                    output=root / "out.mp4",
                    kind="long",
                    start=50,
                    duration=1,
                    audio_mode="primary",
                    primary_audio_source=primary,
                    audio_start=2,
                )
            command = run_command.call_args.args[0]
            self.assertEqual(["-ss", "50.000", "-i", str(visual)], command[command.index("-ss") : command.index("-ss") + 4])
            primary_index = command.index(str(primary))
            self.assertEqual("2.000", command[primary_index - 2])

    def test_approved_lut_is_applied_in_per_segment_filter_or_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            source = root / "source.mp4"
            lut = root / "creative" / "archive.cube"
            source.write_bytes(b"source")
            lut.parent.mkdir()
            lut.write_text("LUT_3D_SIZE 2\n", encoding="utf-8")
            with (
                patch.object(media, "require_media_tools", return_value=("ffmpeg", "ffprobe")),
                patch.object(media, "_supports_ffmpeg_filter", return_value=True),
                patch.object(media, "probe", return_value={"duration_seconds": 1.0}),
                patch.object(media, "run_media_command") as run_command,
            ):
                media.render_media(
                    source=source,
                    output=root / "out.mp4",
                    kind="short",
                    duration=1,
                    lut_source=lut,
                )
            command = run_command.call_args.args[0]
            video_filter = command[command.index("-vf") + 1]
            self.assertIn("lut3d=file=", video_filter)
            self.assertIn("archive.cube", video_filter)
            with patch.object(media, "_supports_ffmpeg_filter", return_value=False):
                with self.assertRaisesRegex(ACSUserError, "supervised editor adapter"):
                    media.render_media(
                        source=source,
                        output=root / "out-failed.mp4",
                        kind="short",
                        duration=1,
                        lut_source=lut,
                    )

    def test_caption_font_proof_is_local_and_changes_when_custom_bytes_change(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            font = root / "creative" / "fonts" / "caption.ttf"
            font.parent.mkdir(parents=True)
            font.write_bytes(b"font-v1")
            config = {"font": "creative/fonts/caption.ttf", "font_size": 42}
            first = captions.caption_font_proof(config, root)
            self.assertEqual("custom", first["kind"])
            self.assertEqual("creative/fonts/caption.ttf", first["path"])
            font.write_bytes(b"font-v2")
            second = captions.caption_font_proof(config, root)
            self.assertNotEqual(first["sha256"], second["sha256"])
            with self.assertRaises(ACSUserError):
                captions.caption_font_proof({"font": str(font)}, root)

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
