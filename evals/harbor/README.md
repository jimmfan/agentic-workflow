# Harbor evaluation harness

This evaluation was stopped by user direction on 2026-08-16 after one complete
paired SlopCodeBench task. Do not start additional scored pairs from this
harness without new human direction.

The completed `circuit_eval` A/B results, database infrastructure failures, and
the exact stop boundary are reported in
[`2026-08-16-harbor-slopcodebench-stopped-after-circuit.md`](../reports/2026-08-16-harbor-slopcodebench-stopped-after-circuit.md).
The earlier provider gate is preserved in
[`2026-08-15-harbor-provider-compatibility-gate.md`](../reports/2026-08-15-harbor-provider-compatibility-gate.md).

## Frozen environment

- Agentic Workflow: `0.11.1` from Git commit
  `37e35b0be95b1b835f460af15187c91d915ca4dc`
- Provider set: all 14 declared `mattpocock/skills@v1.2.3` providers in B
- Harbor: `0.21.0`
- Codex CLI: `0.144.6`
- Model: `gpt-5.6-sol`
- Reasoning effort: `high`
- Environment: Harbor Docker environment, one trial at a time, one attempt,
  zero retries
- Dataset: `gabeorlanski/slopcodebench`, immutable dataset hash
  `sha256:73a17cda817d37ce3352d18c272c40a3f6b623061023bee365b4df74adcd11b5`

The frozen task selection remains `circuit_eval`, `database_migration`, and
`trajectory_api`; see [`selection.md`](selection.md). Only `circuit_eval`
completed as a valid pair. No `trajectory_api` scored run started.

## Completed scored evidence

The only completed paired evidence is:

- A: `evals/harbor/jobs/2026-08-15-slopcodebench-circuit-eval-a-validated/`
- B: `evals/harbor/jobs/2026-08-15-slopcodebench-circuit-eval-b-validated/`

Both jobs completed one trial, all eight checkpoints, zero Harbor exceptions,
zero retries, and the unchanged SlopCodeBench verifier. Their result files must
not be modified or normalized.

Condition B was the complete normal lifecycle installation, with the frozen
revision, all 14 providers, zero missing providers, and zero workflow/provider
`*.py` files in the application scoring roots. Its current provider declaration
marks Wayfinder `user-only` under Codex. The benchmark did not explicitly invoke
`$wayfinder`, so Wayfinder was not implicitly or automatically routable and did
not activate. B did activate the local implementation adapter and independent
verification, while the upstream `implement` provider also remained user-only
and fell back truthfully to host-native implementation.

## Preserved non-comparable artifacts

- `evals/harbor/jobs/2026-08-15-slopcodebench-a/` is the earlier interrupted
  vanilla `circuit_eval` checkpoint. It is partial/superseded evidence only.
- `evals/harbor/jobs/2026-08-15-slopcodebench-database-migration-a-validated/`
  is a failed environment build. Codex never started and no checkpoint ran.
- `evals/harbor/jobs/2026-08-16-database-envfix-smoke-a/` is a failed
  install-only infrastructure smoke. Codex task inference never started.
- `evals/harbor/jobs/2026-08-16-database-envfix-smoke-a-2/` is the interrupted
  second install-only smoke. It was cancelled at the user's stop request; its
  result remains unfinished and unscored.

None of these artifacts belongs in the completed circuit comparison. No scored
database B run started, and no database result may be inferred from them.

## Evaluation infrastructure retained for audit

The harness uses `run_harbor.py` to place evaluation-local `uv==0.11.32` on the
host `PATH`, make the existing Codex auth available, and pass GitHub
authentication only to B lifecycle setup. The B adapter uploads the frozen
checked-in package, runs its public lifecycle, removes transient setup inputs,
and fails closed unless all provider/revision/contamination checks pass.

The immutable `database_migration` v5 Dockerfile failed on 2026-08-16 because
its mutable `npm@latest` install resolved to npm 12.0.2, which rejected the
task's pinned Node 22.12.0. The following evaluation-only repair work is
preserved but was not used for a completed scored result:

- [`database-migration.Dockerfile`](database-migration.Dockerfile) derives from
  the unchanged task Dockerfile, pins npm 11.16.0, and adds an NVM path bridge
  required by Harbor's Codex installer.
- [`harbor_environments.py`](harbor_environments.py) selects that local image
  through Harbor's custom-environment interface and checks the original task
  Dockerfile hash and image provenance labels.
- The local image was
  `agentic-workflow-harbor/database-migration-env:v5-npm11.16.0-arm64`, image
  ID `sha256:a9b52d91d7220dff045e2252bf95cf4e108ce7d5087721ca872d27f17c6f3db2`.

The registry task package, task instructions, verifier, scoring logic, Agentic
Workflow product, provider versions, and provider contents were not modified.

## Original setup commands

```bash
python3 -m venv evals/harbor/.venv
evals/harbor/.venv/bin/python -m pip install -r evals/harbor/requirements.txt
evals/harbor/.venv/bin/harbor --version
docker --version
codex --version
evals/harbor/.venv/bin/harbor dataset download \
  'gabeorlanski/slopcodebench@3' \
  --output-dir evals/harbor/cache/slopcodebench \
  --export
```

Authentication used Codex's existing local `auth.json` and the host GitHub CLI
credential store. No credential is stored in this directory or in job
artifacts.
