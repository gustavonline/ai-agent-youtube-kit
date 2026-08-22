# Reference Analysis

Use this workflow to study videos you want the channel to learn from. This is
inspired by `Mharis-code/videoanalyzer`, but kept repo-local and AI-first.

The goal is not to clone another creator. The goal is to extract reusable
patterns for hooks, structure, pacing, visual proof, captions, CTAs, packaging,
and production choices.

## When To Use

- Before creating a new branded clone.
- Before planning a new content lane.
- When a specific video performs well and you want to understand why.
- When you need examples for hook structure, CTA timing, screen-record pacing,
  or visual proof.

Do not use this for your own source edit workflow. Use
`docs/LOCAL_TRANSCRIPTION.md` and an ACS workspace's local transcript view for
that. Reference analysis remains separate from ACS execution truth.

## Setup Check

Reference analysis needs `yt-dlp`, `ffmpeg`, and `ffprobe`:

```bash
python3 scripts/analyze-reference-video.py --check
```

Install missing binaries:

```bash
brew install yt-dlp ffmpeg
```

## Prepare A Reference Video

```bash
python3 scripts/analyze-reference-video.py "https://www.youtube.com/watch?v=..."
```

For a local file:

```bash
python3 scripts/analyze-reference-video.py /absolute/path/to/reference.mp4
```

For long videos, analyze a focused section:

```bash
python3 scripts/analyze-reference-video.py "https://www.youtube.com/watch?v=..." --start 00:00 --end 01:30
```

If captions are unavailable and you want local transcription:

```bash
python3 scripts/analyze-reference-video.py "https://www.youtube.com/watch?v=..." --local-whisper --language en
```

Local Whisper uses this repo's `.venv/` and `.cache/whisper/`. Set it up with:

```bash
./scripts/setup-local-transcription.sh
```

## Output

The script writes:

```text
channel/references/<date-platform-slug>/
  source.json
  frames_manifest.json
  transcript.md
  analysis.md
  agent-prompt.md
  download/          ignored
  frames/            ignored
```

`download/` and `frames/` stay local. The durable tracked outputs are metadata,
transcript, the analysis report, and the prompt that explains how to finish the
analysis.

## Agent Analysis Procedure

1. Read `DESIGN.md`, `PROJECT_MEMORY.md`, `MOTION_PHILOSOPHY.md`,
   `channel/PROFILE.md`, and `channel/STYLE_GUIDE.md`.
2. Read `source.json`, `transcript.md`, and `frames_manifest.json`.
3. Inspect the frame paths listed in `frames_manifest.json`.
4. Fill `analysis.md` using `templates/reference-analysis.md`.
5. Add one row to `channel/REFERENCES.md`.
6. Promote only reusable lessons to `channel/STYLE_GUIDE.md`.
7. Do not add one-off reference details to `DESIGN.md`.

## What To Extract

- Hook type and exact first promise.
- Visual hook and what is visible before the viewer understands the topic.
- Story beat order and timestamps.
- How proof is introduced.
- Caption/on-screen text density.
- Pattern interrupts and edit pace.
- CTA mechanic and placement.
- Title/thumbnail curiosity mechanism.
- Repeatable lessons for this channel.

## Hard Rules

- Do not invent content that is not visible in frames or transcript.
- If there is no transcript, mark spoken hook as unavailable.
- Do not copy another creator's brand identity, face, logo, or exact format.
- Add lessons to `channel/STYLE_GUIDE.md` only when they can be reused.
- Keep raw downloaded videos and extracted frames out of git.
