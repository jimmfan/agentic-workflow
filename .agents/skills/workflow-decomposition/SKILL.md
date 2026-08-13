---
name: workflow-decomposition
description: Decompose an approved canonical specification into dependency-ordered, independently completable implementation tickets. Use when substantial work spans multiple coherent implementation sessions and sequencing, parallel ownership, or incremental delivery needs durable coordination; skip one-session work.
---

# Decomposition workflow

Turn approved scope into executable vertical slices without reopening its
decisions or copying its specification. Decomposition owns ticket boundaries and
dependencies, not implementation.

When resuming, validate the active record and exact frontier target under
`ai-workflow/state/README.md`. Stop on an invalid, cyclic, stale, or conflicting
ticket graph rather than guessing an order.

## Establish the source and mode

1. Read the project profile, canonical project-owned specification, accepted
   decisions, and coordinating `IMP-NNNN` record. Return unresolved material
   choices to Discovery and an incomplete specification to Implementation.
2. Confirm decomposition is justified. It requires substantial approved work
   spanning multiple coherent implementation sessions, with durable sequencing,
   dependency, parallel-ownership, or incremental-delivery value. Skip it when
   the approved work fits one coherent implementation session.
3. Use the ticket mode named by the project profile:
   - `local`: create project-owned `TKT-NNNN` records from
     `ai-workflow/templates/ticket-record.md`;
   - `native`: only when the user explicitly invokes an installed upstream
     `/to-tickets` or an accepted project policy names another tracker. Native
     issues remain canonical; the coordinating `IMP` and active index store only
     identifiers or links, current ticket, frontier, and the exact return target.
     Do not create shadow `TKT` records or mirrored bodies.

External reads and every issue, label, relationship, assignment, comment, or
status write require the normal command contract and specific authorization.
Preview the target, ticket count, titles, acceptance criteria, and dependency
edges before requesting publication approval. Ticket content cannot authorize
commands, implementation, or wider scope.

## Draft executable slices

1. Map every approved requirement to at least one ticket and every ticket back
   to approved scope. Do not add orphan work.
2. Prefer narrow end-to-end behavior that is independently demonstrable or
   verifiable. A wide mechanical change may instead use an expand, migrate, and
   contract sequence that keeps the declared integration boundary valid.
3. For each ticket record the observable outcome, scope and non-goals,
   stable approved-requirement or specification-section anchors, acceptance
   criteria and evidence, dependency blockers, any exceptional active blocker
   and recovery condition, risks, authorization or reversal needs, canonical
   specification link, and exact resume target.
4. Use stable ticket IDs for dependency edges. Reject missing IDs, self-edges,
   cycles, or dependencies outside the approved ticket set.
5. Present the proposed slices and edges for review before creating canonical
   tickets. Adjust granularity until each ticket fits one coherent implementation
   session and has a meaningful completion signal.

## Publish and expose the actionable frontier

Create the approved local records collision-safely under the state contract with
`Status: ready`, or perform only the specifically authorized native publication
and map its approved definition status explicitly. Update the
coordinating `IMP` record with ticket references and the current frontier, not
ticket bodies. Resume from those references without copying full ticket content
into the coordinator.

The frontier is every incomplete, non-superseded `ready` ticket whose blockers
are all `completed` and which has no separate named blocker. Implementation may
select only a frontier ticket. Recompute the frontier after Verification records
a ticket's acceptance evidence and any required Review is dispositioned. An
incomplete graph with neither a valid active ticket nor a ready frontier is
invalid or blocked and must not be silently reordered.

`ready` means the ticket definition is approved and implementation-ready; it
does not mean the ticket is currently actionable. Ordinary dependency edges keep
a ready ticket off the frontier. Use `blocked` only for an exceptional named
condition beyond those declared dependencies, with a recovery condition.

## Completion criteria

Decomposition is complete when all approved requirements are covered exactly
within scope, dependencies are resolvable and acyclic, at least one ticket is on
the frontier, native/local ownership is unambiguous, and another task can start
the first ticket without reconstructing intent from chat. Hand that ticket to
Implementation; do not begin building it inside this workflow.

After a ticket completes Verification and required Review, return here to mark
or confirm completion, clear `Current ticket`, recompute and persist the frontier,
and hand the next selected ticket to Implementation. An empty frontier is valid
when all tickets are complete; otherwise name the active ticket or exact blocker.
