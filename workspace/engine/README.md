# ACS engine boundary

This directory is the visible system-level boundary for the Agentic Content
System engine. The implementation remains importable as the top-level
`agentic_content_system` Python package so the installed `acs` command and
existing integrations remain stable; this map keeps the domain-specific
engine discoverable without introducing a second runtime package.

| Engine responsibility | Stable implementation surface |
| --- | --- |
| CLI and orchestration | `workspace/engine/agentic_content_system/cli.py` |
| Local contracts and validation | `workspace/engine/contracts/schemas/` and `workspace/engine/agentic_content_system/project.py` |
| FFmpeg/ffprobe media boundary | `workspace/engine/agentic_content_system/media.py`, `render.py`, `inspect.py` |
| Transcript adapters | `workspace/engine/agentic_content_system/transcript.py` and `workspace/engine/scripts/transcribe-local-whisper.py` |
| Deterministic derivatives/package | `workspace/engine/agentic_content_system/derive.py`, `package.py`, `publisher.py` |
| Static review and result proof | `workspace/engine/agentic_content_system/report.py` and `result.py` |

The map is intentional: ACS owns this Python/FFmpeg engine and its local
contracts. Agentic Design System is not a runtime, package, or schema
dependency. FreeCut is the one normal supervised video Studio route and
remains external to this engine. Remotion or generic code-based motion may
produce a bounded asset only for a concrete deliverable need; it is not another
editor or prerequisite. Retained HyperFrames/editor material is
migration/recovery input only. The existing recovery-import and supervised
publisher boundaries are documented in `docs/ADAPTERS.md`.

Use `acs init` for a content workspace. Do not create an upstream Project
record for each video or post by default.
