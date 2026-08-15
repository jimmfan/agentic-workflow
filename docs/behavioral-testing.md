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

## Three layers

1. **Contract/unit tests** validate TOML schema, supported behavior vocabulary,
   fixture size, evaluator failure modes, route-marker optionality, and the
   command-runner protocol.
2. **Fixture/integration tests** copy every consuming-project fixture into a new
   temporary directory. They exercise install, update, repeated update, remove,
   and reinstall, comparing project-owned state after every operation. Fixture
   validation commands begin in a known failing state where implementation is
   required.
3. **Live behavioral smoke tests** are opt-in. A caller supplies an agent command
   that reads the scenario prompt from standard input and operates in the
   temporary fixture working directory. Five high-value scenarios are enabled:
   simple bounded work, external factual uncertainty, existing Wayfinder state,
   verification failure/recovery, and a blocked project.

The deterministic first two layers plus package checks are the required
pre-merge gate. Live smoke tests are manual or suitable for a separately
credentialed scheduled/release job; they are not required on ordinary pull
requests.

## Related deterministic catalogs

The TOML files described below are the only scenarios loaded by `behavior.py`.
Two separate JSON catalogs live directly under `skills/agentic-workflow/tests/`:

- `acceptance-scenarios.json` is a concise index of lifecycle product acceptance
  cases exercised by the lifecycle suite; and
- `decision-contract-scenarios.json` supplies representative routing decisions
  to `test_routing.py`.

These JSON files are deterministic product catalogs, not fixture-backed or live
behavioral scenarios, so they do not use the TOML schema. The package verifier
checks their catalog schemas directly, then invokes `behavior.py validate` to
validate every TOML scenario and fixture reference.

## Human-authored scenario format

Scenarios are TOML files under
`skills/agentic-workflow/tests/scenarios/`. TOML is readable and available in
Python 3.11 without another dependency. A maintainer normally supplies:

```toml
schema_version = 1
id = "example-scenario"
name = "Readable scenario name"
fixture = "example-project"
request = "Natural-language request given to the live agent."
starting_state = [
  "A resolved project decision exists.",
  "One non-blocking unknown remains.",
]
expect = [
  "existing_state_reused",
  "meaningful_repository_change",
  "verification_performed",
]
must_not = [
  "repeat_resolved_discovery",
  "invent_unknown_answers",
]
live = false
verification_command = "Run python verify.py after the change."
preserve_paths = ["project-state/unknowns.md"]
forbid_created_globs = ["docs/decisions/**"]
route_must_not_include = ["discovery"]
state_must_include = [".ai-workflow-state/wayfinder/example/map.md"]
state_must_not_include = [".ai-workflow-state/wayfinder/example/unknowns/U9-unrelated.md"]

[[assertions]]
kind = "path_contains"
path = "app.py"
value = "observable result"

[[assertions]]
kind = "glob_count"
path = ".ai-workflow-state/wayfinder/example/unknowns/U*.md"
count = 1

[[assertions]]
kind = "glob_contains"
path = ".ai-workflow-state/wayfinder/example/unknowns/U1-*.md"
value = "known unresolved question"
```

`expect` and `must_not` use a deliberately small vocabulary implemented in
`tests/behavior.py`. Case-specific assertions support path existence, UTF-8
substring presence/absence, and case-insensitive substring checks or exact
regular-file counts for a safe relative glob. A broad count can reject extra
children while a stable-ID content glob such as `U1-*.md` requires the intended
identity and meaning without fixing the descriptive filename slug. This keeps
contracts focused on outcomes and prevents the harness from becoming a second
router.

The optional `state_must_include` and `state_must_not_include` arrays constrain
the public `state_used` report. They make progressive-loading behavior observable
without asking for private reasoning: a relevant map/child must be reported as
consulted, while a known unrelated child must not be. Every named path must be a
regular file in the starting fixture.

A new scenario should need one TOML file and one small fixture directory. The
validator rejects unknown behavior names, unsafe paths, missing preserved files,
unknown fields, and unsupported assertion kinds.

## Fixtures and reset

Fixtures live under `skills/agentic-workflow/tests/fixtures/`. They contain only
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
  selected/executed provider claims, blockers, and an optional route marker; and
- case-specific path assertions.

Route markers are useful evidence when present but remain optional. No evaluator
asks for chain-of-thought, private model reasoning, exact prose, a fixed stage
count, or one exact workflow sequence.

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

The fast behavioral contract suite is deterministic and read-only outside
temporary directories:

```bash
python3 -B -m unittest discover -s skills/agentic-workflow/tests -p 'test_behavior_*.py' -v
```

The fixture lifecycle exercise is also deterministic and uses only disposable
temporary copies:

```bash
python3 skills/agentic-workflow/tests/behavior.py fixtures
```

The full required pre-merge gate runs package/static checks plus every
deterministic unit, lifecycle, routing, and fixture test:

```bash
python3 skills/agentic-workflow/scripts/verify_package.py --tests
```

For a live run, use an environment with the chosen agent executable, model
credentials, and any research/network permission required by the selected
scenarios. This can consume model quota and contact external services. The
command must read the prompt from standard input and operate in its current
working directory. Run:

```bash
python3 skills/agentic-workflow/tests/behavior.py live \
  --agent-command-json '["/absolute/path/to/your-agent-adapter"]' \
  --output /tmp/agentic-workflow-live-report.json
```

If the agent CLI needs explicit paths, the JSON command may use the placeholders
`{workspace}`, `{prompt_file}`, and `{report_file}`. For example:

```bash
python3 skills/agentic-workflow/tests/behavior.py live \
  --agent-command-json '["/absolute/path/to/your-agent-adapter", "--workspace", "{workspace}", "--prompt", "{prompt_file}"]' \
  --keep-workspaces /tmp/agentic-workflow-live \
  --output /tmp/agentic-workflow-live-report.json
```

`--scenario simple-bounded-task` may be repeated to select named contracts,
including contracts outside the default smoke set. Without it, all five
default-live scenarios run. Kept workspaces and reports are persistent caller
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
- Optional route markers cannot prove execution and are never the sole pass
  condition.
- Provider-native tracker interactions and live editor-host behavior need a
  separately credentialed environment and are not represented as deterministic
  success.
- The live runner is command-based rather than tied to one vendor CLI. A host
  adapter must satisfy the documented stdin/current-directory contract.
