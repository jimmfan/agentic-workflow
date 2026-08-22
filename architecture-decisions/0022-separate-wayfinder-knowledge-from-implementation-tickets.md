# ADR-0022: Separate Wayfinder knowledge from implementation tickets

- Status: accepted
- Date: 2026-08-18
- Amends: ADR-0011, ADR-0016, and ADR-0020
- Preserved by: ADR-0023 and ADR-0028

## Context

The local Wayfinder adapter introduced U# questions, D# decisions, and T# work
items so the upstream issue-tracker method could operate in project-owned Git
state. The framework now also has a dedicated `to-tickets` workflow whose native
artifacts preserve dependency edges and implementation frontiers. Keeping T# in
Wayfinder therefore creates two ticket concepts, duplicate routing rules, and a
second status surface that must be reconciled.

Wayfinder already uses its map as the low-resolution re-entry point and already
records observations and established conclusions informally. Those concepts
need clearer semantics when they are independently durable, but making every
effort materialize a full ontology would replace one bookkeeping burden with
another.

## Decision

Wayfinder owns sparse durable project knowledge:

- U# is an unresolved consequential question;
- E# is an independently useful evidence item recording an observation with
  provenance, scope, and limitations;
- F# is a sufficiently established, scoped descriptive conclusion; and
- D# is a committed choice made under project authority.

Every child type is optional and lazy. `map.md` alone is a valid effort. Small
observations and conclusions stay inline unless independent preservation,
revision, dispute, reuse, or provenance makes a child valuable. Facts link their
supporting evidence or direct authoritative sources; reciprocal evidence
backlinks are optional.

`map.md` owns current state, blockers, dependencies, and the smallest coherent
next work. `implement` or its authorized host-native fallback may consume that
scope directly. When remaining work needs dependency ordering or independently
deliverable sessions, Wayfinder hands off to `to-tickets` and links its canonical
native frontier. Wayfinder does not create or mirror T# work items.

When evidence conflicts with an F#, preserve the evidence. Mark the fact
disputed and surface or reopen the relevant U# while the conflict remains. Once
resolved, update the same scoped F# with a concise change note and review
dependent decisions without changing them silently.

Keep the full vocabulary and reconciliation rules in the lazily loaded
Wayfinder state contract. The installed framework README provides a short human
pointer; root routing context does not enumerate the model, and lifecycle does
not seed a README or any other file in project-owned Wayfinder state.

Older `tickets/T#` artifacts receive no compatibility code or automatic
migration. Lifecycle preserves them only because all project-owned state is
opaque. Before resuming an old effort, a project owner manually copies its live
status, blockers, dependencies, and next action into `map.md`, invokes
`to-tickets` if substantial decomposition is still useful, updates map links,
and then keeps or removes the old files according to project needs.

## Consequences

Fresh-session continuity no longer depends on a Wayfinder ticket: the map alone
contains the orientation and current handoff. Complex implementation planning
has one owner, `to-tickets`, and implementation consumes one canonical scope.
Agents normally load only the map; E#/F# detail costs context only when linked
and relevant.

The change is intentionally breaking before 1.0. Existing efforts that rely on
T# status cannot resume correctly until manually migrated. This avoids ongoing
dual-read behavior, version detection, automatic state rewrites, and tests for a
retired ticket model.

## Alternatives considered

- Keep T# as lightweight work and use `to-tickets` only for large work: rejected
  because size does not create a clean ownership seam and agents must still
  choose and reconcile two ticket systems.
- Retain transparent T# read compatibility: rejected because it preserves the
  ambiguous implementation input and adds a code path solely for pre-1.0 state.
- Rename T# to another Wayfinder work-item abstraction: rejected because it does
  not remove the overlap.
- Require E# and F# for every effort: rejected because map-only state is enough
  for ordinary continuity and mandatory extraction would increase context and
  bookkeeping.
