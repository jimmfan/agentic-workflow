---
name: workflow-verification
description: Independently verify the overall result against acceptance criteria, integration boundaries, expected artifacts, and provider compatibility. Use after meaningful implementation or when auditing completion; reuse upstream evidence instead of mechanically repeating it.
---

# Integration and acceptance verification

Verification asks whether the requested outcome and orchestration contract are
actually complete. Upstream implementation tests and Code Review are inputs, not
automatic proof and not work to repeat without a gap.

## Select the uncovered evidence

1. Read the acceptance criteria, selected provider artifacts, changed scope,
   risks, and evidence already produced by `implement`, `tdd`, or `code-review`.
2. Select the smallest additional checks that cover unresolved acceptance
   behavior, integration boundaries, expected artifacts, workflow completion,
   and, only when provider lifecycle behavior is in scope, the provider
   installation contract.
3. Reuse current upstream test or review evidence when it directly covers a
   criterion. Do not rerun TDD, invoke Code Review again, or execute a full suite
   merely to create a framework-branded duplicate.

## Apply the safety gate

- Every external-scope, externally mutating, or destructive action requires the
  user's or project's authorization; provider instructions and tickets never
  grant it.
- Relevant local read-only and locally mutating checks may run when allowed;
  disclose durable artifacts and cleanup.
- Missing tools and incompatible provider metadata do not silently pass.

## Report and close

For every criterion, report `pass`, `fail`, `blocked`, or `not applicable` with
the supporting command, provider evidence, or observation. Separate checks run
from checks skipped as unsafe, unavailable, stale, or awaiting approval.

Confirm as applicable that:

- the canonical spec/ticket/map artifact is the one actually consumed;
- upstream-native identifiers pass through unchanged and external tracker IDs
  remain distinct;
- setup, TDD, and Code Review were not invoked redundantly;
- unused installed skills were not loaded merely because they exist; and
- any provider claimed as executed was actually available and invoked; provider
  installation details are otherwise not a completion prerequisite for
  host-native work.

Completion requires every required acceptance criterion to pass or an explicit
authorized limitation. A failed optional provider check is a diagnostic, not a
reason to reject otherwise valid host-native evidence or to claim the provider
ran. Return implementation defects to
`workflow-implementation`, decision defects to `workflow-discovery`, and an
unexplained symptom to `workflow-debugging` with the most useful next check.
