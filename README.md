# Agentic Content System

Agentic Content System is a local-first, cloneable workspace for turning a
content decision and source material into reviewed content plus a supervised
publisher handoff.

ACS is deliberately small. It consists of skills, Markdown context and
templates, a versioned content graph, a supervised handoff, and focused
zero-dependency Node checks. It is not a media editor, render engine, Python
application, dashboard, database, or automatic publisher.

For ordinary video work, [FreeCut](https://github.com/walterlow/freecut) is the
only normal browser Studio. It handles owner-recorded long-form and shorts,
cuts, trims, audio/music, captions, overlays/assets, and supervised export. ACS
records the reviewed outputs and their lineage; it does not render them again.

## Start

Requirements: Node.js 22 or newer and Git. FreeCut has its own pinned external
checkout and setup contract.

```text
npm test
npm run check:graph
npm run check:repository
```

For a real outcome:

1. Read `AGENTS.md` and the repository-local production skill.
2. Create `workspace/productions/<slug>/` only when a real content outcome
   exists.
3. Copy the content-graph and review templates, then replace fixture values with
   truthful production paths, hashes, provenance, relationships, and review
   state.
4. Use FreeCut for video editing and supervised export.
5. Validate the graph and optional handoff with the Node checker.
6. Hand off only independently approved nodes. Nothing posts automatically.

The normative contracts are in [Content graph](docs/CONTENT_GRAPH.md), the
workflow is in [Workflow](docs/WORKFLOW.md), and Studio setup/runtime is in
[FreeCut Studio](docs/FREECUT_STUDIO.md).

## Boundaries

- Optional local Whisper and reference-analysis helpers may use Python and
  FFmpeg, but they are preprocessing/research tools, not an ACS media pipeline.
- ADS is optional. An accepted immutable `DESIGN.md` plus selected assets may
  be hash-bound in a production, but ACS works without ADS.
- Upstream HeyGen HyperFrames is a specialist route only for a full
  code-animated video or bounded overlay asset. It is not another editor.
- There is no desktop app requirement. The same Node/Vite/Chromium FreeCut path
  runs on macOS, Linux, and Windows.

See [Real-video acceptance](docs/REAL_VIDEO_ACCEPTANCE.md) for the next
owner-recorded usability tracer. Generated fixtures prove contracts only.
