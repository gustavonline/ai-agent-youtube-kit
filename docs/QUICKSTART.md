# Quickstart

## Prerequisites

Install Python 3.10 or newer and FFmpeg, including `ffprobe`, on PATH.

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

The optional Windows helper is `workspace/engine/scripts/setup-agentic-content-system.ps1`.

Check the environment without a workspace:

```text
.venv/bin/python -m agentic_content_system doctor
.venv/bin/python -m agentic_content_system --help
```

There is no hosted backend, database, auth, queue, cloud AI, or external
publisher required for the standalone ACS runtime.

## Configure the clone before a workspace

Use the setup skill or an agent to resolve only the business, audience, offer
and content promise, channel policy, cadence, and delivery defaults that are
still missing. Store the durable channel policy in
`workspace/channel/PROFILE.md` and `workspace/channel/brand.json`, then
validate it without creating a content workspace:

```text
.venv/bin/python -m agentic_content_system doctor
.venv/bin/python -m agentic_content_system validate-profile workspace/channel/brand.json
```

Do not create a content workspace until a real content outcome is requested.

## First standalone ACS workspace

```text
.venv/bin/python -m agentic_content_system init workspace/productions/my-content --brand workspace/channel/brand.json
```

The command validates the supplied profile before writing and copies it into
the workspace. Edit the workspace `brand.json` only for this run's approved
policy, and edit `project.json` for the run-specific delivery intent. Generic
`acs init <workspace>` remains available and uses the starter policy.

Add source media under the workspace's `sources/` directory. Keep the source
rights owner, license, URL, attribution, and provenance in `project.json`.
Choose one of the nine formats in `workspace/content-formats/formats.json`,
then edit the promise, audience, points, CTA, and output windows in
`edit-plan.json`.

A transcript can be the open JSON shape below or an existing local Whisper
JSON file:

```json
{
  "schema_version": "1.0",
  "source": "source.mp4",
  "segments": [
    {"start": 0, "end": 2, "text": "The buyer question and promise."}
  ]
}
```

## Transcript and approval-gated flow

The CLI accepts canonical transcript JSON, local Whisper JSON, Markdown, SRT,
or VTT:

```text
.venv/bin/python -m agentic_content_system ingest-transcript workspace/productions/my-content transcript.json
```

The complete route is:

```text
inspect -> validate -> ingest transcript -> review/edit plan -> approve
  -> render -> derive -> package -> verify -> static review report -> export result
```

Use `.venv/bin/python -m agentic_content_system plan workspace/productions/my-content --approve --by <name>`
only after the plan is reviewed. Delivery intent is owned by
`project.json.delivery_intent`; edit it and reapprove when a route needs a
scheduled date/time and explicit timezone. No external post occurs;
`publish/` is a validated package for later supervised shipping.

After one deliberate full route, record one success or failure in the local
append-only run relation with the tracer documented in
`docs/WORKFLOW.md`. Low-level ACS subcommands do not create ledger records.

For context from an AIOS Space, conversation, or brief, copy only the
resolved values that this run needs into the local ACS contracts. There is no
required upstream schema or importer. Review `project.json`, `brand.json`,
`content-brief.md`, and `recording-plan.md`. Scheduling remains an intent,
not an external post. See `docs/INPUT_OWNERSHIP.md` and the setup skill for
the task-level mapping pattern.

## Local Whisper compatibility

The existing local workflow remains available:

```text
./workspace/engine/scripts/setup-local-transcription.sh
.venv/bin/python workspace/engine/scripts/transcribe-local-whisper.py workspace/productions/my-content --model large --pack
```

Use the generated JSON with `acs ingest-transcript`. Cloud transcription is
not required and credentials must stay outside the repository.

On Windows, the repo-local interpreter is `.venv\Scripts\python.exe`; on
macOS/Linux it is `.venv/bin/python`. Do not use system `pip install` on a
Homebrew-managed Python; create the venv first.

## Optional motion and editor adapters

HyperFrames workspaces under
`workspace/engine/motion-adapters/video-projects/` remain available for a
motion asset when motion clarifies a point. They are optional adapter material,
not the ACS product identity. Timeline Studio, OpenReelio, and supervised
publishers are documented seams only; v0.2 does not vendor or depend on them.

## Cleanup

Remove generated workspace outputs without deleting decisions or inputs:

```text
.venv/bin/python -m agentic_content_system clean workspace/productions/my-content --outputs
```

For repo-local Whisper runtime/cache cleanup, use the existing
`workspace/engine/scripts/clean-local-artifacts.sh` with its documented flags.

## CI and proof

GitHub Actions covers macOS, Windows, and Linux with Python 3.10–3.13 and an
FFmpeg setup step. The repository's deterministic tests use generated media;
large media is not committed. This is CI configuration evidence until a
pushed run exists; it is not a claim that all OSes passed locally.
`workspace/engine/scripts/create-fixture-media.py` can create a small local
source for a manual end-to-end run. See `docs/CI.md`.
