# Agentic Content System

Agentic Content System turns business context and raw footage into reviewed videos, posts, and a publish-ready handoff locally.

```text
business context -> brief -> capture -> approved edit -> video + posts -> review -> handoff
```

The public shell is intentionally small: `AGENTS.md`, this `README.md`,
`.agents/skills/`, `docs/`, `workspace/`, and curated `examples/`. Persistent
operational truth lives under `workspace/`; technical implementation, local
contracts, scripts, tests, templates, and optional adapters live under
`workspace/engine/`. Root `pyproject.toml` and hidden CI are toolchain
exceptions.

## Use it when

- an agent needs a transparent, repeatable content workflow for a business;
- a human needs local contracts, FFmpeg media proof, review files, and a supervised delivery handoff;
- AIOS or another caller can provide context, but the execution must remain standalone.

## Skip it when

- the job needs a hosted editor, dashboard, cloud processing, or automatic posting;
- there is no real content outcome yet; configure the clone first and create a workspace only when the outcome is known;
- the source rights, approval owner, or channel policy cannot be resolved.

## Agent-first start

Ask an agent:

```text
Set up this ACS clone for my business. Use any business, audience, offer,
content-promise, channel, cadence, and delivery context already available.
Ask only for missing decisions, update workspace/channel/PROFILE.md and workspace/channel/brand.json,
run doctor and profile validation, and stop before creating a content workspace.
When I give you a real content outcome, create it with the configured brand defaults.
```

The manual equivalent starts with:

```text
python3 -m venv .venv
.venv/bin/python -m pip install -e .
.venv/bin/python -m agentic_content_system doctor
.venv/bin/python -m agentic_content_system validate-profile workspace/channel/brand.json
.venv/bin/python -m agentic_content_system init workspace/productions/my-content --brand workspace/channel/brand.json
```

Windows PowerShell uses `.venv\Scripts\python.exe` for the same module
commands. `acs` is the equivalent installed command.

## Concrete outputs

- clone defaults: `workspace/channel/PROFILE.md`, `workspace/channel/brand.json`, and the reusable `workspace/channel/STYLE_GUIDE.md`;
- workspace execution truth: `brand.json`, `project.json`, `content-brief.md`, `recording-plan.md`, and `edit-plan.json`;
- local proof: inspected sources, immutable raw ASR, reviewed transcript truth, approved FFmpeg renders, optional caption sidecars, selected derivatives, and a static review report;
- supervised handoff: `publish/manifest.json`, `publish/publisher-handoff.json`, and `results/run-result.json`.

## Setup and ownership

The setup skill is the primary route for configuring a clone before its first
real video. `workspace/channel/brand.json` is the small ACS-owned source of durable
channel policy, cadence, and delivery defaults. `acs init --brand` validates it
before writing a copy into the new production workspace. That workspace `brand.json` is
execution truth; `project.json` owns run-specific content and delivery intent.
Use `.agents/skills/setup-content-system/SKILL.md` for setup and
`.agents/skills/audit-content-system/SKILL.md` for a strictly read-only audit.

AIOS is optional. It may own durable business or audience defaults and pass
resolved context in prose or files. ACS does not maintain an AIOS↔ACS JSON
handoff contract, caller IDs, database, API, or AIOS runtime dependency. The
package's only optional runtime helper beyond Python and FFmpeg is Pillow for
the portable burned-caption fallback.

## Tested boundary and current limitation

The v0.2 boundary is the cross-platform Python CLI, versioned JSON contracts,
FFmpeg/ffprobe, local transcript adapters, static reports, and explicit human
approval. `external_posting` remains `false`; the publisher handoff is
`not_posted: true` and awaits separate authorization. Full local tests and the
system shell check exercise this boundary without a server or cloud dependency.

Generated fixtures and the retained public-source run prove engine and
contract behavior. They do not prove owner usability: a real usability PASS
still requires the owner to run the protocol with owner-recorded footage.

Each deliberate full production-route attempt must append exactly one
structured record to `workspace/history/runs.jsonl` and write evidence under
`workspace/runs/<run-id>/`. Ordinary repeats link with `predecessor`; explicit
recovery consumes one unresolved failed run once. The ledger references
production proof and bounded failure/recovery facts; it never stores raw
requests and is not an AIOS service. Curated examples are promoted separately
with the local tracer and never become operational state.

## Lower-level CLI

```text
acs init <workspace> [--brand workspace/channel/brand.json]
acs validate-profile <brand-profile>
acs inspect <workspace>
acs validate <workspace> [--contracts-only]
acs ingest-transcript <workspace> <transcript>
acs review-transcript <workspace> <reviewed-transcript> --by <reviewer>
acs plan <workspace> --approve --by <reviewer>
acs render <workspace> --kind all
acs derive <workspace>
acs package <workspace>
acs verify <workspace>
acs review-report <workspace>
acs export-result <workspace>
```

Optional editor results enter through `acs import-adapter`; the output and its
JSON plan/manifest are copied into the production `adapters/` boundary,
hash-bound, and included in the ordinary package and result proof. They never
remain unproved side files.

Rendering and packaging are approval-gated. Re-run inspection after declared
source changes; re-approve after policy, project, delivery, or edit-plan
changes. Packaging includes enabled routes only and never posts.

`transcripts/raw.json` is immutable ASR/input evidence. `transcripts/reviewed.json`
is explicit reviewer-owned truth; captions and publish-ready text fail closed
when selected ranges are not covered or source bytes are stale. Configure
optional per-output captions in `edit-plan.json` under `captions.long` and
`captions.short`. A successful run writes `results/index.md` as the smallest
human-facing file index. `examples/` contains only deliberately promoted
demonstrations; production truth stays under `workspace/productions/`.

See `docs/REAL_VIDEO_ACCEPTANCE.md` for the generic owner-recorded protocol,
`docs/CLI.md` for command details, and `docs/ADAPTERS.md` for optional seams.
HyperFrames and legacy adapters remain below the ACS contract/FFmpeg boundary;
they are not the product identity.

The proposed GitHub repository description is recorded in
`docs/GITHUB_DESCRIPTION.md`; remote metadata is intentionally unchanged.
