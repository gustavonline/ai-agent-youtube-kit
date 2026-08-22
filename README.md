# Agentic Content System

Agentic Content System is a local-first, cloneable system for turning bounded
company context into useful content: content decision -> format/script/outline
-> capture/ingest -> transcript -> approved long-form edit -> selected short
derivatives -> posts -> publish-ready handoff -> learning.

It is not a phone-first editor, a mini-Premiere, a hosted app, or a publishing
bot. The durable truth is transparent JSON, Markdown, media, and proof files.
ACS accepts resolved context from a conversation, brief, AIOS Space task, or
another useful source, but it runs standalone once that context is copied into
the workspace. No upstream system or shared integration schema is a runtime
dependency.

The ownership boundary is deliberate: a persistent AIOS Space may own durable
company, offer, buyer, channel defaults, and learning; a caller or judgment
layer copies only the resolved values needed for one run; the receiving ACS
workspace becomes canonical for execution truth; and a caller reads proof,
supervised-publisher state, and learning back through its normal task flow. A
delivery date is intent only. v0.1 never posts externally, and a separate
authorization is required by any later publisher.

## Quickstart

Install Python 3.10+ and FFmpeg/ffprobe, then from the repository root:

```text
python3 -m venv .venv
.venv/bin/python -m pip install -e .
.venv/bin/python -m agentic_content_system doctor
.venv/bin/python -m agentic_content_system init examples/my-content --example gustav
```

On Windows PowerShell use `py -m venv .venv`, then
`.venv\Scripts\python.exe -m pip install -e .` and invoke the same module with
`.venv\Scripts\python.exe`. The setup helpers are
`scripts/setup-agentic-content-system.sh` and
`scripts\setup-agentic-content-system.ps1`. This venv-first flow avoids
modifying Homebrew/system Python.

Add source media under `examples/my-content/sources/`, complete the rights and
provenance fields in `project.json`, and follow the contract-gated flow:

```text
.venv/bin/python -m agentic_content_system inspect examples/my-content
.venv/bin/python -m agentic_content_system validate examples/my-content
.venv/bin/python -m agentic_content_system ingest-transcript examples/my-content transcript.json
.venv/bin/python -m agentic_content_system plan examples/my-content --approve --by reviewer
.venv/bin/python -m agentic_content_system render examples/my-content --kind all
.venv/bin/python -m agentic_content_system derive examples/my-content
.venv/bin/python -m agentic_content_system package examples/my-content
.venv/bin/python -m agentic_content_system verify examples/my-content
.venv/bin/python -m agentic_content_system review-report examples/my-content
.venv/bin/python -m agentic_content_system export-result examples/my-content
```

The installed `acs` command is equivalent. Windows users can use the module
form exactly as shown; no POSIX shell is required.

## What v0.1 owns

- Versioned JSON Schemas for brand/channel policy, content workspace metadata, edit plan,
  transcript, and publish manifest.
- A cross-platform Python CLI: doctor, init, inspect, validate, plan/diff,
  transcript ingestion, deterministic render, derive, package, verify,
  review-report, and clean.
- FFmpeg/ffprobe as the controlled media boundary for 16:9 long-form and 9:16
  short output.
- Explicit edit-plan approval before render, derivatives, or package creation.
- Provenance and rights metadata carried into the publish manifest.
- A versioned workspace-owned `delivery_intent` for manual/no-date or scheduled
  routes with an explicit timezone, plus an atomic
  `publish/publisher-handoff.json` containing only enabled routes and an
  awaiting-authorization/not-posted assertion.
- Static local HTML review, deterministic reruns, understandable failures, and
  no arbitrary shell execution from input contracts.
- Enabled-channel-only handoff. Gustav's example enables YouTube and LinkedIn,
  permits an optional Instagram short route, and disables TikTok with a clear
  fit reason; policy is per brand/client.

## Existing workflow assets

The original local Whisper transcription scripts, footage conventions, content
pipeline, templates, and HyperFrames projects remain useful. Local Whisper is
optional and stays repo-local; HyperFrames is an optional motion adapter for a
specific explanatory beat, never the product identity. Timeline Studio,
OpenReelio, HyperFrames, and supervised publishers have documented seams but
are not vendored or required by v0.1.

The committed `examples/gustav/` directory is the visible, contract-only
example boundary. Source media and generated proof under an example are
ignored, so examples remain understandable without committing large files.
Use `scripts/new-content-example.py <slug>` when you want a new local example.

Read these first:

- `docs/QUICKSTART.md` - setup and first ACS workspace.
- `docs/CLI.md` - stable commands and approval gates.
- `docs/ARCHITECTURE.md` - contract ownership and boundaries.
- `docs/INPUT_OWNERSHIP.md` - source-agnostic context and ownership boundary.
- `docs/CONTENT_FORMATS.md` - nine capture formats and cadence guidance.
- `docs/EDITOR_ENGINE_DECISION.md` - dated editor/engine research and the
  narrow contract + FFmpeg decision.
- `.agents/skills/agentic-content-system/SKILL.md` - repository-local run interface.
- `.agents/skills/audit-content-system/SKILL.md` - periodic read-only health,
  truth, drift, and proof audit for the repository or one named workspace.
- `docs/RECOVERY.md` - safe generated-output cleanup.

Standalone scaffolds write explicit manual/no-date delivery for enabled routes.
The explicit Gustav example schedules YouTube for `2026-09-01T09:00:00` in
`Europe/Copenhagen`, keeps LinkedIn manual, and keeps Instagram/TikTok
disabled. The advisory context is in `examples/gustav-context.md`; it is
guidance for the judgment layer, not an ACS inbound schema or CLI input.

Use the run skill for production work and the audit skill for a periodic,
strictly read-only backstop before handoff or when workspace proof may be
stale. An audit never repairs or regenerates proof.

Brand design and motion principles remain in `DESIGN.md`,
`MOTION_PHILOSOPHY.md`, `PROJECT_MEMORY.md`, `channel/PROFILE.md`, and
`channel/STYLE_GUIDE.md`. The existing HyperFrames starter projects are kept
under `video-projects/` as optional motion assets, not as the system boundary.
The legacy `footage/` directory remains ignored and accepted by the local
transcription helper for older source-side workflows; new ACS runs should use
an `examples/<slug>/` workspace or another explicitly chosen local directory.
