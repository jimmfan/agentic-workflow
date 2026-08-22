# D4: Strengthen isolation and preregistration

- Related: T1, T2

## Decision

For subsequent causal campaigns, freeze prompts, fixtures, mutations, grading criteria, and analysis rules before live runs; create every evaluated phase as an independently initiated fresh conversation; run trials sequentially; match model, reasoning, sandbox, approvals, and permissions across arms; and record a per-run context-isolation audit.

## Why

The three-paired campaign exposed a delegated-source channel and contains one confirmed contamination case. The context-isolated rerun removed that channel, but concurrent execution prevents useful timing comparison and two baseline runs include brief interrupted starts in old Phase 1 conversations. Manual execution also leaves model/cost metadata partly operator-controlled or unavailable.

## Consequences

- Historical limited campaigns remain evidence under D1 but are not used as clean causal proof.
- Accidental old-conversation reuse is a protocol deviation that must be recorded; the next campaign should prevent it rather than relying only on an operator flag.
- Timing and cost comparisons are reported only when captured consistently and without shared-host concurrency confounds.
