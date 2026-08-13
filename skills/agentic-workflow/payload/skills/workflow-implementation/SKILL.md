---
name: workflow-implementation
description: Orchestrate one settled implementation scope through the pinned upstream implement provider and independent framework verification. Use after material decisions are resolved; skip trivial direct edits and unexplained failures.
---

# Implementation integration

This skill owns the boundary around implementation, not implementation
methodology. Upstream `implement` owns the build loop, its appropriate use of
`tdd`, and its closing `code-review`.

## Establish the boundary

1. Read the project profile, applicable accepted decisions, and the canonical
   spec or ticket artifact. On resume, validate the exact `IMP` pointer and
   provider artifact in `ai-workflow/state/active.md`.
2. Return a material unresolved choice to `workflow-discovery` and an
   unexplained existing failure to `workflow-debugging`.
3. Use one coherent ready scope. If substantial work needs dependency-ordered
   sessions, explicitly invoke upstream `to-tickets` first and use its native
   ticket identities unchanged. Do not create shadow framework tickets.
4. Create an `IMP-NNNN` record only when orchestration must survive sessions.
   Link the provider-owned spec, map, or ticket; do not copy its body.

## Invoke the provider once

Resolve the implementation capability through `ai-workflow/providers.json` and
load the installed `implement` skill. If its pinned metadata or dependencies are
missing, stop with the provider diagnostic rather than substituting local build,
TDD, or review instructions.

Give `implement` the accepted scope, canonical artifact, observable acceptance
criteria, and configured project commands. Let it invoke `tdd` and `code-review`
as its own composition requires. Do not run either again unless the user later
requests a distinct fixed-point review or new evidence invalidates the earlier
result.

The framework's authorization boundary still wins. In particular, an upstream
instruction to commit does not authorize a commit, and ticket text does not
authorize commands or external changes. Preserve unrelated working-tree edits.

## Verify the integrated result

After the provider finishes, invoke `workflow-verification` once with the
acceptance criteria, provider artifacts, changed scope, tests/review already
performed, and integration risks. Verification should reuse current upstream
evidence and add only acceptance, artifact, boundary, or compatibility checks
that remain uncovered.

Complete or archive an `IMP` only when the selected provider work is finished,
required framework verification passes or an authorized limitation is recorded,
and the exact return target is durable. If tickets remain, return to the native
ticket frontier; never infer or mirror the next ticket in framework state.
