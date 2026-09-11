# Remaining behavior audit protocol

Evaluate four pre-existing hypotheses against fetched `origin/main` `1510e74540e3ebdb7c07966274fae7aeeac09386` after PR #32.
Runtime instructions, skills, contracts, terminology, architecture, VERSION and real consumers are outside the mutation scope.
The [report](REPORT.md) maintains results; this file maintains the predeclared design and adjudication rules.

## Design

Use the existing `tests/behavior.py` blind-scenario harness and disposable fixture installation.
Requests and fixture content contain task evidence, without desired route names or evaluator answers.
H4 necessarily names its existing effort; its request does not prescribe preservation, pruning, references or readback steps.
Inspect actual tool calls and results, final files, diffs and test outcomes; a loaded skill, report or route marker alone proves no method execution.
The existing harness still asks for an evidence report and marker, so this measures behavior under that common observation instruction rather than completely unprompted reporting.

| Cases | Question and decisive observation |
|---|---|
| `audit-source-answer`, `audit-source-continuation`, `audit-plan` | H1: a bounded read of a synthetic publisher's primary protocol, a consequential scoped claim needed in later sessions, and an ordinary configuration rename plan. Negative/control cases must avoid Wayfinder execution and state; the positive must preserve usable continuation. |
| `audit-diagnosis`, `audit-trivial-fix`, `audit-causal-fix` | H2: diagnose a cross-account cache regression without editing; repair a small configuration mismatch; diagnose and repair the cache defect with a regression test. Separate investigation, build, closing review and acceptance verification in the trace. |
| `audit-integration`, `audit-test-first`, `audit-ui`, `audit-cli`, `audit-research`, `audit-rename`, `audit-spec`, plus `audit-diagnosis` | H3: coverage for established behavior, explicit test-first feature, interactive alternatives, CLI feasibility, current external uncertainty, mechanical rename, settled specification synthesis, unexplained regression. Judge sufficient method, not skill inventory or an exact route sequence. |
| `audit-resolution` | H4: fresh resume after authoritative evidence arrives. Preserve the useful scoped answer, reconcile readiness and references, prune U7, preserve U8 and unrelated bytes, verify retrieval before pruning and reread saved results before completion. |

Run each of the 14 distinct cases once, then repeat the H1 negative case once in another fresh session (15 planned invocations).
No failed behavior run is replaced; no prompt tuning after observing a subject response.
Run sequentially, with a 360-second per-subject limit.
A single successful run is bounded positive evidence, not a reliability estimate.
H1's positive also satisfies a continuation signal, so it checks the desired boundary but cannot isolate the causal contribution of one hard-signal sentence.
Repeated H1 over-selection permits a smallest wording recommendation only; do not apply it here.

## Execution and isolation

Use a fresh Codex CLI session/home per invocation, the current installed consumer payload, medium reasoning, and `gpt-5.6-sol` as the campaign model.
Ignore personal configuration/rules; disable apps, plugins and memories; permit native parallel reviewers so H2 does not lose its closing-review capability by construction.
Restrict subject filesystem access to its disposable workspace and executable/runtime necessities; deny tool network except the native web-search capability for the external-research case.
Keep credentials outside the subject filesystem and delete the isolated credential copy in cleanup.
Audit model-visible inputs before spending a subject invocation: no authoring checkout, campaign protocol, hidden rubric, sibling workspaces, personal skills or prior conversation.
Record any automatic system skills exposed by the host.
The [official Codex execution documentation](https://learn.chatgpt.com/docs/github-action#configure-codex-exec) supports separate model/effort, sandbox and final-output controls; actual installed CLI help and prompt inspection determine available controls.
Probe basic sandbox tool execution first.
If tools cannot execute, diagnose the host boundary without relaxing subject isolation; do not spend the entire matrix on an unchanged infrastructure failure.
An infrastructure-blocked matrix remains unexecuted, not successful or behaviorally failed.

## Adjudication

Deterministic checks validate fixtures, hidden criteria, retained bytes and evaluator rejection behavior.
They never establish live selection, investigation, test-first ordering, independent review, source accuracy or saved-result reads.
Manual trace adjudication is required for those dimensions; retain compact event citations and actual outputs alongside the report, with raw logs/workspaces in ignored `evals/artifacts/` or outside the checkout.
Use existing `CheckResult`/`verdict` semantics: observed violation = FAIL; required unobserved dimension = INCONCLUSIVE; every required dimension observed and satisfied = PASS.
Infrastructure-blocked describes execution failure separately from the INCONCLUSIVE behavioral result.

- H1: inspect policy/skill resources loaded, executed method, answer/plan usefulness and created state.
  Loading alone may be excess context without establishing Wayfinder execution.
- H2: diagnosis must explain the real divergence using executed evidence and leave code unchanged; trivial repair must fix the causal value without unjustified overhead.
  Meaningful repair must address cross-account isolation and refresh semantics, demonstrate that the regression catches the original defect and passes after repair (the test itself may be authored before or after the repair), and receive proportionate closing review and acceptance coverage.
  `implement` itself is not mandatory.
  Missing independent reviewer capability is an execution limitation, not proof of a composition defect.
  Classify coherent behavior as A, demonstrated handoff ambiguity with a material coverage gap as B, otherwise C.
- H3: integration tests do not by themselves imply test-first development; explicit test-first work requires red-before-green evidence.
  UI exploration must support comparison of interactions; CLI experimentation needs a real process-level observation without gratuitous HTML.
  Research needs fetched primary evidence with correct scope.
  Mechanical rename needs preserved behavior without a module-design investigation.
  Specification synthesis must retain settled choices without reopening them.
- H4: inspect the ordered trace for artifact preservation and pre-pruning retrieval, reference/readiness updates, U7 removal, and final saved-result readback.
  A usable linked primary source can retain detail; a dangling link or empty artifact cannot.
  U8 must still block only deployment.
  No new approvals, authority, dependencies or records without independently justified value.
  File state alone cannot prove safe temporal order.

Negative controls must reject deletion of U7 with no usable retained result and a success claim lacking a saved-result check.
For an otherwise correct final snapshot, missing temporal evidence stays INCONCLUSIVE; observed pruning before preservation is FAIL even when later repairs make the final files look correct.
Document semantic judgments and textual-check limits rather than treating regular expressions as a second router.
Do not promote the prior infrastructure-blocked map-authoring campaign or separate manual ARC observations into controlled successes.

## Verification and reproduction

Run `uv run --locked python -m unittest discover -s tests -p 'test_remaining_audit_controls.py' -v` before live execution, then the required gates in [verification](../../docs/verification.md).
Validate scenarios with `uv run --locked python tests/behavior.py validate`.
Run selected cases through the existing live command with `--scenario audit-...`, `--keep-workspaces` outside the repository, and `codex_subject.py --output-root /tmp/remaining-audit/subjects` as `--agent-command-json` (a JSON array prefixed by the absolute Python executable and wrapper paths).
For `audit-research` only, append `--web` to that wrapper command.
Use a 420-second outer harness timeout, allowing the wrapper's 360-second process limit to save interrupted evidence and remove its credential copy.
The wrapper records the actual invocation, context audit, public events and final response; it does not grade behavior.
Independent Standards and Spec reviewers inspect design, fixture leakage, outcome criteria and conclusions before delivery.

## Execution-boundary amendment

The [report](REPORT.md#infrastructure-and-evidence-limits) records an observed isolation failure and the resulting stopped campaign; no subject prompt was tuned or unsuccessful attempt replaced.
The current adapter requires a synthetic data/credential-canary check before it copies authentication or launches a model.
Use `--preflight-only` to test that boundary without a model invocation.
Do not bypass a failed preflight; require an effective host boundary and a successful native-tool denial probe before resuming the matrix.
The [official permission-profile documentation](https://learn.chatgpt.com/docs/permissions#file-access-limited-to-workspace) describes explicit root/temp deny rules, but configured rules alone did not establish enforcement in this campaign.
