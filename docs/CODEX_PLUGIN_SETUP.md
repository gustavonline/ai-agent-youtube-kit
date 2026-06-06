# Codex Plugin Setup

OpenAI Codex currently has an official HyperFrames plugin, but Video Use is not an official Codex plugin in this setup. After cloning this repo, create the local Video Use plugin first so Codex has both halves of the video workflow available.

## Target State

You want:

- Official HyperFrames plugin available in Codex.
- Local Video Use plugin installed from `browser-use/video-use`.
- FFmpeg available on `PATH`.
- Local Whisper available for transcription.

## Fast Codex Prompt

Use this in Codex after cloning this repo:

```text
Use the plugin-creator skill. Create a local Codex plugin called video-use from https://github.com/browser-use/video-use. Put it in ~/plugins/video-use, add it to the default personal marketplace, preserve the upstream SKILL.md/helpers/static files under skills/video-use, add accurate manifest metadata, and validate the plugin. Do not transcribe anything yet. After the plugin exists, run ./scripts/harden-video-use-plugin.sh so this kit uses local Whisper by default.
```

That is the preferred workflow because Codex can use its local `plugin-creator` validator and marketplace conventions.

## Local Whisper Hardening

Video Use upstream may still document ElevenLabs/Scribe as its transcription
helper. This repo intentionally defaults to local Whisper instead.

After creating the local plugin, run this from the repo root:

```bash
./scripts/harden-video-use-plugin.sh
```

The script appends an idempotent policy block to:

```text
~/plugins/video-use/skills/video-use/SKILL.md
```

That block tells Codex to use
`.venv/bin/python scripts/transcribe-local-whisper.py ... --model large --pack`
inside this kit and to treat ElevenLabs/Scribe as explicit cloud opt-in only.

## Manual Shape

The local plugin should end up like this:

```text
~/plugins/video-use/
  .codex-plugin/plugin.json
  assets/
    video-use-banner.png
  skills/
    video-use/
      SKILL.md
      install.md
      helpers/
      skills/manim-video/
      static/
      pyproject.toml
```

The personal marketplace entry should live at:

```text
~/.agents/plugins/marketplace.json
```

The entry should point to:

```json
{
  "name": "video-use",
  "source": {
    "source": "local",
    "path": "./plugins/video-use"
  },
  "policy": {
    "installation": "AVAILABLE",
    "authentication": "ON_INSTALL"
  },
  "category": "Productivity"
}
```

## Runtime Prerequisites

Install FFmpeg before rendering or final Video Use exports:

```bash
brew install ffmpeg
```

Verify:

```bash
ffmpeg -version
ffprobe -version
npx --yes hyperframes doctor
```

Install local Whisper for transcription:

```bash
./scripts/setup-local-transcription.sh
```

This kit transcribes footage locally through
`scripts/transcribe-local-whisper.py`, stores Whisper models in repo-local
`.cache/whisper/`, then lets Video Use consume the packed transcript. Do not put
API keys in this repo.

## First-Run Order

1. Clone this kit.
2. Create/install the local `video-use` plugin using the Codex prompt above.
3. Run `./scripts/harden-video-use-plugin.sh`.
4. Confirm the official HyperFrames plugin is available in Codex.
5. Install FFmpeg.
6. Install local Whisper.
7. Customize `DESIGN.md` and `assets/brand-tokens.css`.
8. Drop raw footage into `footage/<slug>/`.
9. Run local Whisper transcription and packing.
10. Ask Video Use to inventory the packed transcript and propose a strategy.
11. Use HyperFrames for motion graphics after the edit plan is approved.
