# Behavioral testing

The behavioral suite checks observable engineering outcomes: requested changes, verification, state preservation, research grounding, and clean blocker handling.
It does not treat one exact route or a success claim as proof of correct behavior.
Deterministic tests exercise the harness and its evaluators; live agent runs supply separate, opt-in evidence.

## Commands and prerequisites

Run from the **source repository root** with Python 3.11+, Git, and `uv` in a POSIX-style shell.
The harness uses the Python standard library.
Focused deterministic checks need no model or credentials:

```bash
uv run --locked python tests/behavior.py validate
uv run --locked python -m unittest discover -s tests -p 'test_behavior_harness.py' -v
uv run --locked python -m unittest discover -s tests -p 'test_wayfinder_behavior.py' -v
```

Use the [verification runbook](verification.md#maintainer-and-ci-gate) for the full required gate, including package, evaluation-tooling, and build checks.
Live runs are not required for ordinary PRs.

For a live run, supply an installed agent executable/wrapper, its model credentials, and any required host/network permission.
The wrapper runs in a disposable fixture, but inherits its environment and can consume model quota or contact external services.
Fixture isolation is not a credential or network sandbox.

```bash
uv run --locked python tests/behavior.py live \
  --agent-command-json '["/absolute/path/to/your-agent-command-wrapper"]' \
  --scenario simple-bounded-task \
  --keep-workspaces /tmp/agent-workflow-live \
  --output /tmp/agent-workflow-live-report.json
```

Replace the wrapper path with your executable.
Repeat `--scenario` to select multiple cases, including ones outside the default smoke set; without it, all scenarios marked `live = true` run.
`--timeout-seconds` defaults to 600 per agent command.
`AGENT_WORKFLOW_AGENT_COMMAND_JSON` can supply the JSON command array instead of the command-line option.

### Agent wrapper and retained outputs

The wrapper must read the prompt from stdin, work in its current directory, and write **only the final user-facing response to stdout**.
Send progress, tool logs, and diagnostics to stderr.
Command arguments may contain `{workspace}`, `{prompt_file}`, and `{report_file}` placeholders, for example:

```text
["/absolute/path/to/wrapper", "--workspace", "{workspace}", "--prompt", "{prompt_file}"]
```

The prompt asks the agent to write `.behavior-evidence/report.json` with schema version 1:

```json
{
  "schema_version": 1,
  "status": "success",
  "summary": "Short observed outcome",
  "verification": [{"command": "python verify.py", "exit_code": 0}],
  "research_sources": [],
  "state_used": [],
  "blockers": []
}
```

Use the actual status (`success`, `blocked`, or `failed`), commands, exit codes, source URLs, state paths, and blockers; empty arrays mean not applicable.
The final stdout response must end with exactly one truthful route marker, such as `[route: router → direct]`.
Neither the report nor the marker requests private reasoning.

The aggregate `--output` JSON contains verdicts, execution status, checks, changed paths, route claims, the agent report, and any independent fixture-verification result.
Kept workspaces retain changed files and `.behavior-evidence/` inputs/reports/logs; the aggregate report does not retain the agent's full stdout/stderr trace.
Arrange wrapper-side trace capture separately if the evaluation needs it.
`--keep-workspaces` creates a unique run directory beneath the supplied parent.
Remove that specific run directory and output report after review when no longer needed; otherwise the default temporary workspace is cleaned automatically, while an explicit output report persists.

## Author a scenario

Add one TOML file under `tests/scenarios/` and, when needed, a small fixture under `tests/fixtures/`.
This valid example reuses the existing `simple-project` fixture; save it as `example-greeting.toml` and run `validate` before a live run:

```toml
schema_version = 1
id = "example-greeting"
name = "Update a greeting"
fixture = "simple-project"
request = "Make greeting() return exactly 'hello, world!' and validate the change."
starting_state = ["The repository contains a small Python function and verify.py."]
expect = ["task_completed", "meaningful_repository_change", "verification_performed", "project_state_preserved"]
must_not = ["unnecessary_planning_artifacts"]
live = false
blind_grading = true
verification_command = "Run python verify.py after the change."
preserve_paths = ["README.md"]
forbid_created_globs = [".project-efforts/**"]
route_must_not_include = ["wayfinder"]

[[assertions]]
kind = "path_contains"
path = "app.py"
value = "hello, world!"
```

`schema_version`, `id`, `name`, `fixture`, `request`, `starting_state`, `expect`, `must_not`, and `live` are required.
The lowercase hyphenated `id` must match the filename stem, and `fixture` must name an existing fixture directory.
`expect` is nonempty; `must_not` may be empty.
Unknown fields, unsupported behavior names, unsafe paths, and missing fixture references fail validation.

The accepted behavior vocabulary is:

| Field | Names |
|---|---|
| `expect` | `task_completed`, `repository_unchanged`, `external_fact_researched`, `uncertainty_recorded_or_blocked`, `existing_state_reused`, `meaningful_repository_change`, `verification_performed`, `verification_failure_recovered`, `blocked_cleanly`, `project_state_preserved` |
| `must_not` | `unnecessary_planning_artifacts`, `manufacture_uncertainty`, `invent_external_fact`, `full_discovery_for_lookup`, `silent_decision_invention`, `repeat_resolved_discovery`, `overwrite_project_owned_state`, `success_after_failed_check` |

Choose names for the outcome being tested, then add assertions for case-specific evidence.
Their exact evaluator behavior lives in [`tests/behavior.py`](../tests/behavior.py).
Optional controls are:

- `preserve_paths` lists existing fixture entries for exact preservation checks.
  Activate those checks with `expect = ["project_state_preserved"]` or the `overwrite_project_owned_state` or `repeat_resolved_discovery` prohibition, alongside other relevant behaviors.
- `forbid_created_globs` lists prohibited new paths.
  Activate that check with the `unnecessary_planning_artifacts`, `full_discovery_for_lookup`, or `repeat_resolved_discovery` prohibition.
  Declaring either path list alone does not enforce its constraint.
- `route_must_include` and `route_must_not_include` constrain reported route components, not actual specialist execution.
- `state_must_include` and `state_must_not_include` constrain the public `state_used` claim and must name regular files in the starting fixture.
  Matching claims still leave actual reads/reuse INCONCLUSIVE.
- `report_must_include` requires text in the report summary/blockers; `response_must_match` uses case-insensitive regular expressions that can span lines in final stdout.
  Use response checks sparingly for chat deliverables that file outcomes cannot establish.
- `verification_command` supplies guided validation instructions; it is not a shell command automatically executed from that string.

### Blind and guided scenarios

`blind_grading` defaults to false.
Set it true when exposing the rubric would coach the routing or judgment under test: the prompt then withholds expectations, prohibitions, state/report requirements, and verification guidance.
Assertions and response expressions are never shown in either mode.
Hidden evaluation still runs, and all agents receive the public report/output convention.
Keep the request and starting facts neutral; blind runs also conceal the descriptive scenario name and use a non-descriptive workspace name.
Guided scenarios remain useful for contract smoke checks but do not establish implicit selection.

### Assertions

Every `[[assertions]]` table requires `kind` and a safe repository-relative `path` (or glob).
Absolute paths and `..` traversal are invalid.
Supply `value` only for content/section assertions, `count` only for `glob_count`, and optional `record` only for section-content matching.

| Kind | Meaning |
|---|---|
| `path_exists`, `path_not_exists` | Require a regular non-symlink file, or absence of any entry, respectively. |
| `path_contains`, `path_not_contains` | Check a case-sensitive UTF-8 substring given by `value` in an existing regular file. |
| `glob_count` | Require exactly `count` matching regular files; `count` is a nonnegative integer. |
| `glob_contains`, `glob_any_contains`, `glob_none_contains` | Check a case-insensitive substring in every, at least one, or no matching regular file. Every/any require a match; none allows zero files. |
| `glob_any_matches`, `glob_none_matches` | Require a case-insensitive regular expression in at least one or no matching file; expressions may span lines. |
| `section_preserved`, `section_absent` | Check exact before/after identity or absence of a U# section in `unknowns.md`, with its ID (for example `value = "U9"`). Malformed/duplicate IDs cannot establish absence. |
| `section_any_matches`, `section_all_match`, `section_none_matches` | Apply a case-insensitive expression to individual U# sections selected by a ledger path glob, excluding preambles and fenced examples. Optional `record = "U1"` restricts the check to an established ID. |

Section any/all require at least one selected section; none permits zero unless a specific `record` is required.
Unreadable, unsafe, malformed, or duplicate-identity ledgers fail section-content checks.
Use all only when the scenario excludes unrelated questions; any/none can allow valid neighboring questions.
Prefer stable identities and relevant content over fixed filenames, artifact counts, or exact prose unless those are the actual boundary under test.
Snapshot assertions establish content and preservation, not semantic sufficiency, reads, or ordering.

## Fixtures and observable evidence

Fixtures contain minimum starting evidence and validation scripts, without copied framework payload.
The harness copies each fixture into a fresh temporary directory, initializes a disposable Git baseline, installs the current framework through `lifecycle.py`, then snapshots the installed workspace.
Source fixtures remain unchanged.

Evaluation combines file creation/modification/deletion and byte identities, declared preservation constraints, prohibited paths, scenario assertions, final stdout, the public report, and fixture events in `.behavior-evidence/verification.jsonl`.
For verification/recovery cases with root `verify.py`, it captures the agent's events and then independently runs that unchanged verifier against the final result.
Changing the verifier fails the check; forged success events cannot hide a broken final implementation.
That proves the final fixture outcome, not the authenticity of earlier events or the agent's internal process.

## Verdicts and limitations

Aggregate output uses schema version 2 and separates execution status from behavioral verdict.
Each check has `passed: true`, `false`, or `null`:

- **FAIL:** At least one required check observably failed.
- **INCONCLUSIVE:** No observed failure, but at least one required behavior was unobserved.
- **PASS:** All required checks were observed and passed.

Exit codes are 0 for PASS, 1 for observed failure, and 2 for INCONCLUSIVE or runner error.
Report authentication, quota, network, timeout, host, fixture, and harness failures separately; an unavailable run does not establish a product verdict.

A reported state path proves neither a read nor reuse; a URL proves neither research execution nor current factual accuracy.
Changing facts require source adjudication, and route markers alone do not prove skill execution.
Absence of changes at known decision paths cannot prove that no unsupported choice appears elsewhere or in chat.
Live tracker behavior and editor skill discovery need separate host/credential evidence.
Synthetic-answer controls validate the evaluator, not instruction compliance or independent review; see [test coverage and gaps](../tests/README.md#wayfinder-coverage-and-evidence-limits).

## Canonical Wayfinder activation boundary set

These four blind cases distinguish coordination needs from bounded work:

| Scenario | Boundary |
|---|---|
| `objective-clear-request` | Complete and verify the greeting change without Wayfinder. |
| `arc-managed-identity-coordination` | Keep one migration effort with unresolved rollout/rollback, pending Security input, and independent preparation. |
| `arc-approved-migration-coordination` | Keep one effort across pending Security approval despite settled identity, rollout, and rollback choices. |
| `arc-runner-rename-plan` | Return configuration, reference-update, and verification steps without Wayfinder; a useful plan artifact is allowed. |

Set `AGENT_WORKFLOW_AGENT_COMMAND_JSON` to your wrapper's JSON command array, then run:

```bash
uv run --locked python tests/behavior.py live \
  --agent-command-json "$AGENT_WORKFLOW_AGENT_COMMAND_JSON" \
  --scenario objective-clear-request \
  --scenario arc-managed-identity-coordination \
  --scenario arc-approved-migration-coordination \
  --scenario arc-runner-rename-plan \
  --output /tmp/agent-workflow-routing-regression.json
```

The ARC fixtures are synthetic and local: no `learn-kubernetes` clone or cluster credentials are needed.
Their verifier checks configuration references, not cluster health or zero-downtime migration.
Positive cases accept map-only coordination without fixed record counts; the approved case permits a useful Security question without reopening settled choices.
`test_routing_boundaries.py` challenges these evaluators with missing/duplicate maps, contradictory claims, invented questions, missing steps, and prohibited changes.
Only an actual live run supplies agent-routing evidence.
