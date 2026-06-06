# Setup

Fresh setup for AI Agent YouTube Kit.

This repo is meant to work as a reusable base kit. Keep the base kit generic, then create one separate copy or clone per brand/channel, for example:

```text
~/Downloads/ai-agent-youtube-kit
~/Downloads/gustav-online-youtube-kit
~/Downloads/client-name-youtube-kit
```

Each branded copy can have its own `DESIGN.md`, assets, footage, starter projects, and project history.

## 1. Create A Brand Workspace

Recommended: create a new folder for the specific brand instead of tailoring the base kit directly.

If cloning from GitHub, replace `gustav-online-youtube-kit` with the folder name for the brand:

```bash
cd ~/Downloads
git clone https://github.com/gustavonline/ai-agent-youtube-kit.git gustav-online-youtube-kit
cd gustav-online-youtube-kit
```

If copying from an existing local base kit before a remote exists:

```bash
cd ~/Downloads
BRAND_WORKSPACE="gustav-online-youtube-kit"
rsync -a \
  --exclude ".git" \
  --exclude ".venv" \
  --exclude ".cache" \
  --exclude "footage/*" \
  --exclude "video-projects/*/renders/" \
  ai-agent-youtube-kit/ "$BRAND_WORKSPACE/"
cd "$BRAND_WORKSPACE"
git init
```

Use a folder name that matches the channel or client. Good examples:

- `gustav-online-youtube-kit`
- `acme-ai-youtube-kit`
- `client-name-video-kit`

## 2. Decide What This Clone Is For

Before editing files, write down the intended brand direction:

```text
Channel or client name:
Audience:
Main video type:
Tone:
Primary colors:
Logo files available:
Reference videos or screenshots:
Examples to avoid:
```

This prevents the clone from becoming a generic AI-video workspace.

## 3. Tailor The Brand Files

Update these files inside the branded clone:

```text
README.md
DESIGN.md
assets/brand-tokens.css
assets/README.md
docs/BRANDING.md
```

At minimum, set:

- channel/client name
- channel promise
- target audience
- colors
- fonts
- caption style
- logo/mark assets
- thumbnail direction
- examples to imitate and avoid

Recommended asset folders:

```text
assets/
  logo/
  backgrounds/
  fonts/
  audio/
  references/
```

Keep raw footage in `footage/<video-slug>/`, not in `assets/`.

## 4. Create The First Branded Starter Project

Copy the starter project that is closest to the first video format.

For a 9:16 short:

```bash
BRAND_PROJECT="gustav-online-short"
cp -R video-projects/youtube-short-template "video-projects/$BRAND_PROJECT"
```

Then update these files in the copied project:

```text
video-projects/<brand-project>/package.json
video-projects/<brand-project>/meta.json
video-projects/<brand-project>/README.md
video-projects/<brand-project>/DESIGN.md
video-projects/<brand-project>/assets/brand-tokens.css
video-projects/<brand-project>/index.html
```

Use the copied starter project for brand-specific text, logo placement, caption layout, and first visual examples. Leave the original `youtube-short-template` intact so future projects still have a clean template.

## 5. Verify Node And HyperFrames

HyperFrames needs Node.js 22 or newer.

```bash
node -v
npx --yes hyperframes --version
npx --yes hyperframes doctor
```

Codex has an official HyperFrames plugin in this environment. The CLI is still used inside each `video-projects/<project>/` folder.

## 6. Install FFmpeg

FFmpeg is required for HyperFrames rendering and Video Use final exports.

```bash
brew install ffmpeg
ffmpeg -version
ffprobe -version
```

## 7. Create The Local Video Use Plugin

Codex has an official HyperFrames plugin, but Video Use should be created as a local Codex plugin.

Paste this into Codex:

```text
Use the plugin-creator skill. Create a local Codex plugin called video-use from https://github.com/browser-use/video-use. Put it in ~/plugins/video-use, add it to the default personal marketplace, preserve the upstream SKILL.md/helpers/static files under skills/video-use, add accurate manifest metadata, and validate the plugin. Do not transcribe anything yet.
```

Expected local shape:

```text
~/plugins/video-use/
  .codex-plugin/plugin.json
  assets/
  skills/
    video-use/
      SKILL.md
      install.md
      helpers/
      static/
      pyproject.toml
```

Expected marketplace file:

```text
~/.agents/plugins/marketplace.json
```

More detail: `docs/CODEX_PLUGIN_SETUP.md`.

## 8. Set Up Local Whisper Transcription

This kit uses local Whisper transcription by default. No transcription API key
is required for the standard workflow.

Install the repo-local transcription runtime:

```bash
./scripts/setup-local-transcription.sh
```

This creates `.venv/` for Python packages and `.cache/whisper/` for downloaded
Whisper models. Both live inside the repo clone and are ignored by git. Deleting
the clone removes the local runtime and model cache.

To clean repo-local runtime/cache artifacts later:

```bash
./scripts/clean-local-artifacts.sh
```

Transcribe footage from the repo root:

```bash
.venv/bin/python scripts/transcribe-local-whisper.py footage/<video-slug> --model large --pack
```

For Danish footage:

```bash
.venv/bin/python scripts/transcribe-local-whisper.py footage/<video-slug> --model large --language da --pack
```

The command writes cached transcripts to
`footage/<video-slug>/edit/transcripts/` and creates
`footage/<video-slug>/edit/takes_packed.md`. The first `--model large` run also
downloads the Whisper model to `.cache/whisper/`.

Do not put API keys in this repo. ElevenLabs/Scribe can still be used as a
deliberate cloud alternative, but it is not the default for this kit.

## 9. Check Starter Projects

Check the branded starter project first:

```bash
cd video-projects/<brand-project>
npm run check
```

Or check every project:

```bash
./scripts/check-projects.sh
```

The generated reference projects may have warnings. The custom `youtube-short-template` should pass cleanly.

## 10. Preview A Starter Project

```bash
cd video-projects/<brand-project>
npm run dev
```

For render after FFmpeg is installed:

```bash
npm run render
```

## 11. Add Footage

```text
footage/<video-slug>/
  raw clips here
```

Do not start by rendering. Start with inventory and strategy.

Codex prompt:

```text
Use local Whisper transcripts from footage/<video-slug>/edit/takes_packed.md, then use video-use and HyperFrames. Inventory footage/<video-slug>, propose a YouTube edit strategy, and identify which beats need motion graphics. Do not cut or render until I approve the plan.
```

## 12. Production Loop

1. Drop raw footage in `footage/<slug>/`.
2. Run local Whisper transcription with `.venv/bin/python scripts/transcribe-local-whisper.py footage/<slug> --model large --pack`.
3. Use Video Use to inventory the packed transcript and propose an edit.
4. Approve the strategy.
5. Use HyperFrames for motion graphics, UI explainers, lower thirds, title cards, and transitions.
6. Let Video Use assemble, subtitle, grade, and self-check the final timeline.
7. Keep final outputs under `footage/<slug>/edit/`.

## 13. Pre-Commit Brand Check

Before committing a branded clone, search for old placeholder names:

```bash
rg -n "temporary|TODO|YourLogo|example.com|your-channel|youtube-short-template|AI Agent YouTube Kit" .
```

Keep hits that are intentionally documenting the base template. Replace hits that appear in brand-facing files, project metadata, titles, or rendered composition text.
