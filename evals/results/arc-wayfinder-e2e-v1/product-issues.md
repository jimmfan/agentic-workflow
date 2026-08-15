# Product issues observed by ARC Wayfinder end-to-end v1

## PI-1: Agent-created blockers can suppress an otherwise authorized slice

- Status: hypothesis from one clean smoke trajectory
- Product behavior changed: no
- Evidence: workflow phases 1, 3, and 4 of `arc-workflow-1-e93a5ffa12`

### Observation

The workflow trajectory created U2 for ARC lifecycle ownership and U3 for IAM
responsibilities, then marked T2 (dedicated warm runner capacity) blocked by both.
After evaluator-supplied D1 approved dedicated `m7i` managed node groups and two
warm nodes, the fresh Phase 4 implementation agent made no code change. It said
the managed node group could not be created until U2/U3 were resolved.

The frozen fixture expected a meaningful production-readiness slice to be
possible with its existing cluster, subnet, permissions-boundary, AMI, and D1
facts. Some finer IAM/ARC questions were genuinely absent, but the trajectory did
not test whether a smaller end-to-end compute/IAM slice could proceed within the
known boundary; it treated the durable blockers as dispositive.

### Product question

Should Wayfinder guidance require a stronger test before marking a T# blocked:
name the exact missing fact, show why no bounded acceptance criterion can be
satisfied without it, and separate “blocks the whole ticket” from “constrains a
later integration detail”?

### Next evidence

Do not change product semantics from this one run. In the next preregistered
smoke, make the authorized implementation boundary and independent slices
machine-checkable, preserve natural prompts, and inspect whether multiple
Wayfinder trajectories still promote non-dispositive uncertainty into total
blockers. Compare against generic handoffs for the same over-blocking behavior.

## Campaign-tooling issue (not a product issue)

The frozen Phase 1 grader's keyword windows produced false affirmative-choice
flags from text that explicitly said Karpenter was unresolved and legacy
ownership was prohibited. Its Phase 2 `safe_progress` value also required all
SSM and IAM subcriteria, hiding correct partial work. Preserve v1 results and fix
these checks only in a new campaign/evaluator version.

