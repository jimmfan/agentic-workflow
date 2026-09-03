# Token forensics

`token_forensics` is a local, standard-library-only analyzer for explaining token and context pressure in saved agent traces.
It is intentionally separate from ITBench and Agent Workflow runtime behavior:

```text
raw trace -> format parser -> normalized trace -> generic analysis -> JSON/text report
```

Codex is the first parser.
The saved `codex exec --json` format reports usage on `turn.completed`; Codex defines those counters as usage **during that Codex turn**, so the analyzer sums completed-turn observations.
Persisted Codex rollouts instead emit repeated `token_count.info.total_token_usage` cumulative snapshots; the parser deduplicates identical snapshots and takes the final monotonic value rather than summing them.
This distinction prevents the most important double-counting failure.

Run it against an existing trace without invoking Codex:

```bash
python3 -m token_forensics path/to/codex.jsonl
python3 -m token_forensics path/to/codex.jsonl \
  --json-out token-forensics.json \
  --text-out token-forensics.md \
  --label "Scenario 17"
```

## Evidence boundaries

- Exact when present: token counters, Codex turns, tool calls, command status and exit code, trace-embedded output bytes, and explicit compaction events.
- Derived: uncached input, cached-input ratio, safe cumulative trajectories, and repeated commands.
- Heuristic: file reads inferred from command text, broad/unbounded searches, framework/skill loading, and whether large tool output plausibly contributed to later context pressure.

Bytes are never treated as tokens.
The Codex exec stream currently aggregates internal model activity within a high-level Codex turn, so it cannot expose an exact internal model-call count or assign later input tokens to a particular tool result.
`command_execution` also supplies combined `aggregated_output` in the historical traces, so stdout and stderr cannot be split there.

The parser tolerates missing fields and incomplete older logs.
Unavailable measurements remain `null` in JSON and `unknown / unavailable` in text.

The current JSON shape is `token-forensics/v2`.
Only current `<effort>/map.md`, `facts.md` and `decisions.md` ledgers, and canonical U#/E# artifact paths are classified as current Wayfinder state.
All other `.agent-wayfinder/` paths remain visible in generic repository observations but are not classified as current state.

Primary schema references:

- [Codex non-interactive JSONL documentation](https://learn.chatgpt.com/docs/non-interactive-mode.md#make-output-machine-readable)
- [Codex exec event types and per-turn usage semantics](https://github.com/openai/codex/blob/main/codex-rs/exec/src/exec_events.rs)
