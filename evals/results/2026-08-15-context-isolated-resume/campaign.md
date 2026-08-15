# Context-isolated Resume rerun

- Campaign ID: `2026-08-15-context-isolated-resume`
- Date: 2026-08-15
- Purpose: rerun only the Resume decision-boundary and continuity experiment without delegated-source context
- Scenarios: Resume only
- Trial count: three baseline and three workflow results, each with a new Phase 1 conversation and a separate new Phase 2 conversation
- Framework Git revision at preparation: `34ee372dcd5d4f099625494a9ce71295e320bb4d`
- Evaluator: Resume prompts, fixture, grading criteria, thresholds, and Phase 2 mutation frozen from the three-paired-trials campaign; pre-organization `evals/run.py` SHA-256 was `aa0b326d679ad5c956530d0816d936bb2a4abe95b4c72ad7814053d7a311e4d6`
- Model/configuration: operator-confirmed GPT-5.6 Terra with medium reasoning for all evaluated conversations
- Evidence status: **completed primary Resume evidence**; no confirmed context contamination, with two disclosed known limitations
- Associated report: [Context-isolated Resume rerun](../../reports/2026-08-15-context-isolated-resume-rerun.md)

## Isolation requirement

Each evaluated conversation was manually created independently from its isolated repository rather than spawned by the controller. It received only its repository, the exact frozen prompt, and the normal equalized Codex configuration. The observable audit found no delegated parent, cross-conversation read, cross-repository access, result/report access, or evaluation-purpose disclosure in any evaluated conversation.

Both phases ran concurrently across the six unique repositories. This preserves filesystem separation but is a known limitation for timing and shared host/network contention; the campaign makes no efficiency claim.

The exact frozen Phase 1 prompt has SHA-256 `07a99dfd7efa2f1c0a1add945da1f4ae502a3cdb703013aa486901d5aa494f3e`. The exact frozen Phase 2 prompt has SHA-256 `e65bcf91ceb90d98efb49a3c20788a07c971c6b91cb80e44bc903ccc2ce0b64a`.

## Completed runs and evidence status

Evidence-quality status is independent of whether the implementation passed its grader.

- `resume-baseline-1-19df7998ef.json` — **known limitation, no observed contamination**: the Phase 2 prompt was briefly sent to and interrupted in the old Phase 1 conversation before a genuinely new evaluated Phase 2 conversation; no file change was recorded from the old conversation.
- `resume-baseline-2-1deddc60e0.json` — **known limitation, no observed contamination**: the same brief interrupted-start pattern occurred, with no recorded file change before the new evaluated Phase 2 conversation.
- `resume-baseline-3-a9a60c99be.json` — **clean at the observable context boundary**.
- `resume-workflow-1-cc411342e0.json` — **clean at the observable context boundary**.
- `resume-workflow-2-924811020f.json` — **clean at the observable context boundary**.
- `resume-workflow-3-14f9208696.json` — **clean at the observable context boundary**.

No run is marked `potentially confounded` or `confirmed contaminated` by evaluation-context access. See the report for the aggregate results, implementation anomalies, historical comparison, confidence assessment, and recommended next evaluation.
