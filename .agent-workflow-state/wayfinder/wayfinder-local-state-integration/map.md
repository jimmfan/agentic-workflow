# Wayfinder runtime projection and effort selection

## Destination

A lifecycle-safe, Agentic Workflow-owned Wayfinder runtime projection derived
from the pinned upstream method, with a sparse Git-native U/E/F/D knowledge
model, stable effort naming and resumption, a map-owned continuation boundary,
and native `to-tickets` artifacts only when implementation needs decomposition.

## Current state

- [ADR-0022](../../../architecture-decisions/0022-separate-wayfinder-knowledge-from-implementation-tickets.md) is accepted and implemented: `map.md` owns current state, blockers, dependencies, and next work; implementation work items remain outside Wayfinder.
- U#/E#/F#/D# children are optional and lazy. A map-only effort is valid, and facts require an evidence or direct-source link.
- [ADR-0023](../../../architecture-decisions/0023-own-the-wayfinder-runtime-projection.md) replaces the former dual-spec prepend overlay with one concise, framework-owned runtime body. The pinned raw snapshot remains immutable provenance and selective upstream ideas can be ported deliberately.
- ADR-0023 now also protects the reasoning method inside that owned runtime:
  destination, fog, frontier, conditional Domain Modeling, fit-for-purpose
  uncertainty resolution, no-state assessment, and genuine authority gates.
- [ADR-0025](../../../architecture-decisions/0025-preserve-human-authority-across-workflows.md) establishes the cross-workflow rule that authority-dependent assumptions cannot become accepted decisions, specifications, tickets, or implementation direction.
- The projection, provider declaration and adapter, routing and state contracts, documentation, generated skill, and deterministic effort-selection fixtures use the owned-runtime boundary.
- An effort is selected by exact requested path when supplied, otherwise by progressively reading the candidate directory names and maps. Ambiguity is reported without mutation; creation requires selected Wayfinder, authorized and materially useful durable state, no existing match, and a materially distinct destination.
- The focused contract suite passes all 41 tests; the full deterministic package
  gate passes all 111 tests; all 14 declared provider skills match the bundled
  projection; and package verification passes.
- Independent Standards and Spec review found one impossible scenario
  expectation, incomplete Research/Debugging reconciliation assertions,
  duplicated prose fingerprints, and an incidental manifest update. All were
  corrected; both review axes are now clear. Workflow verification confirmed
  authored/generated parity, raw-snapshot integrity, provider compatibility,
  acceptance coverage, and final diff hygiene.
- The effective runtime is 7,020 bytes, 129 lines, and 967 words versus 10,635
  bytes, 195 lines, and 1,530 words at this correction's fixed point. Detailed
  identifier, locking, retirement, lifecycle, and settlement mechanics now stay
  behind the state contract; these are instruction-size measurements, not token
  or model-quality claims.
- The focused live `wayfinder-contract-smoke` passed: it resumed map-only state,
  created only one justified E#/F# chain, emitted no Wayfinder work items, handed
  three substantial slices to `to-tickets`, and left ticket 01 as `map.md` next work.
- The frozen `wayfinder-local-state-smoke-v1` campaign remains unchanged historical evidence. It does not validate the current U/E/F/D contract.
- Pre-contract files under this effort's `tickets/` directory remain untouched project history and are not a current work frontier.

## Blockers and dependencies

None for this implementation.

## Next work

No implementation remains for this focused correction. Future Wayfinder runtime
changes should preserve the reasoning and authority boundaries established by
ADR-0023 and ADR-0025 while leaving detailed state mechanics in the state
contract.

## Notes

- [U1 — How should the pinned Wayfinder method be adapted to local state?](unknowns/U1-adaptation-boundary.md) is now resolved by [D2 — Own the runtime projection and stable effort boundary](decisions/D2-own-runtime-projection.md); D1 remains superseded history.
- Live source and current user authority outrank stale saved assumptions.
- The detailed semantics stay in the lazily loaded [Wayfinder state contract](../../../.agent-workflow/contracts/wayfinder-state.md); root routing instructions remain compact.
- Repository history contains no authoritative released I#/X#/O# syntax or semantics. The owned runtime therefore uses the established H1 destination plus U#/E#/F#/D# vocabulary and introduces no compatibility parser.
- This directory deliberately keeps its established `wayfinder-local-state-integration` slug even though the refined H1 is broader. Existing effort paths do not move when wording improves.

## Decisions so far

- [D1 — Use a fingerprinted local-mode provider overlay](decisions/D1-fingerprinted-local-mode-overlay.md) — Superseded historical decision to prepend a local-mode block.
- [D2 — Own the runtime projection and stable effort boundary](decisions/D2-own-runtime-projection.md) — Replace the recognized pinned body with a concise authored runtime projection and define deterministic effort selection without renaming existing paths.
- [ADR-0022 — Separate Wayfinder knowledge from implementation tickets](../../../architecture-decisions/0022-separate-wayfinder-knowledge-from-implementation-tickets.md) — Keep map-first U/E/F/D knowledge sparse and hand substantial decomposition to `to-tickets`.
- [ADR-0023 — Own the Wayfinder runtime projection](../../../architecture-decisions/0023-own-the-wayfinder-runtime-projection.md) — Establish the package-owned runtime body, immutable raw provenance, and selective upstream-porting boundary.
- [ADR-0025 — Preserve human authority across workflows](../../../architecture-decisions/0025-preserve-human-authority-across-workflows.md) — Keep authority-dependent assumptions out of accepted decisions, specifications, tickets, and implementation direction.

## Not yet specified

- Automatic Wayfinder remains experimental and should keep its conservative threshold.

## Out of scope

- Broadening automatic Wayfinder routing for bounded debugging or ordinary work.
- Building a generic projection framework, upgrading the pinned upstream snapshot, adding settlement/archive machinery, or introducing another durable state tree.
- Rewriting or retroactively regrading completed ITBench, Harbor, or frozen Wayfinder smoke results.
