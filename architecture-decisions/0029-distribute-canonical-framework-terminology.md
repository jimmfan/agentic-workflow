# ADR-0029: Distribute canonical framework terminology

- Status: accepted
- Date: 2026-09-06

## Context

Agent Workflow's root `CONTEXT.md` previously defined framework terms such as Objective, Scope, Dependency, and Project-owned only in the source repository.
Consuming projects use those same concepts but did not receive their canonical definitions.
The filename also overlapped with Domain Modeling's separate project-owned context artifacts.

These meanings span routing, Wayfinder, authority, and lifecycle ownership.
They need a shared source without enlarging always-loaded root policy or turning a glossary into a behavior contract.

## Decision

Use `.agent-workflow/terminology.md` as the one canonical source of Agent Workflow terminology in the source repository and consuming projects.
Author it at that path and distribute it identically through the existing framework lifecycle.
It is framework-owned and reconstructable; install and update replace it with current source bytes, and remove deletes it with `.agent-workflow/`.

The distributed root policy tells agents to read the file and use its definitions when an Agent Workflow-specific term materially affects interpretation or behavior.
This is progressive loading, not a requirement to read it on every request.
Root policy does not duplicate its definitions.

Terminology owns cross-cutting term meanings; specialized contracts, runtime instructions, and source own required behavior.
The file lives directly under `.agent-workflow/`, outside `contracts/`, because its language spans framework areas rather than one narrow contract.

Domain Modeling's project-owned `CONTEXT.md`, `CONTEXT-MAP.md`, and per-context files remain a separate capability, including its existing `CONTEXT-FORMAT.md` guidance.
Domain Modeling does not own or modify `.agent-workflow/terminology.md` in consuming projects.

Remove the old source-repository root `CONTEXT.md` without an alias, compatibility path, migration mechanism, or second terminology source.

## Consequences

Maintainers and consuming agents interpret the same framework language while loading definitions only when useful.
Framework terminology follows ordinary desired-state convergence and can be reconstructed from the selected snapshot.
Project domain models retain their own meanings, locations, and preservation boundary.
Framework terminology changes remain source-repository maintenance decisions rather than consuming-project Domain Modeling edits.

## Alternatives considered

- Keep terminology only at the source root: rejected because consuming projects need the same meanings and the name overlaps with project domain artifacts.
- Copy definitions into root policy: rejected because it increases always-loaded context and creates another terminology representation.
- Place terminology under `contracts/`: rejected because these meanings cross multiple framework boundaries rather than specifying one behavior contract.

## Reconsideration trigger

Reconsider if framework areas require independently maintained meanings that cannot remain clear in one progressively loaded terminology source.
