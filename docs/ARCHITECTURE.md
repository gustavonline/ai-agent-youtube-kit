# Agentic Content System Architecture

Agentic Content System is a local-first, cloneable execution system. It runs
without AIOS and keeps the durable truth in inspectable files. There is no
hosted backend, auth, database, queue, Electron/Tauri shell, cloud AI, or real
publisher in v0.2.

```text
Conversation, brief, AIOS task, or standalone context
          |
          v
channel/PROFILE.md + channel/brand.json -> acs init --brand -> local brief/recording plan -> ACS workspace contracts
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
- The clone-owned `channel/brand.json` is a small source of defaults; `acs
  init --brand` validates it and copies it into the workspace before the first
  run. The workspace copy is execution truth.
- `project.json` owns the content promise, audience, capture format, source
  provenance, rights, transcript reference, and run-specific delivery intent.
- `edit-plan.json` owns the deterministic render intent and explicit approval
  state. It is the gate before render, derivative generation, and packaging.
- `publish/manifest.json` owns the generated publish-ready handoff, hashes,
  enabled routes, disabled routes, and the v0.2 no-external-posting assertion.
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
- `contracts/schemas/` versions the shapes. The CLI validates them without a
  runtime database or network call.
- `run-result.schema.json` owns the caller-agnostic proof/learning result. It
  contains no upstream-system fields and does not validate a caller return
  shape.

FFmpeg/ffprobe are the deterministic media boundary. Local Whisper remains an
optional transcript adapter through the existing repo script. The browser
surface is a static report, not an editing studio.

The dated editor/engine comparison and the rationale for keeping this narrow
contract + FFmpeg boundary are recorded in
[`EDITOR_ENGINE_DECISION.md`](EDITOR_ENGINE_DECISION.md); full editors remain
supervised adapters rather than v0.2 core dependencies.

The persistent AIOS Space may remain the owner of durable business defaults and
learning. A task-level caller or judgment layer copies resolved values into a
new ACS workspace; independent ACS then executes locally, and the caller reads
proof and learning back through its normal task flow. No shared maintained
schema is required. The setup skill configures the clone; the run skill owns
production execution.

See [`INPUT_OWNERSHIP.md`](INPUT_OWNERSHIP.md) for the source-agnostic routing
and the explicit prohibition on upstream runtime coupling.
