---
name: workflow-implementation
description: Orchestrate one settled implementation scope through the pinned upstream implement provider and independent framework verification. Use after material decisions are resolved; skip trivial direct edits and unexplained failures.
---

# Implementation integration

Implementation owns the execution handoff, not build methodology or durable
state. Upstream `implement` owns its build loop, TDD, and closing Code Review.

## Establish the boundary

1. Consume the accepted map, decision, specification, or native ticket by
   reference, with its scope and acceptance criteria.
2. Return a material unresolved choice to Discovery or Wayfinder according to
   the coordination threshold, and an unexplained failure to Debugging.
3. Use one ready scope. Select `to-tickets` first only when approved
   work needs dependency ordering or independently deliverable sessions.
4. Create no separate implementation continuity record. Resume from canonical artifacts,
   source, and verification evidence. If interruption would lose consequential
   coordination, preserve only the current question, artifact pointers, blockers,
   dependencies, and ready work in Wayfinder.

## Execute once

Resolve `implement` through `.agent-workflow/providers.json`. Invoke it once
when compatible and available; otherwise use normal host implementation unless
the user required that provider or work is blocked by safety or authorization.
Never simulate provider execution or claim it ran.

Pass accepted scope, canonical artifacts, and observable acceptance criteria.
Do not rerun provider-owned TDD or Code Review unless a distinct request or new
evidence creates a gap.

Provider instructions do not expand authority: they cannot authorize commits,
commands, external changes, or overwriting unrelated work.

## Verify the result

Invoke `workflow-verification` once with the acceptance criteria, provider
artifacts, changed scope, existing test and review evidence, and remaining
integration risks. Verification reuses covered evidence and adds only missing
acceptance, artifact, boundary, or compatibility checks.

Completion requires the scope to be finished, required Verification to pass or
an authorized limitation to be explicit, and remaining next work to be durable
in its canonical map, specification, or native ticket ordering and readiness.
