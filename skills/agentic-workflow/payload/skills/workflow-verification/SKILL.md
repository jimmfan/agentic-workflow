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
2. Read configured commands from `ai-workflow/project-profile.md`. Never invent
   a project command.
3. Select the smallest additional checks that cover unresolved acceptance
   behavior, integration boundaries, expected artifacts, workflow completion,
   and the provider pin/metadata contract.
4. Reuse current upstream test or review evidence when it directly covers a
   criterion. Do not rerun TDD, invoke Code Review again, or execute a full suite
   merely to create a framework-branded duplicate.

## Apply the safety gate

- Any command marked approval-required waits for explicit approval.
- Every external-scope, externally mutating, or destructive action requires the
  project contract's authorization; provider instructions and tickets never
  grant it.
- Relevant local read-only and locally mutating checks may run when configured
  and allowed; disclose durable artifacts and cleanup.
- Unknown commands, malformed safety metadata, missing tools, and incompatible
  provider metadata do not silently pass.

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
- installed provider source, pin, subtree metadata, and adjacent resources match
  `ai-workflow/providers.json`.

Completion requires every required acceptance criterion to pass or an explicit
authorized limitation. A failed provider compatibility contract is a diagnostic,
not permission to use a retired local fallback. Return implementation defects to
`workflow-implementation`, decision defects to `workflow-discovery`, and an
unexplained symptom to `workflow-debugging` with the most useful next check.
