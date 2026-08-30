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
   Record the core idea and intended sales job first: attention, nurture/proof,
   or conversion/next step.
3. Configure clone defaults in `workspace/channel/PROFILE.md` and `workspace/channel/brand.json`,
   validate them, then scaffold a workspace with `acs init --brand`; copy resolved values into the local
   `brand.json`, `project.json`, `content-brief.md`, `recording-plan.md`, and
   `edit-plan.json`.
4. Choose manual/no-date or scheduled delivery for each enabled route in
   `project.json.delivery_intent`. Disabled routes stay disabled.
5. Add source media and rights/provenance metadata.
6. Draft/refine `content-brief.md`, `recording-plan.md`, and the optional
   `creative-direction.md`, then run `acs inspect` and ingest a transcript.
   Keep raw ASR separate; use `acs review-transcript` for corrected or bounded
   truth before captions or publish-ready text. For a video outcome, use the
   repository-local `freecut-studio` skill for the one normal supervised Studio
   edit and return the reviewed export to the existing ACS proof flow. The ACS
   render command remains a deterministic engine boundary, not another Studio.
7. Record explicit approval with `acs plan --approve --by <reviewer>`.
8. Run `acs render`, `acs derive`, `acs package`, `acs verify`,
   `acs review-report`, `acs export-result`, and reviewer-owned `acs semantic-eval`.
9. Let the caller read the local proof, `publish/publisher-handoff.json`, and
   `results/run-result.json` and its semantic-evaluation outcome through its normal task flow. The publisher handoff
   is awaiting separate authorization; v0.3 never posts externally.
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

### Normal FreeCut return

After the human reviews and approves the FreeCut export, copy it as an ordinary
file into the active ACS production before continuing:

```text
cp /path/to/reviewed-export.mp4 workspace/productions/<slug>/sources/freecut-reviewed.mp4
```

Add `sources/freecut-reviewed.mp4` to `project.json.sources` using the existing
source shape and truthful `status`, `owner`, `license`, `source_url`, and
`attribution` values. Set `edit-plan.json.source` and every intended
`long_form.segments[].source` and `short_form.segments[].source` to that same
relative path. Then run the ordinary gates and proof route:

```text
acs inspect workspace/productions/<slug>
acs ingest-transcript workspace/productions/<slug> <transcript-for-reviewed-export>
acs review-transcript workspace/productions/<slug> <reviewed-transcript> --by <reviewer>
acs plan workspace/productions/<slug> --approve --by <reviewer>
acs render workspace/productions/<slug> --kind all
acs derive workspace/productions/<slug>
acs package workspace/productions/<slug>
acs verify workspace/productions/<slug>
acs review-report workspace/productions/<slug>
acs export-result workspace/productions/<slug>
acs semantic-eval workspace/productions/<slug> <assessment.json> --by <reviewer>
```

Use `review-transcript` when reviewed transcript truth is applicable; do not
invent a review when it is not. The normal FreeCut return path must never use
`acs import-adapter`, a FreeCut manifest, reference JSON, schema, bridge, or any
other integration layer. That command and its manifest remain legacy
migration/recovery only.

## Editorial defaults

Use promise + proof + plan, usually in three points, with a contextual CTA and
an outro to the next useful video. The operational sequence is core idea +
intended sales job -> chosen capture format -> core video -> only enabled,
channel-native harvests -> contextual CTA/handoff. Source ideas from
work/client questions, mistakes, proof, mechanism, philosophy, and current
tests. Treat attention, nurture, and conversion as connected outcomes; buyer
relevance is more important than mass reach. Reformat the idea/copy for each
selected channel rather than blindly duplicating one video file.

The planning reference is three core videos per week for 26 weeks (78 core
videos) plus 22 useful shorts (100 assets). Vlogs are usually a 5–20% minority.

## Production tools and recovery inputs

- Local Whisper is the default optional transcription engine through
  `workspace/engine/scripts/transcribe-local-whisper.py`.
- FFmpeg/ffprobe own deterministic inspection and render boundaries.
- FreeCut is the one normal supervised video Studio route.
- Remotion or another code-based motion technique may produce one bounded ACS
  asset only when a concrete deliverable needs it; it is not an editor route or
  prerequisite.
- Retained HyperFrames and other editor material is migration/recovery input
  only. It is not an ordinary parallel choice.
- A supervised publisher consumes the existing handoff only after separate
  authorization; it is not an editor.

See `docs/ADAPTERS.md` for boundary rules and `docs/RECOVERY.md` for safe
cleanup.
