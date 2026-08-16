# ITBench Scenario 17 token-spike replication protocol

Status: frozen before the single scored execution

Campaign ID: `itbench-s17-token-replication-v1`

## Purpose

Run exactly one fresh normal-routing Agentic Workflow attempt against the frozen
ITBench-AA Scenario 17 snapshot. This is a targeted replication of the prior
`B-new` token-usage outlier, using passive token-forensics instrumentation.

## Frozen inputs and treatment

- Source campaign: `itbench-wayfinder-auto-regression-v1`
- Dataset revision: `76df38a82288f75ba9e41dc8c515033332497473`
- Scenario: 17 only
- Prompt: byte-identical neutral B-new diagnosis template
- Product: current `feature/wayfinder-auto` revision, installed into a fresh workspace
- Routing: normal product routing; no explicit Wayfinder invocation or hint
- Scoring: unchanged frozen deterministic native matcher plus controller practical assessment

The evaluated workspace contains the installed product and no historical
diagnosis, transcript, report, ground truth, prior Wayfinder state, or
controller notes.

## Execution controls

- Model: `gpt-5.6-terra`
- Reasoning effort: `medium`
- One fresh `codex exec --ephemeral` process
- Unique minimal `CODEX_HOME` containing only copied authentication material
- `--ignore-user-config`, `--ignore-rules`, and strict config
- Approval policy `never`; sandbox `workspace-write`
- Minimal inherited environment: `PATH`, `TMPDIR`, `LANG`, `LC_ALL`, `TERM`
- No network by task contract
- 1,800-second timeout
- Shared frozen snapshot remains read-only and is hashed before and after

No model-based isolation probe or reasoning grader is launched, because this
replication authorizes exactly one new evaluated-agent process. Isolation,
integrity, native scoring, practical assessment, and token forensics are
controller-side deterministic checks.

## Storage and stop rule

Raw JSONL, stderr, workspace copies, and temporary homes remain under the
ignored `evals/artifacts/` area or the system temporary directory. Compact
manifest, preflight, execution, native grade, token-forensics, comparison, and
report artifacts are retained here.

After the one completed or timed-out Scenario 17 attempt, do not retry it and do
not run any other benchmark cell. A launch failure before `thread.started` may
be retried once under the inherited infrastructure policy.
