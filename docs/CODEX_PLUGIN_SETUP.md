# Optional Codex tooling

ACS requires no plugin. Repository-local skills plus Node 22 are enough for its
contracts. For video, the Diffusion skill and launcher start the pinned external
Electron/DAPI Studio; Codex opens the one-time loopback URL in its built-in
browser for read-only inspection.

HyperFrames skills remain upstream and are installed only for the specialist
code-motion route. Local Whisper is optional and uses the repository-local
venv/cache documented in `LOCAL_TRANSCRIPTION.md`.
