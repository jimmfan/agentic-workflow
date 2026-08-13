---
name: workflow-discovery
description: Resolve one bounded consequential project decision before implementation. Use when viable alternatives materially affect architecture, security, cost, dependencies, or visible behavior; use upstream Wayfinder instead for huge multi-session fog.
---

# Bounded decision discovery

Discovery owns a decision small enough to settle without a Wayfinder map. It
does not own huge-effort planning, teaching methodology, or implementation.

## Start or resume

1. Read the project profile only for relevant facts and commands.
2. Validate or create a `DEC-NNNN` record under the state contract. Resume only
   at its exact pending question; preserve and report invalid or conflicting
   state.
3. If the effort is too foggy or large for one session, hand off to the pinned
   upstream `wayfinder` provider. Its map remains canonical.

## Resolve the decision

1. State the precise question and why it blocks or materially changes the work.
2. Separate verified facts, constraints, assumptions, preferences, unknowns,
   and out-of-scope matters. Inspect repository evidence before asking the user
   for facts the workspace can answer.
3. Use primary sources for consequential or time-sensitive external facts. Use
   upstream `research` when a cited durable research artifact and isolated
   background work add value; otherwise keep the lookup proportional.
4. Compare only viable alternatives by benefits, costs, risks, reversibility,
   and evidence that would change the choice.
5. Mark a consequential decision accepted only when the user accepts it or a
   named project policy delegates that authority. Autonomous progress may record
   only a reversible provisional choice with a review trigger.

If the user explicitly wants sustained learning before deciding, preserve this
decision's unanswered question and exact return target, then invoke upstream
`teach` in a dedicated learning workspace. A simple conceptual question should
receive a direct explanation without starting a course workspace. Restore the
Discovery pointer before resuming the decision; never let teaching decide it.

## Provider identity boundary

When Discovery hands off to Wayfinder, preserve its issue IDs, URLs, linked
titles, and `wayfinder:*` labels unchanged. Do not allocate `DEC`, `TKT`, `UNK`,
or another framework alias for Wayfinder-owned state. A framework return pointer
stores the native reference and exact return target only; Jira and GitHub issue
identifiers remain external tracker identities.

Finish with the decision status, rationale, consequences, rejected alternatives,
remaining uncertainty, and the appropriate provider or direct implementation
handoff. Do not reopen an accepted decision without conflicting new evidence or
an explicit request; supersede it visibly instead of rewriting history.
