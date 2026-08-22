# T3: Run corrected ARC Wayfinder v2 smoke

- Status: done
- Blocked by: none
- Related: D1, D2, D3, D4, U1, U2, U3

## Outcome

Create, freeze, and run one corrected four-phase smoke trajectory for each of
three conditions: vanilla Codex with neutral durable handoff, Agent Workflow
with the same neutral durable-handoff intent and no explicit Wayfinder request,
and Agent Workflow with explicit Wayfinder during mapping and reconciliation.
Use twelve fresh sequential ephemeral Codex processes, preserve complete raw
evidence and snapshots, and report A-vs-B, B-vs-C, and A-vs-C separately.

The completed `arc-wayfinder-e2e-v1` campaign remains historical evidence. It
showed a promising exact-fact continuity/actionability signal for explicit
Wayfinder, but also exposed deterministic grader defects. Its Phase 4 fixture
was not sufficiently unambiguous to establish whether Wayfinder truly
over-blocked, and its treatment did not isolate Wayfinder from broader Agentic
Workflow behavior.

T1 and T2 remain valid at their existing statuses. This human-authorized T3 is
the immediate evaluation; it does not claim that T1 or T2 ran or supersede their
designs. Larger repetitions remain deferred until the v2 smoke is reviewed.

## Acceptance

- The v2 fixture, prompts, mutations, primitive evaluator, isolation audit,
  exact Agent Workflow revision, and model/runtime controls are frozen before
  an evaluated agent runs.
- Isolation is demonstrated for all three conditions, including identical
  Agent Workflow installation in B/C and no sibling, controller, credential,
  parent-instruction, resume, or grader leakage.
- Semantic state observations retain exact path/line/snippet evidence and use
  explicit affirmative, explicit negative, unresolved, absent, or ambiguous
  classifications instead of keyword-window yes/no inference.
- Fact preservation, fact location, fact consumption, fact implementation, SSM
  progress, IAM progress, other reversible progress, every Phase 4 component,
  verification, rework, overhead, and B-arm treatment crossover are recorded
  independently without an opaque overall score.
- The Phase 3 mutation makes the bounded Phase 4 slice executable without
  resolving or taking ownership of the legacy resource and without authorizing
  external infrastructure mutation.
- One complete A, B, and C trajectory runs sequentially, with all twelve phases
  using fresh `codex exec --ephemeral` processes pinned to GPT-5.6 Terra,
  medium reasoning, workspace-write, approvals `never`, and matched environment
  and network policy.
- A final report answers the preregistered comparisons and repetition-readiness
  questions, records product issues separately, stops before repetitions, and
  makes no Agent Workflow product change.

## Result

Completed 2026-08-15. All twelve fresh sequential phases exited successfully,
and A, B, and C each preserved/consumed the exact AMI fact, respected mapping
boundaries, and completed the full bounded phase-4 slice. Condition C did not
over-block the authorized implementation.

The smoke is informative but not ready for repetitions. Neutral condition B
automatically selected Wayfinder and used its state in every phase, making the
B-versus-C incremental explicit-invocation contrast potentially confounded.
The frozen semantic classifier also retained material misclassifications that
require manual interpretation. Preserve the frozen machine evidence; repair
treatment separation and semantic grading only in a new campaign.

Canonical report:
[`evals/reports/2026-08-15-arc-wayfinder-e2e-v2.md`](../../../../evals/reports/2026-08-15-arc-wayfinder-e2e-v2.md).
Repetitions and automatic-routing changes remain deferred for human review.
