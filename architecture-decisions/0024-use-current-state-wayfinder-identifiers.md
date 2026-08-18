# ADR-0024: Use current-state Wayfinder identifiers

- Status: accepted
- Date: 2026-08-18
- Amends: ADR-0011, ADR-0016, ADR-0022, and ADR-0023

## Context

Wayfinder's U/E/F/D files are current knowledge roles: unresolved questions,
independently useful evidence, established descriptive conclusions, and
committed choices. Their numeric identifiers make current links readable; no
repository workflow treats them as immutable historical primary keys. Git
already identifies and preserves each historical version of a removed file.

Retaining obsolete children or adding durable high-water state solely to keep
retired numbers unique would make current navigation carry historical identity
bookkeeping that has no independent navigational value.

## Decision

U/E/F/D identifiers are stable while their records remain current. Existing
current records are never renumbered. A new record uses one greater than the
highest current identifier of its type, or `1` when none exists. Atomic creation
of one empty transient `.wayfinder-mutation-lock/` directory serializes all map
and child mutation for an effort, including allocation and retirement. It is
removed after mutation, contains no data, and is never committed or treated as
durable Wayfinder state. A busy or stale lock is never stolen; work waits through
host coordination or stops conservatively.

A record may leave Wayfinder after all current map and child references are
reconciled and recoverable Git history contains its current content. Its number
is then no longer reserved and may be reused in a later repository state. Git
distinguishes the historical meanings.

## Consequences

Wayfinder retains only its smallest useful current representation and needs no
allocation metadata or migration. Numeric references are repository-state
local, so a number seen in historical discussion must be interpreted at that
Git revision or with its historical path.

Permanent tombstones, `allocation.md`, archive trees, registries, event logs,
history or lifecycle databases, graph indexes, and package-manager-style
ownership are rejected. They solve repository-lifetime identity, which
Wayfinder does not require.
