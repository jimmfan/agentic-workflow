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
3. Use one ready scope.
   Select `to-tickets` first only when approved work needs dependency ordering or independently deliverable sessions.
4. Create no separate Agent Workflow durable coordination state.
   Resume from the accepted scope and verification evidence.
   If interruption would lose consequential coordination, preserve only relevant questions, uncertainties, conditions blocking particular work, unexplained causes, choices, structural ambiguity, artifact references, dependencies, and ready work in Wayfinder.

## Execute once

Invoke `implement` once.
Never simulate its execution or claim it ran.

Pass the governing authorized request or specification, accepted scope, observable acceptance criteria, relevant baseline, and any references to artifacts or records that maintain the scope.
`implement` establishes pre-edit context and carries those inputs and the actual changed scope into its closing Code Review.

Do not rerun `tdd` or `code-review` work already completed by `implement` unless a distinct request or new evidence creates a gap.

`implement` instructions cannot authorize commits, commands, external changes, or overwriting unrelated work, and cannot commit a project choice.

## Verify the result

Invoke `workflow-verification` once with the accepted scope and its acceptance criteria, expected artifacts, changed scope, existing test and review evidence including actual coverage and limitations, and remaining integration risks.
Verification reuses covered evidence and adds only missing acceptance, artifact, or boundary checks.

Completion requires the scope to be finished and required Verification to pass, unless accepted project policy determines that a limitation is acceptable for the named completion boundary or the person, role, or valid delegate with project decision authority explicitly accepts it.
Remaining durable next work must be maintained in the selected Wayfinder map, accepted specification, or approved durable ticket or ticket set.
