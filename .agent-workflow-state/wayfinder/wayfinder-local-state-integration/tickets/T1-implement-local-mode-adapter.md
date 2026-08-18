# T1: Implement and deterministically verify the local-mode adapter

- Status: done
- Blocked by: none
- Related: D1, T2

## Outcome

Fresh and existing pinned Wayfinder provider projections receive the authoritative local-mode instructions plus activation metadata, while already-adapted content is idempotent and unknown or modified content is preserved without partial writes.

## Acceptance

- Projected, payload, and lifecycle-visible instructions agree on local canonical storage and U/D/T semantics.
- Fresh install, update, status, and remove safely distinguish recognized upstream, adapted, and incompatible provider content.
- Focused deterministic tests cover idempotence, fail-closed behavior, project-state preservation, routing boundaries, progressive resume, state evolution, and prohibited alternate stores.

## Result

Implemented the fingerprinted local-mode provider adapter, schema/lifecycle
support, payload and installed contracts, decision documentation, and
deterministic behavior scenarios. The release verifier passes 61 tests. Provider
status reports one ready adapter with no pending or incompatible adapters, and
the recognized prior loading rule upgrades transactionally without changing the
pinned upstream method body.
