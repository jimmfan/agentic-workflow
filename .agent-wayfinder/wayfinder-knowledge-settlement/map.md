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
- The existing `.agent-wayfinder/archive/` contract belongs to DEC/IMP/DBG
  records, not Wayfinder children or effort directories.
- The accepted design treats numbers as current-state references, not historical
  primary keys. Child files leave current state when they lack independent
  navigational value; their numbers may later reappear through ordinary
  highest-current-plus-one allocation. Allocation never searches interior gaps.
- Current child filenames retain numeric prefixes and readable slugs. Existing
  current records are never renumbered, and same-type current numbers cannot
  collide.
- Bare U#/E#/F#/D# references are shorthand within one effort's current state,
  not repository-wide identity. Durable references from outside the effort use
  readable repository-relative Markdown links to a current child path or a
  longer-lived canonical artifact.
- Atomic creation of one empty transient per-effort lock serializes all map and
  child mutations. Readable slugs make path-only no-overwrite insufficient for
  allocation, and the same lock closes retirement's final reference-scan/remove
  race. The lock is coordination only, not durable knowledge or allocation
  state.
- Retirement requires preservation of independently useful current information
  and reconciliation of current effort references plus any known current
  canonical reference that would break or mislead. It requires neither a
  repository-wide scan nor Git reconstruction, and a retiring child's exact
  contents need not enter Git first.
- Each map gains one optional `Status: current | completed | abandoned |
  superseded` line. Explicit current efforts outrank historical ones during a
  likely resume; historical efforts remain accessible when directly relevant.
- The authored contract, installed payload, generated runtime, documentation,
  ADR, fixtures, and deterministic behavior catalog now agree on this model.
- Final verification passed 108 source-package tests, 69 evaluation tests, 29
  static behavioral scenarios, package verification with tests, projection
  regeneration, and `git diff --check`. Both closing review axes completed; all
  substantive findings were corrected, and the Spec re-review was clean.
- The reference-scope clarification in version 0.16.2 passed 11 focused
  Wayfinder-state tests, 109 full source-package tests, and package verification
  with tests. Evaluation code and fixtures did not change, so evaluation tests
  were not rerun for this clarification.

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
- The repository audit found no workflow that consumes repository-lifetime
  U/E/F/D numeric uniqueness; the earlier invariant was self-imposed.
- Permanent compact tombstones and high-water metadata confuse current knowledge
  with historical identity. Neither is needed. The existing archive convention
  remains scoped to other workflow records.

## Decisions so far

- Use current-state identifiers plus map-owned effort status. ADR-0024 explicitly
  rejects lifetime-uniqueness bookkeeping, tombstones, registries, archive trees,
  event logs, and lifecycle databases.
- Retain the transient effort mutation lock because it is the smallest single
  mechanism that prevents readable-slug allocation collisions and makes
  reference-safe retirement atomic; do not turn it into durable state.

## Not yet specified

None currently.

## Out of scope

- Reopening runtime ownership, projection mechanics, effort naming, stable
  paths, routing, the U/E/F/D model, or the `to-tickets` boundary without a
  concrete contradiction.
- Migrating unrelated or consuming-repository Wayfinder state.
- Building an archive subsystem, history database, global registry, generic
  migration, or automatic settlement sweep.
