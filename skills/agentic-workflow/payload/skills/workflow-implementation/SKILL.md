---
name: workflow-implementation
description: Orchestrate one settled implementation scope through the pinned upstream implement provider and independent framework verification. Use after material decisions are resolved; skip trivial direct edits and unexplained failures.
---

# Implementation integration

This skill owns the execution and handoff boundary, not implementation
methodology or durable workflow state. Upstream `implement` owns the build loop,
appropriate TDD, and closing Code Review.

## Establish the boundary

1. Read the project profile, applicable accepted decisions, and the canonical
   map, specification, or native ticket. Consume that artifact by reference.
2. Return a material unresolved choice to Discovery or Wayfinder according to
   the coordination threshold, and an unexplained existing failure to Debugging.
3. Use one coherent ready scope, including `map.md` Next work when sufficient.
   If approved work needs dependency-ordered or independently deliverable
   sessions, select `to-tickets` first and preserve its native identities.
4. Create no IMP or replacement execution record. Resume from the canonical
   map, specification, ticket, source, and verification evidence. If an
   interrupted implementation would otherwise lose consequential coordination,
   transition to Wayfinder before stopping and persist only the exact frontier,
   artifact pointers, blockers, and next work needed to continue.

## Resolve the provider before execution

Resolve implementation through `.agent-workflow/providers.json` and validate
the installed `implement` skill when available. If installation, configuration,
or active-host support is missing, continue with normal host implementation and
report that the preferred provider did not run. Stop only when the user required
that provider or safety or authorization blocks work.

On Codex and GitHub Copilot, invoke the compatible installed `implement`
provider once after its activation metadata and prerequisites are ready.
Otherwise use host-native implementation without loading or simulating provider
internals or claiming provider execution.

## Execute once

Give the provider the accepted scope, canonical artifact, observable acceptance
criteria, and configured project commands. Let it invoke TDD and Code Review as
capabilities inside Implementation. Do not run either again unless the user
requests a distinct review or new evidence invalidates the earlier result.

The framework authorization boundary still wins. An upstream instruction to
commit does not authorize a commit, and a ticket does not authorize commands or
external changes. Preserve unrelated working-tree edits.

## Verify the integrated result

After provider or host-native implementation finishes, invoke
`workflow-verification` once with acceptance criteria, provider artifacts,
changed scope, tests and review already performed, and remaining integration
risks. Verification reuses upstream evidence and adds only uncovered acceptance,
artifact, boundary, or compatibility checks.

Completion requires the implementation scope to be finished, required
Verification to pass or an authorized limitation to be explicit, and any
remaining next work to be durable in its canonical map, specification, or
native ticket frontier.
