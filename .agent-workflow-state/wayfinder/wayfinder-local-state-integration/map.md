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
- The projection, provider declaration and adapter, routing and state contracts, documentation, generated skill, and deterministic effort-selection fixtures use the owned-runtime boundary.
- An effort is selected by exact requested path when supplied, otherwise by progressively reading the candidate directory names and maps. Ambiguity is reported without mutation; creation requires selected Wayfinder, authorized and materially useful durable state, no existing match, and a materially distinct destination.
- The full deterministic package suite passes all 97 tests, the evaluation-harness suite passes all 69 tests, all 14 declared provider skills match the bundled projection, and the release verifier passes after refreshing the required version metadata.
- Independent Standards and Spec review found contract gaps in the first implementation pass; those findings were corrected and both axes are now clear. Independent workflow verification confirmed projection parity, raw-snapshot integrity, mirrors, provider compatibility, and acceptance behavior.
- The effective skill is 8,001 bytes, 159 lines, and 1,122 words versus 15,963 bytes, 192 lines, and 2,529 words at the starting revision. The complete upstream tracker body and its operational tracker mechanics are absent; effort-selection and stable-path guidance is present. These are instruction-size measurements, not token or model-quality claims.
- The focused live `wayfinder-contract-smoke` passed: it resumed map-only state,
  created only one justified E#/F# chain, emitted no Wayfinder work items, handed
  three substantial slices to `to-tickets`, and left ticket 01 as `map.md` next work.
- The frozen `wayfinder-local-state-smoke-v1` campaign remains unchanged historical evidence. It does not validate the current U/E/F/D contract.
- Pre-contract files under this effort's `tickets/` directory remain untouched project history and are not a current work frontier.

## Blockers and dependencies

None for this implementation.

## Next work

No implementation remains for this change. The separate follow-up may design
resolved-knowledge and completed-effort settlement after this owned runtime and
stable naming boundary is accepted. Do not reuse or edit frozen campaigns for
that work.

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

## Not yet specified

- Automatic Wayfinder remains experimental and should keep its conservative threshold.

## Out of scope

- Broadening automatic Wayfinder routing for bounded debugging or ordinary work.
- Building a generic projection framework, upgrading the pinned upstream snapshot, adding settlement/archive machinery, or introducing another durable state tree.
- Rewriting or retroactively regrading completed ITBench, Harbor, or frozen Wayfinder smoke results.
