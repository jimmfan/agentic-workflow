# Map-authoring verification

The authored change and deterministic gate pass; live map-authoring behavior is INCONCLUSIVE because the only subject invocation was infrastructure-blocked.
No live map was produced, and there is no observed general or comparative improvement claim.

## Change and boundary

The state contract maintains the new default order, visible honest blocker assessment, optional nested Ownership, direct versus source-linked assignments, scoped unknown ownership, and existing-layout preservation.
The skill retains navigation and specialist method, with formatting delegated to the contract.
Conflicting current documentation is reconciled; routing, terminology, architecture decisions, identifiers, lifecycle, VERSION and distribution inventory are unchanged.
The domain-language effort retains unrelated coherence-review work.
Historical fixtures, persistence campaign inputs/reports/results and all other efforts are unchanged.

## Deterministic verification

PASS: `uv run --locked ruff format --check .`, `uv run --locked ruff check .`, `uv run --locked python agent_workflow/verify_package.py --tests`, `uv run --locked python -m unittest discover -s evals/tests -p 'test_*.py' -v`, `uv run --locked python tests/wheel_smoke.py`, and `git diff --check`.
A temporary `UV_CACHE_DIR=/tmp/map-authoring-uv-cache` was used because the default host cache was not writable; no global setting changed.
The package suite ran 151 tests, the evaluation suite 65 tests, and wheel smoke 2 tests.
Focused map-authoring evaluator tests also pass.
Hosted CI, other platforms and authenticated publication beyond the requested Git push were not exercised locally.

## Evaluator controls

PASS: controlled candidate maps distinguish default ordering/visible assessment, direct assignments and source-linked orientation, lost provider/decision-maker, erased unknowns, invented authority/approval, stale mirrored maintenance, old endpoint blocking, false absence and unnecessary alternate-layout conversion.
The scenarios use the existing evaluator; no parser, normalization engine or evaluation harness was added.
Their narrow textual signals are not semantic correctness evidence; the [predeclared rubric](README.md#frozen-inputs-and-expected-outcomes) requires actual artifact, reference and action inspection for live conclusions.

## Live observations

Settings: `gpt-5.6-sol`, medium reasoning, Codex CLI 0.144.6, isolated fresh home, ignored user configuration/rules, no tool network, no apps/plugins/memory/delegation, approval policy `never`, workspace-only writes and minimal filesystem reads.
Exactly one subject invocation ran; no automatic retries.
It completed in 40.27 seconds with process exit 0, but all four attempted tool calls failed before command execution with `sandbox_apply: Operation not permitted`, including a basic `pwd` probe.
The response correctly reported inability to read or write; before/after filesystem snapshots are identical.
This is infrastructure-blocked execution and INCONCLUSIVE product behavior, not PASS because the process exited successfully and not a demonstrated Wayfinder regression.

The standalone non-model isolation probe passed both writer and reader checks.
An initial prompt audit rejected a disposable consumer placed beneath the repository before any subject invocation; the outside-repository setup subsequently passed the same audit.
That correction changed only test placement, without relaxing restrictions.
The host's live tool sandbox nevertheless failed.
No credentials were changed globally, exposed to subject tools or retained in evidence; the isolated credential copy was removed after the run.

Correct, Read and Resume are unexecuted.
There was no saved Create map to transfer; no manually repaired state or ideal correction fixture substituted for the missing result.
No further subject invocations were spent after isolation proved unavailable in the live host.
The stage inputs and expected outcomes remain available for a separately authorized future run when safe host execution works.

Retained evidence: [result and snapshots](results/create.json), [public events](results/create-events.jsonl), [actual attempted tool calls and errors](results/create-actions.json), and [successful prompt audit](results/create-prompt-input.json).
Complete disposable state and original rollout remain locally at `/private/tmp/wayfinder-map-authoring-smoke/create`; the initial failed audit remains under ignored `evals/artifacts/map-authoring/create/raw`.
The event stream reports 59,408 input tokens, 46,592 cached input tokens and 794 output tokens, including 327 reasoning output tokens.
These are observed usage counters, not a comparative cost claim.

## Closing review

### Standards

PASS — 0 findings.
The independent reviewer found no documented-standard violations or actionable baseline code smells.
Presentation stays in the state contract, navigation stays in the skill, authority distinctions remain intact, and repeated synthetic fixture documents are appropriate isolated inputs.

### Spec

PASS — 0 material findings.
The independent reviewer found the authoring requirements implemented within scope, with PR #30 preservation intact and the unavailable live stages disclosed as required.
This review does not convert unavailable live observations into compliance evidence.

## Integration acceptance

| Boundary | Result | Evidence |
|---|---|---|
| Default authoring, visible assessment and ownership contract | PASS | Authored diff, focused evaluator controls and closing Spec review |
| Existing-map recognition, identifiers, reconciliation and scoped acceptance | PASS | Recognition preamble and entire Current knowledge/reconciliation tail match the base byte-for-byte; package gate passes |
| Distribution, lifecycle and project-data protection | PASS | Package and wheel gates; VERSION, inventory, routing, terminology, other efforts and persistence campaign unchanged |
| Fresh-session Create / Correct / Read / Resume behavior | INCONCLUSIVE | Create infrastructure-blocked; remaining stages unexecuted |
| Closing Standards and Spec review | PASS | Independent parallel reviews, 0 findings on each axis |

The final package/link verification passed after evidence and documentation were added.
The focused evaluator suite passed after its last adjustment; the full gate evidence above is reused rather than repeating covered checks.

## Readiness

The change is suitable for code review with deterministic checks passing.
Live acceptance is withheld: meaningful ownership, correction, fresh read and alternate-layout behavior have not been observed in this smoke.
Do not claim the full requested verification is complete or merge-ready without resolving or explicitly accepting this named evidence gap.

## Correction-control follow-up

The follow-up starts from reviewed branch HEAD `4a139402` and changes only the correction scenario, its disposable evaluator controls, and this note.
Before the fix, the new stale-context negative failed its regression assertion because the evaluator returned no failures even though `context.md` still said the endpoint was unavailable and integration could not proceed.
After the fix, two fixture-specific context checks require the availability fact in a retained file and reject the obsolete unavailability/blocking claim without requiring an exact sentence.
The stale-context control now fails only those context assertions and their dependent task-completion check; the corrected positive has no evaluator failures.
Missing context, erased availability, and a retained blocking claim are also rejected, and every candidate starts from a fresh disposable fixture copy.
Existing controls and checked-in starting fixtures are unchanged in meaning; corrected copies preserve provider/maintainer assignments, production restrictions, constraints, and unknowns.
Passing these controls does not establish live behavior or require every broader evaluator verdict to be PASS rather than INCONCLUSIVE.

Newly executed checks: focused controls PASS (3 tests), Ruff format/check PASS, package gate PASS (151 tests), wheel smoke PASS (2 tests), and `git diff --check` PASS.
The evaluation suite ran 65 tests and FAILED one: `test_no_raw_execution_exhaust_is_tracked_under_evals` rejects the tracked `evals/map-authoring/results/create-events.jsonl`.
That evidence file and the storage test are unchanged from `4a139402`; historical evidence was preserved as requested, so the current full gate is not clean.
The scoped diff review found no material correction-control issues.
No live agents were rerun: authoring, correction, and continuation remain unverified, and the recorded infrastructure-blocked / behavior-INCONCLUSIVE result and unaccepted evidence gap remain unchanged.
