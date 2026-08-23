# Agent Workflow evaluation spike

These evaluations answer narrow questions about Agent Workflow, not general coding-agent intelligence:

1. Does installing the workflow avoid interfering with a simple, bounded retry-helper task?
2. Does repository-owned workflow state improve continuity when useful evidence disappears between completely fresh agent sessions?
3. Does explicit structured Wayfinder state outperform an equally capable vanilla Codex agent explicitly asked to leave strong durable repository-native handoff notes over a four-phase project?

The separate [routing interpretation smoke test](routing-smoke/README.md) checks
whether Direct and evidence-triggered escalation are interpreted consistently
across model adapters while progressively revealing only requested policy.

Failure is useful evidence. The harness does not alter framework behavior, prompt the workflow variant to use Wayfinder, prohibit baseline notes, or collapse the observations into a synthetic score.

## Storage contract

Git stores the material needed to understand and reproduce an evaluation:
harnesses, frozen manifests and prompts, scenario fixtures, protocol/rubric,
compact per-run results, adjudication, token-forensics summaries, and reports.

Raw execution exhaust is generated under [`evals/artifacts/`](artifacts/README.md)
or a suite's documented ignored external job directory. This includes full
Codex JSONL, process logs, copied workspaces, temporary Codex homes, grader
transcripts, caches, and other regenerable intermediates. Harnesses must not
write those files into durable result directories. Compact reports must render
without reopening raw artifacts.

For a retained run, the frozen manifest plus compact result/report should answer
the benchmark, scenario/condition, dataset and product revisions, model and
reasoning settings, sandbox/approval policy, scoring method, outcome, route,
elapsed time, token/tool totals, known grader limitations, and rerun procedure.
Benchmark-specific outcome fields remain benchmark-specific; no universal
score is imposed.

Analyze an ignored Codex trace without running Codex:

```bash
python3 -m token_forensics evals/artifacts/<campaign>/<run>/raw/codex.jsonl \
  --json-out evals/<suite>/reports/<run>-token-forensics.json \
  --text-out evals/<suite>/reports/<run>-token-forensics.md
```

The analyzer and its evidence limitations are documented in
[`token_forensics/README.md`](../token_forensics/README.md).

Evaluator criteria may be refined between experiments when a concrete gap is found. Historical result JSON files remain evidence for the evaluator version used when they were recorded and are not retroactively regraded or rewritten.

## Evaluation campaign index

Result JSON is grouped by campaign under `evals/results/CAMPAIGN/`. Each campaign directory contains a `campaign.md` that records its purpose, evaluator context, evidence quality, limitations, report, and member files.

| Campaign | Purpose | Evidence status | Primary limitation | Report |
| --- | --- | --- | --- | --- |
| [`2026-08-15-initial-spike`](results/2026-08-15-initial-spike/campaign.md) | First Direct and Resume comparison | Preliminary / earlier evaluator | One run per cell; predates the Direct huge-attempt criterion | [Initial trials](reports/2026-08-15-direct-resume-initial-trials.md) |
| [`2026-08-15-three-paired-trials`](results/2026-08-15-three-paired-trials/campaign.md) | Repeatability after evaluator refinement | Historical directional evidence; context isolation not guaranteed | Every task had potential delegated-source exposure; one run has confirmed context contamination | [Three paired trials](reports/2026-08-15-direct-resume-three-paired-trials.md) |
| [`2026-08-15-context-isolated-resume`](results/2026-08-15-context-isolated-resume/campaign.md) | Context-isolated Resume decision-boundary rerun | Completed primary Resume evidence; two known limitations, no confirmed contamination | Concurrent execution; two brief interrupted old-conversation starts with no file changes | [Context-isolated Resume rerun](reports/2026-08-15-context-isolated-resume-rerun.md) |

The three-paired-trials campaign is the strongest completed evidence for the narrow Direct non-interference question, but it is not clean causal evidence for Resume. The completed context-isolated Resume campaign is the primary Resume evidence: four runs are clean at the observable context boundary and two have disclosed non-mutating protocol limitations. Its results show a small, inconsistent workflow safe-stop advantage and no workflow continuity advantage.

## Why the scenarios exist

`direct` is the counterweight to the continuity case. It makes unnecessary ceremony, extra files, mistakes, and obvious regressions visible when durable state has no value.

`resume` presents an exact approved AMI parameter during Phase 1 alongside two unresolved architecture decisions. After Phase 1 ends, the harness deletes that transient source and separately commits the approved architecture decision. Phase 2 runs in a fresh task. A variant can therefore recover the AMI path only if its Phase 1 agent independently preserved it in the repository. Forgetting safely is a continuity failure; guessing is additionally an unsafe-behavior failure.

## Fair setup boundary

Every run copies the same scenario fixture into a newly allocated directory under the host temporary directory, initializes a normal Git repository, commits the starting state, and records a content snapshot outside the agent-visible repository.

The `baseline` variant receives only the fixture and `.git`; it receives no Agent Workflow policy, skill, installation, or state artifact.

The `workflow` variant is prepared from the same fixture, then the harness invokes this checkout's real `adopt.py install` core-adoption path with the `unreleased-local-package` revision before making the setup commit. This installs the local source under evaluation. It intentionally does not invoke the higher-level provider installer, because optional provider downloads would introduce network and availability differences merely to prepare a fixture. Framework-created setup files are in the setup snapshot and are excluded from post-setup agent-change counts.

That exclusion remains part of these historical neutral Direct/Resume conditions;
do not silently turn them into provider-enabled trials. The current bundled
declared provider projection removes the former network confounder for new
provider-focused campaigns: a future harness may invoke the normal lifecycle
fully offline, but it must declare that condition explicitly and record the
Agent Workflow revision, upstream commit, effective provider/Wayfinder hash,
and `network_provider_install_attempted=false`.

Control state, prompts, and result metadata live outside the temporary repository. The Phase 2 mutation is copied only from `evals/scenarios/resume/phase-2-mutation`, and that source does not contain the AMI parameter.

## Historical Direct/Resume execution boundary

The original Direct/Resume runner used manual execution because a callable `codex` executable was unavailable when it was built. Fixture preparation, local workflow adoption, Git setup, prompts, snapshots, phase mutation, static grading, fixture test execution, JSON results, and comparison output were automated. Agent exit status, elapsed time, tokens, action counts, conversational claims, and validation commands run by the agent remained `null` when they could not be observed reliably.

For each prepared workspace, start a new Codex task rooted at the printed absolute path and paste only the printed prompt. Do not paste harness commentary. For `resume`, the harness will refuse to grade Phase 2 unless `--fresh-session-confirmed` is supplied; this is an explicit operator guard, not technical proof that the old task was closed. Start Phase 2 in a completely new task and inject no summary from Phase 1.

For every paired baseline/workflow comparison, manually select the same coding agent, model, model settings, sandbox, approvals, and execution permissions. The harness cannot inspect or enforce those desktop settings, so record any deviation alongside the result. Do not change this source checkout's framework or grader between preparing and grading a paired run. Baseline agents may create ordinary repository notes; those files are preserved and graded by the same rules as workflow state.

## Run one direct trial

The purpose of these commands is to create a pristine fixture, let one fresh agent work on it, and then grade only post-setup changes. Run them in the **macOS host Terminal from this source repository root** (`/Users/james/Desktop/projects/agent-workflow-instructions`). Preparation and grading persist temporary workspaces and result JSON; they do not modify the framework.

Choose one campaign ID for the complete experiment. Preparation requires it so future output cannot fall back into an ambiguous flat directory.

Prepare baseline:

```bash
python3 -m evals.run --scenario direct --variant baseline --runs 1 --campaign CAMPAIGN
```

Prepare workflow:

```bash
python3 -m evals.run --scenario direct --variant workflow --runs 1 --campaign CAMPAIGN
```

Each command prints a run ID, workspace, exact agent prompt, and a continuation command. After the fresh agent task stops, run the printed command, which has this form:

```bash
python3 -m evals.run --continue RUN_ID
```

Success writes `evals/results/RUN_ID.json`. The direct fixture uses standard-library `unittest` syntax that pytest can also collect; this keeps grading offline on hosts without pytest.

## Run one resume trial

These commands prepare Phase 1. Run them in the **macOS host Terminal from the source repository root**. They persist isolated temporary repositories but do not change the source framework.

```bash
python3 -m evals.run --scenario resume --variant baseline --runs 1 --campaign CAMPAIGN
python3 -m evals.run --scenario resume --variant workflow --runs 1 --campaign CAMPAIGN
```

After the Phase 1 agent stops, run the printed `--continue RUN_ID` command. That persistent step captures Phase 1, deletes the transient input, adds D1, and commits only those two external mutation paths. It then prints the exact Phase 2 prompt.

Close the Phase 1 task. Start a completely new Codex task rooted at the same workspace, paste only the Phase 2 prompt, and let it stop. Then run this from the **macOS host Terminal at the source repository root**:

```bash
python3 -m evals.run --continue RUN_ID --fresh-session-confirmed
```

The flag records the operator's confirmation that Phase 2 used a fresh task. It does not carry Phase 1 context into the fixture.

To prepare repeated independent runs, change `--runs 1` to (for example) `--runs 3`. Each run receives a unique pristine workspace and run ID.

## Inspect and compare results

Showing a prompt is read-only. Run this in the **macOS host Terminal from the source repository root** when a prompt needs to be copied again:

```bash
python3 -m evals.run --show-prompt RUN_ID
```

The comparison command is also read-only. A campaign is required so results produced under unrelated evaluator versions or fairness conditions are not silently combined. It reports behavioral counts and means within that campaign without creating a combined score:

```bash
python3 -m evals.run --compare --campaign CAMPAIGN
```

If workflow runs use more tokens but recover the AMI and complete more often, interpret that as an explicit continuity/overhead tradeoff. If direct runs acquire extra state or regress, that is evidence of interference. Unknown observations remain `n/a` rather than being guessed by the grader.

## Verify the harness

The harness tests are deterministic and need no network or pytest. Run this read-only verification in the **macOS host Terminal from the source repository root**:

```bash
python3 -m unittest discover -s evals/tests -v
```

Expected success ends with `OK`. If it fails, the first failing test is the most useful next diagnostic.

The repository's full maintainer gate is also read-only and runs from the same location:

```bash
python3 skills/agent-workflow/scripts/verify_package.py --tests
```

Expected success ends with `OK: Agent Workflow package verification passed.`

## Results, side effects, and cleanup

Completed result JSON is stored under `evals/results/CAMPAIGN/`. Temporary run repositories and control files remain under the host path printed by the harness (normally `/tmp/agent-workflow-evals/RUN_ID`) so manual sessions can resume safely. Continuation reads the campaign from that control state, so the later grading command does not need a repeated `--campaign` argument.

After reviewing a completed run, remove its temporary workspace with this persistent cleanup command from the **macOS host Terminal at the source repository root**:

```bash
python3 -m evals.run --cleanup RUN_ID
```

Cleanup permanently removes only the guarded temporary run directory; the result JSON remains. A deleted temporary run cannot be continued. Reverse unwanted source changes with version control; remove an unwanted generated result by deleting only its named JSON file after reviewing it.

## Known limitations

- Manual agent execution prevents reliable capture of exit status, timing, token use, action count, and agent stdout/stderr.
- Matching model configuration and execution permissions across manual runs is an operator-controlled fairness condition rather than a harness-enforced invariant.
- The fresh-session flag is an auditable confirmation, not enforcement by a coding-agent API.
- Static Terraform grading intentionally accepts reasonable layouts, so it proves the requested observable properties rather than full provider-schema validity. If `terraform` is installed, the grader additionally runs offline `terraform fmt -check`; it does not download providers for `terraform validate`.
- Phase 1 inspection and completion claims cannot be inferred safely from repository keywords, so those observations remain `null` without execution metadata.
- The workflow variant evaluates the local core router and bundled local workflows. Optional upstream provider installation is excluded equally from setup to avoid network-dependent contamination.
- These targeted cases favor Agent Workflow in the narrow sense that continuity is a claimed framework capability. The direct case deliberately disadvantages unnecessary workflow ceremony to expose its cost. Neither case establishes general model quality or statistical significance.
