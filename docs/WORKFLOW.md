# Workflow

Agentic Content System is the execution layer for a solo founder or small
business. It accepts phone, camera, screen recording, podcast, Q&A, demo, vlog,
tablet, or whiteboard capture. The source mode is chosen by the content job;
the system is not a phone-first editor.

## Decision to publish-ready handoff

1. Bring useful context from a conversation, brief, AIOS Space task, or
   standalone business/content notes.
2. Choose a buyer problem, proof requirement, practical group, and one of the
   nine capture formats in `content-formats/formats.json`.
3. Scaffold a workspace with `acs init`; copy resolved values into the local
   `brand.json`, `project.json`, `content-brief.md`, `recording-plan.md`, and
   `edit-plan.json`.
4. Choose manual/no-date or scheduled delivery for each enabled route in
   `project.json.delivery_intent`. Disabled routes stay disabled.
5. Add source media and rights/provenance metadata.
6. Draft/refine `content-brief.md` and `recording-plan.md`, then run
   `acs inspect`, ingest a transcript, and review the declarative plan.
7. Record explicit approval with `acs plan --approve --by <reviewer>`.
8. Run `acs render`, `acs derive`, `acs package`, `acs verify`,
   `acs review-report`, and `acs export-result`.
9. Let the caller read the local proof, `publish/publisher-handoff.json`, and
   `results/run-result.json` through its normal task flow. The publisher handoff
   is awaiting separate authorization; v0.1 never schedules or posts
   externally.

## Editorial defaults

Use promise + proof + plan, usually in three points, with a contextual CTA and
an outro to the next useful video. Source ideas from work/client questions,
mistakes, proof, mechanism, and philosophy. Treat attention, nurture, and
conversion as connected outcomes; buyer relevance is more important than mass
reach. A core video can be harvested into selected shorts and posts, but
channel policy decides which derivatives exist.

The planning reference is three core videos per week for 26 weeks (78 core
videos) plus 22 useful shorts (100 assets). Vlogs are usually a 5–20% minority.

## Optional adapters

- Local Whisper is the default optional transcription engine through
  `scripts/transcribe-local-whisper.py`.
- FFmpeg/ffprobe own deterministic inspection and render boundaries.
- HyperFrames can supply a motion asset when it clarifies a point.
- Timeline Studio, OpenReelio, and supervised publishers are documented seams,
  not v0.1 dependencies.

See `docs/ADAPTERS.md` for boundary rules and `docs/RECOVERY.md` for safe
cleanup.
