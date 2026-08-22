# CLI

The stable invocation is either the installed `acs` command or the portable
module form:

```text
python -m agentic_content_system <command> <workspace>
```

The module form works from a checkout on macOS, Linux, and Windows without
POSIX shell features. Create a repo-local venv first, then install with the
venv interpreter (`.venv/bin/python -m pip install -e .` or
`.venv\Scripts\python.exe -m pip install -e .`). Never ask users to modify
system/Homebrew Python.

## Core flow

```text
acs validate-profile channel/brand.json
acs init <workspace> --brand channel/brand.json
acs inspect <workspace>
acs validate <workspace>
acs ingest-transcript <workspace> <transcript.json>
acs plan <workspace> --approve --by <reviewer>
acs render <workspace> --kind all
acs derive <workspace>
acs package <workspace>
acs verify <workspace>
acs review-report <workspace>
acs export-result <workspace>
```

`render`, `derive`, and `package` stop with an understandable error until the
edit plan is explicitly approved. `package` includes only enabled channels;
disabled channels remain visible with their policy reason. A successful package
installation invalidates the active `reports/review.html`, bound
`reports/review.json`, and `results/run-result.json`; rerun `verify`,
`review-report`, and `export-result` for the new package. With no manifest,
`review-report` may produce a valid `not_packaged` review; once a manifest
exists it rechecks the complete current package before replacing any report
bytes and fails closed on stale approval, policy, provenance, renders,
derivatives, handoff, assets, or verification. No command invokes a shell
string from a JSON input.

`acs init` is the canonical scaffold for every run. The judgment layer may use
context from a conversation, brief, AIOS task, or another source, then copies
only resolved values into the ACS-owned `brand.json`, `project.json`,
`content-brief.md`, `recording-plan.md`, and `edit-plan.json`. `context/` may
hold optional notes but is not read by the runtime. `derive` creates only
policy-allowed derivatives and never overwrites an existing post. The
workspace-owned `delivery_intent` sets each enabled route to `manual` or
`scheduled` with an explicit date/time and timezone. A clone may store manual or
scheduled defaults in `channel/brand.json`; the copy in a workspace is execution
truth and can be changed as run-specific intent in `project.json`.

`package` stages `manifest.json` and the versioned
`publisher-handoff.json` together and atomically installs the package. The
publisher handoff contains enabled asset/post references, delivery intent,
manifest/asset hashes, `awaiting-separate-authorization`, `not_posted: true`,
and `external_posting: false`. `verify` rejects missing, stale, tampered, or
disabled-route handoff state. `verify`, `review-report`, and `export-result`
also require `inspection.json` to exactly match the current declared source
order, bytes, rights/provenance, kind/role, and ffprobe claims. A review record
stores that inspection hash. `export-result` requires that current handoff,
review, verification, inspection, and manifest bindings agree, then returns the
handoff path/hash/status in the versioned result.

If the transcript changes after a LinkedIn derivative is registered, package
fails closed until `acs derive` is run again to regenerate or explicitly
re-register the reviewed post. If an edit output is later disabled, `acs
render`, `package`, or `review-report` removes it from the active render record
and archives the bytes under `recovery/disabled-renders/`.

Useful supporting commands:

- `acs doctor [--json]` checks Python and FFmpeg/ffprobe. Whisper is optional.
- `acs plan <workspace> --diff` shows the current plan against its previous snapshot.
- `acs validate <workspace> --contracts-only` validates an empty scaffold before media is added.
- `acs clean <workspace> --outputs` removes `renders/`, `derived/`, `publish/`,
  `reports/`, `results/`, and `inspection.json` while preserving contracts,
  sources, and transcripts.

`derive` and `package` have no `--force` flag: they proceed only when their
current approval and input bindings are valid. Use `render --force` only for
an explicit deterministic rerender.

Publish-ready packaging and verification require source rights status
`owned`, `licensed`, `public-domain`, `cc0`, or `cc-by`. Draft and inspect work
may retain `permission-pending` or `unknown`, but those statuses fail closed at
the publish gate.
