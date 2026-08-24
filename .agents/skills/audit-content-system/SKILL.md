---
name: audit-content-system
description: "Audit an Agentic Content System repository or one named content workspace for health, truth, current proof, contract drift, readiness, or recovery risk. Use when asked to audit, check, health-check, reconcile, investigate drift, or assess readiness, especially periodically, before handoff, or when proof may be stale."
---

# Audit Content System

Use this skill as a periodic, holistic backstop for an evolved Agentic Content
System repository or one explicitly named content workspace. It is not a new
lifecycle phase and is not mandatory after every trivial change.

Keep the audit strictly read-only. Do not repair, edit, render, derive,
package, verify, create a review report, export a result, clean, publish,
transfer, or otherwise mutate. Do not run `acs verify`, `acs review-report`, or
`acs export-result` during an audit: those commands can write current state and
are not audit-safe. Do not create a second audit engine when the existing ACS
commands and repository checks provide evidence.

## Set scope

State one scope before inspecting anything:

- repository: shell, contracts, docs, skills, dependencies, tests, CI, and Git
  state;
- one named workspace: that workspace's local contracts, declared sources, and
  existing proof; or
- both: the repository plus that one named workspace.

Never silently scan every client or workspace. If the requested workspace,
authority, or required input is unavailable, report `BLOCKED`; do not broaden
the scope or manufacture evidence.

## Gather safe evidence

Read current truth rather than template parity. For a repository audit, read
`AGENTS.md`, `README.md`, the run skill, relevant `docs/`, package metadata,
schemas, scripts, tests, and CI. Check the documented ownership boundary,
canonical commands, enabled routes, and the distinction between ACS execution
truth and upstream context. Use read-only checks such as:

```text
python -m agentic_content_system --help
python -m agentic_content_system --version
python -m agentic_content_system doctor
python workspace/engine/checks.py
PYTHONPATH=workspace/engine python -m unittest discover -s workspace/engine/tests -v
git status --short --branch
git diff --check
```

Run only checks that are available in the checkout and disclose skipped or
unavailable checks. Compare cross-platform claims with actual local or CI
evidence; configuration alone is not an OS result. Run optional networked or
slow motion-adapter checks only when relevant to the stated scope, and record
when they were skipped.

For a named workspace, inspect its current `brand.json`, `project.json`,
`edit-plan.json`, transcript, inspection, render record, derivatives,
`publish/manifest.json`, `publish/publisher-handoff.json`, reports, and
results. Use `acs validate <workspace>` (or `--contracts-only` for an empty
scaffold) only as a read-only validation check. Inspect source paths and
SHA-256 values without changing files. Reconcile:

1. outcome, ownership, content decision, capture format, and valid routes;
2. skill metadata/frontmatter and documented command truth;
3. Python/FFmpeg/ffprobe readiness and bounded dependency claims;
4. declared source order, rights/provenance, approval, inspection, and
   currentness bindings;
5. existing render, derivative, package, review, and result proof without
   regenerating it;
6. delivery intent, enabled routes only, disabled-route reasons, and absence
   of disabled routes from the publisher handoff;
7. `external_posting: false`, `not_posted: true`, and separate authorization;
8. secrets, private paths, arbitrary shell execution, failure visibility, and
   proportional recovery/stop paths.

Treat an existing file or a status word as insufficient by itself. Hash the
bytes that are safe to inspect and compare them with the stored bindings,
manifest, approval, policy, provenance, and review/result records. Missing
evidence is not PASS. A contradictory or defective current state is `FAIL`;
missing authority, access, or required input is `BLOCKED`.

## Return the audit

Return exactly one top-level result in this order, with concise evidence:

```text
Result: PASS | FAIL | BLOCKED
Scope: repository, one named workspace, or both
Checks:
- check: evidence and status
Evidence gaps:
- missing, skipped, or unavailable proof; write “none” only when none remain
Smallest next action:
- one safe, bounded action for the owner or judgment layer
```

Use `PASS` only when every in-scope check has current evidence. Use `FAIL`
when accessible current truth is contradictory, unsafe, stale, or defective.
Use `BLOCKED` when the audit cannot establish truth because authority, access,
or required input is unavailable. Do not fix the finding inside the audit;
return the smallest next action and leave all inputs and generated artifacts
unchanged.
