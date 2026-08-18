# T5: Run controlled ITBench Wayfinder evaluation

- Status: complete
- Blocked by: none
- Related: D1, D2, D3, D4, U1, U2, U3

## Outcome

Design and run a frozen-product A/B/C evaluation on ITBench or ITBench-AA SRE/Kubernetes scenarios 102, 34, 83, 17, 24, and 80:

1. vanilla Codex without Agentic Workflow exposure;
2. the frozen current Agentic Workflow under normal routing, without explicitly requesting Wayfinder or Domain Modeling; and
3. the same frozen workflow with explicit Wayfinder invocation but no independent Domain Modeling request.

Carry the authorized work through Phase 0 reconnaissance, isolated harness preparation, preflight validation, context-isolated execution, native grading, a separately frozen uncertainty/causal-reasoning rubric, capability-trajectory observation, and a plain-English final report. The experiment evaluates the current product as it exists and must not modify routing, Wayfinder, Domain Modeling, prompts inside the product, provider behavior, benchmark inputs, or native grading.

## Acceptance

- Record immutable or content-addressed identities for the complete frozen product state, benchmark/runtime/dataset, six task inputs, prompts, conditions, model/settings, tool permissions, ordering, retry/timeout policy, native grader, reasoning rubric, and output paths before the first evaluated agent runs.
- Inspect exact agent-visible task descriptions for root-cause leakage and replace a selected scenario only if it is invalid under the human's stated same-criteria rule; never replace it for difficulty or poor performance.
- Prefer one complete randomized or rotated A/B/C pass over incomplete scenario coverage. Estimate time/token cost from the initial complete pass before authorizing repetitions; preserve all three conditions.
- Keep every evaluated run context-isolated and prevent controller, sibling, rubric, ground-truth, reference-trajectory, and product-source leakage.
- Preserve official native correctness separately from frozen reasoning-quality judgments. Record root-cause precision/recall/false positives, uncertainty discipline, unsafe remediation, visibility boundaries, elapsed time/tokens where observable, and actual Wayfinder, Domain Modeling, Debugging, Research, and other material capability invocations.
- Produce isolated manifest, frozen configuration, scenario metadata, transcripts/trajectories, native and reasoning grades, per-scenario comparisons, aggregate A/B/C analysis, causal reference models, limitations, and final report under `evals/`.
- Document snapshot/runtime limits, infrastructure-only fixes, blocked or invalid runs, and any inability to run the native benchmark without silently weakening the design.
- Reconcile this ticket and the low-resolution map with the observed result. Do not modify the frozen product or make product recommendations until all valid authorized runs are complete.

## Result

Completed the full 54-run design with 54 normal executions, 54 valid native
grades, and 54 schema-valid reasoning grades. The frozen product fingerprint
remained unchanged.

Strict native success was A 3/18, B 4/18, and C 3/18. The single B advantage is
not a credible correctness gain: it matched the expected scenario-34 Pod while
missing the ground-truth authentication mechanism. Exact entity matching also
rejected many substantively correct Schedule/generated-chaos or ResourceQuota
diagnoses. Preserve the frozen score, but require the blinded adjudication
packet before using absolute correctness for a product decision.

The reasoning rubric found no consistent B-over-A or C-over-B improvement.
Relative to A, B used 58% more elapsed time and 42% more input tokens; C used
43% more time and 51% more input tokens. B selected Workflow Debugging in all
18 runs and Wayfinder in none. C used the explicit Wayfinder treatment but made
no durable state; its net contribution was `mixed` in 15/18 grades and
`not_observable` in 3/18. Domain Modeling was never invoked.

Canonical report:
`evals/itbench-wayfinder/reports/evaluation-report.md`.
