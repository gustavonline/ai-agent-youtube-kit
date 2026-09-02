# Content graph contract

`content-graph.json` is the small, channel-agnostic manifest for one content
family. The normative executable contract is
`workspace/engine/scripts/check-content-graph.mjs` and the readable fixture is
`workspace/engine/tests/fixtures/content-graph/content-graph.json`.

Start from `workspace/engine/templates/content-graph.json`. The template is
intentionally incomplete until at least one real node is added. Create the
publisher handoff from `workspace/engine/templates/publisher-handoff.json` only
after final node review; its empty selection and placeholder graph hash are
also intentionally invalid until replaced.

## Identity and versions

- `contract_version` is `acs-content-graph/1.0`.
- `family.id` and each `node.id` are stable lowercase kebab-case IDs. They are
  not derived from file paths, titles, or channel names.
- `family.version` and every node `version` are positive integers. Increment a
  node version when its bytes or content identity changes; increment the family
  version when the graph revision is deliberately superseded.

## Nodes

Supported kinds are `source`, `transcript`, `thesis`, `master`, and
`derivative`. A production uses only the nodes it actually needs. Every node
contains:

- a normalized relative `path` inside the production;
- a lowercase media-type `format`;
- `sha256:<64 lowercase hex>` over the actual file bytes;
- provenance `type`, statement, and optional references;
- its own review status, reviewer, and review reference; and
- optional `channel_targets`, which are arbitrary stable IDs rather than a
  global allowlist.

Review states are `not_reviewed`, `in_review`, `approved`, and `rejected`.
Decided states require a reviewer and reference. Other states require both to
be null. No review state is inherited.

## Edges

Edges are explicit `{type, from, to}` records. `from` is the node making the
relationship and `to` is the referenced node. Supported relations are:

- `derived_from`
- `excerpt_of`
- `adaptation_of`
- `variant_of`
- `companion_to`
- `promotes`

Edges describe lineage or editorial relationship only. They never propagate
approval.

## Optional design handoff

`design_handoff` may record exactly one immutable `DESIGN.md` plus selected
assets. It requires a revision, provenance, review reference, relative paths,
roles, and hashes. Omit the whole field when no accepted ADS/design-owner
handoff exists; ACS and Diffusion remain fully usable.

## Publisher handoff

`publisher-handoff.json` binds to the graph file hash and family version. Every
selection repeats the node ID, version, and hash. The validator rejects a
selection unless that exact node's own review status is `approved`, even when
the family, source, or master is approved.

The handoff contract fixes:

```json
{
  "status": "awaiting-separate-authorization",
  "supervised": true,
  "not_posted": true,
  "external_posting": false
}
```

Optional selection targets must be a subset of the selected node's declared
targets. There is no posting command.

## Validate

```text
node workspace/engine/scripts/check-content-graph.mjs <production>/content-graph.json
node workspace/engine/scripts/check-content-graph.mjs <production>/content-graph.json <production>/publisher-handoff.json
```

The checker is read-only and exits nonzero with field-specific errors.
