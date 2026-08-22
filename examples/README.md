# Examples

`acs init <workspace> --example gustav` creates an explicit Gustav-style example
policy: YouTube and LinkedIn enabled, Instagram optional/disabled until fit is
documented, and TikTok disabled with a clear buyer-fit reason. The scaffold is
generic enough to clone; edit the brand and ACS-owned content contracts before real work.

`gustav-context.md` is an advisory resolved-context example. It can be sourced
from an AIOS Space task, a conversation, or a brief, but it is not an ACS
schema and ACS does not import or validate it. Run `acs init <workspace>
--example gustav`, then copy only the needed values into the workspace-owned
contracts. The example schedules YouTube for `2026-09-01T09:00:00` in
`Europe/Copenhagen`, keeps LinkedIn manual/no-date, and leaves Instagram and
TikTok disabled. The resulting publisher handoff is awaiting separate
authorization and never posts.

The repository does not commit large demo media. Use the fixture helper or a
rights-safe source with pinned provenance for local proof.
