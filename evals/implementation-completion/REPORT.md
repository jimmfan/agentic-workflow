# Implementation completion findings

The instruction correction makes required completion obligations explicit across implementation, review and acceptance verification.
Behavioral improvement remains INCONCLUSIVE.
The first campaign stopped during its baseline primary; the separately authorized new campaign completed that case but stopped during the candidate primary on different sandbox runtime failures.
Neither campaign produced a completed pair.

## Owning boundaries

| Gap | Correction |
|---|---|
| The inner implementation method did not explicitly return direct invocations to outer completion. | Return meaningful work to the outer acceptance step without repeating covered build or review work. |
| Maintaining references and project policies were not explicit throughout reviewer handoffs. | Carry governing inputs and relevant maintaining-artifact references through implementation, both reviewers and Verification. |
| Review guidance left required updates to unchanged artifacts implicit. | Identify concrete unmet requirements even outside the diff, while preserving read-only operation and explicit comparison limits. |
| Completion reconciliation only named efforts selected earlier. | The coordinator reassesses new findings and relevant references under the existing threshold, including a clearly relevant effort missed earlier. |

The coordinator retains routing and authorized state maintenance.
Verification checks acceptance and supplies uncovered evidence; Code Review reports findings read-only.
Existing sufficient content or references satisfy the obligation without a rewrite, new record, global effort search or repeated review.
The accepted ownership and authorization decisions remain unchanged.

Completion mechanics are maintained in `workflow-implementation`'s Verify the result step; routing and `implement` carry short handoffs to that owner.
Direct invocation resumes at that step without re-entering the build loop.
Unchanged-artifact reads must support an in-scope requirement; presence, topic overlap and unrelated links do not create update obligations.
Verification reuses adequate review evidence and checks only uncovered obligations.

## Regression coverage

The fictional photo editor supplies exact configuration snapshots and test-generated historical Git commits.
Controls cover recovery, implicit relevance, an unchanged stale plan absent from the diff, finding handoff, saved reconciliation and verification evidence.
They include ambiguous intent, sufficient state, unrelated work, read-only requests and limited review scope.
Copy integrity and user-reported output quality remain separate from independently tested image output.

These are deterministic evaluator controls with real local Git/file observations and constructed candidate responses.
They establish neither agent behavior nor whether acceptance verification was executed in any unobserved session.
The [protocol](README.md) owns the detailed boundaries and evidence limits.

## Validation

Validation passed: 17 focused controls, 224 package tests, 65 evaluation-tooling tests, two wheel checks, Ruff format/lint, scenario validation and `git diff --check`.
The focused instruction cleanup reran these checks on Linux with Python 3.12.14; all four edited skills also passed skill validation.
The existing ownership tests remain unchanged and pass in the package gate.
Generated distributions were inspected, with the packaged regression tests matching reviewed source.
The instruction correction and supporting harness were preserved without behavioral weakening.
Detailed counts and evidence limits are recorded in [results.json](results.json).
Those counts describe the earlier instruction correction and cleanup, not live behavior.
The follow-up validation and execution limits are recorded below.

## Standards

The sanitized baseline received independent review of all 26 proposed paths, including privacy, narrative meaning, generated fixture data and preservation of unrelated references, with zero findings.
Scoped follow-up review covered all seven cleanup files in full context, including instruction ownership, scope and loading boundaries, terminology and evidence reuse, with zero findings.
The later evaluation follow-up received an independent Standards review of all six pending paths, controller scripts and observed execution evidence: zero actionable findings or material design smells.

## Spec

The baseline review covered required behavior and ownership boundaries, including source dependencies and the separate evaluator controls, with zero findings.
Scoped follow-up review covered the seven-file cleanup and found no missing requirement, semantic regression, scope expansion or conflicting ownership/loading instruction.
The later evaluation follow-up received an independent Spec review of all six pending paths and actual requests, traces, fingerprints and diagnostic records: zero actionable findings.
The review confirmed that incomplete preflight coverage, delayed stop and unrun cases are disclosed, and that the behavioral conclusion remains INCONCLUSIVE.
Delivery reviewers did not run live evaluations; final validation records and publication checks remain with the coordinator.

Review summary: Standards 0 findings; Spec 0 findings.

## Bounded comparison follow-up

The frozen baseline is `4b4ac408cbc4543e2e7a433f52c03a48f7044ca7`; the candidate is `b6ca58c2f8f343e635c53f731ef53d628faf6eaa`.
Neither differed from the supplied revision.
Ten disposable photo-export fixtures, identical corresponding requests and grading expectations were prepared before launch, using the existing historical-Git controls.
The [protocol](README.md#frozen-behavioral-comparison) and [compact results](results.json) retain the design, exact requests, fingerprints, per-session usage and exclusions.
The intended comparison covers the combined branch correction; it cannot isolate the cleanup commit.

| Case | Baseline | Candidate |
|---|---|---|
| Direct `implement` | Infrastructure-blocked; product result INCONCLUSIVE | Not run |
| Review-only detection and handoff | Not run | Not run |
| Already-sufficient state and evidence | Not run | Not run |
| Unrelated effort | Not run | Not run |
| Limited read-only review | Not run | Not run |
| Fresh reader after completed primary | Not run; primary incomplete | Not run; primary unrun |

Two native preflight sessions ran, followed by one scenario session; no fresh-reader or nested-reviewer session ran.
The writer trace shows an allowed project read, denied evaluator/sibling reads, a successful native patch and readback.
The independent reader session shows allowed reads, denied outside reads, command-write denial, native patch rejection and unchanged file content.
Both loaded the expected synthetic project instructions and frozen candidate skills in fresh homes; credentials were removed afterward.
These observations cover the exercised tools, not every capability required by the campaign.
In particular, the preflights omitted Git and nested reviewer execution.

The first baseline scenario failed to run `/usr/bin/git`: the restricted profile hid `/Library/Developer/CommandLineTools`, causing an `xcrun` invalid-developer-path error.
The subject inspected Git objects with Ruby, restored the exact historical configuration and updated the existing recovery map with the source revision, restored path, pending engine and verification limits.
Only the configuration and map changed among snapshotted project files, and `HEAD` remained unchanged; Git metadata was not comprehensively snapshotted.
Those partial observations neither establish completed acceptance nor show an improvement over the candidate.
No independent reviewer spawn, completed acceptance handoff or final response was observed before the session ended with an account usage-limit error (exit 1, about 136 seconds).

The controller discovered the Git failure in the full rollout after the subject had already continued into alternative inspection.
The short CLI output stream had not yet exposed that failure.
An attempted process-identification/stop command was rejected by automatic approval review because of the account usage limit; the session then ended on the same limit.
No remaining scenario or reader was launched and no failed sample was replaced.
Future monitoring must inspect the full rollout promptly rather than wait for the short event stream to flush.
The observed subject counters total 375,240 input tokens (274,432 cached) and 7,198 output tokens; the failed final request may be unaccounted.
These counters exclude controller work and the separate delivery review.

## Focused launcher correction

The defect belongs to evaluation execution permissions and preflight coverage, not Agent Workflow runtime instructions.
A non-model comparison reproduced the Git error under the original profile and restored Git by granting read access to the selected Apple developer directory.
The existing `evals.persistence.config_args` now makes that bounded addition on macOS; other platforms retain their previous configuration.
The isolation helper attempts actual canary reads and checks Git startup rather than relying only on readability predicates.
No new execution framework, terminology, runtime instructions, project write permission or command network access was introduced.

Non-model checks passed for the corrected profile: Git version, status and exact historical-blob reads worked; evaluator/sibling reads and read-only writes stayed denied.
The existing isolation helper passed for writer and reader modes.
Git still emitted cache-write warnings because system temporary writes remain restricted; the observed Git operations returned zero.
The new permission test failed before the correction and passed afterward, and a Linux control confirms that Apple toolchain discovery is not required there.
The corrected launcher has not received a native preflight: the authorized two native sessions were already spent.
A separately authorized follow-up must verify actual Git operations and required nested reviewer boundaries before launching another frozen comparison.
An installation of Command Line Tools is not indicated: the selected toolchain already exists and works outside the restricted profile.

The original runtime instruction reviews remain applicable.
The new execution-boundary and interpretation reviews found zero actionable findings on either axis.
Final local checks passed on macOS/Python 3.14.6: 224 package tests, 67 evaluation-tooling tests, two wheel checks, Ruff, all 57 scenarios and `git diff --check`.
The 17 existing photo-export controls are included in the package gate.
`VERSION` remains 0.34.4, valid above the unchanged remote main and latest release v0.34.3.
Hosted PR checks are separate delivery evidence.
No product regression, duplicate completion logic or new canonical terminology was established by this interrupted sample; those questions retain the earlier source-review evidence and the current behavioral uncertainty.

## New campaign: verified Git boundary, interrupted candidate

This separately authorized campaign reused the frozen baseline `4b4ac408cbc4543e2e7a433f52c03a48f7044ca7` and candidate `b6ca58c2f8f343e635c53f731ef53d628faf6eaa`.
The actual starting PR head was `4cd10600edc788f077d79e4d82bf430d284d6af9`, a plain-wording follow-up to the reported launcher head `c3cf6855e0d7a80b50b3d5135320a947333da4b5`.
The later wording was not substituted into the frozen candidate.
The CLI remained 0.144.6 with `gpt-5.6-sol / medium`, fresh subject homes and the same 360-second/2,000,000-byte limits.
All ten paired starting projects were checked against the original fixture snapshots; the previous partial baseline was not counted as a new sample.
Supported capacity information allowed ordinary usage and showed 3% of the weekly account window consumed before launch.

The first writer preflight failed because native Git attempted to read the denied personal `.gitconfig`.
The targeted retry disabled personal/system Git configuration instead of granting access to it.
The writer retry and initial read-only preflight each passed all five Git operations, three outside-canary denials and command/patch probes in the parent and two real native reviewers.
Writer changes were limited to the six expected probe files; reader content and all preflight Git snapshots were unchanged.
Three top-level preflights and four nested preflight reviewers ran; the unused read-only retry did not authorize replacing a failed scenario.

Independent harness review found and fixed delayed cleanup on monitoring exceptions and skipped cleanup when a process-group leader had already exited.
Both defects were reproduced with deterministic subprocess tests before correction.
The cleanup-only change was frozen before scenario launch without changing subject permissions, runtime instructions or prompts.
Earlier and final manifest hashes are retained separately in the compact results.

| Case | Baseline | Candidate | Observed difference |
|---|---|---|---|
| Direct `implement` | Completed restoration, map reconciliation and local validation; explicit outer completion handoff not observed | Infrastructure-blocked before review and acceptance completion | No completed pair; improvement INCONCLUSIVE |
| Review-only | Not run | Not run | Unobserved |
| Already sufficient | Not run | Not run | Unobserved |
| Unrelated effort | Not run | Not run | Unobserved |
| Limited read-only comparison | Not run | Not run | Unobserved |
| Fresh reader | Not run after campaign stop | Not run; primary incomplete | Unobserved |

The baseline restored the exact historical bytes and updated only the existing recovery map alongside the configuration.
The saved map identifies source revision, path, purpose, pending engine and the local validation limits.
Two native reviewers completed their reads of the actual changes and relevant governing artifacts and reported no findings.
The parent checked JSON, historical equality, recovery links and unchanged HEAD; it repeated the byte/JSON checks after review as a final integrity check.
It did not repeat implementation or spawn a second review pair.
No explicit transition to the outer completion owner was observed; instruction loading or a route marker alone is not the grading criterion.
This supports the observed local outcomes, without claiming every completion-handoff requirement passed.

The candidate restored the same exact bytes and updated its recovery map, then encountered two infrastructure failures during local JSON validation.
At about 89.3 seconds, Ruby startup was denied access to `/Library/Ruby/Gems/2.6.0/specifications/default` (`Errno::EPERM`).
At about 110.1 seconds, Perl startup failed because its system `libperl.dylib` was blocked by the sandbox.
A separate `plutil` attempt rejected JSON input; that tool-selection error is distinct from the runtime permission failures.
The subject continued to a successful `jq` check and started two reviewers before the coordinator stopped it.
Neither reviewer completed, and acceptance completion was not observed.
Only the configuration and existing map changed, and Git snapshots were unchanged in both primary runs.
These partial candidate observations are not a product PASS or a demonstrated semantic regression.

The automatic monitor did not recognize the Ruby/Perl signatures in this frozen run.
Full-rollout inspection exposed the gap; after verifying process ownership, the coordinator killed only the candidate evaluation process group at about 148.9 seconds.
Thus this campaign did not meet the automatic-stop requirement for the newly observed failures: approximately 59.6 seconds elapsed after the first runtime error before termination.
The controller retained the interrupted evidence, marked infrastructure failure, removed copied credentials and blocked further launches.
No remaining scenario, fresh reader or replacement sample ran.

After stopping, a targeted regression test reproduced both missed signatures and then passed with their detection added.
Replaying the captured candidate rollout now reports infrastructure failure at the first Ruby error.
This correction grants no additional filesystem access, changes no runtime instruction and has no corrected live retest in this campaign.
The successful native permission preflights remain evidence for their exercised Git/command/patch boundary; they did not establish arbitrary interpreter startup.
The monitor recognizes the documented failure forms, not every possible infrastructure diagnostic.

Usage comprises three top-level preflights, two scenario sessions, zero readers and eight nested reviewers: four preflight reviewers, two completed baseline reviewers and two interrupted candidate reviewers.
Observed counters total 2,518,781 input tokens (2,214,528 cached) and 34,219 output tokens, including 880,372 total tokens attributable to nested reviewers after subtracting inherited parent counters.
Counters from interrupted requests may be incomplete; controller work and separate delivery reviews are excluded.
Raw delegation-message bodies are encrypted in native traces, so exact reviewer prompts cannot be inspected; native spawn timing, model settings, child tool inputs/outputs and resulting state remain observable.
No result from the first campaign was added to these totals.

The concrete premerge blocker remains the missing behavioral comparison, including candidate acceptance completion, all four negative/control cases and both fresh readers.
The next bounded step is non-model verification of interpreter startup and monitoring under the restricted profile, followed by a separately authorized fresh comparison with successful native preflights.
Do not widen access to personal configuration, replace this failed sample, or combine a later run with these results.
The successful baseline alone demonstrates no candidate improvement and does not eliminate semantic risk.

### New campaign delivery validation

Local validation passed: 224 package tests, 78 evaluation-tooling tests, two wheel checks, Ruff format/lint, all 57 scenario definitions and `git diff --check`.
The package/wheel evidence and original runtime-instruction reviews were reused where the evaluated surface was unchanged; focused monitor tests and captured-rollout replay cover the post-stop detector correction.
The prior campaign JSON values, frozen manifest, actual launch counts, exact candidate bytes and credential cleanup were independently checked.
Remote PR base and semantic tags still identify `4b4ac40` / v0.34.3, so the existing unreleased `VERSION` 0.34.4 remains valid.
Hosted CI and publication are separate delivery evidence.

### Standards

The independent final review covered all eight pending repository paths, the actual rollout fingerprints and state changes, and reused the prior controller review.
Both earlier cleanup findings are resolved; zero actionable findings remain.
No actionable duplication, speculative machinery or new canonical terminology was found.

### Spec

The independent final review covered all eight paths, campaign limits and frozen inputs, actual errors, snapshots, usage and outcome interpretation.
Zero actionable findings remain in the evidence and harness changes.
The failed live automatic stop and missing behavioral comparison remain explicit premerge blockers; review success does not turn those outcomes into PASS.

Review summary: Standards 0 remaining findings; Spec 0 remaining findings.
