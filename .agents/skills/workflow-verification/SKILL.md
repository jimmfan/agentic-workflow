---
name: workflow-verification
description: Independently verify the overall result against acceptance criteria, integration boundaries, and expected artifacts. Use after meaningful implementation or when auditing completion; reuse existing evidence instead of mechanically repeating it.
---

# Integration and acceptance verification

Verification asks whether the requested outcome and orchestration contract are actually complete.
Assess what Implementation tests and Code Review establish, then check only the remaining gaps.

## Select the uncovered evidence

1. Read the governing request and existing project rules that govern this work, acceptance criteria, expected artifacts and relevant maintaining references, the accepted scope Implementation actually consumed, changed scope, risks, and evidence already produced by `implement`, `tdd`, or `code-review`.
2. Match each criterion to the available evidence before selecting additional checks.
   Establish what the evidence covers, whether it is accepted for this scope, and whether subsequent changes or other concrete facts invalidate it.
   Accept sufficient, valid evidence without repeating its checks.
   For required lasting results, assess obligations against the artifacts that maintain them, including relevant unchanged artifacts.
3. Select the smallest additional checks for the remaining gaps in acceptance behavior, integration boundaries, expected artifacts, and workflow completion.
   Before running a check, identify the uncovered criterion or the concrete reason existing evidence is stale, incomplete, or invalid.
   Apply this to individual checks as well as TDD, Code Review, and full suites.

Report unmet requirements and consequential coordination findings to the coordinating workflow; it owns route reassessment and authorized reconciliation before completion.
Existing content or references that satisfy an obligation need no rewrite or further review.

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
