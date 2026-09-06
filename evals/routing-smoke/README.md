# Routing interpretation smoke test

This opt-in evaluation asks two deliberately small questions of multiple models:

1. Does a bounded read remain Direct without loading the detailed router?
2. Does a request that begins bounded select Wayfinder after reconnaissance reveals consequential coordination signals?

The runner sends root `AGENTS.md` rendered from the canonical consumer template (tested against a disposable installation) and only the named synthetic case evidence or detailed routing policy that the model explicitly requests from a names-and-size catalog.
It does not send project source, project documentation, durable state, Git history, credentials, or arbitrary repository files.

## What it measures

Each round returns a schema-constrained public decision containing the initial route, current route, Wayfinder assessment and selection, requested resources, and a concise explanation.
The same routing-only contract is sent through each adapter.
The harness does not simulate host discovery, skill availability, or invocation behavior.
The report records every revealed resource in order plus the exact prompt bytes and any usage metadata exposed by the adapter.

This isolates cross-model interpretation of the routing contract.
It is not operating-system file-access tracing and does not prove that every interactive coding-agent host will discover or invoke the installed files identically.
End-to-end host discovery and invocation remain outside this smoke test's evidence and require a separately authorized live exercise.

## Inspect the payload without contacting a model

```bash
python3 -m evals.routing_smoke payload
```

## Run Codex

The built-in adapter uses an ephemeral, read-only Codex execution with ignored user configuration, low reasoning effort, and schema-constrained output.
Write reports outside the repository:

```bash
python3 -m evals.routing_smoke run \
  --adapter codex \
  --model gpt-5.6-sol \
  --max-estimated-cost-usd 2 \
  --input-price-per-million 5 \
  --cached-input-price-per-million 0.5 \
  --output-price-per-million 30 \
  --output /tmp/routing-smoke-codex.json
```

Use `--executable /absolute/path/to/codex` when the CLI is not on `PATH`.

## Run Claude

The Claude adapter requires an installed, authenticated `claude` CLI.
It uses print mode, safe mode, plan permissions, no session persistence, no browser integration, one turn per invocation, JSON output, and a JSON Schema.
Each invocation also has a native `$0.20` maximum, so the hard four-round/two-case limit stays below `$2` even if the outer token estimate lags.
The harness never reads or stores Claude credentials:

```bash
python3 -m evals.routing_smoke run \
  --adapter claude \
  --model claude-opus-5 \
  --max-estimated-cost-usd 2 \
  --input-price-per-million 5 \
  --cached-input-price-per-million 0.5 \
  --output-price-per-million 25 \
  --output /tmp/routing-smoke-claude.json
```

If the executable is unavailable, the run stops as unavailable; it does not manufacture a Claude result.

## Run a smaller model

Use the Codex adapter with a smaller model available to the same authenticated Codex account:

```bash
python3 -m evals.routing_smoke run \
  --adapter codex \
  --model gpt-5.4-mini \
  --max-estimated-cost-usd 2 \
  --input-price-per-million 0.75 \
  --cached-input-price-per-million 0.075 \
  --output-price-per-million 4.5 \
  --output /tmp/routing-smoke-small.json
```

## Compare reports

Compare the two completed Codex reports above with the model difference declared explicitly:

```bash
python3 -m evals.routing_smoke compare \
  /tmp/routing-smoke-codex.json \
  /tmp/routing-smoke-small.json \
  --vary model
```

Both reports must record known `effort: "low"` and the same observed Codex adapter version, along with matching harness, policy, cases, and execution constraints.
Different token prices do not block this comparison; an undeclared model difference does.
Comparison reports whether the models completed the same case matrix, passed the case checks, and agreed on the initial and final routes.
The Claude adapter currently leaves effort unavailable, so including its report prevents a fully comparable result even with model and adapter differences declared.
Declaring `--vary effort` does not supply that missing observation.

## Cost and safety limits

The hard limits are four rounds and 120,000 prompt bytes per case; command-line values may lower but not raise them.
Every live run also requires current input, cached-input, and output prices plus an estimated cost limit no greater than $2.
The runner sums adapter-reported usage after every round and stops before starting another round once the limit is reached.
Pricing examples above were current on 2026-08-19; verify vendor pricing before a later run.

The dollar guard is an estimate, not a billing-system reservation.
A single model request is already in flight before its usage is known, and vendor caching, hidden host context, reasoning tokens, subscription credits, and price changes may affect final accounting.
The schema-constrained output and hard round/prompt limits bound that residual risk.

Live execution contacts the selected model service and consumes API quota or subscription credits.
Deterministic tests use fake adapters and make no network requests.

## Provenance, interruption, and comparison

Schema version 2 records product and harness revisions, the actual harness fingerprint, policy and case/fixture fingerprints, model and effort settings, adapter identity/version when observable, execution `limits`, and separate `token_prices`.
The policy and cases are frozen before execution, so working-tree edits are represented by their actual input fingerprints.
Routing-resource fingerprints retain case identity so different contents at the same resource name cannot mask an input change.
Source-only maintainer policy never enters the prompt or policy fingerprint.
Missing observations remain unavailable; no version, usage, or read is inferred from a label.

Each case records execution status separately from PASS, FAIL, or INCONCLUSIVE.
Reports retain completed cases, observed early failures, incomplete-case counts, received responses, usage, and available current-round prompts when a later adapter exception, timeout, or budget limit stops the run.
Premature Wayfinder selection remains an observed failure even if the final transition is unobserved.
The Codex adapter captures any available structured response file and usage before timeout cleanup; valid received decisions can be graded while execution remains interrupted.
A received response is recorded before enforcing its resulting cost limit.
Reports are written after each case using the existing outside-repository storage rule; there is no checkpoint store or database.
Infrastructure failure does not become a product failure merely because a final decision was not received.

Comparison requires matching harness, policy, cases, model, effort, adapter, and limits.
Execution `limits` include rounds, prompt size, timeout, and the dollar budget; those conditions must still match.
The input, cached-input, and output token prices remain recorded under `token_prices` for cost calculation and review, but price equality is not required for routing-result comparison.
Cost calculation and budget enforcement still use each run's supplied prices; an interrupted or incomplete run cannot establish successful complete-run agreement.
Use repeated `--vary model`, `--vary effort`, `--vary adapter`, or `--vary policy_sha256` only to name deliberate experimental variables.
Other mismatches and missing legacy provenance make the reports incomparable and leave interpretation agreement unavailable.
Unavailable adapter versions or effort observations cannot be promoted to known settings.
Model agreement under an explicit variable is an observation about those runs, not evidence of host discovery or skill execution.

Fake-adapter tests exercise policy isolation, working-tree input fingerprints, mismatched reports, a successful first case followed by timeout, retained early failures, and a response crossing the budget.
They validate harness behavior without running a model.
