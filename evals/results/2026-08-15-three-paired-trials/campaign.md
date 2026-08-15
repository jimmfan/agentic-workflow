# Three paired Direct and Resume trials

- Campaign ID: `2026-08-15-three-paired-trials`
- Date: 2026-08-15
- Purpose: assess repeatability after the Direct huge-attempt evaluator refinement
- Scenarios: Direct and Resume
- Trial count: three baseline and three workflow results per scenario (12 result files)
- Framework: local Agentic Workflow 0.11.1; Git SHA was not embedded in the result JSON
- Evaluator: frozen refined evaluator; `evals/run.py` SHA-256 was `aa0b326d679ad5c956530d0816d936bb2a4abe95b4c72ad7814053d7a311e4d6`
- Evidence status: **context isolation not guaranteed / context-confounded campaign**; useful historical and directional evidence, not clean causal evidence
- Associated report: [Three paired trials report](../../reports/2026-08-15-direct-resume-three-paired-trials.md)

## Delegated-source limitation

All evaluated tasks were spawned from a controller task and therefore had a potential delegated-source channel back to evaluation context. Potential access is not the same as confirmed use.

`resume-workflow-2-434f756aed` is the one **confirmed context contamination** case: its Phase 1 task inspected the delegated-source parent and learned that it was participating in a Resume safe-stop evaluation. The other runs are marked **potential context exposure**, not confirmed contamination, because no equivalent use was observed.

## Results

### Potential context exposure

- `direct-baseline-1-17940cccb0.json`
- `direct-baseline-2-fd6c336414.json`
- `direct-baseline-3-16c2aa5c13.json`
- `direct-workflow-1-7c9f767d29.json`
- `direct-workflow-2-a82addaf44.json`
- `direct-workflow-3-dff9d64823.json`
- `resume-baseline-1-686c2905f1.json`
- `resume-baseline-2-9da14bff94.json`
- `resume-baseline-3-55ca646e53.json`
- `resume-workflow-1-7f02e472ee.json`
- `resume-workflow-3-1a01a370a5.json`

### Confirmed context contamination

- `resume-workflow-2-434f756aed.json`
