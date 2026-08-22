# ACS engine boundary

This directory is the visible system-level boundary for the Agentic Content
System engine. The implementation remains importable as the top-level
`agentic_content_system` Python package so the installed `acs` command and
existing integrations remain stable; this map keeps the domain-specific
engine discoverable without introducing a second runtime package.

| Engine responsibility | Stable implementation surface |
| --- | --- |
| CLI and orchestration | `agentic_content_system/cli.py` |
| Local contracts and validation | `contracts/schemas/` and `agentic_content_system/project.py` |
| FFmpeg/ffprobe media boundary | `agentic_content_system/media.py`, `render.py`, `inspect.py` |
| Transcript adapters | `agentic_content_system/transcript.py` and `scripts/transcribe-local-whisper.py` |
| Deterministic derivatives/package | `agentic_content_system/derive.py`, `package.py`, `publisher.py` |
| Static review and result proof | `agentic_content_system/report.py` and `result.py` |

The map is intentional: ACS owns this Python/FFmpeg engine and its local
contracts. Agentic Design System is not a runtime, package, or schema
dependency. Full editors, HyperFrames, and supervised publishers are optional
adapters documented in `docs/ADAPTERS.md`.

Use `acs init` for a content workspace. Do not create an upstream Project
record for each video or post by default.
