# Wayfinder knowledge settlement

- Status: completed

## Destination

Define and implement the smallest safe lifecycle that keeps Wayfinder focused
on current navigation, settles resolved or obsolete U/E/F/D knowledge, and
makes completed, abandoned, or superseded efforts progressively distinguishable
while Git retains historical evolution.

## Current state

- The prior runtime-projection and stable effort-selection work is present and
  explicitly left settlement and effort completion to this distinct effort.
- The working tree was clean at the start of this effort.
- The current contract allocates each U/E/F/D identifier as one greater than the
  highest current identifier of that type and never renumbers current records.
- The existing `.agent-workflow-state/archive/` contract belongs to DEC/IMP/DBG
  records, not Wayfinder children or effort directories.
- The accepted design treats numbers as current-state references, not historical
  primary keys. Child files leave current state when they lack independent
  navigational value; their numbers may later be reused and Git preserves the
  historical meanings.
- Atomic creation of one empty transient per-effort lock serializes all map and
  child mutations. Allocation uses the current maximum; retirement holds the
  same lock while rechecking references and removing a file whose current
  content is already recoverable from Git. Unsafe state retains the record.
- Each map gains one optional `Status: current | completed | abandoned |
  superseded` line. Explicit current efforts outrank historical ones during a
  likely resume; historical efforts remain accessible when directly relevant.
- The authored contract, installed payload, generated runtime, documentation,
  ADR, fixtures, and deterministic behavior catalog now agree on this model.
- Final verification passed 107 source-package tests, 69 evaluation tests, 29
  static behavioral scenarios, package verification with tests, projection
  regeneration, both closing review axes, and `git diff --check`.

## Blockers and dependencies

None. Current identifier stability, concurrent mutation safety, project-owned
state, provider projection parity, and legacy maps are covered without a
migration sweep.

## Next work

None for this effort.

## Notes

- [Wayfinder state contract](../../../.agent-workflow/contracts/wayfinder-state.md)
- [ADR-0022](../../../architecture-decisions/0022-separate-wayfinder-knowledge-from-implementation-tickets.md)
- [ADR-0023](../../../architecture-decisions/0023-own-the-wayfinder-runtime-projection.md)
- [ADR-0024](../../../architecture-decisions/0024-use-current-state-wayfinder-identifiers.md)
- Git is the history mechanism; this effort introduces no second archive,
  registry, event log, allocation database, or global maintenance sweep.
- Permanent compact tombstones and high-water metadata confuse current knowledge
  with historical identity. Neither is needed when Git owns historical meaning.
  The existing archive convention remains scoped to other workflow records.

## Decisions so far

- Use current-state identifiers plus map-owned effort status. ADR-0024 explicitly
  rejects lifetime-uniqueness bookkeeping, tombstones, registries, archive trees,
  event logs, and lifecycle databases.

## Not yet specified

None currently.

## Out of scope

- Reopening runtime ownership, projection mechanics, effort naming, stable
  paths, routing, the U/E/F/D model, or the `to-tickets` boundary without a
  concrete contradiction.
- Migrating unrelated or consuming-repository Wayfinder state.
- Building an archive subsystem, history database, global registry, generic
  migration, or automatic settlement sweep.
