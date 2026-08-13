---
name: workflow-teach
description: Build the user's project-grounded understanding for an informed decision or safe action. Use for an explicit learning request, a stated knowledge gap, or resuming a decision interrupted for teaching; return control without deciding or implementing.
---

# Teach workflow

Teach enough for the user's stated outcome, then return control. Do not silently
make the architecture decision or implement the interrupted work.

When resuming from `active.md`, require `Active workflow: teach`, validate the
record pointers, and continue at the stored `Resume target` before introducing a
new learning target.

## Establish the learning target

1. Read the project profile and any active state needed for context.
2. Identify the concrete decision or task the learning supports, the user's
   stated prior knowledge, the observable success condition, and topics that are
   out of scope. Ask a focused question only when this cannot be inferred.
3. If invoked from Discovery, preserve the interrupted workflow, pending
   decision, and resume target in `ai-workflow/state/active.md`.

## Teach

1. Start with a compact mental model and define unfamiliar terms at first use.
2. Ground examples in the actual project when helpful, but label examples and
   assumptions so they are not mistaken for project facts.
3. Prefer primary, high-trust sources for time-sensitive or consequential facts.
4. Use short explanation-practice-feedback loops. Check understanding when it
   informs the next step; do not equate exposure with mastery.
5. Correct misconceptions explicitly and let the user reason about the pending
   choice. Distinguish factual understanding from value judgments or preferences.

For multi-session learning, create `LRN-NNNN` from
`ai-workflow/templates/learning-record.md`. Record demonstrated understanding,
corrected misconceptions, sources, and the next useful exercise—not a transcript.
For a short lesson, durable learning state is optional unless another workflow
must resume later.

## Optional upstream Teach

Use an installed upstream `/teach` only when the user explicitly invokes it for
its audited multi-session learning-workspace use case. Apply the ownership and
workspace boundary in `docs/reference-research.md`; never mirror its course
artifacts. If it is unavailable, say so and offer this bounded local workflow.

## Return control

Understanding is sufficient when the user can explain the relevant model or
tradeoff accurately enough for the pending action, or explicitly says they are
ready while remaining uncertainty is visible. If Discovery was interrupted:

1. Update the learning record if used.
2. Restore `active workflow: discovery` in `active.md`.
3. Clear the interrupted-workflow field only after copying the exact resume
   target into the active Discovery state.
4. Resume the pending decision without silently deciding it.

If no workflow was interrupted, summarize what is now understood, what remains
uncertain, and the safest next practice or engineering step.
