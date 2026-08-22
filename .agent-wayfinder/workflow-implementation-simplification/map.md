# Workflow implementation simplification

- Status: completed

## Destination

Determine from current `main` whether `workflow-implementation` owns meaningful
unique behavior. If it is redundant, remove it completely while preserving
ready implementation routing, provider fallback, authority boundaries,
Wayfinder handoff, exactly-once Verification, concise route reporting, and
package/install integrity.

## Territory

- Routing ownership: root policy and `.agent-workflow/routing.md` select work and
  enforce decision and authority boundaries.
- Execution ownership: provider configuration resolves upstream `implement` or
  the authorized host-native fallback.
- Completion ownership: `workflow-verification` independently checks meaningful
  implementation once.
- Distribution ownership: payload, installed projection, manifests, tests, and
  fixtures must agree on the active skill set.
- Coordination ownership: Wayfinder may hand off coherent ready scopes and
  remains the only framework continuity layer.

## Current state

The wrapper was redundant and has been removed from the source payload,
installed projection, distribution/install manifests, routing descriptions,
active documentation, tests, and evaluation harness setup. Ready work now routes
directly to `implement`, or its authorized host-native fallback, then
Verification. [ADR-0028](../../architecture-decisions/0028-use-wayfinder-as-sole-durable-coordinator.md)
records the current execution boundary.

Deterministic evidence establishes the instruction, packaging, projection, and
fixture contracts: package/install verification passes 132 tests, the historical
evaluation harness passes 14 tests, lifecycle status is healthy, and all 14
provider skills are ready. These tests do not execute a model router. Existing
live evaluations did not isolate the wrapper, so they show no wrapper-specific
outcome benefit; no new live A/B was warranted.

## Blockers and dependencies

None.

## Next work

None for this completed effort.

## Notes

- User authority explicitly permits deletion in this task if the evidence
  supports it.
- Do not change the other `workflow-*` skills except removing stale return or
  handoff references required by deleting this wrapper.
- Out of scope: project renaming, `.agent-wayfinder/` redesign, and uv CLI work.
- The only wrapper rule not already explicit elsewhere was the project-profile
  command safety gate; it now lives in the always-loaded root policy.

## Not yet specified

None.

## Out of scope

Unrelated architectural changes or a broad benchmark campaign.
