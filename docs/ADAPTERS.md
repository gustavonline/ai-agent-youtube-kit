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
| Supervised publisher | Consume `publish/publisher-handoff.json` after separate human authorization | Handoff contract only; v0.2 never posts |

Adapters must not become hidden owners of workspace truth. They may consume or
produce files named by the contract and should report hashes and failures back
to the local project. A publisher adapter must accept only the current handoff,
honor its enabled-route policy and manual/scheduled delivery intent, verify the
manifest/asset bindings, and require authorization outside ACS. A scheduled
intent is not permission to post.
