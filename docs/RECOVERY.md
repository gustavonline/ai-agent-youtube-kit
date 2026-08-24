# Recovery And Clean Operations

Generated work is recoverable from the declarative contracts and source
references. The safe reset command is:

```text
acs clean path/to/workspace --outputs
```

It removes `renders/`, `derived/`, `publish/`, `reports/`, `results/`, and
`inspection.json` only. It preserves `brand.json`, `project.json`,
`edit-plan.json`, `sources/`, and `transcripts/`. Re-run `inspect`, `render`,
`derive`, `package`, `verify`, and `review-report` after checking the plan.

If a render fails, inspect the source with `acs inspect` and run `acs doctor`.
If a package fails verification, do not manually edit the manifest: rerun
`acs package` after fixing the source, plan, or channel policy. A disabled
channel must be enabled with a reason in `brand.json` before it can receive a
route.

After changing a declared source, its rights/provenance, kind/role, or the
source order, rerun `acs inspect`; verification and static proof reject stale
inspection claims. After changing the active transcript, rerun `acs derive` so
the LinkedIn derivative record carries the current transcript hash. Disabling
an edit output archives its old bytes under `recovery/disabled-renders/` and
removes it from active render records.

If a package exists, `acs review-report` revalidates the complete current
package before replacing the active report. A stale approval, policy,
provenance, render, derivative, handoff, asset, or verification binding leaves
the prior report untouched and requires the smallest relevant rebuild.

Publish-ready packaging and verification require every source to have one of
these cleared rights statuses: `owned`, `licensed`, `public-domain`, `cc0`, or
`cc-by`. `permission-pending` and `unknown` remain valid for draft, inspect,
and edit work but cannot enter the publish-ready handoff.

After a new package is installed, the active review HTML/record and run result
are intentionally absent until `acs review-report` and `acs export-result` are
rerun. The package's manifest and publisher handoff are installed together;
failed replacement restores the prior package and its generated claims. If an
export fails while an older result exists, the older result is moved to
`recovery/stale-results/` and is not an active caller result.

Record the route outcome once after the complete attempt with
`workspace/engine/tracer.py`. A failed route remains immutable in
`workspace/history/runs.jsonl`; a normal repeat points to its predecessor, and
an explicit recovery points to one unresolved failed run and cannot consume it
again. The tracer evidence references production-owned proof and does not copy
raw prompts or request text. Do not rewrite or delete the ledger during
cleanup.

Ignored local runtime artifacts from the existing Whisper workflow remain
available through `workspace/engine/scripts/clean-local-artifacts.sh`; that script is separate
from project-output cleanup.
