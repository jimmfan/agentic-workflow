# Domain language normalization

## Objective

Keep Agent Workflow's canonical language coherent across routing, Wayfinder,
authority boundaries, packaged projections, documentation, and deterministic
tests while preserving the accepted Phase 2 design.

## Scope

Included:

- deterministic initialization of canonical new Wayfinder maps;
- the distinction among ready work, dependencies, and blockers;
- ownership and authority boundaries;
- the relationship between a U# unresolved-question record and unresolved
  consequential uncertainty that may block particular work;
- the identified ambiguous `settled`, `project-owned`, Current state, and nearby
  acceptance wording;
- synchronization of authored, packaged, runtime, generated, and installed
  surfaces; and
- focused semantic, structural, synchronization, and compatibility coverage.

Excluded:

- redesigning the 18-term glossary, U/E/F/D records, Wayfinder effort
  recognition or resumption, routing architecture, provider integration,
  lifecycle behavior, or public interfaces;
- changing identifiers, provider schemas, lifecycle commands or statuses,
  `<skill>-handoff`, or `Derived from`;
- modifying pinned provider snapshots or creating migration, compatibility,
  history, backup, rollback, or registry machinery; and
- rewriting unrelated existing Wayfinder maps to match the new authored shape or
  performing another broad terminology or architecture audit.

## Ready work

None.

## Current state

- Current source distinguishes project decision authority from action
  authorization and host permission, uses unresolved consequential uncertainty
  as the potentially blocking condition, preserves U# as the unresolved-question
  record, and retains delegated technical judgment within its authorized scope.
- The identified ambiguous `settled`, decision-related `project-owned`, and
  `semantic coordination state` constructions remain removed from current
  canonical prose while historical fixture names and identifiers remain
  available for compatibility coverage.
- The user committed the canonical eight-heading new-map structure. Ready work
  follows Objective and Scope; Dependencies and Blockers are separate; Ownership
  and Key references are explicit; headings without current content retain
  `None.`.
- The earlier recommendation to combine blockers and dependencies and omit other
  empty headings is rejected and no longer represents current project direction.
- A framework-owned literal schema and installed Python initializer now own
  deterministic new-map shell creation. Wayfinder retains semantic judgment and
  existing maps remain resumable without migration or formatting-only rewrites.
- The Wayfinder skill now invokes that initializer with one short command, and
  the state contract retains only map semantics rather than initializer or schema
  implementation policy. Authored and installed projections remain synchronized.

## Dependencies

None.

## Blockers

None.

## Ownership

- `CONTEXT.md` owns Agent Workflow's canonical domain vocabulary.
- Root policy and accepted ADR-0025 own the operational separation among project
  decisions, action authorization, host permission, and delegated technical
  judgment.
- The literal framework schema owns exact new-map headings, ordering,
  placeholders, and empty representation.
- The installed Python helper owns safe deterministic creation of a new map
  shell.
- The Wayfinder state contract and skill own persistence selection, semantic
  content, reconciliation, resumption, and effort ending.
- Lifecycle owns replaceable `.agent-workflow/` delivery and does not manage
  project-owned `.agent-wayfinder/` state.

## Key references

- [Project language](../../CONTEXT.md)
- [Map-first architecture decision](../../architecture-decisions/0011-use-map-first-wayfinder-state.md)
- [Ownership architecture decision](../../architecture-decisions/0010-separate-framework-output-from-project-owned-state.md)
- [Authority architecture decision](../../architecture-decisions/0025-preserve-authority-at-consequential-boundaries.md)
- [Wayfinder state contract](../../skills/agent-workflow/payload/agent-workflow/contracts/wayfinder-state.md)
- [Canonical map schema](../../skills/agent-workflow/payload/agent-workflow/schemas/wayfinder/map.md)
- [Wayfinder initializer](../../skills/agent-workflow/payload/agent-workflow/tools/wayfinder.py)
