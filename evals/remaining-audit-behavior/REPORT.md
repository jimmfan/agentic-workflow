# Remaining behavior audit

No Agent Workflow runtime source change is justified by this campaign.
The observed routing outcomes were mostly appropriate, and the meaningful cache repair was correct, but the intended execution isolation failed.
Six subject sessions completed; the seventh was interrupted; eight of the 15 planned invocations remain unexecuted.
All four hypothesis-level conclusions remain INCONCLUSIVE, with the unfinished skill matrix and lifecycle exercise infrastructure-blocked.

The base is fetched `origin/main` `1510e74540e3ebdb7c07966274fae7aeeac09386` (PR #32).
The [protocol](README.md), [frozen inputs and amendments](inputs.json), and [compact execution evidence](results.json) retain the design, conditions, selected tool outputs, diffs, usage and adjudication.
Runtime routing, skills, contracts, terminology, architecture and VERSION are unchanged.

## H1 — Source-grounded work may over-select Wayfinder

**Result: INCONCLUSIVE; observed outcomes support retaining the policy provisionally.**

Fixture/scenarios: `audit-source-answer`, `audit-source-continuation`, and `audit-plan` use a synthetic publisher's primary protocol and the existing disposable ARC configuration fixture.
Requests contain no expected route names or copied hard-signal wording.
The ordinary planning case asks for a configuration rename plan without file changes.

Observed execution: the bounded answer read `protocol.md`, correctly distinguished v2 account-scoped keys and 24-hour retention from v1, loaded no workflow resources and created no Wayfinder state.
The continuation case loaded Wayfinder, Research, routing and the state contract, then saved one map and F1 with the scoped source and reread the result.
The ordinary plan stayed Direct, correctly distinguished scale-set references from the unchanged namespace, ran the existing verifier and left project content unchanged.
These conclusions use commands, outputs and artifacts, not just route markers (`results.json`, attempts 1–3).

Deterministic evidence: controls reject unwanted state despite a Direct claim, missing positive continuation, and planning mutations.
The generic evaluator returned PASS for the two source cases and INCONCLUSIVE for the chat-only plan; manual inspection supplied the plan-content evidence.
Neither those checks nor the observed outcomes repair the failed isolation boundary.
The planned negative repeat did not run, and the positive case also contains a continuation signal, so it cannot isolate the causal effect of one sentence.

Practical consequence/source change: no over-selection was observed in the required three cases; no wording correction is justified.
Smallest follow-up: repeat this three-case set on a host with verified isolation, including the planned negative repeat.

## H2 — Debugging's transition may omit meaningful closing review

**Result: INCONCLUSIVE; classification C.**

Fixture/scenarios: `audit-diagnosis` and `audit-causal-fix` share a real account-cache regression whose existing two tests pass.
A shared cache returns alpha's total for beta; a fresh service returns beta's correct total.
`audit-trivial-fix` uses a separate one-value port mismatch.

Observed execution: diagnosis loaded Debugging, reproduced `shared=(12,12,1), fresh_beta=31`, identified the account-agnostic cache and changed no source.
The trivial case used Debugging and Verification, changed only `8008` to `8080`, and observed the existing check fail then pass; no implementation/review orchestration or durable state followed.
It loaded more instruction context than Direct would need, but no material harm from that overhead was demonstrated.

The meaningful case read Debugging and routing, repaired the cache by account, added a service-boundary regression, loaded Verification, ran three passing tests and inspected the diff.
No `implement` or Code Review resource read, reviewer invocation, or independent closing review was observed (`results.json`, attempt 6).
Its initial documented test command failed to launch; it did not execute the original symptom before editing.
The controller separately proved that the new test fails against the original source and passes against the repair, and that independently timed account expirations preserve cache reuse.
Those are additional outcome checks, not actions performed by the subject.

Deterministic evidence: controls establish the real defect and missed baseline coverage, reject source mutation during diagnosis, and verify the trivial causal repair.
The meaningful repair's independent before/after checks support code correctness.
The generic evaluator leaves diagnosis and meaningful completion INCONCLUSIVE where its snapshot/report checks lack outcome evidence.

Practical consequence/source change: a direct Debugging → Verification transition and absent independent closing review were observed, but no material code-coverage defect was demonstrated.
Failed isolation, launcher errors and unexercised reviewer capability prevent a clean attribution to instruction composition.
This is a specific follow-up target, not evidence that every debugging fix must invoke `implement`, and no Debugging/Implementation rewrite is justified here.
Smallest follow-up: repeat the meaningful fix with working diagnostics and independently usable reviewer capability, distinguishing causal investigation, build, closing review and acceptance checks.

## H3 — Actual skill selection has sparse live evidence

**Result: infrastructure-blocked; behavior INCONCLUSIVE.**

The discriminating matrix was authored and validated in the existing blind-scenario harness:

| Intent / scenario | Observed execution |
|---|---|
| Established integration coverage / `audit-integration` | Added three tests using real temporary files, kept production code unchanged and ran four passing tests; no TDD or other skill resource read. Controller interrupted before the final response after discovering the isolation failure. |
| Explicit test-first feature / `audit-test-first` | Unexecuted. |
| Interactive UI alternatives / `audit-ui` | Unexecuted. |
| CLI feasibility / `audit-cli` | Unexecuted. |
| Current external technical uncertainty / `audit-research` | Unexecuted; native web search was planned only for this case. |
| Mechanical rename / `audit-rename` | Unexecuted. |
| Settled design synthesis / `audit-spec` | Unexecuted. |
| Unexplained regression / `audit-diagnosis` | Debugging method observed as described above. |

Deterministic evidence: scenario validation and a metamorphic control prove that changing hidden route/outcome rubrics does not change delivered prompts.
They do not prove appropriate skill selection.
The interrupted integration run's raw evaluator FAIL reflects its missing final response/marker and terminated process; it is not a product FAIL.
Its partial integration and test evidence remains usable as a qualified observation.

Practical consequence/source change: integration coverage did not automatically induce TDD in the observed partial run, and regression diagnosis used an appropriate method.
The remaining six selection intents have no live result; no skill-description or routing change is justified.
Smallest follow-up: finish the interrupted integration case in a fresh session and execute the six unrun selection cases after isolation is restored.

## H4 — Answered-U# preservation, reconciliation and pruning

**Result: infrastructure-blocked; behavior INCONCLUSIVE.**

Fixture/scenario: `audit-resolution` seeds consequential U7, a map linking its implementation blocker, independent inventory work, deployment-only U8, unrelated project-owned bytes, and the designated `docs/retry-contract.md` destination.
The publisher's scoped answer is delivered as newly arrived authoritative evidence before the fresh resume.
The request asks only to resume and reconcile for the next implementer.
Following independent design review, the original-request-key requirement exists initially only in U7, so its transfer before deletion is discriminating.

Observed execution: none.
Recognition of the answer, preservation, readiness/reference reconciliation, U7 pruning, unrelated-state preservation, saved-result readback, and avoidance of invented authority/dependencies/records are all unobserved.

Deterministic evidence: controls reject deleting U7 while leaving an unusable retained artifact and reject loss of U8.
A correct final snapshot passes structural checks, but adding an unobserved temporal requirement yields INCONCLUSIVE; an explicitly observed premature-pruning/no-readback failure yields FAIL.
That temporal control manually supplies the existing `CheckResult` and tests verdict aggregation; it does not detect trace ordering.
A real lifecycle PASS still requires inspecting preservation before pruning and saved-result readback in an actual trace.

Practical consequence/source change: no lifecycle source change is justified.
Smallest follow-up: run this one frozen fresh-resume case on a verified host, then adjudicate all seven obligations against its ordered execution and retained result.
No real ARC-on-EKS project was accessed or modified.

## Infrastructure and evidence limits

Subjects requested Codex CLI 0.144.6, `gpt-5.6-sol`, medium reasoning, fresh homes/sessions, ignored personal configuration/rules, disabled apps/plugins/memories, native reviewer capability, restricted file access and denied tool network.
Exact requested settings, prompt-audit fingerprints and observed event counts/usage are retained per attempt.
The host exposed its five automatic system skills and the 15 installed curated skills; no personal skill or controller rubric was found in the audited prompt inputs.
Requested settings are not proof of enforcement.

The initial native read/patch/readback probe succeeded when the launcher ran outside the enclosing sandbox with the subject sandbox enabled.
Early Git-runtime and Python-launcher failures were recovered within subjects; adapter amendments and their limits are recorded.
Subsequent standalone probes and two native tool probes nevertheless read a synthetic sibling sentinel despite intended deny rules, including an explicit campaign-directory deny.
The root cause of that configuration/enforcement discrepancy remains undetermined; this is a demonstrated campaign isolation failure, not a general Codex security conclusion.
No sibling/rubric reads were observed in the seven subject traces, but fully isolated evidence cannot be claimed.

The controller stopped the matrix and retained the interrupted integration attempt without replacing it.
The adapter now checks synthetic outside-data and credential canaries before copying credentials or launching a model.
Its actual preflight returned `outside-read-permitted` and stopped with exit 2; no model log or credential copy was created by that check.
All temporary credential copies from earlier invocations were removed.
Three model infrastructure probes are separate from the seven subject attempts; interrupted integration usage remains unavailable.
Raw traces, logs and disposable workspaces remain outside Git under `/private/tmp/remaining-audit-behavior-live`; compact evidence includes selected outputs and trace hashes.

The prior map-authoring campaign remains infrastructure-blocked and behaviorally INCONCLUSIVE.
Separate manual ARC Create/Resume/Correct observations are not controlled comparative evidence for this campaign.

## Verification and independent review

Focused controls: PASS, 11 tests; existing behavior-harness controls: PASS, 19 tests; all 53 scenarios validate.
Final required gates from [the verification guide](../../docs/verification.md#maintainer-and-ci-gate) passed using `uv run --locked`: Ruff format/check, package verification with tests (182), evaluation-tooling tests (65), and wheel smoke (2), plus `git diff --check`.
The wheel build was initially blocked by PyPI DNS access in the enclosing sandbox; its network-enabled rerun passed.
Hosted CI and other platforms were not exercised.

### Standards review

Independent design and closing review covered the scenarios, fixtures, controls, adapter, protocol, frozen inputs, retained evidence and effort map, including raw trace/hash checks, the causal repair and interrupted integration evidence, and isolation probes.
The design review corrected an overly strict test-before-fix criterion: the meaningful debugging repair may demonstrate its regression test against the original source after authoring it.
Closing review found one stale map statement that still described a completed isolation probe as pending; that finding was corrected and independently rechecked.
Final Standards result: no remaining findings in reviewed scope.
The reviewer did not independently rerun the deterministic gates.

### Spec review

Independent design and closing review assessed coverage of the four hypotheses, blind prompts, behavior-based criteria, source-change restraint, raw trace references and evidence qualifications.
It corrected the H2 criterion above and made H4 preservation discriminating before execution by removing a duplicated requirement from the destination artifact.
It also identified the stale map statement; the correction was independently rechecked.
Final Spec result: no remaining findings; H2 classification C and the explicitly incomplete, infrastructure-limited conclusions are supported.
The reviewer did not execute subject sessions or establish behavioral PASS for any hypothesis.

## Prioritized recommendation

1. **Change now:** retain the evaluation adapter's demonstrated fail-closed correction; restore and verify execution isolation before spending further subject invocations.
2. **Retain current behavior:** make no runtime instruction changes from this campaign; the observed H1 outcomes and correct bounded repair provide no basis for a preemptive rewrite.
3. **Gather more evidence:** prioritize H4's unexecuted lifecycle and a clean meaningful-fix/review transition, then finish the small skill matrix and H1 repeat.
