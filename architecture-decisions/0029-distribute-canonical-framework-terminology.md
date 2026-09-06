# ADR-0029: Distribute canonical framework terminology

- Status: accepted
- Date: 2026-09-06

## Context

Agent Workflow's root `CONTEXT.md` previously defined framework terms such as Objective, Scope, Dependency, and Project-owned only in the source repository.
Consuming projects use those same concepts but did not receive their canonical definitions.
These meanings span routing, Wayfinder, authority, and lifecycle ownership.

## Decision

Use `.agent-workflow/terminology.md` as the one canonical source of Agent Workflow terminology in the source repository and consuming projects.
Author it at that path and distribute it identically through the existing framework lifecycle.
It is framework-owned and reconstructable; install and update replace it with current source bytes, and remove deletes it with `.agent-workflow/`.

The distributed root policy tells agents to read the file and use its definitions when an Agent Workflow-specific term materially affects interpretation or behavior.

Terminology owns cross-cutting term meanings; specialized contracts, runtime instructions, and source own required behavior.
The file lives directly under `.agent-workflow/` because its language spans framework areas.

Domain Modeling separately maintains optional project-owned `CONTEXT.md`, `CONTEXT-MAP.md`, and per-context files using its existing `CONTEXT-FORMAT.md` guidance.

## Consequences

Maintainers and consuming agents interpret the same framework language while loading definitions only when useful.
Framework terminology follows ordinary desired-state convergence and can be reconstructed from the selected snapshot.
Framework terminology changes are source-repository maintenance decisions.
