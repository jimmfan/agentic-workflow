# ARC Wayfinder end-to-end v1

- Campaign ID: `arc-wayfinder-e2e-v1`
- Status: **first clean A/B smoke pair completed; interpretation qualified by frozen-grader limitations**
- Research question: does explicit structured Wayfinder state provide meaningful value beyond an equally capable vanilla Codex agent explicitly asked to maintain strong repository-native handoff notes?
- Arms: vanilla durable handoff (`baseline`) and local Agentic Workflow plus explicit Wayfinder (`workflow`)
- Trajectories: one smoke trajectory per arm, four completely fresh agent contexts per trajectory
- Model/configuration: GPT-5.6 Terra, medium reasoning, workspace-write sandbox, approvals disabled for unattended execution, sequential phases
- Production behavior: unchanged; this campaign modifies only `evals/` artifacts

## Scope and relation to the durable evaluation map

The older Wayfinder T2 record describes a later four-arm comparison and marks it
blocked behind T1. The human-authored brief for this campaign authorizes a
narrower two-arm smoke comparison of the two persistence conditions needed to
answer U1: generic durable handoff versus explicit Wayfinder. This campaign does
not claim that T1 ran, does not replace the four-arm T2 design, and cannot answer
the separate automatic-routing question.

Historical Direct and Resume campaigns remain unchanged and are not pooled with
this campaign.

## Frozen human-defined behavior

The machine-readable preregistration is
[`evals/campaigns/arc-wayfinder-e2e-v1.json`](../../campaigns/arc-wayfinder-e2e-v1.json).
It fixes the four prompts for both arms, matched model/configuration, sequential
execution order, evidence-quality vocabulary, independent dimensions, and the
prohibition on an opaque overall score.

The fixture and grader encode the brief's pre-live expectations:

- Phase 1 distinguishes current facts, stale `m6i`, four unresolved decisions,
  and safe actionable IAM/SSM work without implementing Terraform.
- Phase 2 deletes the sole evaluator-owned source of
  `/platform/arc/runner-ami`, then measures exact recovery, useful IAM/SSM
  progress, verification, and decision discipline before D1 exists.
- Phase 3 adds D1 and benchmark evidence, then measures resolution of the old
  compute questions, retention of still-valid facts, evidence interpretation,
  legacy-ownership uncertainty, and contradictory state.
- Phase 4 measures the expected dedicated managed-node-group implementation,
  `m7i`, two warm nodes, SSM AMI resolution, private networking, permissions
  boundary, ownership safety, and offline validation.

Speculative rework and continuation cost remain separate observations. Tokens,
time, tool calls, files read before the first observed write, and repeated reads
are recorded only when Codex JSONL exposes them; unavailable values remain
`null`.

## Context-isolation gate

Automatic execution is disabled by default. `--ephemeral` and the absence of a
resume command are necessary but not sufficient.

Before `--run-pair` or `--run-next` can launch an evaluated phase, the harness
requires a passing `context-isolation-audit.json` bound to both:

1. the exact frozen evaluator digest; and
2. stable hashes of global `AGENTS.md`/`CLAUDE.md` plus a fresh exact-marker scan
   of global skills for Agentic Workflow or Wayfinder.

The audit creates a disposable Git repository under `/private/tmp`, outside the
Agentic Workflow source hierarchy. It checks that a vanilla workspace has no
`AGENTS.md`, `.ai-workflow/`, `.ai-workflow-state/`, `.agents/`, or Wayfinder
skill; scans relevant `CODEX_HOME`, home, and root instruction/skill files for
Agentic Workflow or Wayfinder; verifies the Git root and ancestry; and runs one
non-evaluated read-only Codex probe. A canary `AGENTS.md` above the probe's Git
root detects parent-instruction traversal. Raw probe JSONL and stderr are
retained. Any failed check, evaluator change, global instruction change, or new
Agentic Workflow/Wayfinder skill marker keeps auto mode disabled. The full skill
path/hash inventory is retained for diagnosis, while unrelated plugin-cache
churn is not treated as controller-context contamination.

The probe is behavioral and static evidence, not a formal proof of every
undocumented context channel. Manual, independently created top-level tasks
remain the fallback.

The completed audit passed. Its machine record is
[`context-isolation-audit.json`](context-isolation-audit.json), with a concise
human review and raw evidence under [`isolation-audit/`](isolation-audit/).
The first pre-live probe failure and its original freeze remain under
[`preflight/`](preflight/) rather than being erased. Attempt 1 found inherited
controller `CODEX_*` environment variables before a model ran. Attempt 2 passed
the probe but was invalidated by unrelated global plugin-cache churn, exposing
an overbroad aggregate gate. The sanitizer and invariant were corrected, the
27-test eval suite passed, and the final pre-live evaluator was frozen before
the successful probe.

## Deterministic verification and freeze procedure

Run these commands in the **macOS host Terminal from the source repository
root** (`/Users/james/Desktop/projects/agentic-workflow-instructions`). The test
commands are read-only outside disposable temporary directories and do not run
evaluated agents.

First, run the campaign-specific deterministic tests:

```bash
python3 -B -m unittest evals.tests.test_arc_wayfinder -v
```

Expected success ends with `Ran 13 tests` and `OK`.

Then run all evaluation harness tests:

```bash
python3 -B -m unittest discover -s evals/tests -v
```

Finally, run the repository's full deterministic gate:

```bash
python3 skills/agentic-workflow/scripts/verify_package.py --tests
```

Expected success ends with
`OK: Agentic Workflow package verification passed.` If any command fails, the
first failing test is the next diagnostic; do not freeze or run the campaign.

After all checks pass, freeze the evaluation-critical harness, manifest,
fixture, and mutation files:

```bash
python3 -m evals.arc_wayfinder --freeze
```

This persistent command writes `frozen-evaluator.json`. It refuses to overwrite
an existing freeze. If a critical defect is found after live evidence exists,
preserve this campaign and create a new campaign ID rather than refreezing.

## Isolation audit procedure

After freezing, run this in the **macOS host Terminal from the same source
repository root**:

```bash
python3 -m evals.arc_wayfinder --audit-auto-isolation --timeout 300
```

This consumes one small non-evaluated Codex call and writes persistent audit
evidence under this campaign directory. It does not create an evaluated A/B
result. Success prints `Context-isolation audit passed`. Failure preserves the
audit and raw logs, returns exit status 2, and leaves automatic mode disabled.

Recheck the gate at any time without launching an agent:

```bash
python3 -m evals.arc_wayfinder --verify-freeze
```

## Completed smoke execution

The first pair was prepared after deterministic verification, freeze, and the
isolation audit passed. The automated controller then ran all eight phases
sequentially with the explicit app-bundled Codex executable. The evaluated
invocations were pinned to GPT-5.6 Terra with medium reasoning.

For a future new campaign, prepare isolated repositories from the **macOS host
Terminal at the source repository root** only after its own freeze and audit:

```bash
python3 -m evals.arc_wayfinder --prepare-pair
```

Preparation persistently creates two repositories under
`/private/tmp/agentic-workflow-arc-wayfinder-evals` (or the host-equivalent temp
path), installs Agentic Workflow and the reviewed Wayfinder v1.2.3 skill only in
the workflow arm, and records control state outside both repositories.

Automatic execution, if that campaign's audit remains valid, is:

```bash
python3 -m evals.arc_wayfinder --run-pair --timeout 1800 \
  --codex-executable /Applications/ChatGPT.app/Contents/Resources/codex
```

It starts one new ephemeral `codex exec` process per scheduled phase, never uses
`resume`, gives the process only the frozen prompt through standard input, runs
all eight phases sequentially, and preserves raw events, phase JSON, complete
phase snapshot archives, result JSON, commit SHAs, and isolation metadata. It
does not run paired agents concurrently.

The explicit executable path is the one used successfully on this macOS host.
The shorter default works only when `codex` is already on the invoking shell's
`PATH`; the first controller attempt on this host found no such entry and
launched zero evaluated agents.

For the manual fallback, use the workspace and exact prompt printed by
`--prepare-pair`, start a new top-level Codex task yourself, then record each
finished phase with the printed command. The required form is:

```bash
python3 -m evals.arc_wayfinder --advance RUN_ID --fresh-session-confirmed --task-id TASK_ID --evidence-quality clean
```

The task ID must be unique across phases. Use `known_limitation`,
`potentially_confounded`, or `confirmed_contaminated` instead of `clean` when
the audit warrants it; inconvenient evidence is preserved.

Inspect progress and completed comparisons with read-only commands:

```bash
python3 -m evals.arc_wayfinder --status
python3 -m evals.arc_wayfinder --compare
```

No overall score is produced.

## Side effects, cleanup, and reversal

Preparation and execution persist temporary repositories and control files.
Phase evidence and results persist under
`evals/results/arc-wayfinder-e2e-v1/runs/`; the isolation audit persists under
this campaign directory. Agent shell commands receive no inherited environment,
and the prompt prohibits external infrastructure mutation. The grader may run
offline unit tests and `terraform fmt -check`; it never runs `terraform init`,
`plan`, or `apply`.

After a trajectory is completed and its result is safely retained, remove only
its temporary workspace with this persistent, guarded command from the
**macOS host Terminal at the source repository root**:

```bash
python3 -m evals.arc_wayfinder --cleanup RUN_ID
```

The command refuses incomplete runs and paths outside the campaign temp root.
It does not delete result JSON or phase evidence. A removed temporary workspace
cannot be resumed. Source changes can be reversed through version control; do
not delete or rewrite live result evidence to change an outcome.

## Results and report

The completed run IDs are:

- baseline: `arc-baseline-1-68edd44151`
- workflow: `arc-workflow-1-e93a5ffa12`

All eight phases completed with clean observable context-isolation evidence.
Wayfinder recovered the exact SSM fact in Phase 2 while baseline did not; neither
arm completed the Phase 4 production-readiness slice. The frozen grader also
produced demonstrable Phase 1 keyword-window false positives, so the report
separates machine results from snapshot-based interpretation rather than
rewriting evidence.

See the [final report](../../reports/2026-08-15-arc-wayfinder-e2e-v1.md) and the
separate [product-issue record](product-issues.md). Preserve this campaign; make
grader fixes under a new campaign/evaluator version before repeating.
