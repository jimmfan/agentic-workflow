# ADR-0003: Keep Wayfinder and Teach optional references

- Status: accepted
- Date: 2026-08-12

## Context

Wayfinder and Teach provide useful public workflow patterns but are not installed
dependencies, use broader artifact/tracker conventions, and do not jointly supply
the exact project-local Teach-to-Discovery resume contract required here.

## Decision

Implement original minimal Discovery and Teach skills inside the framework.
Attribute the reference designs and immutable revision, but do not execute, copy,
or require them. They remain explicit opt-in capabilities when separately
installed: upstream Wayfinder only for a user-requested foggy multi-session map,
and upstream Teach only for a user-requested multi-session learning project in a
dedicated workspace. Preserve their native artifacts as canonical and store only
the origin and exact return target in framework state. If unavailable, explain
the intended handoff and offer the local workflow.

## Consequences

The MVP remains functional offline and without third-party skills. It does not
inherit or duplicate their richer tracker maps or lesson artifact system.
Upstream invocation is explicit-only and may mutate its tracker or teaching
workspace, so normal authorization and workspace boundaries still apply.

## Alternatives considered

- Hard-depend on both upstream skills: richer behavior but unavailable by default
  and incomplete cross-workflow composition.
- Vendor their contents: more maintenance and license-copy obligations.
- Ignore the references: smaller research effort but loses proven persistence and
  responsibility-boundary ideas.
