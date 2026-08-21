# Agentic Workflow evaluation program

## Destination

A decision-ready body of evidence about whether Agentic Workflow provides measurable value over a capable baseline agent on long-lived engineering work, with the effects of default routing, generic repository-native handoffs, and explicit Wayfinder state distinguished rather than conflated.

## Notes

- This is an evaluation-planning effort. Do not modify Agentic Workflow product behavior while working this map.
- The manual EKS focused-Wayfinder comparison is prepared and frozen. A and B
  preserve the same dirty working-directory snapshot, Agentic Workflow
  `wayfinder-replace` revision `1ac833d08640ff5eb5246355273c4105fb40e5bf`,
  package/provider projection, empty initial Wayfinder state, prompt, and
  `Terra 5.6` Medium model setting. The corrected shared prompt explicitly
  requires Wayfinder in both conditions: A uses the built-in general Agent with
  canonical Wayfinder, while B selects the focused workspace Wayfinder agent.
  The focused host projection is the sole intended treatment difference.
  The [protocol](../../../evals/manual-vscode/eks-focused-wayfinder-v1/protocol.md)
  also excludes local/Copilot memory and user/organization customization where
  the host exposes controls. The current Codex host cannot execute and capture
  the real VS Code custom-agent condition, so the paired live runs and evidence
  return remain the ready boundary. Supporting source research is
  [recorded here](../../../docs/focused-wayfinder-eks-experiment-research.md).
  Neutral prompts that let A's router decide whether to select Wayfinder remain
  eligible only for a separate later router-vs-focused product experiment and
  cannot support this primary causal claim.
- The human has authorized [T5 — Run controlled ITBench Wayfinder evaluation](tickets/T5-controlled-itbench-wayfinder-evaluation.md). This ticket carries reconnaissance, isolated evaluation-infrastructure work, execution, grading, and reporting inside the map while the product remains frozen.
- [T5 — Run controlled ITBench Wayfinder evaluation](tickets/T5-controlled-itbench-wayfinder-evaluation.md) is complete. Its full 54-run public-data-derivative campaign found no reliable correctness or reasoning advantage for normal Agentic Workflow or explicit Wayfinder on bounded offline SRE diagnosis, while both workflow treatments increased observed cost. B selected Debugging rather than Wayfinder in all 18 runs; forced Wayfinder created no durable state; Domain Modeling never ran. Exact native entity matching has material controller/child and condition-validity defects, so preserve the primary score and use the blinded adjudication packet before any product decision. The canonical report is [`evals/itbench-wayfinder/reports/evaluation-report.md`](../../../evals/itbench-wayfinder/reports/evaluation-report.md).
- Canonical evidence remains in [`evals/`](../../../evals/), especially its campaign records, result JSON, and reports. Historical or context-limited runs remain directional evidence and are not deleted or retroactively regraded.
- ARC v1 is complete. It found a promising one-trajectory continuity signal: explicit Wayfinder operationalized the deleted-source SSM fact while vanilla preserved but did not consume it. Phase 4 readiness was ambiguous and the frozen semantic grader produced false positives, so v1 remains qualified hypothesis-generating evidence.
- [T3 — Run corrected ARC Wayfinder v2 smoke](tickets/T3-corrected-arc-wayfinder-v2-smoke.md) is complete. V2 corrected readiness and found no final-outcome advantage for explicit Wayfinder over a strong generic handoff in that trajectory: all arms preserved and consumed the fact, evolved with D1, completed the bounded implementation, verified it, and avoided speculative rework. Vanilla used the least observed time, tokens, tool activity, and reconstruction reads.
- V2 neutral condition B automatically selected Wayfinder in every phase. It therefore measured normal Agentic Workflow behavior but did not provide a clean non-Wayfinder framework control. Automatic routing remains an open question under [U2](unknowns/U2-automatic-wayfinder-routing.md) and must not be changed from this evidence.
- Larger repetitions of the same ARC v2 scenario are deferred. [T1 — Run the preregistered evidence-precedence experiment](tickets/T1-evidence-precedence-experiment.md) remains valid and ready only when separately authorized. [T2 — Run the multi-phase durable-continuation comparison](tickets/T2-multi-phase-durable-continuation.md) remains deferred and blocked by T1.
- [T4 — Run branching-state complexity smoke](tickets/T4-branching-state-complexity-smoke.md) is complete. The isolated pair exercised the intended branching and partial supersession. Vanilla matched explicit Wayfinder on every valid comparison with materially less observed overhead. The intended W4 comparison is confounded: the frozen fixture omitted required alarm metric semantics, A safely refused to invent them, and B's ready ticket led to unsupported invented values that the incomplete frozen grader rewarded. Preserve the result; do not regrade or repeat it unchanged.
- Dogfooding evidence: distributed durable state can itself become partially stale when only some linked map/U/D/T artifacts are reconciled after new evidence. After v2, T3 and U2 were current while the map/frontier still described creating or selecting v2 as future work. [U4 — Distributed-state reconciliation consistency](unknowns/U4-distributed-state-reconciliation-consistency.md) records the unresolved net-cost question; this reconciliation repairs the observed program state without assuming the answer.
- [ADR-0016 — Reconcile relevant Wayfinder state at completion](../../../docs/decisions/0016-reconcile-relevant-wayfinder-state-at-completion.md) assigns the acting agent scoped reconciliation ownership during authorized mutating work. It was adopted in response to the U4 incident without claiming that structured state has proven net value or reliability; U4 remains open for that empirical question.
- Acceptance coverage now checks successful affected-state reconciliation, preservation and exclusion of an unrelated effort, read-only stale-state reporting, and refusal to guess through a reconciliation conflict. The deterministic 65-test release gate passes; the two new live-agent safety scenarios were not run, so this is contract coverage rather than new reliability evidence for U4.
- Open questions: [U1 — Does structured Wayfinder state outperform ordinary handoff notes?](unknowns/U1-wayfinder-vs-handoff-notes.md), [U2 — When should Agentic Workflow select durable Wayfinder state automatically?](unknowns/U2-automatic-wayfinder-routing.md), [U3 — Does Agentic Workflow create net value on long-lived engineering work?](unknowns/U3-net-value-long-lived-work.md), and [U4 — Does distributed Wayfinder state remain coherent at acceptable maintenance cost?](unknowns/U4-distributed-state-reconciliation-consistency.md).
- The `arc-wayfinder-e2e-v1`, `arc-wayfinder-e2e-v2`, `arc-wayfinder-state-complexity-v1`, and `itbench-wayfinder-v1` reports and machine evidence are canonical under [`evals/`](../../../evals/) and remain preserved historical evidence. T4 and T5 were evaluation-infrastructure and fixture work only and did not authorize product changes; ADR-0016 is a separately authorized subsequent product decision.
- The completed v2 report is canonical at [`evals/reports/2026-08-15-arc-wayfinder-e2e-v2.md`](../../../evals/reports/2026-08-15-arc-wayfinder-e2e-v2.md), with raw evidence and product/tooling issues under [`evals/results/arc-wayfinder-e2e-v2/`](../../../evals/results/arc-wayfinder-e2e-v2/). The completed T4 report is canonical at [`evals/reports/2026-08-15-arc-wayfinder-state-complexity-v1.md`](../../../evals/reports/2026-08-15-arc-wayfinder-state-complexity-v1.md), with raw evidence, manual review, and issues under [`evals/results/arc-wayfinder-state-complexity-v1/`](../../../evals/results/arc-wayfinder-state-complexity-v1/). The completed T5 report and machine evidence are under [`evals/itbench-wayfinder/`](../../../evals/itbench-wayfinder/). Those campaigns authorize no further product change or evaluation run.

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
- Changing Agentic Workflow or Wayfinder product behavior in response to the smoke; product-design concerns remain separately recorded hypotheses.

## Next work

Run A and B manually in fresh VS Code Copilot chats with the exact shared
`Use Wayfinder to orient yourself...` prompt under the frozen protocol, then
preserve chat/debug exports and post-run repositories. Evaluate each condition
independently with the frozen comparison template before comparing them; make
no Agentic Workflow product change during the pair.
