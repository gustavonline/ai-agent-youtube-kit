# Agentic Content System Setup

This repository is a persistent, standalone local-first content system. A
single ACS checkout can hold many content workspaces; keep brand/client truth in
the workspace that owns the run, or use a separate clone when isolation is
needed. `examples/<slug>/` is the readable boundary for committed contract
examples and ignored local proof.

## Runtime

Install Python 3.10+ and FFmpeg/ffprobe. Then install the package in editable
mode:

macOS/Linux:

```text
python3 -m venv .venv
.venv/bin/python -m pip install -e .
```

Windows PowerShell:

```text
py -m venv .venv
.venv\Scripts\python.exe -m pip install -e .
```

PowerShell users can also run `scripts\setup-agentic-content-system.ps1`.

Verify:

```text
.venv/bin/python -m agentic_content_system doctor
.venv/bin/python -m agentic_content_system --help
```

There is no hosted backend, database, auth, queue, Electron/Tauri app, cloud
AI, or external publisher required for v0.2.

## Configure the clone

Use the repository-local setup skill for an agent-first intake. Resolve only
missing business, audience, offer/content promise, channel policy, cadence,
and delivery-default decisions. Store the durable profile in
`channel/PROFILE.md` and `channel/brand.json`, then run:

```text
.venv/bin/python -m agentic_content_system doctor
.venv/bin/python -m agentic_content_system validate-profile channel/brand.json
```

Do not create a content workspace until a real content outcome is requested.

## First ACS workspace

```text
.venv/bin/python -m agentic_content_system init examples/my-content --brand channel/brand.json
```

The command validates the supplied profile before writing and copies it into
the workspace. Edit the workspace `brand.json` only for this run's approved
policy, and edit `project.json` for the run-specific delivery intent. Generic
`acs init <workspace>` remains available and uses the starter policy.

Add source media under the workspace's `sources/` directory. Keep the source
rights owner, license, URL, attribution, and provenance in `project.json`.
Choose one of the nine formats in `content-formats/formats.json`, then edit the
promise, audience, points, CTA, and output windows in `edit-plan.json`.

## Transcript

The CLI accepts canonical transcript JSON, local Whisper JSON, Markdown, SRT,
or VTT:

```text
.venv/bin/python -m agentic_content_system ingest-transcript examples/my-content transcript.json
```

The existing local Whisper workflow is optional and preserved:

```text
./scripts/setup-local-transcription.sh
.venv/bin/python scripts/transcribe-local-whisper.py examples/my-content --model large --pack
```

Do not add API keys to this repository. See `docs/CLOUD_TRANSCRIPTION.md` only
for an explicitly requested cloud alternative.

## Approval-gated flow

```text
inspect -> validate -> ingest transcript -> review/edit plan -> approve
  -> render -> derive -> package -> verify -> static review report
```

Use `.venv/bin/python -m agentic_content_system plan examples/my-content --approve --by <name>`
only after the plan is reviewed. Delivery intent is owned by
`project.json.delivery_intent`; edit it and reapprove when a route needs a
scheduled date/time and explicit timezone. No external post occurs;
`publish/` is a validated package for later supervised shipping.

## Optional motion and editor adapters

HyperFrames workspaces under `video-projects/` remain available for a motion
asset when motion clarifies a point. They are optional adapter material, not
the ACS product identity. Timeline Studio, OpenReelio, and supervised
publishers are documented seams only; v0.2 does not vendor or depend on them.

## Cleanup

Remove generated workspace outputs without deleting decisions or inputs:

```text
.venv/bin/python -m agentic_content_system clean examples/my-content --outputs
```

For repo-local Whisper runtime/cache cleanup, use the existing
`scripts/clean-local-artifacts.sh` with its documented flags.
