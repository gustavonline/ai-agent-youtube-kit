---
name: agentic-content-system
description: "Run a local-first Agentic Content System workspace from bounded context through approved media proof and publish-ready handoff."
---

# Agentic Content System Skill

This workspace-local skill is the orchestration/interface layer for the
Agentic Content System. The skill is not the product by itself: the JSON
contracts, CLI, source files, proof artifacts, and human approval state remain
the product surface.

## Any useful context, then local ownership

Accept useful context from a conversation, Markdown brief, client note, AIOS
Space task, or an existing workspace. It may be rough or resolved. The judgment
layer chooses only what this run needs and copies the resolved values into an
ACS-owned workspace with `acs init`:

- `brand.json`: channel policy, enabled/disabled reasons, and cadence;
- `project.json`: content decision, source rights/provenance, transcript
  reference, and per-enabled-route `delivery_intent`;
- `content-brief.md` and `recording-plan.md`: the pre-capture script/outline;
- `edit-plan.json`: ordered segments and explicit approval.

Once copied, the receiving ACS workspace is canonical for execution truth. The
upstream source is not a runtime or schema dependency. Optional files under
`context/` are human/source notes only; ACS does not parse, validate, hash, or
execute them. There is no shared maintained AIOS↔ACS input or return schema.

If AIOS is present, the persistent Space may own durable company, offer, buyer,
channel defaults, and learning. A task-level caller maps a resolved decision to
`acs init`; ACS executes independently; the caller reads local proof and
learning back through its normal task flow. This skill is the run interface,
not the product.

Read `docs/ARCHITECTURE.md`, `docs/INPUT_OWNERSHIP.md`,
`docs/CONTENT_FORMATS.md`, and `docs/CLI.md` before planning a new content
workspace.

Before planning an ordinary repeat or explicit recovery, inspect the relevant
prior records in `workspace/history/runs.jsonl` and the referenced
`workspace/runs/<run-id>/run.json` evidence. Choose `predecessor` for an
ordinary repeat or one explicit `--recover <run-id>` for a deliberate recovery
based on that evidence.

## Execution sequence

1. Start from configured clone defaults with
   `python -m agentic_content_system init <workspace> --brand workspace/channel/brand.json`.
   Generic `init <workspace>` remains valid when a starter policy is enough.
2. Use bounded context and format guidance to draft/refine
   `content-brief.md` and `recording-plan.md` before capture. Carry the
   promise, proof, three-point plan, contextual CTA, and chosen format into
   `project.json` and `edit-plan.json`. ACS does not embed cloud AI; Codex or
   another agent is the judgment layer.
3. Put media under the workspace `sources/` folder and complete rights/provenance
   in `project.json`.
4. Set `project.json.delivery_intent` for every enabled route: `manual`
   (no date) or `scheduled` with an explicit date/time and timezone. Disabled
   channels can never become publisher routes.
5. Run `inspect`, ingest an open transcript JSON, local Whisper JSON, Markdown,
   SRT, or VTT, and select ordered edit segments.
6. Have a human or explicitly designated reviewer run `plan --approve --by
   <name>`; the approval hash covers current policy, provenance,
   delivery intent, edit intent, and source bytes.
7. Run `render`, `derive`, `package`, `verify`, `review-report`, and
   `export-result`.
8. Return proof paths/hashes, enabled/disabled route results, and the
   `publish/publisher-handoff.json` path/hash/status to the calling context. Do
   not post externally.
9. After the complete route succeeds or fails, record exactly one deliberate
   attempt with `python workspace/engine/tracer.py record
   workspace/productions/<slug> --status succeeded|failed`. Low-level ACS CLI
   subcommands do not create ledger records. Use `--recover <run-id>` only for
   one explicit recovery of an unresolved failed attempt.
   The append-only relation is `workspace/history/runs.jsonl`, and evidence
   directories are kept under `workspace/runs/`.

After a successful full route, promotion to `examples/` is optional and
deliberate only: use `python workspace/engine/tracer.py promote-example
--run-id <id> --slug <slug>`. Never promote automatically; examples are
curated proof, not operational state.

Re-run `inspect` after changing a declared source, its rights/provenance,
kind/role, or source order. Verification, review reports, and proof export bind
the inspection claims to those current inputs. If the transcript changes after
a LinkedIn derivative is registered, run `derive` again to regenerate or
explicitly re-register the reviewed post before packaging.

`render`, `derive`, and `package` are approval-gated. Re-running them is safe:
renders use a content/hash record, derivatives are deterministic, and package
routes and publisher delivery intent are rebuilt from the current enabled-
channel policy. Package installation stages the manifest and publisher
handoff atomically and invalidates old generated review/result claims only
after success.

## Editorial defaults

Use promise + proof + plan, usually three points. Pull ideas from work/client
questions, mistakes, proof, mechanism, and philosophy. Treat attention,
nurture, and conversion as connected outcomes. Harvest a core video into only
the derivatives that fit an enabled channel. Vlog is a minority format, about
5–20%, unless the workspace has a documented reason to differ.

## Failure/recovery

Read the CLI error, fix the contract or local prerequisite, and rerun the
smallest command. Use `acs clean <workspace> --outputs` to remove generated
outputs while preserving inputs and decisions. Never solve a disabled-channel
failure by silently adding a route; update policy and obtain the appropriate
approval.
