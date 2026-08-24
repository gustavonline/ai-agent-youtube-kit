# ACS Workspace

`workspace/` is the persistent operational truth for Agentic Content System.

- `workspace/channel/` holds clone-owned channel policy, style, and brand assets.
- `workspace/content-formats/` and `workspace/content-pipeline/` hold inspectable ACS planning state.
- `workspace/productions/` holds one local ACS content workspace per production.
- `workspace/references/` holds durable reference-analysis metadata and lessons.
- `workspace/learning/` holds durable memory and general motion lessons.
- `workspace/runs/` holds structured evidence for deliberate full production-route attempts.
- `workspace/history/runs.jsonl` is the append-only relation between those attempts.
- `workspace/engine/` contains only the technical implementation, local contracts, tests,
  scripts, templates, and optional adapters.

The run ledger references production-owned inputs, outputs, and proof. It does
not store raw requests, prompt transcripts, credentials, or upstream-system
records. ACS remains independently runnable without AIOS, a server, a database,
or an external publisher.
