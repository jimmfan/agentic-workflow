# ADR-0005: Add durable decomposition and independent review

- Status: accepted
- Date: 2026-08-12

## Context

The completed framework could preserve one implementation plan but did not own a
durable dependency graph for approved work spanning multiple sessions. Its
Verification workflow gathered executable evidence but did not define a
separate independent review of specification fit, standards, correctness,
security, validation gaps, and unintended scope.

Current Matt Pocock `to-tickets`, `diagnosing-bugs`, `tdd`, `code-review`,
`implement`, `to-spec`, and `writing-for-agents` contracts were audited at
commit `84fdeffd12f2ee307994d1eb6feb48173b6e0502`. Their useful mechanics do not
justify replacing the framework's safer specification, debugging,
implementation, authorization, or verification ownership.

## Decision

Add `workflow-decomposition` and project-owned `TKT-NNNN` records for approved
multi-session work. A separately installed, explicitly invoked native ticket
workflow may own its tracker artifacts; framework state then keeps only links
and the return target. Never mirror complete ticket bodies.

Add `workflow-review` as a proportional completion gate after Verification for
meaningful changes. Review may use independent read-only passes, but the parent
validates findings and owns disposition. Trivial work bypasses both workflows.

Strengthen the existing Debugging skill with feasible exact-symptom feedback,
minimization, falsifiable hypotheses, targeted removable instrumentation, and
correct validation seams. Keep diagnosis-only scope nonmutating. Add TDD only as
an optional technique inside the existing Implementation workflow when a stable
observable seam and independent expected result exist.

The project-owned specification remains canonical. The existing Implementation
and Verification workflows remain the build and executable-evidence owners.
Upstream `to-spec` and `implement` remain excluded, and no runtime is added.

## Consequences

Large approved work can resume from an actionable frontier without reconstructing
intent from chat. Meaningful completion receives independent scrutiny without
making review ceremony mandatory for trivial edits. Local TKT records add one
identifier and template; external ticket mutation remains unavailable unless a
project explicitly configures it and the user authorizes the exact action.

## Alternatives considered

- Put every slice inside one `IMP` body: fewer record types, but weaker ownership,
  collision handling, independent status, and resume targets.
- Adopt upstream `to-tickets` and `code-review` unchanged: richer native behavior
  but tracker, Git, delegation, and review-scope assumptions conflict with the
  portable authorization and verification contracts.
- Replace Implementation or Debugging: rejected because the audited upstream
  alternatives omit important general-purpose safety and scope boundaries.
