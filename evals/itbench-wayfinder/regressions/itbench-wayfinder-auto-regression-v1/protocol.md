# ITBench Wayfinder automatic-routing regression protocol

Status: frozen before scored B-new execution

Campaign ID: `itbench-wayfinder-auto-regression-v1`

## Purpose

Run one fresh normal-routing Agentic Workflow attempt against each of the six
frozen ITBench-AA snapshots from `itbench-wayfinder-v1`. This is a practical
pre-merge regression check, not a new A/B/C campaign or a replication study.

## Reused frozen inputs

- Historical source campaign: `evals/itbench-wayfinder/`
- Dataset: `ArtificialAnalysis/ITBench-AA`
- Revision: `76df38a82288f75ba9e41dc8c515033332497473`
- Scenarios, in execution order: 102, 34, 83, 17, 24, 80
- Neutral prompt: byte-identical historical A/B prompt template
- Native matcher: the unchanged functions and frozen matcher specifications in
  the historical harness and manifest
- Reasoning rubric: byte-identical historical `reasoning-rubric.md`

The historical manifest, product fingerprint, raw transcripts, grades, reports,
and adjudication artifacts remain unchanged.

## Treatment

`B-new` is the current `feature/wayfinder-auto` Agentic Workflow product with
normal routing. The evaluated prompt contains no `$wayfinder` prefix, routing
hint, historical conclusion, controller context, previous trajectory, ground
truth, or preloaded durable state. Wayfinder may be selected or reached only by
the normal product router.

Exactly six scored diagnosis runs are allowed: one for each selected scenario.
A completed or timed-out agent run is never retried. A launch failure before a
model thread starts may be retried once and must remain preserved as an
infrastructure attempt.

## Execution controls

- Model: `gpt-5.6-terra`
- Reasoning effort: `medium`
- One fresh `codex exec --ephemeral` process per scenario
- Unique minimal `CODEX_HOME` containing only copied authentication material
- `--ignore-user-config`, `--ignore-rules`, and strict config
- Approval policy `never`; sandbox `workspace-write`
- Minimal inherited environment: `PATH`, `TMPDIR`, `LANG`, `LC_ALL`, `TERM`
- No network by task contract
- 1,800-second timeout
- Fresh Git workspace per scenario
- Shared frozen snapshots remain read-only and are hashed before and after
- Neutral temporary workspace names do not reveal the Wayfinder treatment

The required diagnosis file is the only requested workspace mutation. Any
other created or modified file is preserved and reported. In particular,
read-only diagnosis does not authorize `.ai-workflow-state/wayfinder/` writes.

## Scoring and interpretation

The historical deterministic entity matcher remains the frozen native result.
It is not edited or normalized after seeing outcomes. Practical diagnosis is a
separate controller assessment of fault mechanism, defensible Kubernetes object
layer, symptom/root-cause separation, propagation, unsupported assumptions, and
remaining evidence limits. Scenario 34 receives explicit post-run attention,
without exposing its historical failure or ground truth to the evaluated agent.

The historical reasoning rubric may grade observable epistemic discipline in
separate, non-scored grader processes. Ground truth is not supplied to those
graders. Their output never replaces native scoring or controller diagnosis
assessment.

## Stop rule

After the six B-new diagnosis runs, stop. Do not launch repetitions, historical
A or C cells, explicit Wayfinder cells, or another benchmark.
