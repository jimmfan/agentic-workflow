# ADR-0024: Use current-state Wayfinder identifiers

- Status: accepted
- Date: 2026-08-18
- Amends: ADR-0011, ADR-0016, ADR-0022, and ADR-0023

## Context

Wayfinder's U/E/F/D files are current knowledge roles: unresolved questions,
independently useful evidence, established descriptive conclusions, and
committed choices. Their numeric prefixes make current cross-document links
compact, while readable filename slugs preserve human orientation. No
repository workflow treats the numbers as immutable historical primary keys.
Git preserves historical states that actually enter Git.

Retaining obsolete children or adding durable high-water state solely to keep
retired numbers unique would make current navigation carry historical identity
bookkeeping that has no independent navigational value.

## Decision

U/E/F/D identifiers are stable while their records remain current. Existing
current records are never renumbered, and two current records of one type never
share a number. Filenames retain both, for example
`U17-node-group-isolation.md`. A new record uses one greater than the highest
currently present identifier of its type, or `1` when none exists; allocation
does not search for interior gaps.

Because different readable slugs can produce different paths for the same
number, exact-path no-overwrite is insufficient under concurrent creation.
Rereads likewise cannot close the race between a retirement's final reference
scan and removal. Atomic creation of one empty transient
`.wayfinder-mutation-lock/` directory therefore serializes map and child
mutations for the effort. It is removed afterward, contains no data, and is
never committed or treated as durable Wayfinder state. A busy or stale lock is
never stolen; work waits through host coordination or stops conservatively.
This remains smaller than separate allocation and retirement coordination.

A record may leave Wayfinder after independently useful current information is
preserved and all current map and child references are reconciled. Its exact
contents need not first enter Git. The number is then no longer reserved and may
reappear through the ordinary highest-current-plus-one rule in a later
repository state.

## Consequences

Wayfinder retains only its smallest useful current representation and needs no
allocation metadata or migration. Numeric references are repository-state
local. Git history can interpret states that entered Git, while intentionally
transient navigation records may disappear without a forced historical commit.

Permanent tombstones, `allocation.md`, archive trees, registries, event logs,
history or lifecycle databases, graph indexes, and package-manager-style
ownership are rejected. They solve repository-lifetime identity, which
Wayfinder does not require.
