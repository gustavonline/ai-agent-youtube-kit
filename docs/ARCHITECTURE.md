# Architecture

ACS is a file-based orchestration and proof layer around human judgment and the
external FreeCut browser Studio.

```text
bounded context + source material
          |
          v
content brief / cut plan / optional transcript
          |
          v
FreeCut supervised browser edit (ordinary video)
          |
          v
content-graph.json: artifacts + hashes + provenance + independent reviews
          |
          v
publisher-handoff.json: approved nodes only, supervised, not posted
```

## Owned surfaces

ACS owns repository-local skills, Markdown context/templates, the content-graph
and publisher-handoff contracts, and focused validation. It does not own a
media editor, renderer, derivative generator, package builder, recovery ledger,
database, web service, or publisher.

The validator is a zero-dependency Node script. It reads local files, checks
their hashes and relationships, and never edits them. It does not require a
fixed graph shape, fixture count, or platform name.

## Studio boundary

FreeCut is the only normal Studio for owner-recorded video. The checkout and
native workspace stay outside ACS. Codex can validate and start its built Vite
app on strict loopback, open it in the in-app browser, and participate in a
revision-guarded human/agent/human workflow. The reviewed export returns as an
ordinary graph node; ACS does not render it again.

## Optional helpers

Local Whisper and reference analysis may use Python and FFmpeg. They are
optional preprocessing/research helpers, not an ACS runtime or fallback media
pipeline.

ADS is also optional. An accepted immutable `DESIGN.md` snapshot and selected
assets can be recorded in `design_handoff`; no ADS application, schema, or
editable source is required.

HeyGen HyperFrames is the single specialist code-motion route for an entire
code-animated explainer/motion-graphics video or one bounded overlay asset. Its
upstream skills own that production method. It is not an alternate timeline
editor.

## No posting

The graph proves what exists and what was reviewed. The handoff selects only
independently approved nodes and explicitly records that external posting is
false. A human or separately authorized publisher performs any later delivery.
