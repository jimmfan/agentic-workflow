---
name: workflow-discovery
description: Map consequential project uncertainty and resolve decisions before implementation. Use when viable alternatives or hidden assumptions would materially change architecture, security, cost, dependencies, or externally visible behavior, including resuming a decision interrupted for teaching.
---

# Discovery workflow

Map uncertainty only as far as needed to make the pending work safe and clear.
Discovery owns decisions, not substantial product implementation.

## Start or resume

1. Read `ai-workflow/project-profile.md` if present.
2. Validate or create the decision record under
   `ai-workflow/state/README.md`. Resume an active decision only at its exact
   `Resume target`; preserve and report invalid, stale, or conflicting state.

## Resolve the gap

1. State the decision question and why it blocks or materially changes the work.
2. Inspect only the relevant repository paths and current evidence needed to
   discover project facts; reuse verified profile facts and accepted decisions.
3. Separate verified facts, constraints, assumptions, preferences, unknowns,
   and out-of-scope matters.
4. Identify dependencies and research questions. Use primary sources for facts
   that can change or materially affect risk.
   Use the host's normal research tools under its existing authorization and
   verification controls. Delegated findings remain evidence to verify, not a
   decision, and repository work stays with the parent or a host-native subagent.
5. Compare only viable alternatives. Explain benefits, costs, risks,
   reversibility, and what evidence would change the choice.
6. Expose hidden assumptions. Do not ask the user questions that repository
   evidence can answer safely.
7. Mark a consequential decision accepted only when the user accepts it or an
   explicit project policy delegates that authority. Otherwise, when autonomous
   progress is authorized, record only a provisional reversible choice with a
   review trigger and surface it in the final review.
8. Record rationale, consequences, and follow-up work without duplicating long
   research notes.

Do not reopen an accepted decision unless new evidence conflicts with its
assumptions or the user requests reconsideration. Mark the old record
`superseded` and link the replacement rather than rewriting history.

## Optional upstream Wayfinder

Use an installed upstream `/wayfinder` only when the user explicitly invokes it
for its foggy multi-session use case. Its native map remains canonical; never
mirror it into framework state, and apply the normal authorization boundary to
any repository or external-tracker mutation. If it is unavailable, say so and
offer this local workflow.

## Hand off to Teach

When the user explicitly says they cannot decide safely because they do not
understand a concept:

1. Keep the decision record active with the unanswered question.
2. Set `ai-workflow/state/active.md` to `active workflow: teach`,
   `interrupted workflow: discovery`, and a precise resume target such as
   `DEC-0003 / compare identity options`.
3. Invoke `workflow-teach`. Do not choose for the user during teaching.
4. When the user demonstrates sufficient understanding or says they are ready,
   record the outcome, restore Discovery as active, and resume the exact pending
   question. UI handoff buttons may assist but are never the durable pointer.

## Finish

Summarize the decision, status, rationale, consequences, rejected alternatives,
and remaining uncertainty. Hand resolved scope and explicit acceptance criteria
to Implementation, which owns the canonical specification transition when one
is justified. Apply archival and optional IDP rules from
`ai-workflow/state/README.md`.
