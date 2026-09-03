# Agent Workflow evaluations

Repository evaluation tooling answers narrow questions about the current Agent Workflow contract.
It is not a general coding-agent benchmark, and no live model evaluation is part of the deterministic release gate.

## Current tooling

The [routing interpretation smoke test](routing-smoke/README.md) checks whether Direct and evidence-triggered Wayfinder routing are interpreted consistently while revealing only requested policy.
It is opt-in, contacts the selected model service, and must write reports outside the repository.
Every adapter receives the same routing-only cases; the harness does not simulate host discovery, skill availability, or invocation behavior.

Token forensics analyzes an existing Codex trace without running a model:

```bash
python3 -m token_forensics evals/artifacts/<campaign>/<run>/raw/codex.jsonl \
  --json-out /tmp/token-forensics.json \
  --text-out /tmp/token-forensics.md
```

Its evidence limits are documented in [`token_forensics/README.md`](../token_forensics/README.md).

Run all deterministic evaluation-tooling tests from the repository root:

```bash
python3 -m unittest discover -s evals/tests -p 'test_*.py' -v
```

These tests are standard-library-only, network-free, and separate from the distributed package.

## Storage contract

Git stores only the material needed to understand and reproduce a current evaluation: harnesses, frozen inputs and prompts, scenario fixtures, protocol/rubric, compact results, adjudication, token summaries, and reports.

Raw execution exhaust belongs under [`evals/artifacts/`](artifacts/README.md) or another suite-specific ignored directory.
Full model traces, process logs, copied workspaces, temporary homes, grader transcripts, caches, and other reconstructable intermediates must not enter compact result directories.

A retained run must identify the benchmark and conditions, dataset and product revisions, model and reasoning settings, sandbox and approval policy, scoring method, outcome, route, elapsed time, token/tool totals, known grader limits, and rerun procedure.
Unknown observations stay unavailable rather than being inferred.
Do not combine unlike campaigns into a synthetic score.

## Open evaluation questions

No current campaign resolves these questions:

1. Does the canonical Wayfinder map and supporting state improve continuity, correctness, state evolution, or rework relative to a strong ordinary repository-native handoff on genuinely long-lived work?
2. Can the default router select Wayfinder at a useful threshold without adding net ceremony or false positives?
3. Does Agent Workflow provide repeatable net value after accounting for boundary safety, useful progress, correctness, verification, rework, artifacts, elapsed time, and model usage?
4. Can ordinary scoped reconciliation keep a multi-file Wayfinder effort coherent at acceptable reconstruction cost?

Prior experiments supply hypotheses and risk observations, not current-product answers.
Their exact bundles remain available from Git history.
Do not represent them as if they evaluated the current architecture.

## Protocol for future causal work

No live run is authorized by this document.
If a future campaign is separately approved, first test the narrow evidence-precedence failure mode: a fresh first phase receives a verified fact and an unresolved decision; the transient source is removed; a newer accepted decision resolves the question without contradicting the fact; and a completely fresh second phase must retain the fact, apply the decision, complete the work, and verify it.

Only after that focused experiment should a larger continuation comparison be considered.
A useful design has four matched arms:

1. capable baseline under a neutral prompt;
2. default Agent Workflow under the same neutral prompt;
3. capable baseline explicitly asked to maintain strong repository-native handoff notes; and
4. Agent Workflow with explicit Wayfinder using only current canonical state.

Freeze prompts, fixtures, mutations, grading criteria, analysis rules, model and reasoning configuration, permissions, and sample count before execution.
Start every evaluated phase in an independently created conversation and run trials sequentially.
Audit context isolation per run.

Report safety and useful progress separately: unsupported guesses, preservation of still-valid evidence, speculative work, rework after decisions change, continuity, state accuracy and evolution, final correctness, verification, unnecessary artifacts, elapsed time, tools, and model usage.
Stopping alone is not success.
Preserve protocol defects and keep conclusions conditional on the observed fixture and sample.
