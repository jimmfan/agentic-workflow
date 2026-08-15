# Product issues observed by ARC Wayfinder end-to-end v2

## PI-1: Neutral durable-effort routing selected Wayfinder automatically

- Status: observed in one isolated smoke trajectory
- Product behavior changed: no
- Evidence: all four phases of condition B, especially phase 1 of
  `arc-v2-b-1-0cdb658fca`

### Observation

Condition B installed Agentic Workflow but never mentioned `$wayfinder` or
asked for framework-specific state. In phase 1, the agent read the Wayfinder
skill and created a canonical map, three tickets, and four unknown records.
Fresh phases 2 through 4 read and modified that Wayfinder state. The frozen
crossover audit therefore marks every B phase as crossed over.

This is legitimate observation of normal product behavior, not contamination:
the prompt explicitly described a durable multi-session effort. It does mean
that B and C are not cleanly separated as “Agentic Workflow without Wayfinder”
versus “Agentic Workflow with Wayfinder.” The incremental causal effect of the
explicit `$wayfinder` invocation is not identified by this trajectory.

### Product question

Should a neutral request to map a durable multi-session effort select Wayfinder
automatically, and if so, how should the product expose that selection so users
and evaluations can distinguish automatic routing from explicit invocation?

### Next evidence

Do not change routing from this smoke. A future preregistered design experiment
should separately measure automatic selection and an explicitly direct
Agentic-Workflow route, using a supported product boundary rather than secretly
disabling Wayfinder after observing crossover.

## PI-2 follow-up: v1 whole-ticket over-blocking did not reproduce

- Status: not reproduced under the corrected v2 fixture; hypothesis remains
  unconfirmed rather than disproved
- Product behavior changed: no
- Evidence: phase 3 and phase 4 snapshots for all three v2 conditions

### Observation

The corrected readiness artifact stated exactly which IAM, launch-template,
and node-group work was authorized and explicitly made legacy-resource
ownership non-blocking for that slice. Condition C retained broader controller,
pod-identity, networking, and legacy-ownership unknowns, linked the authorized
slice to an unblocked ticket, and completed every frozen phase-4 component.
Condition B did likewise after automatic Wayfinder crossover.

This narrows the v1 result: Wayfinder can preserve genuine unknowns without
blocking a bounded ticket when the repository supplies an explicit readiness
boundary. The smoke does not determine whether the v1 stall was primarily a
fixture ambiguity, an agent-specific state-modeling choice, or a general
product tendency.

### Product question

Would an explicit readiness test in Wayfinder ticket guidance make this outcome
more reliable across less carefully authored repositories: identify the exact
missing fact and the acceptance criterion it prevents before adding a blocker?

### Next evidence

Keep the v1 issue open as a hypothesis. Test it only after the v2 evaluation
classifier and treatment separation are repaired, then repeat across multiple
trajectories with both dispositive and deliberately non-dispositive unknowns.

## Campaign-tooling issues (not product issues)

The frozen v2 semantic classifier is safer than v1 because it retains exact
path/line/snippet evidence and allows ambiguity, but manual inspection still
found material misclassifications. Examples include condition C's unresolved
phase-1 Karpenter choice classified as `explicit_negative`, condition B's
unresolved phase-1 shared/dedicated choice classified as `explicit_negative`,
and condition C's resolved phase-3 instance choice classified as `ambiguous`.
The raw evidence is adequate to correct the report manually, but the classifier
is not ready for unattended repetitions.

The final corrected isolation audit completed 33 seconds after the final
evaluator freeze, although both completed before workspace preparation or any
evaluated phase and the audit recorded the exact matching frozen SHA-256. This
reverses the requested audit-then-freeze order and is retained as a known
procedural limitation; it did not enable post-result criteria changes.

File-read and repeated-read metrics are conservative event-derived indicators,
not complete filesystem telemetry. In addition, 11 of 12 agents attempted a
recursive `rm` cleanup of Python bytecode that the host safety layer rejected;
they recovered with safer targeted cleanup and all final validation passed.
