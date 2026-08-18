---
name: workflow-discovery
description: Resolve one bounded consequential project decision before implementation. Use when viable alternatives materially affect architecture, security, cost, dependencies, or visible behavior; use Wayfinder when several important state distinctions need durable structured tracking.
---

# Bounded decision discovery

Discovery owns a decision small enough to settle without a Wayfinder map. It
does not own huge-effort planning, teaching methodology, or implementation.

## Start or resume

1. Read the project profile only for relevant facts and commands.
2. Establish the mutation boundary before touching workflow state. A read-only
   request, or any request without authorized repository writes, stays ephemeral:
   inspect evidence and return the analysis without creating or changing a
   durable record or persisting another artifact. A provisional choice is not
   authorization to write.
3. Only when the task requires durable decision state and repository writes are
   authorized, validate or create a `DEC-NNNN` record under the state contract.
   Resume only at its exact pending question; preserve and report invalid or
   conflicting state. Never overwrite or silently merge another durable record.
4. If several consequential unknowns, decisions, dependencies, blockers, or
   conflicting facts become unreliable to hold in the bounded record, select
   the pinned `wayfinder` provider and apply its declared host invocation
   policy. This may happen after Discovery has started; do not wait for a new
   user prompt. Respect an explicit Wayfinder opt-out. When authorized provider
   execution or truthful host-native fallback needs durable local planning,
   follow `.agent-workflow/contracts/wayfinder-state.md`. Its local map is the
   canonical configured representation and re-entry point. Read-only work stays
   ephemeral and creates no map.

## Resolve the decision

1. State the precise question and why it blocks or materially changes the work.
2. Separate verified facts, constraints, assumptions, preferences, unknowns,
   and out-of-scope matters. Inspect repository evidence before asking the user
   for facts the workspace can answer.
3. Use primary sources for consequential or time-sensitive external facts. Use
   upstream `research` when a cited durable research artifact and isolated
   background work add value; otherwise keep the lookup proportional. Research
   is a capability inside the current Discovery workflow here, not a durable
   workflow transition.
4. Compare only viable alternatives by benefits, costs, risks, reversibility,
   and evidence that would change the choice.
5. Mark a consequential decision accepted only when the user accepts it or a
   named project policy delegates that authority. Autonomous progress may record
   only a reversible provisional choice with a review trigger.

If the user explicitly wants sustained learning before deciding, select upstream
`teach` in a dedicated learning workspace and apply its invocation policy. Only
an already-authorized durable Discovery record may preserve the unanswered
question and exact return target; selecting or handing off to Teach does not
create or update one. A simple conceptual question should receive a direct
explanation without starting a course workspace. Restore an existing Discovery
pointer before resuming the decision; never let teaching decide it.

## Provider identity boundary

Local Wayfinder U#/D#/T# identifiers are canonical only inside their configured
effort and must not be wrapped in `DEC`, `IMP`, `TKT`, `UNK`, or another alias.
Preserve any referenced external issue IDs, URLs, linked titles, and
`wayfinder:*` labels unchanged. Jira and GitHub identifiers remain external
tracker identities; this framework neither synchronizes them nor creates a
parallel local copy.

Finish with the decision status, rationale, consequences, rejected alternatives,
remaining uncertainty, and the appropriate provider or direct implementation
handoff. For ephemeral Discovery, report the conclusion as analysis rather than
claiming a durable `DEC` exists. Do not reopen an accepted durable decision
without conflicting new evidence or an explicit request; supersede it visibly
instead of rewriting history.
