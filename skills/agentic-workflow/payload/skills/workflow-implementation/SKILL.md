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
   spec or ticket artifact. The workflow that created that durable artifact owns
   its canonical location; consume it by reference instead of copying it into a
   framework path. On resume, validate the exact `IMP` pointer and provider
   artifact in `.ai-workflow-state/active.md`.
2. Return a material unresolved choice to `workflow-discovery` and an
   unexplained existing failure to `workflow-debugging`.
3. Use one coherent ready scope. If substantial work needs dependency-ordered
   sessions, select upstream `to-tickets` first, apply its host invocation policy,
   and use its native ticket identities unchanged after it actually runs. Do not
   create shadow framework tickets.
4. Do not create an `IMP-NNNN` record merely because Implementation or a
   provider handoff was selected. After execution begins, create one only when
   orchestration must survive sessions and repository writes are authorized.
   Link the canonical spec, map, or ticket; do not copy its body or overwrite a
   different active durable workflow.

## Resolve invocation before execution

Resolve the implementation capability through `.ai-workflow/providers.json` and
validate the installed `implement` skill. If its pinned metadata, dependencies,
or active-host support are missing, stop with the provider diagnostic rather
than substituting local build, TDD, or review instructions.

Apply the declared host invocation policy. When `implement` is user-only and was
selected only from normal intent, state that it is the selected workflow and give
the exact handoff: `$implement` in Codex or `/implement` in GitHub Copilot. If
the active primary host cannot be distinguished between those two, label both
forms without assuming one. Stop before
implementation; do not load or simulate the provider, create its artifacts,
create/update `IMP` or `active.md`, expand authorization, or claim it ran. The
route marker is the root policy's `implement-handoff` form, not an executed
`implement` stage. When the user has explicitly invoked `implement` with valid
host syntax, continue to execution instead of handing it back again.

## Execute the provider once

Only after the provider is actually invoked, give `implement` the accepted
scope, canonical artifact, observable acceptance criteria, and configured
project commands. Let it invoke `tdd` and `code-review` as capabilities inside
the dominant Implementation workflow. Their use does not replace the dominant
durable workflow or require an `active.md` transition. Do not run either again
unless the user later requests a distinct fixed-point review or new evidence
invalidates the earlier result.

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
ticket frontier; never infer or mirror the next ticket in Agentic Workflow
durable state.
