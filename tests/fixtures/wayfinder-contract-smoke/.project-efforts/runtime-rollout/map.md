# Runtime rollout

## Destination

The approved runtime policy has an evidence-backed baseline and a native,
dependency-ordered implementation frontier that fresh sessions can resume.

## Current state

- This effort is valid map-only state at the start of the smoke.
- The approved decomposition is in [`rollout-plan.md`](../../../rollout-plan.md).
- The current policy source has not yet been reconciled into durable evidence.

## Blockers and dependencies

- Publication of the approved implementation frontier is the only coordination
  dependency. The work itself remains outside Wayfinder.

## Next work

Inspect `release-policy.txt`, preserve only independently useful evidence and
facts, publish the approved rollout through `to-tickets`, then replace this
paragraph with one coherent native-ticket next action.

## Notes

- The local Markdown tracker is `docs/agents/runtime-rollout/issues/`.
- The ticket breakdown and blocking edges in `rollout-plan.md` are approved.
- Do not implement the rollout in this smoke.

## Decisions so far

None.

## Not yet specified

None.

## Out of scope

Implementation of the rollout.
