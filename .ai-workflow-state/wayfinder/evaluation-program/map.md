# Agentic Workflow evaluation program

## Destination

A decision-ready body of evidence about whether Agentic Workflow provides measurable value over a capable baseline agent on long-lived engineering work, with the effects of default routing, generic repository-native handoffs, and explicit Wayfinder state distinguished rather than conflated.

## Notes

- This is an evaluation-planning effort. Do not modify Agentic Workflow product behavior while working this map.
- Canonical evidence remains in [`evals/`](../../../evals/), especially its campaign records, result JSON, and reports. Historical or context-limited runs remain directional evidence and are not deleted or retroactively regraded.
- Current evidence is narrow and hypothesis-generating; no current hypothesis is an established product fact. The clean `arc-wayfinder-e2e-v1` smoke pair found an exact-fact continuity and apparent efficiency advantage for explicit Wayfinder, but no Phase 4 completion advantage and a possible over-blocking failure. Its frozen grader also has documented semantic false positives, so repeat only under a corrected evaluator.
- [T3 — Run corrected ARC Wayfinder v2 smoke](tickets/T3-corrected-arc-wayfinder-v2-smoke.md) is complete. All three arms completed the corrected bounded slice, so the v1 over-blocking result did not reproduce; however, neutral condition B automatically crossed into Wayfinder in every phase and the v2 semantic classifier retained material misclassifications. The immediate next action is human review of the canonical v2 report and a decision about a new treatment-separation/grader-repair campaign. Do not repeat v2 unchanged. [T1 — Run the preregistered evidence-precedence experiment](tickets/T1-evidence-precedence-experiment.md) remains ready only when separately authorized, and [T2 — Run the multi-phase durable-continuation comparison](tickets/T2-multi-phase-durable-continuation.md) remains blocked by T1; neither was executed or rewritten by T3.
- Open questions: [U1 — Does structured Wayfinder state outperform ordinary handoff notes?](unknowns/U1-wayfinder-vs-handoff-notes.md), [U2 — When should Agentic Workflow select durable Wayfinder state automatically?](unknowns/U2-automatic-wayfinder-routing.md), and [U3 — Does Agentic Workflow create net value on long-lived engineering work?](unknowns/U3-net-value-long-lived-work.md).
- The `arc-wayfinder-e2e-v1` report and machine evidence are canonical under [`evals/`](../../../evals/) and remain preserved historical evidence. T3 is evaluation-infrastructure and fixture work only; do not change routing, skills, provider behavior, Wayfinder semantics, lifecycle behavior, or installation behavior from the smoke.
- The completed v2 report is canonical at [`evals/reports/2026-08-15-arc-wayfinder-e2e-v2.md`](../../../evals/reports/2026-08-15-arc-wayfinder-e2e-v2.md), with raw evidence and product/tooling issues under [`evals/results/arc-wayfinder-e2e-v2/`](../../../evals/results/arc-wayfinder-e2e-v2/). Repetitions and automatic-routing changes remain deferred.

## Decisions so far

- [D1 — Preserve and qualify every evaluation campaign](decisions/D1-preserve-qualified-evidence.md) — Keep contaminated and preliminary campaigns as explicitly qualified historical evidence; never promote them to clean causal evidence.
- [D2 — Evaluate three distinct behavior layers](decisions/D2-distinguish-behavior-layers.md) — Measure default Agentic Workflow, generic durable handoffs, and explicit Wayfinder separately.
- [D3 — Measure safe and useful continuation](decisions/D3-measure-safe-useful-continuation.md) — Reward correctness and useful progress together, while measuring rework, continuity, evolving state, verification, and cost where observable.
- [D4 — Strengthen isolation and preregistration](decisions/D4-isolation-and-preregistration.md) — Use independent fresh conversations, sequential execution, frozen criteria, matched settings, and per-run context audits for the next campaigns.

## Not yet specified

- If the harder comparison finds a repeatable benefit, determine the minimum task characteristics and evidence threshold needed for a product decision. The exact threshold should wait for distributions from the harder campaign rather than being invented now.
- If structured Wayfinder helps, determine which parts of its structure cause the benefit and which are ceremony. This cannot be specified sharply until the matched durable-note comparison exists.
- If cost/usage becomes observable, determine the acceptable overhead for each class of safety or continuity improvement. No trade-off threshold is justified by current data.

## Out of scope

- Changing router thresholds, evidence precedence, Wayfinder behavior, or any other Agentic Workflow product behavior during this mapping pass.
- Treating the current small campaigns as a general benchmark of coding-agent intelligence or as statistically conclusive product evidence.
- Deleting, rewriting, or silently combining historical result JSON produced under different evaluators or fairness conditions.
- Executing either next experiment as part of this Wayfinder pass.
