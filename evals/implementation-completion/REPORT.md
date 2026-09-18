# Implementation completion findings

**Defer merge: accepted byte-verification evidence is still unnecessarily rechecked, and the implementation parent left an undisclosed temporary directory.**
The original reviewer mutation remains a failed observation; focused retests provide bounded positive evidence for its correction.
The completed comparison demonstrated no behavioral improvement over baseline.
This evidence cleanup changes representation only: no new live evaluations, replaced samples or changed grades.

## Problem and instruction correction

The correction makes consequential completion obligations explicit across implementation, review and acceptance verification.
A direct `implement` invocation must reach the existing outer completion step after building and review.
Existing project rules that govern this work and maintaining-artifact references must reach reviewers and Verification.
An unchanged artifact can violate an in-scope requirement even when it is outside the implementation diff.

| Responsibility | Owning layer and boundary |
|---|---|
| Completion | `workflow-implementation` owns the outer acceptance step; routing and `implement` provide short handoffs without repeating the build/review loop. |
| Findings | Code Review reports concrete unmet requirements and coverage, read-only, including required unchanged artifacts within scope. |
| Evidence | Verification matches criteria to existing evidence and checks uncovered obligations. |
| State maintenance | The coordinator reassesses relevance and reconciles authorized affected state under the existing routing threshold. |

Sufficient existing content satisfies an obligation without rewriting it or creating another record.
Topic overlap, an unrelated link or artifact presence alone does not require an update or global effort search.
Explicit comparison exclusions remain coverage limits; reviewers must not inspect excluded artifacts to manufacture findings.
The correction preserves authorization, ownership and terminology boundaries.
It adds no execution framework or new canonical term.

The focused runtime correction then addressed two supported procedural weaknesses.
Verification previously selected additional checks before resolving existing evidence coverage; it now maps criteria to evidence first and requires a concrete gap before choosing any check, including a narrow check.
Code Review carries the read-only boundary into each delegation, explicitly covers temporary setup/cleanup, and returns genuinely blocked observations to the coordinator instead of repairing the environment itself.
These mitigations address observed execution paths; neither is a proven explanation of the model's reasoning.

## Revisions and execution validity

Full revisions and exact configuration are maintained once in [compact results](results.json).
The [protocol](README.md) owns fixture preparation, requests/check references, execution gates and grading rules.

| Evidence group | Baseline | Runtime candidate | Scope |
|---|---|---|---|
| Two interrupted campaigns | `4b4ac40` | `b6ca58c` | Partial observations only; neither establishes a completed comparison. |
| Completed comparison | `4b4ac40` | `67c0ef5` | Five paired cases, two native preflights and two fresh readers. |
| Focused follow-up | No new baseline | `4a90232` | Five candidate cases, reusing unaffected comparison evidence. |

The focused follow-up started from checkout-policy head `72ccda1`; its evidence was delivered at `1c6d139`.
Later head `884d0cd` removed one redundant Git-environment reminder from Code Review, retaining the explicit `git --no-optional-locks status --short` instruction.
That one-line deletion has deterministic package validation but no new live evaluation.
The latest live-evaluated runtime therefore remains `4a90232`, not the evidence-cleanup head.
The current PR retains the existing unreleased version 0.34.4.

Subjects used `gpt-5.6-sol / medium`, Codex CLI 0.144.6 and the recorded macOS host, with fresh sessions/homes, disabled personal configuration, no command network, and bounded time/output.
Write-capable implementation and top-level read-only scenarios used the respective project permissions.
The exposed native delegation interface provided no per-child permission selector; children inherited their parent's live permissions.
Thus reviewers delegated by implementation had write capability, although their instructions prohibited writes.
No per-reviewer OS enforcement is claimed for those sessions.

## Launcher failures and repairs

The earlier campaigns are retained separately, including every executed parent and nested session's observed usage.
Their unrun cases are not failures or passes.

| Campaign | Material failure and retained limit |
|---|---|
| Initial: three parents, no children | Preflights omitted Git/nested execution. Native Git could not access the selected Apple developer directory; baseline used Ruby to restore files, then quota ended the run before review/acceptance. Git metadata was incompletely observed. |
| Second: five parents, eight children | First writer hit denied personal Git configuration; one targeted retry passed after disabling it. Baseline restored/reviewed/reconciled, but explicit outer completion was unobserved. Candidate Ruby/Perl dependency denials interrupted review and acceptance. |

The launcher now grants only the required Apple developer directory and system Perl/Ruby reads, and isolates Git configuration without granting personal-config access.
Deterministic subprocess controls cover cleanup when monitoring raises and when a process-group leader exits before its child.
The second campaign's frozen monitor missed interpreter failures; coordinator termination occurred about 60 seconds after the first error, so that run did not prove automatic stopping.
The signatures were repaired afterward and checked against captured evidence before any further model call.
Actual non-model sandbox comparisons reproduced the old interpreter failures and passed with the repaired profile while protected-read and read-only-write denials remained intact.
A controlled real sandbox failure exercised monitor cleanup of an owned child after its leader exited.
Native writer/reader preflights then passed Git, interpreter, command/patch and protected-read probes in both parents and four nested reviewers.
Writer probes changed only their six designated files; read-only project and Git snapshots stayed unchanged.
These explicitly authorized preflight writes are not reviewer-compliance samples.

## Completed behavioral comparison

All **14 planned parent sessions and 21 nested agents completed**, with no infrastructure retries, revised candidate or replacement sample.
The session records preserve condition order and distinguish preflight work from scenario behavior.

| Frozen case | Baseline | Candidate |
|---|---|---|
| Primary completion | PASS | PASS |
| Review-only detection/handoff | PASS | PASS |
| Already-sufficient evidence reuse | FAIL | FAIL |
| Unrelated tutorial | PASS | PASS, with additional reviewer mutation |
| Limited read-only comparison | PASS | PASS |
| Fresh reader | PASS | PASS |

Both primary subjects restored exact historical bytes and updated only the existing recovery map.
They retained source revision, path, fallback purpose, pending engine and verification limits, completed two review axes and performed acceptance checks.
Baseline delegated acceptance to another native agent; candidate resumed outer completion itself.
Neither repeated the build or review pair; both repeated narrow JSON/blob checks, which the frozen primary rubric distinguishes from repeating that loop.
Primary PASS therefore does not establish general evidence reuse.

Both review-only subjects identified the unchanged stale availability claim, governing policy and consequence and returned the finding without project/Git changes.
Both limited-read subjects and reviewers respected the permitted comparison and stated excluded obligations as limits.
Both tutorial subjects preserved original configuration/recovery artifacts and created the requested independent example without inventing a fallback obligation.
Both fresh readers recovered revision, path, purpose, pending dependency and verification limits from saved files alone, without Git history, validation execution or project mutation.
Their answers recover recorded evidence, not proof of successful image export.

Both sufficient-evidence subjects read accepted prior byte/review evidence and the statement that no files had changed, then recomputed current/historical hashes and compared the same bytes without identifying a gap.
Baseline used `cmp`; candidate used `git diff --quiet` against the source.
Preserving files and reusing prior review do not clear the separate failed byte-reuse criterion.
The existing rule already required evidence reuse; this is observed noncompliance, not evidence that another prohibition was missing.

In the candidate tutorial, the Standards child successfully created and removed `.review-tmp` after Git observations had already succeeded with cache warnings.
The child had read the governing review instructions and inherited the parent's write-capable sandbox and prior temporary-directory setup.
The temporary mutation violated read-only review despite an unchanged final snapshot; permission did not supply authorization.
It remains a separate reviewer-boundary FAIL without retroactively changing the frozen tutorial grade.
No corresponding reviewer write was observed in the baseline tutorial.
Context imitation is a hypothesis, not an established model-level cause.

Four of five paired cases passed in each condition and one failed in each; **no comparative improvement was demonstrated**.
The additional candidate-only reviewer mutation is also preserved without attributing causality to the instruction change.

## Focused behavioral follow-up

All **five planned parent sessions and six nested reviewers completed**, without infrastructure retries or replacement samples.
The three reserved infrastructure-recovery attempts were unused.
Each workspace passed fresh non-model isolation/Git/JSON probes; native preflight evidence was reused only for the unchanged execution configuration.
Credentials were removed after every run.

| Case | Result and scope |
|---|---|
| Already sufficient | FAIL: explicitly acknowledged accepted byte coverage, then recomputed both hashes without a gap. |
| Invalidated evidence | PASS: detected quality 80 versus historical 90, reported incomplete restoration, reused unaffected review and preserved project/Git state. |
| Tutorial implementation | PASS: exact example copy and preserved recovery artifacts; both delegated reviewers issued no explicit mutating commands. |
| Primary implementation | Frozen criteria PASS: exact restoration, map reconciliation, two review axes and outer acceptance; additional parent defects below. |
| Limited comparison | PASS: parent and both reviewers respected permitted reads, comparison semantics and exclusions, with unchanged state. |

Evidence sufficiency reached the deciding agent; reordered verification steps did not prevent the repetition.
Independent prior review found no further specific missing instruction in that trace.
Another synonymous prohibition or an unchanged rerun is not a justified repair.
The evidence-reuse finding remains unresolved and unaccepted.

Both tutorial reviewers and both primary reviewers inherited workspace-write permissions and nevertheless made no explicit mutating commands, native patches or successful temporary-directory changes.
These four observations cover the implementation-to-review path, not merely an externally read-only scenario.
Git/xcrun attempted incidental cache writes that were denied while required reads succeeded; these differ from reviewer-issued environment-repair commands.
The original successful `mkdir`/`rmdir` remains a failure.
The corrected reviewer guidance has bounded positive retest evidence, without causal isolation, universal reliability or OS enforcement claims.

The primary parent left an empty `.tmp` directory and omitted it from its final report.
The filesystem snapshot detected this additional change; Git status alone did not.
The parent also repeated narrow checks and reran a script after asserting an incorrect expanded HEAD, then corrected that value from Git.
That was an ordinary in-session check error, not infrastructure recovery.
These observations are not reviewer writes, do not alter the frozen primary grade, and remain unaccepted limits on completion and evidence reuse.
No unrelated existing artifact or Git metadata changed.

## Deterministic coverage and delivery verification

The 17 photo-export controls retain real local Git/filesystem observations and constructed-answer checks at review detection, coordinator handoff and completion seams.
They cover implicit relevance, stale unchanged plans, sufficient state, unrelated artifacts, read-only requests, limited scope, byte integrity and symlink rejection.
The invalidated-evidence fixture protects legitimate re-verification when a later change invalidates accepted evidence.
Permission and monitor tests discriminate infrastructure failures, expected denials and ordinary tool errors.
They do not establish model compliance or live photo-export success.

Prior delivery passed 224 package tests, 78 evaluation-tooling tests, two wheel checks, Ruff format/lint and all 57 scenario definitions; the focused controls are included in the package gate.
The cleanup passed those gates again, including all 17 focused controls, plus JSON references, historical-result preservation, Markdown links and diff hygiene.
The preservation audit reconciled all 27 parent sessions and 35 native children across the four campaigns; exact requests, grades, counters, elapsed times and changed-path inventories match the prior record.
One independent cleanup review closed with zero remaining actionable evidence-integrity or storage-contract findings.
It caught an overstatement of the initial reader snapshot; the corrected record marks the full inventory unavailable and retains only the observed unchanged probe content.
This review approves evidence representation, not the unresolved subject behavior.
Earlier runtime/harness reviews remain applicable to unchanged source.
Hosted CI is separate delivery evidence reported on PR #48.

## Evidence retention and remaining limits

The compact record retains each campaign separately, exact scenario requests once, execution configuration, per-session counters, paired/reader references and material anomalies.
Nested usage subtracts inherited parent counters; cached input is part of input and reasoning output is part of output.
Controller and delivery-review usage is excluded; interrupted final requests may be unaccounted.
Child elapsed times, aggregate tool counts and actual route summaries were not retained in the previous compact data and remain unavailable rather than inferred.
Encrypted delegation-message bodies remain unavailable; observed fork/spawn behavior, settings, tool activity and saved state support the reported findings.

Git history at `884d0cd` preserves the expanded campaign structures, previous adjudications, validation/review chronology and raw-artifact fingerprints removed by compaction.
Raw traces, manifests, controller scripts and copied workspaces remain local execution exhaust outside Git; their continued availability is not guaranteed.
The retained protocol and fixtures support reconstructing the evaluation design, not bit-identical replay without those artifacts.
This cleanup removes redundant narratives and unusable local paths without altering runtime instructions, fixture semantics, tests or observed results.

**Merge recommendation: defer.**
Evidence reuse is still failed, and the parent's cleanup/disclosure defect is not accepted.
The reviewer boundary has positive bounded follow-up evidence while its original failure stays visible.
Further correction requires materially different supporting evidence within the existing thin-layer scope; neither a broader runtime nor blind retries are justified by these results.
No access, quota or infrastructure blocker prevented the completed follow-up or this evidence cleanup.
