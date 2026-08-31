---
name: workflow-implementation
description: Orchestrate one ready implementation scope through `implement` and independent framework verification. Use after material consequential choices are resolved; skip trivial direct edits and unexplained failures.
---

# Implementation integration

Implementation defines the workflow transition into execution, not build
methodology or durable state. `implement` defines its build loop, TDD,
and closing Code Review.

## Establish the boundary

1. Consume the selected map, current decision record, accepted specification, or
   approved ticket or ticket set by reference, with its scope and acceptance criteria.
2. Return a material unresolved choice to Discovery or Wayfinder according to
   the coordination threshold, and an unexplained failure to Debugging.
3. Use one ready scope. Select `to-tickets` first only when approved
   work needs dependency ordering or independently deliverable sessions.
4. Create no separate Agent Workflow durable coordination state. Resume from
   the selected map, current decision record, accepted specification, approved
   ticket or ticket set, and verification evidence. If interruption would lose consequential
   coordination, preserve only relevant questions, uncertainties, conditions
   blocking particular work, unexplained causes, choices, structural ambiguity,
   links to affected source, specifications, decision records, tickets,
   research results, or reviews, dependencies, and ready work in Wayfinder.

## Execute once

Invoke `implement` once with the accepted scope, observable acceptance criteria,
and references to the selected map, decision record, specification, ticket, or
ticket set. Never simulate its execution or claim it ran.

Do not rerun `tdd` or `code-review` work already completed by `implement` unless
a distinct request or new evidence creates a gap.

`implement` instructions cannot authorize commits, commands, external changes, or
overwriting unrelated work, and cannot commit a project choice.

## Verify the result

Invoke `workflow-verification` once with the acceptance criteria; the selected
map, decision record, specification, ticket, or ticket set; changed scope;
existing test and review evidence; and remaining integration risks.
Verification reuses covered evidence and adds only missing acceptance,
expected-result, or integration-boundary checks.

Completion requires the scope to be finished and required Verification to pass,
unless accepted project policy determines that a limitation is acceptable for
the named completion boundary or the person, role, or valid delegate with project
decision authority explicitly accepts it. Remaining next work must be
maintained in its selected map or specification, or in the ticket or ticket set
produced by `to-tickets`.
