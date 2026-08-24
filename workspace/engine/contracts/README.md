# Versioned Contracts

The schemas in `workspace/engine/contracts/schemas/` are the versioned shapes owned by the local
CLI. The project-facing files use the same `schema_version` field:

- `brand.json` -> `brand.schema.json`
- `project.json` -> `content-project.schema.json`
- `edit-plan.json` -> `edit-plan.schema.json`
- `transcripts/active.json` -> `transcript.schema.json`
- `publish/manifest.json` -> `publish-manifest.schema.json`
- `publish/publisher-handoff.json` -> `publisher-handoff.schema.json`
- `reports/review.json` -> `review-record.schema.json`
- `results/run-result.json` -> `run-result.schema.json`

`workspace/channel/brand.json` is the clone-owned source of validated channel policy,
cadence, and optional delivery defaults. `acs init --brand` copies it into a
workspace, where `brand.json` becomes execution truth. `project.json.delivery_intent` is the ACS-owned run intent. New scaffolds write
it explicitly and it must cover every enabled channel exactly once: manual
routes have no date, while scheduled routes require an ISO date/time and
explicit timezone. When the host exposes the standard-library IANA zoneinfo
database, ACS also rejects unknown timezone names; on a bare host without that
database it still requires a non-empty timezone but makes no semantic name
claim. The publisher handoff is generated from that intent and is
the only v0.2 scheduling/publisher boundary; it never grants posting
permission. Its manifest binding excludes only the mutable verify-time
`verification` block; the handoff's asset hashes and the package's verification
record still bind the current bytes.

`context/` is optional human/source-note space. ACS does not parse, validate,
hash, or execute files there. An upstream caller may read the resulting local
proof and learning, but it does not maintain an ACS schema or become a runtime
dependency.

Source rights statuses remain editable during draft and inspection. Packaging
and verification are publish gates: every source must be `owned`, `licensed`,
`public-domain`, `cc0`, or `cc-by`; `permission-pending` and `unknown` are not
cleared for a publish-ready handoff.

Keep schema changes additive or bump the schema version and migration docs.
The v0.2 validator intentionally covers the transparent subset needed by the
CLI and does not require a third-party validation service.
