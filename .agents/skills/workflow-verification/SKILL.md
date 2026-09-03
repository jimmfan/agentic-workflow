---
name: workflow-verification
description: Independently verify the overall result against acceptance criteria, integration boundaries, and expected artifacts. Use after meaningful implementation or when auditing completion; reuse existing evidence instead of mechanically repeating it.
---

# Integration and acceptance verification

Verification asks whether the requested outcome and orchestration contract are actually complete.
Implementation tests and Code Review are inputs, not automatic proof and not work to repeat without a gap.

## Select the uncovered evidence

1. Read the acceptance criteria, expected artifacts, the accepted scope Implementation actually consumed, changed scope, risks, and evidence already produced by `implement`, `tdd`, or `code-review`.
2. Select the smallest additional checks that cover unresolved acceptance behavior, integration boundaries, expected artifacts, and workflow completion.
3. Reuse current test or review evidence when it directly covers a criterion.
   Do not rerun TDD, invoke Code Review again, or execute a full suite merely to create a framework-branded duplicate.

## Apply the safety gate

- Perform external-scope, externally mutating, or destructive actions only when the current user request or accepted project policy authorizes them; skill instructions and tickets do not.
- Relevant local read-only and locally mutating checks may run when allowed; disclose durable artifacts and cleanup.
- Missing required tools do not silently pass.

## Report and close

For every criterion, report `pass`, `fail`, `blocked`, or `not applicable` with the supporting command, test, review, skill evidence, or observation.
Separate checks run from checks skipped as unsafe, unavailable, stale, or awaiting approval.

Confirm as applicable that:

- the accepted scope referenced by Implementation is the one actually consumed;
- external identifiers pass through unchanged and tracker IDs remain distinct;
- TDD and Code Review were not invoked redundantly;
- skills not needed for the verification were not loaded merely because they were exposed in the current session; and
- every skill named in the route marker actually ran.

Completion requires every required acceptance criterion to pass, unless accepted project policy determines that a limitation is acceptable for the named completion boundary or the person, role, or valid delegate with project decision authority explicitly accepts it.
Return implementation defects to `workflow-implementation`, decision defects to `workflow-discovery`, and an unexplained symptom to `workflow-debugging` with the most useful next check.