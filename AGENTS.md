# Agentic Content System Instructions

Agentic Content System (ACS) is an AI-first, cloneable content-production
workspace. Keep it local, transparent, and file-based. Do not turn it into a
hosted app, publishing bot, media editor, render engine, database, or dashboard.

The product boundary is:

- repository-local skills and agent-readable context;
- Markdown briefs, plans, reviews, and learning;
- the versioned content-graph and supervised publisher-handoff files;
- small zero-dependency Node validation;
- optional local transcript/reference helpers; and
- the external FreeCut browser Studio for ordinary video editing.

There is no ACS-owned Python application or media pipeline. Do not restore
in-repository media rendering, derivative generation, package generation,
adapter imports, run tracing, recovery ledgers, or static report generation as
a hidden fallback.

## Read before production work

1. `workspace/channel/DESIGN.md`
2. `workspace/learning/PROJECT_MEMORY.md`
3. `workspace/learning/MOTION_PHILOSOPHY.md`
4. `workspace/channel/PROFILE.md`
5. `workspace/channel/STYLE_GUIDE.md`
6. `docs/ARCHITECTURE.md`
7. `docs/CONTENT_GRAPH.md`
8. `docs/WORKFLOW.md`

Use `workspace/content-pipeline/ideas.md` for lightweight planning and
`workspace/references/` for reference analysis.

## Workflow router

- Clone setup: use `.agents/skills/setup-content-system/SKILL.md`. Do not create
  a production merely to prove setup.
- Production work: use `.agents/skills/agentic-content-system/SKILL.md`.
- Audit/readiness: use `.agents/skills/audit-content-system/SKILL.md` and remain
  read-only.
- Ordinary video: use `.agents/skills/freecut-studio/SKILL.md`. FreeCut is the
  only normal Studio for owner-recorded long-form, shorts, trims/cuts, audio,
  music, captions, overlays, assets, and supervised export.
- Code-native specialist motion: use the upstream HeyGen HyperFrames router
  only for an entire code-animated explainer/motion-graphics video or one
  bounded overlay asset. It is not an alternate timeline editor and is not the
  ordinary long-form route. See `docs/SPECIALIST_MOTION.md`.
- Reference analysis: follow `docs/REFERENCE_ANALYSIS.md`.
- Local transcription: follow `docs/LOCAL_TRANSCRIPTION.md`.
- Real owner-video acceptance: follow `docs/REAL_VIDEO_ACCEPTANCE.md`.

## Content truth

Each production keeps a `content-graph.json` beside its artifacts. Family and
node IDs are stable; versions change deliberately. Every node owns its content
hash, provenance, and review state. Approval never propagates from a family,
source, master, or sibling node. A publisher handoff may select only nodes whose
own review status is `approved`; it remains supervised, not posted, and awaits
separate authorization.

Validate a production with:

```text
node workspace/engine/scripts/check-content-graph.mjs <production>/content-graph.json [<production>/publisher-handoff.json]
```

Do not require a fixed node count or a named channel. Channel targets are
optional, arbitrary stable IDs declared per node.

## Visual-direction boundary

ADS is optional. ACS and FreeCut must work without it. When accepted direction
does arrive from ADS or another design owner, copy only the immutable
`DESIGN.md` snapshot and selected assets needed by the production. Record their
paths, revision, hashes, provenance, and review reference in the optional graph
`design_handoff`. Do not create an ADS runtime dependency or editable-source
bridge.

## Transcription and learning

Local Whisper is an optional helper, not ACS runtime. Keep credentials outside
the repository. Source media and generated transcripts remain ignored local
files under the production boundary. After a finished project, promote only
durable lessons to `workspace/learning/PROJECT_MEMORY.md` or
`workspace/channel/STYLE_GUIDE.md`; replace `workspace/channel/DESIGN.md` only
with direction accepted by its visual-design owner.

## Safety and shipping

No ACS tool posts externally. Human review and separate publishing authority
are mandatory. Preserve unrelated owner changes. Repository changes are not
committed, pushed, or published without explicit ship authorization.
