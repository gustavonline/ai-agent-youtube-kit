---
name: setup-content-system
description: "Configure a cloneable Agentic Content System for a business before its first real video. Use when an agent is asked to set up ACS, onboard a brand, resolve channel defaults, or prepare the repository for content work."
---

# Setup Content System

Configure the clone before creating a content workspace. Use business context
already available in the conversation, AIOS, or brief; never require an
AIOS-specific schema, caller ID, API, or runtime dependency.

## Resolve only missing decisions

Ask one concise question at a time, and ask only for information not already
resolved:

- business or offer context;
- audience/buyer;
- offer and content promise;
- enabled channels and the reason for each disabled channel;
- sustainable cadence;
- delivery defaults for each enabled channel (`manual` or a dated,
  timezone-aware `scheduled` intent).

Keep unknowns unknown. Do not invent a brand, audience, promise, cadence,
credentials, or posting authority.

## Configure the clone

1. Read `workspace/channel/PROFILE.md`, `workspace/channel/STYLE_GUIDE.md`, `workspace/channel/DESIGN.md`, and
   `workspace/learning/PROJECT_MEMORY.md`.
2. Record resolved channel identity, audience, promise, lanes, offers, CTAs,
   and constraints in `workspace/channel/PROFILE.md`.
3. Copy the resolved channel policy and cadence into the ACS-owned,
   schema-compatible `workspace/channel/brand.json`. Keep `delivery_defaults` explicit
   for every enabled channel. Update `workspace/channel/STYLE_GUIDE.md` only with
   reusable style decisions, not one-off content or private business notes.
4. Run environment and profile checks without creating a content workspace:

   ```text
   python -m agentic_content_system doctor
   python -m agentic_content_system validate-profile workspace/channel/brand.json
   ```

Do not create the first content workspace during setup. Setup is complete when
the clone defaults validate and the owner can state the next real content
outcome.

## Start a real content outcome

When a real content outcome is requested, copy the clone defaults into the
workspace execution truth with:

```text
python -m agentic_content_system init <workspace> --brand workspace/channel/brand.json
python -m agentic_content_system validate <workspace> --contracts-only
```

`<workspace>/brand.json` is the policy input and execution truth for this run. Edit
`<workspace>/project.json` for the run-specific promise, audience, source
rights, and `delivery_intent`; edit and explicitly approve `edit-plan.json`
before rendering or packaging. The run skill owns the production sequence.

Use `docs/REAL_VIDEO_ACCEPTANCE.md` for owner-recorded acceptance. Keep
`external_posting: false`, `not_posted: true`, and separate human
authorization; ACS never posts.

Keep the audit skill strictly read-only and do not use it as a setup or repair
workflow.
