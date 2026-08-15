# Initial Direct and Resume spike

- Campaign ID: `2026-08-15-initial-spike`
- Date: 2026-08-15
- Purpose: first narrow baseline/workflow comparison for Direct non-interference and Resume continuity
- Scenarios: Direct and Resume
- Trial count: one baseline and one workflow result per scenario (four result files)
- Framework: local Agentic Workflow 0.11.1; Git SHA was not captured in the result JSON
- Evaluator: earlier evaluator, before the later preregistered Direct huge-attempt criterion; Git SHA was not captured
- Evidence status: **preliminary / earlier evaluator**; useful historical and directional evidence, not retroactively regraded
- Associated report: [Initial trials report](../../reports/2026-08-15-direct-resume-initial-trials.md)

## Known limitations

- There is only one trial per variant and scenario.
- The Direct evaluator did not yet include the later `retry_delay(1_000_000) == 30.0` criterion.
- Model, token, and other execution metadata were unavailable.
- Context isolation was not established as a clean causal boundary for this campaign.

## Results

All four files retain their original JSON contents and evaluator meaning:

- `direct-baseline-1-b27e6dbd54.json` — preliminary / earlier evaluator
- `direct-workflow-1-583922fcb9.json` — preliminary / earlier evaluator
- `resume-baseline-1-3e01672ee1.json` — preliminary / earlier evaluator
- `resume-workflow-1-a7da21356d.json` — preliminary / earlier evaluator
