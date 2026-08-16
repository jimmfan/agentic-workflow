# Frozen semantic evidence and manual-review rubric

This rubric is evaluator-owned and must remain outside evaluated workspaces. It
is frozen before live execution.

## Evidence packet schema

Every semantic question records:

- condition and phase (from the enclosing phase evidence);
- semantic question;
- repository-relative file path;
- exact one-based line number and bounded snippet;
- `deterministic_structured_value` only when the representation contract defines
  the field's semantics; and
- `manual_review_required: true` for arbitrary prose.

Absence of a matching line is absence of extracted evidence, not proof that the
agent held the opposite belief.

## Deterministic structured fields

Only Wayfinder fields explicitly defined by the installed contract may be
parsed semantically: `Status`, `Blocked by`, `Related`, and `Resolves`. Exact
Terraform syntax, literals, resource types, command events, diffs, snapshots,
and validation results are objective checks and do not require semantic review.

Do not classify arbitrary vanilla prose as resolved, unresolved, blocking,
actionable, superseded, or contradictory with keyword windows. Do not infer a
positive decision from nearby subject and decision words.

## Manual questions by phase

Phase 1:

- Is stale `m6i` distinguished from current truth?
- Are all W1 choices unresolved, W2 actionable, W3 blocked but isolated, and W4
  blocked for its missing destination?

Phase 2:

- Did the fresh agent treat the preserved SSM value as trusted project truth,
  beyond merely reading it?
- Did W3 or W4 incorrectly suppress safe W2 progress?

Phase 3:

- Did D1 retire the old W1 unknowns without reviving `m6i`?
- Is W3 still blocked but non-blocking for new fixture-owned W1/W2 resources?
- Is W4 still blocked?

Phase 5:

- Is D2 represented as superseding only `m7i.large`?
- Do dedicated compute, managed node groups, no Karpenter, and 2/2/6 remain
  active?
- Did W4 transition to actionable while W3 remained blocked?
- Are any old/new instance-size claims simultaneously represented as active?

Phase 6:

- Did the agent preserve unaffected W1/W2 implementation rather than rewrite it?
- Did any durable state remain contradictory after implementation?

## Interpretation rules

Review exact packets and final snapshots without access to sibling-condition
results until each condition's judgments are recorded. Use `yes`, `no`, or
`unclear`; prefer `unclear` over inference. Record a short rationale and cited
packet lines. Frozen machine JSON is never rewritten after a discovered grader
defect; defects are preserved and interpreted in the report.
