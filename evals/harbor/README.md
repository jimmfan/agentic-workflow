# Harbor evaluation harness

This directory contains the frozen harness for a three-task paired evaluation
of Agentic Workflow with Harbor. The scored experiment is paused at the
condition-B provider gate. No scored B trial has started.

The gate report is
[`evals/reports/2026-08-15-harbor-provider-compatibility-gate.md`](../reports/2026-08-15-harbor-provider-compatibility-gate.md).
Task selection and external-source research are recorded in
[`selection.md`](selection.md) and [`harbor-research.md`](harbor-research.md).

## Frozen environment

- Agentic Workflow: `0.11.1` from Git commit
  `37e35b0be95b1b835f460af15187c91d915ca4dc`
- Harbor: `0.21.0`
- Codex CLI: `0.144.6`
- Model: `gpt-5.6-sol`
- Reasoning effort: `high`
- Environment: Harbor Docker environment, one trial at a time, one attempt,
  zero retries
- Dataset: `gabeorlanski/slopcodebench`, immutable dataset hash
  `sha256:73a17cda817d37ce3352d18c272c40a3f6b623061023bee365b4df74adcd11b5`

The selected tasks are `circuit_eval`, `database_migration`, and
`trajectory_api`. Their immutable task hashes are in [`selection.md`](selection.md).

## Setup

The commands used to create and inspect the local environment were:

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

Authentication used Codex's existing local `auth.json` via Harbor's supported
`CODEX_FORCE_AUTH_JSON=1` path. No credential is stored here.

## Commands exercised

Run from the repository root with the harness directory on `PYTHONPATH`:

```bash
CODEX_FORCE_AUTH_JSON=1 PYTHONPATH=evals/harbor \
  evals/harbor/.venv/bin/harbor jobs start \
  -c evals/harbor/configs/smoke-a.yaml

CODEX_FORCE_AUTH_JSON=1 PYTHONPATH=evals/harbor \
  evals/harbor/.venv/bin/harbor jobs start \
  -c evals/harbor/configs/smoke-b.yaml

CODEX_FORCE_AUTH_JSON=1 PYTHONPATH=evals/harbor \
  evals/harbor/.venv/bin/harbor jobs start \
  -c evals/harbor/configs/slopcodebench-a.yaml
```

Both infrastructure smokes passed. The B smoke proved that the task image lacks
`gh skill`: the supported lifecycle installed the healthy core but reported
`0 present, 14 missing` optional providers. The A scored command was stopped at
the new provider gate after `circuit_eval` checkpoint 1 completed; its raw
artifacts remain under the ignored `evals/harbor/jobs/` tree.

Do not run `slopcodebench-b.yaml` in the current environment. The B agent now
fails closed unless all 14 declared provider skills are present and the
Agentic Workflow core/provider trees contain no `*.py` files. Before resuming,
provide the documented `gh skill` capability inside the Harbor task environment
and confirm this gate with an install-only run. The host also needs `uv` for the
SlopCodeBench dataset aggregate metric.
