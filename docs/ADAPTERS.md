# Adapter Boundaries

The core system owns declarative intent, approval, provenance, deterministic
rendering, derivation, verification, and handoff. External tools are adapters.
The dated technical comparison and decision rationale are in
[`EDITOR_ENGINE_DECISION.md`](EDITOR_ENGINE_DECISION.md).

| Adapter | Boundary | v0.2 position |
| --- | --- | --- |
| FFmpeg / ffprobe | Source inspection and long/vertical media output | Required deterministic boundary |
| Local Whisper | Audio to agent-readable transcript | Optional; existing script remains supported |
| Timeline Studio | Read/write adapter for a future supervised timeline | Document seam only; not vendored |
| OpenReelio | Read/write adapter for a future supervised editor | Document seam only; not vendored |
| HyperFrames | Motion asset or overlay for a specific explanatory beat | Optional motion adapter, never product identity |
| `computerlovetech/video-edit-cli` | Supervised render/edit adapter with explicit plans, crop, manifests, and caption mapping | Relevant optional reference/import seam; not vendored or required |
| Supervised publisher | Consume `publish/publisher-handoff.json` after separate human authorization | Handoff contract only; v0.2 never posts |

Adapters must not become hidden owners of workspace truth. They may consume or
produce files named by the contract and should report hashes and failures back
to the local project. A publisher adapter must accept only the current handoff,
honor its enabled-route policy and manual/scheduled delivery intent, verify the
manifest/asset bindings, and require authorization outside ACS. A scheduled
intent is not permission to post.

ACS's `import-adapter` command is the supervised seam for a rendered adapter
output plus its JSON plan/manifest. The imported files are copied under the
production's `adapters/` boundary and become ordinary package assets and proof.
The 2026-08-24 reference snapshot for `computerlovetech/video-edit-cli` is MIT,
alpha v0.1.2, Python 3.11+, FFmpeg, immutable sources/provenance sidecars,
JSON result envelopes, explicit edit plans, per-segment crop and separate video
source, output manifests, and transcript-to-output caption mapping. Its 69
tests pass with one integration test deselected. It is macOS/Linux-first and
documents Windows as untested via WSL, so ACS does not claim native Windows
support from it.
