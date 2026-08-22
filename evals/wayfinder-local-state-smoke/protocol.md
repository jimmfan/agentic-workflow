# Wayfinder local-state smoke v1 protocol

## Gate and purpose

Run this campaign only after the local-state semantic audit passes. It is a
mechanism smoke, not proof that Wayfinder is generally better and not a repeat
of the bounded ITBench campaign.

The smoke asks whether the fixed instructions can support one messy ARC runner
migration through four true process breaks:

1. map incomplete and conflicting evidence without implementing;
2. resume after the transient platform-facts source is removed and implement
   only decision-independent work;
3. reconcile later authoritative architecture and benchmark evidence that
   supersedes stale assumptions and resolves several unknowns; and
4. resume again and implement the newly unblocked bounded slice.

Every phase uses a new ephemeral Codex process and a unique auth-only
`CODEX_HOME`. Workspaces and durable state persist only within a condition.

## Conditions and fairness

- A is vanilla Codex. The prompts explicitly allow strong repository-native
  continuation notes; the grader rewards equivalent behavior regardless of
  filename or ontology.
- B installs Agent Workflow and receives the same neutral prompts as A. No
  prompt names Wayfinder. Phase 1 must automatically select local Wayfinder and
  create useful state or the smoke stops as unexercised.
- C installs byte-identical Agent Workflow artifacts and explicitly invokes
  `$wayfinder` in mapping/reconciliation phases.

The A and B prompts are byte-identical. C differs only where explicit invocation
and local Wayfinder terminology are necessary. All conditions receive the same
fixture, evaluator mutations, sandbox, model, effort, safety boundaries, and
offline validation access.

## Frozen inputs

Before any evaluated process runs, freeze SHA-256 digests for the campaign,
this protocol, the rubric, the wrapper and base harness, the complete scenario,
and the product payload/provider projection installed into B and C. A critical
digest mismatch invalidates execution; do not refreeze after outcomes.

The evaluator must pass deterministic self-checks and a context-isolation audit
before the trio is prepared.

## Stop rules

- Stop after phase 1 if B did not create local Wayfinder state without an
  explicit prompt or C did not create it under explicit invocation.
- Stop if A receives Agent Workflow artifacts, B/C installations differ, a
  phase is not a fresh process, or evaluator context reaches an agent.
- Stop rather than add repetitions if the state is absent, uses an alternate
  store, is unusable on resume, or does not evolve in phase 3.
- One A/B/C trajectory is the entire authorized smoke. Further repetitions
  require a new decision after reviewing this evidence.

## Reporting

Report each rubric dimension separately. Do not collapse the evidence into an
overall score. Label clean evidence, known limitations, possible confounders,
and observed failures. Preserve raw JSONL, stderr, per-phase evidence, final
workspace snapshots, frozen inputs, and the comparison report under the new
campaign results directory.
