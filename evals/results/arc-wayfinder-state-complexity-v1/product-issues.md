# Product and campaign-tooling issues

No issue recorded here changed Agentic Workflow or Wayfinder behavior.

## PI-1: Ready-ticket salience may suppress unresolved implementation inputs

- Status: hypothesis from one confounded trajectory
- Product behavior changed: no
- Evidence: B Phase 3, Phase 5, and Phase 6 snapshots

B's Phase 3 map correctly stated that W4 lacked namespace, metric name,
dimensions, threshold, period, statistic, and evaluation window. After the
evaluator supplied only the SNS destination, B's Phase 5 reconciliation marked
the destination unknown resolved and created a ready W4 ticket without carrying
those other missing inputs forward. The Phase 6 agent trusted the ticket and
invented alarm semantics.

This could indicate that a salient `ready` ticket encourages a downstream agent
to treat the ticket as a complete implementation contract even when broader
repository evidence is incomplete. It could instead be ordinary single-run
agent error, or primarily an artifact of the fixture's false statement that the
destination was the sole missing input. The campaign cannot separate those
explanations.

Future evidence should use a fully specified workstream and independently check
whether a ready ticket preserves all required inputs. Do not change Wayfinder
from this observation.

## TI-1: Frozen W4 fixture falsely declared the destination sufficient

- Status: confirmed post-freeze campaign defect
- Affected comparison: Phase 5 W4 readiness and Phase 6 complete selective
  continuation
- Historical evidence rewritten: no

The initial fixture said one destination/configuration value was missing, and
the Phase 5 mutation supplied an SNS ARN. It never supplied the alarm namespace,
metric name, dimensions, threshold, comparison operator, period, statistic, or
evaluation window. The intended assertion that W4 was now implementable was
therefore false.

This defect makes A's refusal to invent those values correct and makes B's
implementation unsupported. It prevents the frozen Phase 6 completion Boolean
from serving as evidence that Wayfinder outperformed the neutral handoff.

## TI-2: Frozen W4 deterministic acceptance was materially incomplete

- Status: confirmed post-freeze grader defect
- Historical result changed or regraded: no

The grader checked for `aws_cloudwatch_metric_alarm` and the supplied SNS ARN,
plus broad safety properties. It did not validate the absent project-specific
metric semantics. B therefore received machine credit for invented values.

The two-layer evidence architecture itself worked as intended: objective checks
remained objective, arbitrary prose stayed in inspectable manual packets, and
manual review exposed the missing acceptance boundary. A corrected campaign
must provide every required W4 input before execution and freeze deterministic
assertions for those exact values. It must use a new campaign ID rather than
refreezing or regrading this one.

## TI-3: Initial isolation audit was network-blocked

- Status: preserved procedural event; no evaluated execution affected

The first frozen audit attempt could not resolve the model endpoint under the
controller sandbox. Its failure, raw output, and audit JSON remain under
`preflight/attempt-1/`. No evaluated agent ran. The same frozen audit was rerun
with authorized network access, passed, and only then were run workspaces
prepared. This is not observed context contamination.

