# Setup Checklist

Follow this after cloning the repo.

For the full fresh-install flow, read `install.md`.

1. Create the local Video Use plugin.
   Read `docs/CODEX_PLUGIN_SETUP.md` or use the prompt in that file.

2. Confirm HyperFrames is available.
   Codex should have the official HyperFrames plugin. The CLI should respond:

   ```bash
   npx --yes hyperframes --version
   ```

3. Install FFmpeg.

   ```bash
   brew install ffmpeg
   ```

4. Verify runtime.

   ```bash
   npx --yes hyperframes doctor
   ./scripts/check-projects.sh
   ```

5. Add transcription credentials when needed.
   Set `ELEVENLABS_API_KEY` in the Video Use plugin root `.env` or export it in your shell. Do not commit it here.

6. Customize branding.
   Read `docs/BRANDING.md`, then edit `DESIGN.md` and `assets/brand-tokens.css`.

7. Add raw footage.
   Put clips in `footage/<video-slug>/`.

8. Start with strategy, not rendering.

   ```text
   Use video-use and HyperFrames. Inventory footage/<video-slug>, propose a YouTube edit strategy, and identify which beats need motion graphics. Do not cut or render until I approve the plan.
   ```
