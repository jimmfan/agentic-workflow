# Wayfinder runtime projection and effort selection

- Status: completed

## Destination

A lifecycle-safe, Agent Workflow-owned Wayfinder runtime that preserves the
pinned method's navigation discipline, structures semantic territory before
child knowledge accumulates, and converges toward canonical project ownership
with native `to-tickets` handoff when implementation needs decomposition.

## Territory

- Runtime method — destination, territory, fog, frontier, conditional
  resolution mechanisms, convergence, and no-state assessment.
- State contract — effort selection, flat optional U/E/F/D knowledge,
  reconciliation, locking, retirement, settlement, and completion mechanics.
- Canonical ownership — ADRs, project documentation/source, provider-native
  artifacts, `to-tickets`, and Implementation own durable outcomes appropriate
  to their domains.

The runtime points to the state contract instead of duplicating its mechanics;
the map organizes semantic territory while U/E/F/D classify only independently
useful current knowledge within it.

## Current state

- [ADR-0022](../../../architecture-decisions/0022-separate-wayfinder-knowledge-from-implementation-tickets.md) keeps map-first U/E/F/D knowledge sparse and implementation work items outside Wayfinder.
- [ADR-0023](../../../architecture-decisions/0023-own-the-wayfinder-runtime-projection.md) owns one concise runtime while the pinned raw snapshot remains immutable provenance.
- [ADR-0025](../../../architecture-decisions/0025-preserve-human-authority-across-workflows.md) prevents authority-dependent assumptions from becoming accepted downstream work.
- [ADR-0026](../../../architecture-decisions/0026-structure-wayfinder-territory-and-converge-it.md) requires semantic territory, structure-derived naming, canonical settlement, and shrinkage without a physical area hierarchy.
- Pre-contract files under this effort's `tickets/` directory remain untouched project history and are not a current work frontier.

## Blockers and dependencies

None.

## Next work

None for this effort.

## Notes

- Live source and current user authority outrank stale saved assumptions.
- The detailed semantics stay in the lazily loaded [Wayfinder state contract](../../../.agent-workflow/contracts/wayfinder-state.md); root routing instructions remain compact.
- Repository history contains no authoritative released I#/X#/O# syntax or semantics. The useful identity and structure intent now lives directly in the semantic map and structure-derived naming rules.
- This directory deliberately keeps its established `wayfinder-local-state-integration` slug even though the refined H1 is broader. Existing effort paths do not move when wording improves.
- Automatic Wayfinder remains experimental and keeps its conservative threshold.
- [D1 — Use a fingerprinted local-mode provider overlay](decisions/D1-fingerprinted-local-mode-overlay.md) remains only as the superseded pointer used by pre-contract T# history; ADR-0023 owns the current rule.

## Decisions so far

- [ADR-0022 — Separate Wayfinder knowledge from implementation tickets](../../../architecture-decisions/0022-separate-wayfinder-knowledge-from-implementation-tickets.md) — Keep map-first U/E/F/D knowledge sparse and hand substantial decomposition to `to-tickets`.
- [ADR-0023 — Own the Wayfinder runtime projection](../../../architecture-decisions/0023-own-the-wayfinder-runtime-projection.md) — Establish the package-owned runtime body, immutable raw provenance, and selective upstream-porting boundary.
- [ADR-0025 — Preserve human authority across workflows](../../../architecture-decisions/0025-preserve-human-authority-across-workflows.md) — Keep authority-dependent assumptions out of accepted decisions, specifications, tickets, and implementation direction.
- [ADR-0026 — Structure Wayfinder territory and converge it](../../../architecture-decisions/0026-structure-wayfinder-territory-and-converge-it.md) — Organize semantic territory, derive identity from structure, and converge temporary state into canonical ownership.

## Out of scope

- Broadening automatic Wayfinder routing for bounded debugging or ordinary work.
- Building a generic projection framework, upgrading the pinned upstream snapshot, adding settlement/archive machinery, or introducing another durable state tree.
- Rewriting or retroactively regrading completed ITBench, Harbor, or frozen Wayfinder smoke results.
