---
name: audit-content-system
description: "Audit an ACS repository or one named production for current file truth, graph validity, Studio readiness, and supervised handoff safety."
---

# Audit Content System

Audits are strictly read-only. State one scope: repository, one named
production, or both. Never scan every production silently.

For repository scope, read `AGENTS.md`, `README.md`, the local skills, core
docs, `package.json`, scripts, tests, CI, and Git state. Run only read-only
checks:

```text
npm test
npm run check:graph
npm run check:repository
git status --short --branch
git diff --check
```

For one production, inspect its artifacts, graph, review references, and
handoff, then run:

```text
node workspace/engine/scripts/check-content-graph.mjs <production>/content-graph.json [<production>/publisher-handoff.json]
```

Recompute hashes without changing files. Confirm node-level approval, optional
targets, explicit edges, and the four supervised/not-posted handoff invariants.
Missing evidence is not PASS.

When FreeCut readiness is in scope, use the `freecut-studio` skill's read-only
check. Report origin, pin, cleanliness, package manager, build, headless proof,
and public audit findings separately. Do not install, update, build, start, or
repair FreeCut during an audit.

Return exactly:

```text
Result: PASS | FAIL | BLOCKED
Scope: repository | one named production | both
Checks:
- evidence and status
Evidence gaps:
- gaps, or none
Smallest next action:
- one bounded action
```
