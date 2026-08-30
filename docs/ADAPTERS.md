# Production And Recovery Boundaries

The core system owns declarative intent, approval, provenance, deterministic
rendering, derivation, verification, and handoff. FreeCut is the one normal
supervised video Studio route; it is an external workbench, not an ACS
adapter or runtime dependency. Remotion or another code-based motion technique
may produce a bounded asset only when a concrete deliverable needs it. Retained
HyperFrames and other editor material is migration/recovery input only.

| Surface | Boundary | Current position |
| --- | --- | --- |
| FFmpeg / ffprobe | Source inspection and long/vertical media output | Required deterministic boundary |
| Local Whisper | Audio to agent-readable transcript | Optional; existing script remains supported |
| FreeCut | External native workspace with supervised human/agent revision handoff | One normal video Studio; final reviewed export returns to ACS |
| Remotion or generic code motion | One explicit asset for a concrete approved beat | Optional ACS technique; never a Studio or prerequisite |
| `acs import-adapter` | Already rendered output plus its existing plan/manifest | Explicit migration/recovery seam only; never editor selection |
| Retained HyperFrames projects | Historical motion/editor material | Migration/recovery only; never an ordinary route |
| Supervised publisher | Consume `publish/publisher-handoff.json` after separate human authorization | Handoff contract only; v0.3 never posts |

Non-Studio inputs and recovery imports must not become hidden owners of
workspace truth. A publisher must accept only the current handoff,
honor its enabled-route policy and manual/scheduled delivery intent, verify the
manifest/asset bindings, and require authorization outside ACS. A scheduled
intent is not permission to post.

ACS's existing `import-adapter` command remains available only when an explicit
migration/recovery task already has a rendered output plus its JSON
plan/manifest. The imported files are copied under the production's `adapters/`
boundary and become ordinary package assets and proof. Do not use this command
to choose or construct a parallel normal editor route.

After human review, a normal FreeCut export instead returns as an ordinary file
under the active production's `sources/`. Declare it with normal
rights/provenance in `project.json.sources`; point `edit-plan.json.source` and
every intended long- and short-form segment source at it; re-run `acs inspect`;
use the normal transcript review and `acs plan --approve` gates as applicable;
then continue through `acs render`, `acs derive`, `acs package`, `acs verify`,
`acs review-report`, `acs export-result`, and `acs semantic-eval`. The normal
FreeCut return path must never use `acs import-adapter`, a FreeCut manifest,
reference JSON, schema, bridge, or any other integration layer.

## Historical editor research (not active routing)

Timeline Studio, OpenReelio, and `computerlovetech/video-edit-cli` were dated
research candidates, not current editor choices. The complete historical
comparison and revisit notes are preserved in
[`EDITOR_ENGINE_DECISION.md`](EDITOR_ENGINE_DECISION.md). The 2026-08-24
reference snapshot for `computerlovetech/video-edit-cli` is MIT,
alpha v0.1.2, Python 3.11+, FFmpeg, immutable sources/provenance sidecars,
JSON result envelopes, explicit edit plans, per-segment crop and separate video
source, output manifests, and transcript-to-output caption mapping. Its 69
tests pass with one integration test deselected. It is macOS/Linux-first and
documents Windows as untested via WSL, so ACS does not claim native Windows
support from it. These facts do not reopen the active Studio router.

ACS v0.3 burns captions through its Pillow overlay implementation; it does not
select or expose a built-in FFmpeg text-filter route. Normal workloads are
supported and the resolved font (custom production-local file or selected
system fallback) is hash-bound in render proof. Hundreds of dense cues can
make the per-cue Pillow overlay slow; use the normal supervised FreeCut Studio
for that workload. ACS does not silently record an unapplied LUT: an approved
LUT uses FFmpeg `lut3d` per segment or fails closed for supervised completion in
FreeCut. An already rendered legacy result may use the existing import seam only
as explicit migration/recovery.
