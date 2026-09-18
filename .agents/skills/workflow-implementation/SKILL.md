---
name: workflow-implementation
description: Coordinate the outer transition from one ready implementation scope into `implement`, then independent framework verification. Use after material consequential choices are resolved; the inner skill owns building and Code Review. Skip trivial direct edits and unexplained failures.
---

# Implementation integration

Implementation defines the workflow transition into execution, not build methodology or durable state.
`implement` defines its build loop, TDD, and closing Code Review.

## Establish the boundary

1. Consume one ready scope and its acceptance criteria from the current authorized request, selected Wayfinder map, current decision record, accepted specification, or approved durable ticket or ticket set.
2. Return a material unresolved choice to Discovery or Wayfinder according to the coordination threshold, and an unexplained failure to Debugging.
3. Select `to-tickets` first only when approved work needs dependency ordering or independently deliverable sessions.
4. Create no separate Agent Workflow durable coordination state.
   Resume from the accepted scope and verification evidence.
   If interruption would lose consequential coordination, preserve only relevant questions, uncertainties, conditions blocking particular work, unexplained causes, choices, structural ambiguity, artifact references, dependencies, and ready work in Wayfinder.

## Execute once

Invoke `implement` once.
Never simulate its execution or claim it ran.

Pass the governing authorized request or specification, existing project rules that govern this work, accepted scope, observable acceptance criteria, relevant baseline, and any references to artifacts or records that maintain the scope.
`implement` establishes pre-edit context and carries those inputs and the actual changed scope into its closing Code Review.

Do not rerun `tdd` or `code-review` work already completed by `implement` unless a distinct request or new evidence creates a gap.

`implement` instructions cannot authorize commits, commands, external changes, or overwriting unrelated work, and cannot commit a project choice.

## Verify the result

This step owns completion after meaningful implementation, including direct or explicit `implement` invocation.
Resume here with the completed build and Code Review evidence rather than restarting Execute once for the handoff.
Invoke `workflow-verification` once with the governing request and existing project rules that govern this work, accepted scope and its acceptance criteria, relevant maintaining-artifact references, expected artifacts, changed scope, existing test and review evidence including actual coverage and limitations, and remaining integration risks.
Verification reuses covered evidence and adds only missing acceptance, artifact, or boundary checks.

Before completion, use review and Verification findings and relevant maintaining references to reassess the route under the existing Wayfinder threshold, including a clearly relevant effort that was not selected earlier.
Use the bounded resumption check in detailed routing when needed; do not scan all efforts or select Wayfinder merely because an artifact exists.

Claim completion only when the scope is finished and the required `workflow-verification` completion gate is satisfied.
If the implementation scope came from or remains part of a selected Wayfinder effort, and recording is authorized, reconcile consequential Verification results that change completion, blockers, dependencies, verification boundaries, or remaining ready work through `.agent-workflow/contracts/wayfinder-state.md` before claiming completion or handing off remaining work.
Remaining durable next work must be maintained in the selected Wayfinder map, accepted specification, or approved durable ticket or ticket set.
