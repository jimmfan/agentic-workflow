# Wording micro-tests

This opt-in harness checks whether a wording change alters what a model plans to do, before any larger live campaign.
It adapts the method in obra/superpowers' [writing-skills guidance](https://github.com/obra/superpowers/blob/main/skills/writing-skills/SKILL.md) to Agent Workflow's evidence rules.

Each sample is one fresh model conversation of at most three rounds.
The prompt holds the rendered consumer `AGENTS.md`, a catalog of exposed skill names and descriptions, and one user request.
The model may request a skill's full instructions by name before it returns a structured plan.
The harness reuses the [routing smoke](../routing-smoke/README.md) Codex and Claude adapters, cost guard, and outside-repository report rule.

## Rules the harness enforces

- Every case has exactly one control variant with the guidance removed, and may name one baseline variant holding the current wording.
- Every variant runs at least five repetitions, interleaved so that each repetition runs all variants in order.
- If every sample of the baseline, or of the control when no baseline is named, passes every predicate, the report says the run supports no wording change.
  A baseline sample that failed to run blocks that conclusion.
- A sample whose adapter call fails keeps its error message instead of a score; the summary counts errors per variant and lists each distinct message.
- The report records pass counts per predicate, the number of distinct outcome patterns as a spread measure, and the first-round prompt size so that ties can go to the shorter wording.
- Every sample's full answer is kept in the report, and each one should be read by hand before deciding; predicate counts alone can overstate both failure and success.

## What it cannot show

A sample is a single-turn plan in an isolated, read-only process with no repository access.
It does not show whether a real host discovers or loads a skill, what the agent actually executes, or how behavior holds across many turns or context compaction.
Those remain with the [behavior scenarios](../../tests/scenarios/) and separately authorized live campaigns.

## Cases

| Case | Question |
|---|---|
| `implement-named-handoff` | When the user names `implement`, does its description lead the agent to skip its body or the return to Verification? |
| `ordinary-implementation-selection` | Without a named skill, does description wording change whether meaningful implementation selects `workflow-implementation` and plans Verification? |

Both compare no descriptions (control), the checked-out descriptions (baseline), and candidates limited to triggering conditions and the nearest alternative.
Cases live in [`cases/`](cases/); add one JSON file per question.

## Inspect prompts without contacting a model

```bash
python3 -m evals.wording_micro payload --case implement-named-handoff
```

## Run with Codex

Live runs contact the model service and spend credits.
Run from the repository root with an authenticated `codex` CLI, and write reports outside the repository:

```bash
python3 -m evals.wording_micro run \
  --case implement-named-handoff \
  --adapter codex \
  --model gpt-5.6-sol \
  --reps 5 \
  --max-estimated-cost-usd 3 \
  --input-price-per-million 5 \
  --cached-input-price-per-million 0.5 \
  --output-price-per-million 30 \
  --output /tmp/wording-micro-implement.json
```

Verify current token prices before a run; the example prices are the routing smoke's from 2026-08-19.
The Codex adapter runs each call ephemeral and read-only with ignored user configuration and low reasoning effort unless `--effort` sets `medium` or `high`; the report records the effort.
`--adapter claude` uses the Claude CLI instead.
The cost limit may not exceed $5; the run stops before a sample that would start past it and keeps the completed samples.

## Deterministic tests

```bash
python3 -m unittest discover -s evals/tests -p 'test_wording_micro.py' -v
```

These use a fake adapter and make no network requests.
