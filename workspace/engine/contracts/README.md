# Contracts

The versioned contracts are:

- `acs-content-graph/1.0`, documented in `docs/CONTENT_GRAPH.md` and validated
  by `workspace/engine/scripts/check-content-graph.mjs`;
- `acs-publisher-handoff/1.0`, validated by the same script.

The neutral readable fixture lives under
`workspace/engine/tests/fixtures/content-graph/`. Runtime validation is direct
zero-dependency Node code so there is no second schema library or application.
