# Behavioral testing

## Purpose

The behavioral suite asks whether orchestration improves observable engineering
behavior. It does not treat the current router implementation or one exact route
trace as inherently correct. A scenario succeeds when the requested outcome,
verification, state use, research grounding, or clean blocker behavior is
observable—and prohibited repository effects did not occur.

The framework uses only Python 3.11 standard-library modules. Normal pull
requests do not need a model, network credential, provider, Git repository, or
hidden reasoning trace.

## Testing layers

1. **Production-boundary tests** exercise lifecycle, provider transactions,
   package verification, bootstrap safety, routing, and Wayfinder state through
   their public boundaries.
2. **Behavior-harness tests** validate TOML schema and vocabulary, blind-rubric
   isolation, evaluator failure modes, route-marker syntax, fixture reset, and
   command-runner evidence.
3. **Wayfinder behavioral scenarios** provide fixture-backed observable
   contracts for authority, effort selection, reconciliation, and
   record pruning or effort ending without duplicating product implementation.
4. **Live behavioral smoke tests** are opt-in. A caller supplies an agent command
   that operates in a disposable fixture workspace. The default set remains a
   representative sample rather than an exhaustive catalog.
5. **Evaluation-tooling tests** under `evals/tests/` are deterministic and
   network-free, but remain separate from the distributed package gate.

The deterministic package tests and scenario validation are the required
pre-merge gate. Live smoke tests are manual or suitable for a separately
credentialed scheduled/release job; they are not required on ordinary pull
requests.

## Human-authored scenario format

Scenarios are TOML files under
`skills/agent-workflow/tests/scenarios/`. TOML is readable and available in
Python 3.11 without another dependency. A maintainer normally supplies:

```toml
schema_version = 1
id = "example-scenario"
name = "Readable scenario name"
fixture = "example-project"
request = "Natural-language request given to the live agent."
starting_state = [
  "A resolved project decision exists.",
  "One non-blocking unresolved question remains.",
]
expect = [
  "existing_state_reused",
  "meaningful_repository_change",
  "verification_performed",
]
must_not = [
  "repeat_resolved_discovery",
  "overwrite_project_owned_state",
]
live = false
blind_grading = false
verification_command = "Run python verify.py after the change."
preserve_paths = ["project-state/unknowns.md"]
forbid_created_globs = ["/**"]
route_must_not_include = ["discovery"]
state_must_include = [".agent-wayfinder/example/map.md"]
state_must_not_include = [".agent-wayfinder/example/unknowns/U9-unrelated.md"]

[[assertions]]
kind = "path_contains"
path = "app.py"
value = "observable result"

[[assertions]]
kind = "glob_count"
path = ".agent-wayfinder/example/unknowns/U*.md"
count = 1

[[assertions]]
kind = "glob_contains"
path = ".agent-wayfinder/example/unknowns/U1-*.md"
value = "known unresolved question"

[[assertions]]
kind = "glob_any_contains"
path = ".agent-wayfinder/example/unknowns/U*.md"
value = "external approval"

[[assertions]]
kind = "glob_none_contains"
path = ".agent-wayfinder/example/unknowns/U*.md"
value = "incidental detail"
```

Set optional `blind_grading = true` for behavioral-judgment scenarios where
showing the rubric would coach the agent toward the classification under test.
The live prompt then withholds `expect`, `must_not`, state-loading constraints,
report requirements, and `verification_command`; hidden evaluation and
assertions still run normally. The scenario name, request, and starting state
must remain neutral, and the live workspace uses a non-descriptive case name so the
scenario identifier does not reveal the rubric. Prefer ordinary guided smoke
tests when prompt contamination is not the behavior under evaluation.

`expect` and `must_not` use a deliberately small vocabulary implemented in
`tests/behavior.py`. Case-specific assertions support path existence, UTF-8
substring presence/absence, and case-insensitive substring checks or exact
regular-file counts for a safe relative glob. `glob_any_matches` and
`glob_none_matches` apply a case-insensitive expression that may span newlines
to require a match in at least one or no matching files; use them sparingly when
related semantic outcomes must be associated without requiring a particular
document layout. `glob_contains`
requires every match to contain the value, while `glob_any_contains` and
`glob_none_contains` test whether at least one or no matching file contains it
without fixing the artifact count. A broad exact count can reject extra children
while a stable-ID content glob such as `U1-*.md` requires the intended identity
and meaning without fixing the descriptive filename slug. This keeps contracts
focused on outcomes and prevents the harness from becoming a second router.

The optional `state_must_include` and `state_must_not_include` arrays constrain
the public `state_used` report. They make progressive-loading behavior observable
without asking for private reasoning: a relevant map/child must be reported as
consulted, while a known unrelated child must not be. Every named path must be a
regular file in the starting fixture.

A new scenario should need one TOML file and one small fixture directory. The
validator rejects unrecognized behavior names, unsafe paths, missing preserved
files, unrecognized fields, and unsupported assertion kinds.

The deterministic catalog includes pruning behavior for answered U# and
redundant E# files only after reference reconciliation, keeping blocked
efforts resumable, excluding mapless directories from selection, updating the
same D# decision boundary through project decision authority, and preventing reference-system observations from
becoming unsupported current-project facts. These are human-authored behavior
contracts, not evidence that an unrun model obeyed them.

## Fixtures and reset

Fixtures live under `skills/agent-workflow/tests/fixtures/`. They contain only
the minimum repository evidence and validation command needed to make the
starting state understandable. They do not copy framework payload files.

Each deterministic or live run uses `shutil.copytree` into a newly created
temporary directory, installs the current framework with `adopt.py`, and takes
its baseline snapshot only after installation. The source fixture is never
mutated. `--keep-workspaces` creates a unique run directory under a caller-owned
location when post-run inspection is useful; otherwise temporary workspaces are
removed automatically.

## Observable evidence

The evaluator uses public artifacts only:

- file creation, modification, deletion, and SHA-256 identity before/after;
- exact preservation of paths declared project-owned by the scenario;
- prohibited created-path globs;
- fixture verification events in
  `.behavior-evidence/verification.jsonl`, including exit codes and ordering;
- a concise agent-written `.behavior-evidence/report.json` containing status,
  commands/exit codes, cited research URLs, state paths actually consumed,
  selected/executed provider claims, and blockers;
- exactly one syntactically valid route marker ending the agent's stdout final
  response; and
- case-specific path assertions.

Route-marker presence is a required visibility contract. General scenarios do
not require one exact workflow sequence: route-specific exclusions and scenario
evidence evaluate truthfulness only where the scenario establishes it. No
evaluator asks for chain-of-thought, private model reasoning, exact prose, or a
fixed stage count.

The report is a claim, so important outcomes are cross-checked against repository
diffs, fixture verification logs, state preservation, and scenario assertions.
Only fixture-recorded verification events satisfy a verification expectation;
an agent's report cannot turn an unobserved command into a passing check. A
reported state input counts only when that path existed in the starting
repository snapshot.
Research grounding currently proves that the agent supplied a public source; it
does not independently adjudicate every changing external fact.

## Commands

Run all commands from the **source repository root** in the macOS/Linux host
Terminal or the VS Code Dev Container terminal that owns this checkout.

The behavior-harness and Wayfinder behavior suites are deterministic and
read-only outside temporary directories:

```bash
python3 -B -m unittest discover -s skills/agent-workflow/tests -p 'test_behavior_harness.py' -v
python3 -B -m unittest discover -s skills/agent-workflow/tests -p 'test_wayfinder_behavior.py' -v
```

The full required pre-merge gate runs package/static checks plus every
deterministic unit, lifecycle, routing, and fixture test:

```bash
python3 skills/agent-workflow/scripts/verify_package.py --tests
```

For a live run, use an environment with the chosen agent executable, model
credentials, and any host permission for research/network access required by the selected
scenarios. This can consume model quota and contact external services. The
command must read the prompt from standard input, operate in its current
working directory, and write only the final user-facing response to standard
output. Progress, tool, transport, and diagnostic output belongs on standard
error. This output boundary lets the evaluator verify that the final response
ends with exactly one route marker without depending on a host-specific event
stream. Run:

```bash
python3 skills/agent-workflow/tests/behavior.py live \
  --agent-command-json '["/absolute/path/to/your-agent-command-wrapper"]' \
  --output /tmp/agent-workflow-live-report.json
```

If the agent CLI needs explicit paths, the JSON command may use the placeholders
`{workspace}`, `{prompt_file}`, and `{report_file}`. For example:

```bash
python3 skills/agent-workflow/tests/behavior.py live \
  --agent-command-json '["/absolute/path/to/your-agent-command-wrapper", "--workspace", "{workspace}", "--prompt", "{prompt_file}"]' \
  --keep-workspaces /tmp/agent-workflow-live \
  --output /tmp/agent-workflow-live-report.json
```

`--scenario simple-bounded-task` may be repeated to select named contracts,
including contracts outside the default smoke set. Without it, every scenario
marked `live = true` runs. Kept workspaces and reports are persistent caller
artifacts; remove those explicitly after review. The normal temporary mode
cleans workspaces automatically.

## Current limitations

- Existing-state reuse is supported by both a public `state_used` report and
  scenario-specific output assertions; filesystem snapshots cannot observe a
  read by themselves.
- Progressive-loading checks likewise rely on the public `state_used` report;
  they detect overloading reported by a cooperative agent but are not operating
  system file-access tracing.
- External research checks cited public URLs and observable output, but changing
  facts may still require human or domain-specific adjudication.
- Required route markers remain agent claims rather than proof of execution;
  scenario evidence and route-specific checks establish truthfulness where
  observable.
- Provider-native tracker interactions and live editor-host behavior need a
  separately credentialed environment and are not represented as deterministic
  success.
- The live runner is command-based rather than tied to one vendor CLI. A host
  command wrapper must satisfy the documented stdin/current-directory contract.
