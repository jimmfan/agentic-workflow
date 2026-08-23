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

- [ADR-0011](../../architecture-decisions/0011-use-map-first-wayfinder-state.md) owns sparse map-first knowledge, one coherent effective runtime, semantic territory, convergence, and the native `to-tickets` boundary.
- [ADR-0025](../../architecture-decisions/0025-preserve-authority-at-consequential-boundaries.md) prevents authority-dependent assumptions from becoming accepted downstream work.
- Pre-contract files under this effort's `tickets/` directory remain untouched project history and are not a current work frontier.

## Blockers and dependencies

None.

## Next work

None for this effort.

## Notes

- Live source and current user authority outrank stale saved assumptions.
- The detailed semantics stay in the lazily loaded [Wayfinder state contract](../../.agent-workflow/contracts/wayfinder-state.md); root routing instructions remain compact.
- Repository history contains no authoritative released I#/X#/O# syntax or semantics. The useful identity and structure intent now lives directly in the semantic map and structure-derived naming rules.
- This directory deliberately keeps its established `wayfinder-local-state-integration` slug even though the refined H1 is broader. Existing effort paths do not move when wording improves.
- Automatic Wayfinder remains experimental and keeps its conservative threshold.
- [D1 — Use a fingerprinted local-mode provider overlay](decisions/D1-fingerprinted-local-mode-overlay.md) remains only as the superseded pointer used by pre-contract T# history; ADR-0011 owns the current coherent-runtime rule.

## Decisions so far

- [ADR-0011 — Use map-first Wayfinder state](../../architecture-decisions/0011-use-map-first-wayfinder-state.md) — Keep sparse current knowledge, one coherent runtime, semantic territory, canonical settlement, convergence, and native `to-tickets` ownership.
- [ADR-0025 — Preserve authority at consequential boundaries](../../architecture-decisions/0025-preserve-authority-at-consequential-boundaries.md) — Keep authority-dependent assumptions out of accepted decisions, specifications, tickets, and implementation direction.

## Out of scope

- Broadening automatic Wayfinder routing for bounded debugging or ordinary work.
- Building a generic projection framework, upgrading the pinned upstream snapshot, adding settlement/archive machinery, or introducing another durable state tree.
- Rewriting or retroactively regrading completed ITBench, Harbor, or frozen Wayfinder smoke results.
