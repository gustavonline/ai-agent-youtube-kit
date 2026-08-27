# Semantic Evaluation

Semantic evaluation is one local, reviewer-owned checkpoint for a completed
ACS content result. It is separate from JSON/schema validation, deterministic
package verification, static review reporting, and the periodic read-only
system audit. It does not edit media, posts, or `results/run-result.json`.

Run it after `acs export-result` and before recording a successful deliberate
attempt or promoting an example:

```text
acs semantic-eval <workspace> <assessment.json> --by <reviewer>
```

The assessment is a small local JSON file using
`semantic-assessment.schema.json`. It records a human observation for the
approved promise, the proof required by `edit-plan.json`, and the stated
audience. ACS copies those observations into an immutable file under
`<workspace>/evaluations/`, bound to the exported result, approved content
decision, review evidence, and local proof hashes.

The resulting evidence names its subject, checkpoint, observable checks,
required local evidence, outcome, and failure action. A passing outcome means
all three observations passed. A failure is deliberate evidence that a
structurally valid result is materially wrong or irrelevant to the approved
content decision; it is not a schema or FFmpeg failure.

Do not overwrite a failed evaluation. Record it with the tracer:

```text
python workspace/engine/tracer.py record workspace/productions/<slug> \
  --status failed --failure-code semantic_eval_failed --failure-step semantic-eval --retriable
```

Correct the smallest content behavior or fixture, rerun the ordinary export
route, produce a new passing evaluation, and consume the failed run once:

```text
python workspace/engine/tracer.py record workspace/productions/<slug> \
  --status succeeded --recover <failed-run-id>
```

The tracer accepts a successful attempt only with exactly one readable,
workspace-owned passing evaluation bound to its current result. A semantic
failure similarly requires a retained failed evaluation. Ledger validation
checks that evaluation references stay below the owning production workspace,
match their recorded bytes and outcome, recheck the result snapshot and every
required-evidence snapshot, and cannot be replaced after the run is appended.

Use the local regression fixtures in
`workspace/engine/tests/fixtures/semantic-assessment-*.json` before changing
the affected judgment prompt, model, adapter, tool, contract, or harness.
They are ACS test evidence, not a general-purpose scoring rubric or an
automatic AI judge.
