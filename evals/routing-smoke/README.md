# Routing interpretation smoke test

This opt-in evaluation asks two deliberately small questions of multiple models:

1. Does a bounded read remain Direct without loading the detailed router?
2. Does a request that begins bounded select Wayfinder after reconnaissance
   reveals consequential coordination signals?

The runner sends the installed root `AGENTS.md` and only the named synthetic case
evidence or detailed routing policy that the model explicitly requests from a
names-and-size catalog. It does not send project source, project documentation,
durable state, Git history, credentials, or arbitrary repository files.

## What it measures

Each round returns a schema-constrained public decision containing the initial
route, current route, Wayfinder assessment and selection, requested resources,
and a concise explanation. The same routing-only contract is sent through each
adapter. The harness does not simulate host discovery, skill availability, or
invocation behavior. The report records every revealed resource in order plus
the exact prompt bytes and any usage metadata exposed by the adapter.

This isolates cross-model interpretation of the routing contract. It is not
operating-system file-access tracing and does not prove that every interactive
coding-agent host will discover or invoke the installed files identically.
End-to-end host discovery and invocation remain outside this smoke test's
evidence and require a separately authorized live exercise.

## Inspect the payload without contacting a model

```bash
python3 -m evals.routing_smoke payload
```

## Run Codex

The built-in adapter uses an ephemeral, read-only Codex execution with ignored
user configuration, low reasoning effort, and schema-constrained output. Write
reports outside the repository:

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

The Claude adapter requires an installed, authenticated `claude` CLI. It uses
print mode, safe mode, plan permissions, no session persistence, no browser
integration, one turn per invocation, JSON output, and a JSON Schema. Each
invocation also has a native `$0.20` maximum, so the hard four-round/two-case
limit stays below `$2` even if the outer token estimate lags. The harness never
reads or stores Claude credentials:

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

If the executable is unavailable, the run stops as unavailable; it does not
manufacture a Claude result.

## Run a smaller model

Use the Codex adapter with a smaller model available to the same authenticated
Codex account:

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

```bash
python3 -m evals.routing_smoke compare \
  /tmp/routing-smoke-codex.json \
  /tmp/routing-smoke-claude.json \
  /tmp/routing-smoke-small.json
```

Comparison reports whether the models completed the same case matrix, passed the
case checks, and agreed on the initial and final routes.

## Cost and safety limits

The hard limits are four rounds and 120,000 prompt bytes per case; command-line
values may lower but not raise them. Every live run also requires current input,
cached-input, and output prices plus an estimated cost limit no greater than
$2. The runner sums adapter-reported usage after every round and stops before
starting another round once the limit is reached. Pricing examples above were
current on 2026-08-19; verify vendor pricing before a later run.

The dollar guard is an estimate, not a billing-system reservation. A single
model request is already in flight before its usage is known, and vendor
caching, hidden host context, reasoning tokens, subscription credits, and price
changes may affect final accounting. The schema-constrained output and hard
round/prompt limits bound that residual risk.

Live execution contacts the selected model service and consumes API quota or
subscription credits. Deterministic tests use fake adapters and make no network
requests.
