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

The optional Windows helper is `scripts\setup-agentic-content-system.ps1`.

Check the environment without a workspace:

```text
.venv/bin/python -m agentic_content_system doctor
.venv/bin/python -m agentic_content_system --help
```

## Configure the clone before a workspace

Use the setup skill or an agent to resolve the business, audience, offer and
content promise, channel policy, cadence, and delivery defaults. Store the
durable channel policy in `channel/brand.json`, then validate it without
creating a content workspace:

```text
.venv/bin/python -m agentic_content_system doctor
.venv/bin/python -m agentic_content_system validate-profile channel/brand.json
```

## First standalone ACS workspace

```text
.venv/bin/python -m agentic_content_system init examples/my-content --brand channel/brand.json
```

Add a source at the scaffolded `sources/source.mp4`. Update the promise,
audience, format, source rights, and edit plan. A transcript can be the open
JSON shape below or an existing Whisper JSON file:

```json
{
  "schema_version": "1.0",
  "source": "source.mp4",
  "segments": [
    {"start": 0, "end": 2, "text": "The buyer question and promise."}
  ]
}
```

Run `ingest-transcript`, inspect, validate, and obtain explicit approval before
running the consequential commands. The complete command sequence is in
`docs/CLI.md`.

For context from an AIOS Space, conversation, or brief, copy only the resolved
values that this run needs into the local ACS contracts. There is no required
upstream schema or importer. Review `project.json`, `brand.json`,
`content-brief.md`, and `recording-plan.md`. Scheduling remains an intent in
`project.json` and the generated `publish/publisher-handoff.json`; it is not an
external post. See `docs/INPUT_OWNERSHIP.md` and the setup skill for the
task-level mapping pattern.

## Local Whisper compatibility

The existing repository workflow remains available:

```text
.venv/bin/python scripts/transcribe-local-whisper.py examples/my-content --model large --pack
```

Use the generated JSON with `acs ingest-transcript`. Cloud transcription is not
required and credentials must stay outside the repository.

On Windows, the repo-local interpreter is `.venv\Scripts\python.exe`; on
macOS/Linux it is `.venv/bin/python`. Do not use system `pip install` on a
Homebrew-managed Python; create the venv first.

## CI and proof

GitHub Actions covers macOS, Windows, and Linux with Python 3.10–3.13 and an
FFmpeg setup step. The repository's deterministic tests use generated media;
large media is not committed. This is CI configuration evidence until a pushed
run exists; it is not a claim that all OSes passed locally.
`scripts/create-fixture-media.py` can create a small local source for a manual
end-to-end run. See `docs/CI.md`.
