# Workflow

Agentic Content System is the execution layer for a solo founder or small
business. It accepts phone, camera, screen recording, podcast, Q&A, demo, vlog,
tablet, or whiteboard capture. The source mode is chosen by the content job;
the system is not a phone-first editor.

## Decision to publish-ready handoff

1. Bring useful context from a conversation, brief, AIOS Space task, or
   standalone business/content notes.
2. Choose a buyer problem, proof requirement, practical group, and one of the
   nine capture formats in `workspace/content-formats/formats.json`.
3. Configure clone defaults in `workspace/channel/PROFILE.md` and `workspace/channel/brand.json`,
   validate them, then scaffold a workspace with `acs init --brand`; copy resolved values into the local
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
   is awaiting separate authorization; v0.2 never posts externally.
10. For a repeat or explicit recovery, inspect relevant entries in
    `workspace/history/runs.jsonl` and their `workspace/runs/<run-id>/run.json`
    evidence before choosing `predecessor` or an explicit `--recover <run-id>`.
    Record one success or failure for the completed route, then route the
    attempt through the local tracer exactly once:
    `python workspace/engine/tracer.py record workspace/productions/<slug>
    --status succeeded` (or `failed --failure-code <short-code>`). An ordinary
    repeat uses `predecessor`; an explicit `--recover <run-id>` consumes one
    unresolved failed run at most once and creates a new record. After a
    successful full route, optional promotion to `examples/` is deliberate
    only through `python workspace/engine/tracer.py promote-example --run-id
    <id> --slug <slug>`; never promote automatically. The tracer is a local
    proof tool, not a daemon or an AIOS service.

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
  `workspace/engine/scripts/transcribe-local-whisper.py`.
- FFmpeg/ffprobe own deterministic inspection and render boundaries.
- HyperFrames can supply a motion asset when it clarifies a point.
- Timeline Studio, OpenReelio, and supervised publishers are documented seams,
  not v0.2 dependencies.

See `docs/ADAPTERS.md` for boundary rules and `docs/RECOVERY.md` for safe
cleanup.
