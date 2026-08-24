# Agentic Content System Architecture

Agentic Content System is a local-first, cloneable execution system. It runs
without AIOS and keeps the durable truth in inspectable files. There is no
hosted backend, auth, database, queue, Electron/Tauri shell, cloud AI, or real
publisher in v0.3.

```text
Conversation, brief, AIOS task, or standalone context
          |
          v
workspace/channel/PROFILE.md + workspace/channel/brand.json -> acs init --brand -> local brief/recording plan -> ACS workspace contracts
          |
          v
capture/ingest -> inspect -> transcript -> explicit approval
          |
          v
FFmpeg render -> selected derivatives -> enabled-route package
          |
          v
verify -> static HTML review -> local proof/result -> caller reads learning
```

## Contract ownership

- `brand.json` owns channel policy, enabled/disabled reasons, and cadence.
- The clone-owned `workspace/channel/brand.json` is a small source of defaults; `acs
  init --brand` validates it and copies it into the workspace before the first
  run. The workspace copy is execution truth.
- `project.json` owns the content promise, audience, capture format, source
  provenance, rights, transcript reference, and run-specific delivery intent.
- `edit-plan.json` owns the deterministic render intent and explicit approval
  state. It is the gate before render, derivative generation, and packaging.
- `publish/manifest.json` owns the generated publish-ready handoff, hashes,
  enabled routes, disabled routes, and the v0.3 no-external-posting assertion.
- `context/` is optional human/source-note space. It is not a contract and is
  never read by runtime validation, approval, rendering, packaging, or result
  export.
- `publish/publisher-handoff.json` owns the versioned supervised-publisher
  delivery handoff. It binds to the current manifest identity, references the
  current asset/post hashes, includes enabled routes only, and records
  `awaiting-separate-authorization`, `not_posted: true`, and
  `external_posting: false`. Its manifest binding hash covers the immutable
  package fields and deliberately excludes only verify-time
  `manifest.verification` status bytes.
- `reports/review.json` and `results/run-result.json` own currentness bindings
  for the HTML review and outbound proof/result. A package replacement stages
  manifest and publisher handoff together, then invalidates old generated
  review/result claims only after the replacement succeeds.
- `workspace/engine/contracts/schemas/` versions the shapes. The CLI validates them without a
  runtime database or network call.
- `run-result.schema.json` owns the caller-agnostic proof/learning result. It
  contains no upstream-system fields and does not validate a caller return
  shape.

## Persistent System Template-aligned shell

`workspace/` is persistent operational truth. The channel, planning library,
production workspaces, reference library, learning, and run evidence remain
local files; `workspace/engine/` is only the technical implementation. The
append-only `workspace/history/runs.jsonl` relation contains one record per
deliberate full production-route attempt, whether it succeeds or fails. It
references the production `project.json`, `results/run-result.json`, and
`reports/review.json` rather than copying raw requests or prompts.

The local `workspace/engine/tracer.py` records predecessor repeats and explicit
single-use recovery relations. `examples/` is a deliberate curation boundary:
promotion writes only a small README and proof pointer, while operational
production state remains under `workspace/productions/`. Neither the tracer nor
the ACS CLI is an AIOS service, daemon, database, or automatic publisher.

FFmpeg/ffprobe are the deterministic media boundary. Local Whisper remains an
optional transcript adapter through the existing repo script. The browser
surface is a static report, not an editing studio.

The dated editor/engine comparison and the rationale for keeping this narrow
contract + FFmpeg boundary are recorded in
[`EDITOR_ENGINE_DECISION.md`](EDITOR_ENGINE_DECISION.md); full editors remain
supervised adapters rather than v0.3 core dependencies.

The edit plan may bind `audio_start` for a primary-audio B-roll segment. The
visual source still determines the output window and duration; the primary
source at `audio_start` determines audio and reviewed transcript/caption
coverage. Captions map ordered segments to output time, skip muted segments,
and are burned last. A supplied approved LUT is applied with FFmpeg `lut3d`
inside each segment render before concat; a build without that filter fails
closed to a supervised adapter.

The persistent AIOS Space may remain the owner of durable business defaults and
learning. A task-level caller or judgment layer copies resolved values into a
new ACS workspace; independent ACS then executes locally, and the caller reads
proof and learning back through its normal task flow. No shared maintained
schema is required. The setup skill configures the clone; the run skill owns
production execution.

See [`INPUT_OWNERSHIP.md`](INPUT_OWNERSHIP.md) for the source-agnostic routing
and the explicit prohibition on upstream runtime coupling.
