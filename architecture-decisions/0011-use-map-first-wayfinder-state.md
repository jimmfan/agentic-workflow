# ADR-0011: Use map-first Wayfinder state

- Status: accepted
- Date: 2026-08-14
- Consolidated: 2026-08-22

## Context

Durable coordination must let a fresh maintainer or agent recover the useful
shape of an effort without loading a complete activity history. A flat ledger
loses semantic relationships, while an ever-growing structured notebook becomes
an organized warehouse. Duplicating canonical project artifacts or an external
tracker would create competing sources of truth.

Agent Workflow's map-first model and native `to-tickets` handoff also differ
materially from the pinned upstream Wayfinder issue-tracker runtime. Presenting
both operational models at once would force each agent to reconcile conflicting
instructions.

## Decision

When durable coordination is warranted, use project-owned, map-first Wayfinder
state. The current local representation lives under
`.agent-wayfinder/<effort>/`, and `map.md` is its canonical re-entry point.

The map is low-resolution semantic territory, not a type ledger. It preserves
the destination, substantive boundary, major areas, current state, material
blockers and dependencies, and useful next frontier. Optional child knowledge
exists only when it is independently useful; a map-only effort is valid and
child detail loads progressively.

Wayfinder represents current navigation rather than permanent identities or an
append-only journal. Lasting outcomes move to their canonical owners, current
state converges and shrinks, and Git preserves committed historical evolution.
Preserve a question independently only when retaining it or its eventual answer
could materially improve a later developer's ability to make or evaluate a
decision. Expose a ready scope only after its material dependencies are answered
or explicitly dispositioned.

Authorized work that changes represented reality owns scoped reconciliation of
the affected map and state before claiming completion. Canonical artifacts
remain authoritative. Read-only work may report staleness but does not repair
project-owned state.

The effective Wayfinder instructions present one coherent operational model
rather than prepend local state rules to a contradictory tracker specification.
Matt Pocock's pinned skill remains the methodological source and reviewed
provenance. The derived runtime preserves useful destination, map, fog,
frontier, readable-name, progressive-resolution, and authority-sensitive
reasoning concepts while implementing the project's map-first contract.

Lifecycle operations treat the complete `.agent-wayfinder/` tree as opaque
project data. Exact state mechanics remain progressively loaded from the
Wayfinder contract.

## Consequences

A fresh session can orient from one small map and load only relevant detail.
State can remain sparse and human-editable without a database, event log,
global active index, shadow `.scratch/` tree, or duplicated tracker.

Executable decomposition and its native frontier belong to `to-tickets`;
Wayfinder links that artifact rather than mirroring T# work as a second
ticket/status surface.

U/E/F/D schemas, numbering, filenames, effort selection, locks, settlement,
retirement, statuses, templates, and reference rules are contract and test
details, not architectural commitments.

## Alternatives considered

- Persist a complete journal or permanent child identities: rejected because
  current navigation should converge instead of accumulating maintenance state.
- Duplicate provider or project artifacts inside Wayfinder: rejected because
  two canonical copies would drift.
- Layer map-first rules over the upstream tracker runtime: rejected because one
  effective skill must describe one coherent way of operating.
- Require a database, graph index, external tracker, or strict Markdown schema:
  rejected because low-resolution maps, links, agent reasoning, and Git cover
  the current need without making project-owned edits lifecycle failures.

## Reconsideration trigger

Reconsider if fresh sessions repeatedly cannot reconstruct consequential state,
if map convergence loses needed information, or if a different representation
provides a materially simpler and safer re-entry model.
