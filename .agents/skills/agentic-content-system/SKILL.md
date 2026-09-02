---
name: agentic-content-system
description: "Run a file-based ACS production from bounded context through independently approved content nodes and a supervised not-posted handoff."
---

# Agentic Content System

Read `docs/ARCHITECTURE.md`, `docs/CONTENT_GRAPH.md`, `docs/WORKFLOW.md`, and
`docs/INPUT_OWNERSHIP.md` before starting a production.

ACS is the judgment, lineage, review, and handoff layer. It does not own a media
editor or renderer. For an ordinary video, use the repository-local
`diffusion-studio` skill; the external Diffusion project and authoritative
Electron/DAPI runtime remain canonical while editing.

## Production sequence

1. Read the channel direction, memory, profile, style guide, and relevant
   references listed in `AGENTS.md`.
2. Create `workspace/productions/<slug>/` only for a concrete outcome. Fill the
   existing content brief and cut plan from the templates.
3. Put or reference local source files inside that production boundary. Record
   truthful provenance. Optional local transcription may create a transcript
   node; it is not required for every outcome.
4. For ordinary video, use Diffusion for cuts, timing, audio/music, captions,
   overlays/assets, and the supervised export. Use DAPI for authoritative work;
   the browser companion is read-only. A human reviews the export.
5. Register source, transcript, thesis, master, and useful derivative artifacts
   as needed in `content-graph.json`. Do not create placeholder nodes merely to
   satisfy a count. Each node has its own version, content hash, provenance, and
   review state.
6. Record explicit graph edges. Approval is never inherited. A family or source
   may be approved while a derivative remains `in_review` or `rejected`.
7. Run the graph validator. Complete the file-based final review. Fix the
   artifact or graph and increment the affected version when bytes or meaning
   change.
8. Create `publisher-handoff.json` only for independently approved nodes. Run
   the validator with both files. Return exact paths and hashes to the caller.

The handoff must remain `awaiting-separate-authorization`, `supervised: true`,
`not_posted: true`, and `external_posting: false`. Do not post.

## Optional visual handoff

ACS works without ADS. If ADS or another design owner supplied accepted
direction, copy one immutable `DESIGN.md` and only selected assets into the
production. Record revision, hashes, provenance, and review reference in the
optional `design_handoff`. Do not retain an editable design-project dependency.

## Specialist motion

Only when the requested deliverable is an entire code-animated
explainer/motion-graphics video or one bounded overlay asset, route to the
upstream HeyGen HyperFrames `/hyperframes` skill and follow its selected
workflow. Return the reviewed result as a graph node. Never use HyperFrames as
the routine timeline editor for owner-recorded long-form.
