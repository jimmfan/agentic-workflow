# Wayfinder question resolution verification

The bounded implementation starts from fresh `origin/main` `96ec2fbd` and changes optional U# storage and human-review integration.
It makes no comparative quality or reliability claim.
The frozen persistence and PR #33 protocols, manifests, reports, and outcomes remain unchanged; no baseline interaction or comparison campaign was run.

## Evidence boundaries

| Boundary | Evidence and limitation |
|---|---|
| Optional ledger, ID/anchor syntax, neighboring records and unrecognized content | Updated active fixtures, `test_wayfinder_state.py`, and section identity controls in `test_question_review_controls.py`; literal fixture validation, not agent allocation or editing execution. |
| Answered middle U2, unrelated U1, accepted but unresolved U3 | The new synthetic parcel-review fixture and positive/negative snapshot controls preserve neighbors and expose dangling links, lost qualifications, and stale whole-ledger replacement. |
| Map-only and linked-artifact question discovery, mixed prerequisites, proactive input, deferral/revisit, interpretation, unavailable Grilling, standalone Grilling | Fixture-specific candidate responses exercise the existing evaluator, accepting paraphrases and rejecting selected counterexamples; not a general semantic grader or evidence of actual routing. |
| Review authorization and unsupported artifacts | Observed disposable mutations fail the read-only boundary, including skill Markdown implementation and premature ticket creation. |
| PR #33 reconciliation check | Active audit-resolution fixture now prunes U7 from a ledger while a section identity assertion preserves U8; its historical evidence stays frozen. |
| Live ordering, conversion/no-overwrite behavior, interruption and fresh continuation | INCONCLUSIVE; current execution preflight is infrastructure-blocked, so no subject interaction or fresh reader ran. |

The current preflight used the unchanged PR #33 adapter and a disposable installed consumer.
It returned exit 71: `sandbox-exec: sandbox_apply: Operation not permitted`.
The adapter reported `infrastructure-blocked`, copied no authentication, launched no model, and confirmed no credential copy remained.
This is an execution failure, not a product behavior failure or the earlier sibling-read observation repeated successfully.
No current native-tool denial probe ran because the prerequisite failed.
Raw local evidence is `/private/tmp/wayfinder-question-isolation/subject-twirq92p/isolation.json` and its adjacent `invocation.json`.
Those local temporary files are not portable repository evidence; the observed result above is the retained summary.

No verified operator remedy is known for the sandbox-creation failure in this session.
Before any live subject, an operator must establish an effective execution-isolation boundary, obtain a successful current preflight, and then demonstrate native-tool denial of synthetic sibling and credential canaries under the same permissions.
Do not bypass the guard, loosen subject permissions, expose real data, or copy credentials for a behavioral run before those gates succeed.
Isolation repair is outside this task's authorization.

## Bounded smoke procedure when isolation is available

Use a disposable copy of [the parcel-review fixture](../../tests/fixtures/wayfinder-question-review/README.md), install the candidate framework there, and preserve raw events and diffs outside both source and subject trees.
Use the existing [adapter](../remaining-audit-behavior/codex_subject.py) preflight with `--preflight-only --output-root /private/tmp/wayfinder-question-isolation` from that installed disposable consumer.
Run the native-tool denial probe only after preflight succeeds, as required by the [existing execution boundary](../remaining-audit-behavior/README.md#execution-boundary-amendment).
Keep model `gpt-5.6-sol`, medium reasoning, host, permissions, task meaning, and installed candidate fixed through one sequence; do not retry or tune until green.
Use the host's native session continuation for replies, not a new conversation engine or a prompt containing preanswered questions.

1. Ask: “Use Wayfinder to review the parcel-review effort's unresolved questions with me and record our conclusions in its map and docs/pilot.md. You may reconcile affected question sections and references. Do not implement resulting changes.”
   Inspect the actual questions before replying.
   Exposure and support contact are answerable; support hours depend on exposure, capacity needs publisher evidence, and naming is deferred.
   Expect useful context and tradeoffs, not an exact question count or wording.
2. Only after the corresponding questions arrive, supply: “As project owner, I commit staff-only exposure for at most ten accounts, conditional on manual rollback being available. Use email for the support contact. Capacity acceptance still covers only that bounded pilot; production sizing remains blocked. Do not implement or deploy.”
   Do not supply an answer to a question the subject has not asked; record unexpected ordering or omission as evidence.
3. Inspect actual preservation in docs/pilot.md, affected map relationships and links, readback before U2 pruning, retention of U1/U3 qualifications and unrelated bytes, and the next appropriate support-hours question.
   If that question is asked, reply: “Use office hours for the staff-only pilot. This authorizes recording the choice only.”
   Preserve partial or interrupted output; do not repair the consumer for the subject.
4. Start one fresh session on the actual resulting consumer without the previous conversation.
   Ask: “Read the parcel-review effort and explain the current choices, unresolved conditions, and what work may proceed. Do not change files.”
   Check retrievability of cap, condition, authority, support choice, deferred naming, unresolved capacity, and absence of implementation/deployment authorization.

Inspect native events for map-first loading, actual questions before scripted replies, current affected reads before writes, preserving results and repairing references before pruning, and final saved-result reads.
Snapshot PASS cannot establish these temporal dimensions: missing observation is INCONCLUSIVE, observed violation is FAIL, and complete bounded evidence is PASS without implying reliability gains.
If interrupted, keep actual saved state and classify missing evidence; never manufacture a completed round or use manual repair to conceal loss.

## Conversion and delivery scope

Eight affected old U# files in seven active synthetic fixtures were explicitly converted with unchanged IDs, content, sources, and qualifications; nested headings became subsections and known links now target ledger anchors.
Targets and source identity were checked before individual source-file removal; empty old directories were not recursively deleted.
The fixture link checks cover repaired retrieval.
No U# files were found in the three current source effort directories assessed for a semantic match; they were not repurposed.
Old-format negative controls and frozen evidence remain old-format intentionally and are not current runtime representations.
No downstream consumer was assessed or migrated, so absence of a downstream ledger establishes nothing about its questions.

The requested branch is `origin/feat/wayfinder-question-resolution`.
VERSION remains `0.31.0`; no release, tag, merge, or publication decision is made here.

## Executed checks

All commands used the documented locked environment, with `UV_CACHE_DIR=/private/tmp/wayfinder-question-uv-cache` because the host sandbox prevented access to the default cache.

- PASS: `uv run --locked ruff format --check .` and `uv run --locked ruff check .`.
- PASS: `uv run --locked python agent_workflow/verify_package.py --tests` — 188 tests, including disposable distribution and lifecycle checks.
- PASS: `uv run --locked python -m unittest discover -s evals/tests -p 'test_*.py' -v` — 65 tests.
- PASS: `uv run --locked python tests/wheel_smoke.py` — two tests, with isolated build/install and local install/status/update/remove coverage.
- PASS: `uv run --locked python tests/behavior.py validate` — 53 scenarios.
- PASS: final focused `test_wayfinder_state.py` — nine tests, including the subsequently added unrecognized-heading regression; all eight active fixture ledgers and their fixture-local links were also checked directly.
- PASS: focused question-review controls — seven tests, including pruning-only and preamble-only negative controls.
- PASS: `git diff --check`.
- INCONCLUSIVE / infrastructure-blocked: live interaction, native-tool denial, interrupted-session and fresh-reader behavior, and live pre-write/pruning order.

The section snapshot addition initially exposed a tuple/list mismatch through the existing persistence checkpoint tests; JSON-stable dictionaries fixed it without changing frozen packets or weakening the checkpoint guard.
Final fixture validation also caught an overly broad test-helper match for an unrecognized heading beginning with “U”; the corrected identity-like prefix preserves such project-owned headings.
These are evaluator integration corrections, not observed live-agent improvements.
Hosted CI platforms were not run locally.

## Standards

Independent review covered every attributed tracked and new file and subsequent affected deltas.
The stale effort-map preflight statement was corrected to the observed failure and remaining delivery scope.
No Standards findings remain.

## Spec

Independent review found and verified corrections for overbroad effort-path confinement and a ledger predicate that counted pruning/preamble changes as newly recorded uncertainty.
The contract now confines only Wayfinder state paths, and the evaluator compares surviving question sections.
No Spec findings remain; unavailable live evidence retains its explicit limitation.

Review summary: Standards 0 remaining findings; Spec 0 remaining findings.
