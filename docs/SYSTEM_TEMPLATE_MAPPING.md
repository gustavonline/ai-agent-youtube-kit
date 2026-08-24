# ACS → Canonical System Template mapping

Status: mapping-only review artifact. This document is the only file created by
the mapping boundary. No implementation, configuration, documentation, skill,
example, or workspace path has been moved or rewritten yet.

## Decision and boundary

Agentic Content System (ACS) remains a standalone, local-first Agentic System.
The shipped System Template at commit
`52a507428e1bf05a992773799228cd4da9aa4090` is the filesystem reference, not a
runtime dependency, package, shared schema, database, or AIOS integration
library. ACS-specific Python/FFmpeg behavior and versioned local contracts stay
ACS-owned below `workspace/`.

The migration target is:

```text
AGENTS.md                         root operating instructions
README.md                         root product/readme shell
.agents/skills/                   ACS primary, setup, and audit skills
docs/                             public contract, workflow, and mapping docs
examples/                         deliberately curated standalone proof only
workspace/                        persistent ACS operational truth
├── README.md
├── channel/                       clone channel state and brand assets
├── content-formats/               ACS planning library
├── content-pipeline/              ideas, selected, and published pipeline state
├── engine/                        only technical implementation
│   ├── agentic_content_system/    Python package and module entry point
│   ├── contracts/                 local versioned JSON schemas
│   ├── motion-adapters/           optional HyperFrames material
│   ├── requirements/              optional local-transcription requirements
│   ├── scripts/                   local toolchain and compatibility helpers
│   ├── templates/                 agent-readable workflow templates
│   └── tests/                     ACS and System Template structural tests
├── history/runs.jsonl             append-only run relation
├── learning/                      durable memory and motion lessons
├── productions/                   persistent content workspaces
├── references/                    reference-analysis library
└── runs/                          structured run evidence and recovery
```

`pyproject.toml` remains a root toolchain manifest, `.gitignore` remains hidden
root configuration, and `.github/workflows/` remains hidden CI. They are the
only root exceptions beyond the public shell above. No visible root package,
`engine/`, `scripts/`, `tests/`, `channel/`, `contracts/`, `footage/`,
`video-projects/`, or other implementation directory remains after the
migration.

The current ACS run contract remains intact inside each
`workspace/productions/<slug>/` directory: `brand.json`, `project.json`,
`content-brief.md`, `recording-plan.md`, `edit-plan.json`, `sources/`,
`transcripts/`, `renders/`, `derived/`, `publish/`, `reports/`, `results/`,
`recovery/`, and `inspection.json` keep their names and JSON meanings. The
directory's default location changes; the CLI continues to accept any valid
workspace path.

## Source evidence

The inventory below was taken from the actual `origin/main` tree, not from a
template copy:

- ACS `origin/main`, HEAD, and merge-base were all
  `0344d1daefa9286c040cfb86e47bb9eeee4cc401`.
- `git ls-tree -r --name-only HEAD` reported 142 tracked paths.
- The 142 paths comprise 17 tracked directory roots and 8 tracked root files.
- The untouched deterministic baseline was 41 tests, all passing; the exact
  command and result are recorded at the end of this document.
- The pinned System Template tree contains only `workspace/`, `examples/`, and
  `docs/` as visible functional roots, with its shell, checks, tracer, and
  tests below `workspace/engine/`.

The following table is closed over the tracked paths: a `/**` rule includes
every tracked descendant, and split rows account for the exceptions inside a
root. The count column is the count observed in the source tree.

## Exhaustive tracked-root mapping

| Current tracked root or root file | Count | Destination after migration | Compatibility and rationale |
| --- | ---: | --- | --- |
| `.agents/**` | 5 | `.agents/**` | Keep the ACS run skill as the one discoverable ACS System skill. Keep setup and audit as separate real workflows; update their commands and state paths. Do not copy a shared skill implementation from another repository. |
| `.github/**` | 1 | `.github/**` | Hidden CI exception. Update test, structural-check, package-install, and optional adapter paths; retain the cross-platform matrix. |
| `.gitignore` | 1 | `.gitignore` | Hidden root configuration exception. Replace `examples/*` runtime globs, legacy `footage/**`, channel-reference paths, and adapter paths with the new `workspace/productions`, `workspace/references`, and `workspace/engine/motion-adapters` boundaries while retaining safe media/secret ignores. |
| `AGENTS.md` | 1 | `AGENTS.md` | Root shell file stays. Rewrite linked paths to `workspace/channel`, `workspace/learning`, `workspace/references`, `workspace/content-pipeline`, `workspace/productions`, and `workspace/engine`; preserve local Whisper, human approval, and no-AIOS rules. |
| `DESIGN.md` | 1 | `workspace/channel/DESIGN.md` | Stable brand direction is channel state, not root shell. All references and motion-adapter instructions point to this location. |
| `MOTION_PHILOSOPHY.md` | 1 | `workspace/learning/MOTION_PHILOSOPHY.md` | General motion lessons are durable learning. Optional adapter-specific design remains beside its adapter under `workspace/engine/motion-adapters`. |
| `PROJECT_MEMORY.md` | 1 | `workspace/learning/PROJECT_MEMORY.md` | Durable production memory belongs in the Template-aligned learning area. Per-production notes remain in the production workspace. |
| `README.md` | 1 | `README.md` | Root shell file stays. Explain the new target tree, default production path, package install requirement, ledger/run proof, and curated-example boundary. |
| `SETUP.md` | 1 | `docs/QUICKSTART.md` | Merge the setup content into the existing public quickstart, then remove the visible root duplicate. Preserve commands and add the new default `workspace/productions/<slug>` path. |
| `agentic_content_system/**` | 20 | `workspace/engine/agentic_content_system/**` | `git mv` the complete Python package without changing public module names. Configure setuptools to discover it from `workspace/engine`; keep `acs` and `agentic-content-system` entry points unchanged. |
| `assets/**` | 2 | `workspace/channel/assets/**` | Shared brand tokens and asset guidance are channel state. Raw A-roll remains in a production's `sources/`, never in this shared asset area. |
| `channel/PROFILE.md`, `channel/STYLE_GUIDE.md`, `channel/brand.json`, `channel/published-videos.csv` | 4 of 6 | `workspace/channel/**` | Clone-owned profile, policy, style, and performance state move together and remain the defaults copied by `acs init --brand`. |
| `channel/REFERENCES.md`, `channel/references/**` | 2 of 6 | `workspace/references/REFERENCES.md`, `workspace/references/**` | Reference index and analysis artifacts are a separate persistent library. Preserve ignored downloads/frames/local Whisper output rules below this new root. |
| `content-formats/**` | 1 | `workspace/content-formats/**` | The machine-readable format library is durable ACS planning state, not Python implementation and not a new public root. Update its provenance and all links. |
| `content-pipeline/**` | 3 | `workspace/content-pipeline/**` | Move `ideas.md`, `selected/.gitkeep`, and `published/.gitkeep` as persistent pipeline state. No hosted board or database is introduced. |
| `contracts/**` | 10 | `workspace/engine/contracts/**` | Local schemas and the package marker are technical ACS implementation. Keep `contracts` import/package discovery available through the root packaging manifest and keep schema versions unchanged. |
| `docs/**` | 23 current files | `docs/**` | Public documentation root stays. Update every link and command; add this mapping document and later add the final structural/history validation contract. The mapping document is an intentional old-path record and is allowlisted only in stale-path scanning. |
| `engine/**` | 4 | `workspace/engine/**` | Merge the existing engine boundary docs into the Template-aligned technical implementation folder. Its `media/`, `transcription/`, and `motion-adapters/` seams remain optional/local and do not become a second runtime. |
| `examples/**` | 1 tracked file | `examples/**` curated proof | Keep the root as a deliberate promotion boundary. `examples/README.md` is updated to describe curated standalone proof; operational ACS workspaces currently placed under ignored `examples/<slug>/` move to `workspace/productions/<slug>/`. |
| `footage/**` | 1 | `workspace/productions/**` | Move the tracked placeholder to the production boundary. Legacy source/transcript input is accepted by path-compatible adapters, but no `footage/` root alias remains because it violates the canonical shell. |
| `pyproject.toml` | 1 | `pyproject.toml` | Root toolchain-manifest exception. Change only package discovery/data paths and test/tool metadata needed by the move; keep project name, repository identity, dependencies, and installed command names. |
| `requirements/**` | 1 | `workspace/engine/requirements/**` | Optional local-transcription dependency list is technical toolchain material. It is never a runtime cloud or AIOS dependency. |
| `scripts/**` | 12 | `workspace/engine/scripts/**`, with `check-system-shell.py` merged into `workspace/engine/checks.py` | Preserve script flags and local-only behavior. Update repository-root calculations and all path defaults. The System Template-required `checks.py` becomes the single structural/stale-path guard and incorporates ACS naming checks. |
| `templates/**` | 6 | `workspace/engine/templates/**` | Keep video brief, cut, packaging, final review, project, and reference-analysis templates co-located with the technical workflow helpers; update all links to persistent state. |
| `tests/**` | 9 | `workspace/engine/tests/**` | Preserve all 41 existing tests and fixtures, updating only import/root/path discovery required by the move. Add isolated structural, ledger, recovery, and repeatability tests beside them. |
| `video-projects/**` | 29 | `workspace/engine/motion-adapters/video-projects/**` | Preserve each HyperFrames project and its local `AGENTS.md`, design, assets, compositions, metadata, and package files. It remains an optional adapter; no ACS CLI or System Template tracer imports it. |

The split `channel/` row covers all six current paths, and the split `scripts/`
row covers all twelve current paths. Together with the exact root rows and
closed descendant rules, every tracked path in the 142-path inventory has one
destination or an explicit root exception.

### Implementation-file detail

The high-risk implementation moves are intentionally explicit:

| Current path family | New path family | Required path-preserving change |
| --- | --- | --- |
| `agentic_content_system/*.py` | `workspace/engine/agentic_content_system/*.py` | Keep module names, relative imports, `__main__.py`, and CLI command behavior. Update only repository-relative schema/data lookup where the new parent depth changes it. |
| `contracts/README.md`, `contracts/__init__.py`, `contracts/schemas/*.json` | `workspace/engine/contracts/...` | Keep all nine schema filenames and `schema_version` values. `pyproject.toml` discovers `contracts*` from `workspace/engine`. |
| `engine/README.md`, `engine/media/README.md`, `engine/transcription/README.md`, `engine/motion-adapters/README.md` | `workspace/engine/...` | Retain the engine boundary documentation, but describe the new package/scripts/tests/adapters locations. |
| `scripts/check-system-shell.py` | `workspace/engine/checks.py` | Combine the current canonical-identity/stale-language guard with the Template shell, ledger, and curated-example checks. Exclude only this mapping record from old-path checks. |
| `scripts/check-projects.sh` | `workspace/engine/scripts/check-projects.sh` | Keep the compatibility filename if useful, but validate `workspace/productions/*` contract workspaces and invoke the new adapter check path. |
| `scripts/check-motion-adapters.sh` | `workspace/engine/scripts/check-motion-adapters.sh` | Check `workspace/engine/motion-adapters` and its moved HyperFrames project children. |
| `scripts/analyze-reference-video.py` and reference helpers | `workspace/engine/scripts/...` | Write durable metadata/transcript/analysis/prompt files under `workspace/references/<slug>/`; keep media/frame downloads ignored. |
| `scripts/transcribe-local-whisper.py` and setup/cleanup helpers | `workspace/engine/scripts/...` | Retain local Whisper as the default optional adapter, update repo-root and cache paths, and accept `workspace/productions/<slug>` plus direct source paths. No key or cloud service is added. |
| `scripts/create-fixture-media.py`, `new-content-example.py`, `new-video.py` | `workspace/engine/scripts/...` | Keep deterministic fixture and CLI scaffolding behavior. Default new content to `workspace/productions/<slug>`; retain `new-video.py` only as a documented compatibility wrapper. |
| `tests/fixtures/**` and `tests/test_*.py` | `workspace/engine/tests/...` | Preserve fixture bytes and test intent. Change repository-root calculation and temporary run locations from `footage/test-runs` to ignored `workspace/productions/test-runs`. |
| `templates/*.md` | `workspace/engine/templates/*.md` | Preserve template names and fields; update references to the new channel, learning, reference, production, and adapter locations. |
| `video-projects/<slug>/**` | `workspace/engine/motion-adapters/video-projects/<slug>/**` | Preserve each nested project-local instruction file. Update its root design reference and run optional `npm run check` from the moved directory only when the adapter is in scope. |

## Operational-state mapping

The System Template's `workspace/` is the persistent truth. ACS keeps its
domain-specific production contracts as a System extension without creating an
AIOS Project record, external state store, or shared cross-System contract.

| Existing ACS state or concept | Canonical ACS location | Ownership and lifecycle |
| --- | --- | --- |
| Clone profile, channel policy, cadence, delivery defaults | `workspace/channel/PROFILE.md`, `workspace/channel/brand.json` | Clone-owned defaults. `acs validate-profile workspace/channel/brand.json` validates them; `acs init --brand` copies the policy into a production workspace, whose `brand.json` is execution truth. |
| Style guide, stable design, published performance | `workspace/channel/STYLE_GUIDE.md`, `workspace/channel/DESIGN.md`, `workspace/channel/published-videos.csv` | Persistent channel state. It is read before planning/review and updated only for durable evidence. |
| Shared brand assets | `workspace/channel/assets/` | Reusable tokens and brand assets only; raw A-roll stays in a production. |
| Content format library | `workspace/content-formats/formats.json` | ACS-owned planning reference, kept inspectable and independent of the runtime package. |
| Ideas, selected ideas, packaging pipeline | `workspace/content-pipeline/ideas.md`, `selected/`, `published/` | Lightweight Markdown pipeline. It remains a file contract, not a hosted application. |
| Current `examples/<slug>/` ACS workspaces and ignored proof outputs | `workspace/productions/<slug>/` | Persistent content production boundary. Keep all existing ACS contract and generated-output subpaths and hashes inside the production. |
| Legacy `footage/<slug>/` source-side layout | `workspace/productions/<slug>/` with `sources/`, `transcripts/`, and local session notes | A migration adapter may read old caller-supplied paths, but new writes and documentation use the production boundary. Do not preserve a visible `footage/` directory. |
| Curated reviewable examples | `examples/<slug>/README.md` and `examples/<slug>/proof.json` | Promotion output only. It must be standalone and refer to a source production/run without becoming operational truth or a second database. |
| Reference index and analyzed references | `workspace/references/REFERENCES.md` and `workspace/references/<slug>/` | Durable analysis library. Ignored downloads, frames, local Whisper data, and media remain ignored below this boundary. |
| Global durable memory and motion lessons | `workspace/learning/PROJECT_MEMORY.md`, `workspace/learning/MOTION_PHILOSOPHY.md` | Small, human-readable learning. A production's factual session notes remain in its own `learning.json` or notes file. |
| Run evidence for a completed, failed, or recovered route | `workspace/runs/<run-id>/` | One structured evidence directory per run containing references/outputs/proof and failure or recovery evidence. It points to production-owned artifacts rather than copying raw input text. |
| Append-only relation between runs | `workspace/history/runs.jsonl` | One JSON object per run with the Template fields: run ID, timestamps, status, input/output/proof references, previous run relation, failure, and recovery. Never rewrite a failed record; recovery is a new run. |
| ACS Python, FFmpeg/ffprobe boundary, schemas, scripts, tests, templates, requirements, and optional adapters | `workspace/engine/` | Technical implementation only. It is not a new AIOS concept and is not imported by AIOS or the System Template tracer. |

### Run/history contract to add after review

The current ACS pipeline's `results/run-result.json` remains the caller-agnostic
production proof. In addition, the System Template-shaped local tracer will
record a small ledger relation when an ACS route is intentionally run:

```json
{
  "run_id": "run-0001",
  "started_at": "<fixed or explicit UTC timestamp>",
  "finished_at": "<fixed or explicit UTC timestamp>",
  "status": "succeeded | failed",
  "input_ref": "workspace/productions/<slug>/project.json",
  "output_ref": "workspace/productions/<slug>/results/run-result.json",
  "proof_ref": "workspace/productions/<slug>/reports/review.json",
  "previous_run_id": null,
  "previous_run_relation": null,
  "failure": null,
  "recovery": null
}
```

The exact ACS route may use a different run ID namespace after review, but the
fields and rules stay Template-compatible: no raw request text in the ledger,
`predecessor` for ordinary continuation, `recovery` for an explicit recovery,
and at most one recovery record for an unresolved failed run. The tracer is a
proof tool, not a daemon or a required ACS runtime service.

## Python package and CLI compatibility

The compatibility mechanism is packaging configuration, not a second root
package:

1. Move the source package to `workspace/engine/agentic_content_system/` and
   the local `contracts` package to `workspace/engine/contracts/`.
2. Keep root `pyproject.toml` and set setuptools' package discovery `where` to
   `workspace/engine`, including `agentic_content_system*` and `contracts*`.
   Keep schema package data available in the installed distribution.
3. Leave these public entry points unchanged:

   ```text
   acs <command> ...
   agentic-content-system <command> ...
   python -m agentic_content_system <command> ...
   ```

   The documented setup already creates and installs the repository in a
   virtual environment before invoking the module form. CI does the same. A
   source-tree-only test invocation may set `PYTHONPATH=workspace/engine`, but
   no root `agentic_content_system/` compatibility directory is retained.
4. Keep `agentic_content_system.__version__`, `__main__.py`, the CLI command
   names, argument shapes, exit codes, contract paths inside a production, and
   `contracts` schema import behavior unchanged.
5. Preserve `acs init`'s ability to receive an arbitrary workspace path. Only
   the documented/default clone profile and example scaffolding path change to
   `workspace/channel/brand.json` and `workspace/productions/<slug>`.

This preserves installed package behavior and the public CLI without adding an
AIOS package, caller ID, network client, database, or automatic publisher.

## Documentation and skill link-update plan

No linked document is rewritten at the mapping boundary. During the reviewed
implementation, update these groups in one documentation pass and then run a
tracked-text path scan:

| Files or surfaces | Link/wording update |
| --- | --- |
| `AGENTS.md`, `README.md`, `docs/QUICKSTART.md`, `docs/CLI.md`, `docs/WORKFLOW.md` | Make `workspace/channel/brand.json`, `workspace/productions/<slug>`, `workspace/engine/scripts/...`, and curated `examples/` the canonical command paths. Keep install-before-module invocation and no-posting language. |
| `docs/ARCHITECTURE.md`, `docs/INPUT_OWNERSHIP.md`, `docs/CONTENT_FORMATS.md`, `docs/ADAPTERS.md`, `docs/EDITOR_ENGINE_DECISION.md` | Describe `workspace/` operational truth, `workspace/engine/` implementation, local production contracts, and optional adapters without an AIOS runtime or shared schema. |
| `DESIGN.md`, `PROJECT_MEMORY.md`, `MOTION_PHILOSOPHY.md`, `channel/*` | Move content to the mapped workspace locations and update all read order/profile/learning references. Keep reference analysis separate from production execution truth. |
| `docs/BRANDING.md`, `docs/LEARNING.md`, `docs/PACKAGING.md`, `docs/FINAL_REVIEW.md`, `docs/PROMPTS.md` | Update brand, learning, reference, template, packaging, and review paths; distinguish global channel learning, production notes, and curated examples. |
| `docs/REFERENCE_ANALYSIS.md`, `docs/LOCAL_TRANSCRIPTION.md`, `docs/CLOUD_TRANSCRIPTION.md`, `docs/CODEX_PLUGIN_SETUP.md`, `docs/REAL_VIDEO_ACCEPTANCE.md`, `docs/RECOVERY.md` | Update script paths, reference output paths, production source paths, ignored artifact paths, and safe cleanup/recovery instructions. Preserve local Whisper as default and credentials-outside-repository rules. |
| `docs/CI.md`, `.github/workflows/ci.yml`, `scripts/check-system-shell.py` content | Move structural/test command references to `workspace/engine`, retain the 3×4 OS/Python matrix, and separate configuration evidence from live pushed CI evidence. |
| `.agents/skills/agentic-content-system/SKILL.md` | Keep it the ACS primary entry point and route through channel defaults → production workspace → inspect/approve/render/package/proof, plus the run ledger/recovery references. It must not require AIOS. |
| `.agents/skills/setup-content-system/SKILL.md` and `audit-content-system/SKILL.md` | Update profile, command, scope, and read-only audit paths. Setup still stops before a production; audit still never runs write-capable proof commands. |
| `templates/*.md` and all nested HyperFrames `AGENTS.md`/`DESIGN.md` | Update references to workspace channel/learning state and moved adapter paths. Preserve HyperFrames-specific rules and optionality. |
| `docs/REPOSITORY_IDENTITY.md`, `docs/GITHUB_DESCRIPTION.md` | Keep canonical ACS identity and accurate historical redirects. Do not change remote metadata or redirect state at this mapping/build boundary. |

The final scan must allow only intentional historical repository aliases in
`docs/REPOSITORY_IDENTITY.md` and intentional old-path rows in this mapping
document. It must not allow old implementation roots in executable code,
instructions, skills, templates, CI, or current examples.

## Tests, CI, and toolchain path update plan

| Evidence | Migration action and acceptance |
| --- | --- |
| Existing deterministic suite | Move `tests/` to `workspace/engine/tests/` and preserve the current 41 test cases and fixture bytes. The post-move baseline must still be exactly 41 passing before new structural tests are counted. |
| System Template structural proof | Add/adapt `workspace/engine/checks.py`; it must enforce only `workspace/`, `examples/`, and `docs/` as visible functional roots; require the shell, workspace placeholders, history ledger, engine tracer/checks/tests, and curated-proof shape; reject stale root paths and stale runtime/dependency language. |
| System Template history/repeatability proof | Add/adapt `workspace/engine/tracer.py` and isolated tests. A clean temporary copy must produce deterministic success, failure, recovery, append-only ledger, deliberate example promotion, and a second full test pass without changing the source checkout's live history. |
| ACS engine proof | Run the unchanged ACS inspect → transcript → approve → render → derive → package → verify → review → export path against a tiny ignored fixture under `workspace/productions/<slug>`. Do not use a write-capable proof command as an audit step. |
| CLI/package proof | Run editable installation from root, `acs --help`, `python -m agentic_content_system --help`, package version/import checks, and schema loading from the installed package. Verify `project.scripts` names and exit behavior remain unchanged. |
| CI | Keep root `.github/workflows/ci.yml`; update test discovery to `workspace/engine/tests`, structural checks to `python3 workspace/engine/checks.py`, and optional motion checks to `workspace/engine/scripts/check-motion-adapters.sh`. Run package install before module imports. |
| Local checks | Run `git diff --check`, the new structural guard, deterministic tests, optional adapter checks when Node/HyperFrames prerequisites are present, and the path/AIOS scan. Report unavailable OS matrix results as unavailable, never as passed. |
| Toolchain | Keep `pyproject.toml` as the root build manifest. Move only the optional transcription requirements file under `workspace/engine/requirements`; no runtime dependency is added. |

The mapping boundary's untouched baseline is deliberately separate from the
future Template tests: it proves that the current implementation starts from
41/41 before any move.

## Stale-path and no-regression checks

After the move, `workspace/engine/checks.py` and a read-only CI shell check must
cover all of the following:

- enumerate visible root entries and allow only `workspace/`, `examples/`,
  `docs/`, root `AGENTS.md`/`README.md`, root toolchain manifests, and hidden
  configuration/CI;
- reject old visible roots including `agentic_content_system/`, `assets/`,
  `channel/`, `content-formats/`, `content-pipeline/`, `contracts/`,
  `engine/`, `footage/`, `requirements/`, `scripts/`, `templates/`,
  `tests/`, and `video-projects/`;
- verify that every public current path resolves to its `workspace/` or
  `examples/` destination and that no symlink substitutes for a functional
  root;
- scan executable code, current docs, skills, templates, CI, and curated
  examples for stale root paths, old product names, accidental shared-schema/
  package/database/runtime-dependency claims, and automatic-posting claims;
- allow the explicit old-to-new rows in this file and accurate historical
  redirect names in `docs/REPOSITORY_IDENTITY.md` only;
- verify `pyproject.toml` has no AIOS dependency, package discovery reaches the
  moved package/contracts, and no runtime module imports an AIOS package;
- verify the publisher handoff remains `not_posted: true` and
  `external_posting: false`, and that no command turns delivery intent into an
  external post;
- verify the 41 existing tests, the new structural/history tests, and the
  actual CLI/FFmpeg proof all use local files and standard bounded tools.

The scan must distinguish an optional AIOS caller described in prose from a
runtime dependency. ACS may receive resolved context from a caller, but the
receiving production remains independently valid and inspectable.

## Migration ordering

The reviewed implementation should proceed in these bounded phases:

1. Record a clean pre-migration tree and preserve the separate clean local feat
   checkout at `849916fb29421c0402664c8c54a09b56a22deffd`; do not inspect,
   modify, or use it as a source. Keep this mapping commit as the review
   boundary.
2. Add the Template-shaped workspace skeleton and placeholders:
   `workspace/README.md`, `workspace/history/runs.jsonl`,
   `workspace/learning/.gitkeep`, `workspace/runs/.gitkeep`,
   `workspace/productions/.gitkeep`, and the mapped channel/content/reference
   directories. Do not change CLI behavior yet.
3. Move the Python package, local contracts, existing engine docs, optional
   requirements, scripts, templates, tests, and motion adapters with
   `git mv`. Update only the minimum package/root calculation needed to keep
   import and CLI smoke tests green.
4. Move channel state, content formats, content pipeline, reference state,
   learning files, assets, and the legacy placeholder under `workspace/`.
   Migrate any local ignored production data only after listing it and
   preserving source hashes; do not silently delete source media or generated
   proof.
5. Move operational workspaces from the ignored `examples/<slug>/` convention
   to `workspace/productions/<slug>/`, leaving root `examples/` for deliberate
   curated proof. Update scaffolding, cleanup, transcript, reference, and
   packaging defaults together so no half-migrated path is canonical.
6. Update all docs, skills, templates, nested adapter instructions, CI, and
   `.gitignore` paths. Add the structural checks/tracer and their isolated
   tests only after the destination shell is complete.
7. Run the pre-existing 41-test baseline, structural/stale-path checks, new
   history/repeatability tests, package/CLI checks, and the bounded ACS media
   proof. Inspect the resulting diff and path inventory before review.
8. Stop at the Build/review boundary. Accept lead Review revisions, repeat all
   required checks from a clean state, and do not Ship until a fresh PASS is
   explicitly available. PR/merge/push and destination verification are
   outside this mapping-only boundary.

## Rollback, recovery, and data safety

- Tracked moves are reversible `git mv` operations recorded in implementation
  commits. If review or validation fails, correct forward or revert the
  migration commit; do not erase history with a hard reset and do not rewrite
  the append-only run ledger.
- The known pre-migration reference is
  `0344d1daefa9286c040cfb86e47bb9eeee4cc401`. It is a recovery reference, not
  authorization to mutate another checkout or to discard user work.
- Before moving any ignored production/source directory, record its exact
  source path, destination, file list, and SHA-256 values. A failed copy/move
  restores from that explicit inventory; generated outputs can be rebuilt from
  contracts and source references, while owner source media is never treated as
  disposable.
- The existing ACS `recovery/` behavior remains the safe production-level
  cleanup path. `workspace/runs/` and `workspace/history/runs.jsonl` add
  Template-shaped failure/recovery evidence; they do not replace production
  contracts or manually rewrite failed records.
- If a package or proof step fails, preserve the prior valid production result
  and use the existing atomic package/review/result recovery rules. Do not
  manufacture a PASS from a stale report or unavailable OS result.
- No AIOS, System-template, Design-template/ADS, issue, remote metadata, or
  other-repository file is changed by this plan. No credentials or environment
  values are read.

## Unresolved decisions and risks for Review

1. The exact run-trigger point for appending an ACS ledger record needs lead
   Review: the proposed default is one record per intentional production route
   attempt, with `results/run-result.json` remaining the production proof.
2. Existing ignored local examples/proof may be outside Git's 142-path
   inventory. Their migration must be explicit and hash-checked during Build;
   this mapping commit does not discover or move them.
3. Moving public support scripts from `scripts/...` to
   `workspace/engine/scripts/...` changes direct path invocations. Installed
   ACS CLI entry points are preserved; the final docs and any compatibility
   wrappers must make the script-path migration unambiguous.
4. The package-discovery and schema-data layout must be tested from a fresh
   editable install on macOS, Linux, and Windows CI. A passing local import is
   not evidence for all OSes.
5. Optional HyperFrames projects need their moved relative paths and root
   design references checked only when Node/adapter prerequisites are available;
   they must not become an ACS runtime dependency.
6. The unauthenticated read-only API lookup for the supplied
   `AIOS-template#28` URL returned 404 in this environment. The ACS issue
   comment and the pinned shipped System Template tree establish the operative
   mapping here; Review should confirm whether the inaccessible issue contains
   any additional decision before implementation.

## Mapping-document validation and baseline evidence

The document must be checked against the source tree before its commit with:

```sh
git ls-tree -r --name-only HEAD | wc -l
git ls-tree --name-only HEAD
for root in $(git ls-tree --name-only HEAD); do
  rg -F -- "$root" docs/SYSTEM_TEMPLATE_MAPPING.md
done
git diff --check
git diff --name-only
```

The expected pre-document inventory is 142 tracked paths and the root list
represented in the exhaustive table above. `git diff --name-only` must contain
only `docs/SYSTEM_TEMPLATE_MAPPING.md`; no implementation or configuration
path is authorized at this boundary.

Untouched baseline command and exact result:

```text
Command: python3 -m unittest discover -s tests -v
Result: 0 (OK)
Ran 41 tests in 25.769s
```

The CI spelling `python -m unittest discover -s tests -v` was also attempted
in this shell and returned exit 127 because `python` is not installed under
that executable name. It is a command-name availability issue, not a test
failure; the repository-equivalent `python3` command above is the recorded
baseline. `python3 scripts/check-system-shell.py` and `git diff --check` passed
before this document was created.

This document is ready for lead Review only. It is not authorization to enter
Build, move paths, push, create a PR, comment on an issue, merge, or verify a
remote destination.
