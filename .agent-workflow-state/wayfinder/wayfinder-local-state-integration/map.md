# Wayfinder local-state integration

## Destination

A lifecycle-safe Wayfinder integration that preserves the pinned upstream
reasoning method while using a sparse Git-native U/E/F/D knowledge model, a
map-owned continuation boundary, and native `to-tickets` artifacts only when
implementation work needs decomposition.

## Current state

- [ADR-0022](../../../architecture-decisions/0022-separate-wayfinder-knowledge-from-implementation-tickets.md) is accepted and implemented: `map.md` owns current state, blockers, dependencies, and next work; Wayfinder no longer creates T# work items.
- U#/E#/F#/D# children are optional and lazy. A map-only effort is valid, and facts require an evidence or direct-source link.
- The source adapter, installed projection, routing, implementation handoff, contracts, documentation, and current behavioral fixtures use the new boundary.
- `python3 skills/agentic-workflow/scripts/verify_package.py --tests` passes all 90 deterministic checks.
- The frozen `wayfinder-local-state-smoke-v1` campaign remains unchanged historical evidence. It does not validate the current U/E/F/D contract.
- Pre-contract files under this effort's `tickets/` directory remain untouched project history and are not a current work frontier.

## Blockers and dependencies

None for the accepted state-model change.

## Next work

No implementation remains for this change. If new live evidence is needed,
define and freeze a new benchmark against the U/E/F/D contract rather than
reusing or editing the historical v1 campaign.

## Notes

- [U1 — How should the pinned Wayfinder method be adapted to local state?](unknowns/U1-adaptation-boundary.md) remains resolved by [D1 — Use a fingerprinted local-mode provider overlay](decisions/D1-fingerprinted-local-mode-overlay.md).
- Live source and current user authority outrank stale saved assumptions.
- The detailed semantics stay in the lazily loaded [Wayfinder state contract](../../../.agent-workflow/contracts/wayfinder-state.md); root routing instructions remain compact.

## Decisions so far

- [D1 — Use a fingerprinted local-mode provider overlay](decisions/D1-fingerprinted-local-mode-overlay.md) — Insert one authoritative local-mode block before the untouched pinned method, and fail closed unless the pinned provider body is recognized.
- [ADR-0022 — Separate Wayfinder knowledge from implementation tickets](../../../architecture-decisions/0022-separate-wayfinder-knowledge-from-implementation-tickets.md) — Keep map-first U/E/F/D knowledge sparse and hand substantial decomposition to `to-tickets`.

## Not yet specified

- Automatic Wayfinder remains experimental and should keep its conservative threshold.

## Out of scope

- Broadening automatic Wayfinder routing for bounded debugging or ordinary work.
- Forking the full upstream Wayfinder skill, adding an external tracker, or introducing another durable state tree.
- Rewriting or retroactively regrading completed ITBench, Harbor, or frozen Wayfinder smoke results.
