# Gustav Online ACS example

This committed example is a self-contained, reviewable ACS workspace boundary.
It keeps the local contracts, brief, recording plan, and delivery policy visible while
leaving large source media and generated proof ignored. Run the same CLI in a
fresh directory when producing real proof:

```text
python -m agentic_content_system init examples/my-content --example gustav
```

The policy intentionally enables YouTube and LinkedIn, schedules YouTube for
`2026-09-01T09:00:00` in `Europe/Copenhagen`, keeps LinkedIn manual/no-date,
and disables Instagram and TikTok with reasons. The schedule is delivery
intent only. ACS produces a supervised publisher handoff with
`external_posting: false` and `not_posted: true`.

Replace the illustrative source rights and content decision before real use.
The source boundary is `sources/`; generated `renders/`, `derived/`,
`publish/`, `reports/`, and `results/` are local proof, not committed example
media. The example workspace can be validated without media:

```text
python -m agentic_content_system validate examples/gustav --contracts-only
```
