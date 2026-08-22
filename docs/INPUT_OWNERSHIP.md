# Input And Ownership

Agentic Content System accepts useful context from any practical source: an
AIOS Space task, a conversation, a Markdown brief, a client note, or an
existing workspace. The source may be rough or already resolved. The judgment
layer chooses what this run actually needs, then copies only those resolved
values into an ACS workspace with `acs init`.

## Canonical boundary

The receiving workspace becomes the canonical execution truth. ACS owns and
validates its local files:

- `brand.json` owns channel policy, disabled-route reasons, and cadence;
- `project.json` owns the content decision, source rights/provenance, transcript
  reference, and run-specific `delivery_intent`;
- `content-brief.md` and `recording-plan.md` own the pre-capture explanation and
  outline;
- `edit-plan.json` owns ordered segments and explicit approval;
- `transcripts/`, `renders/`, `derived/`, `publish/`, `reports/`, and `results/`
  own the local proof and generated handoff state.

Once values are copied in, the upstream source is never a runtime or schema
dependency. Files in the optional `context/` directory are human/source notes
only: ACS does not parse, validate, hash, execute, or use them for approval,
rendering, packaging, verification, or result export.

## Task-level AIOS routing

When AIOS is present, the ownership is:

```text
persistent AIOS Space defaults + learning
        -> resolved content task/context
        -> acs init + independent local ACS workspace
        -> proof, publisher-handoff state, and learning files
        -> caller reads the result back through its normal task flow
```

The persistent Space owns durable company, offer, buyer, channel defaults, and
learning. A task or judgment layer may select one content decision and route it
to ACS. ACS owns media/edit/package execution and returns inspectable proof.
The result is caller-agnostic; AIOS may read it and bring concise learning back
to the Space without ACS validating an AIOS return shape.

For a proposed AIOS issue or integration task, document this routing and
ownership only. Do not ask AIOS and ACS to maintain a shared inbound schema, do
not add `source_system`, `space_ref`, or caller IDs to ACS runtime contracts,
and do not make an ACS workspace depend on a Space, API, database, or task
record. A useful caller can pass context in prose or files, while the local
workspace remains independently runnable and inspectable.

## Clone defaults and a real run

Before the first real video, the setup skill resolves missing business,
audience, offer/content promise, channel-policy, cadence, and delivery-default
decisions into `channel/PROFILE.md` and `channel/brand.json`. The profile is
validated without creating a workspace. When a real outcome exists,
`acs init <workspace> --brand channel/brand.json` copies the policy into the
workspace. That workspace `brand.json` is execution truth; `project.json` owns
the run-specific content and delivery intent.

Any enabled or disabled channel arrangement is valid when it has explicit
policy reasons and delivery defaults for every enabled route. Disabled channels
cannot become delivery routes, even if a run-level intent mentions them. A
scheduled value is intent only; the generated publisher handoff remains
`not_posted: true` and `external_posting: false`.
