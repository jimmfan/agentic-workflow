# Implementation completion findings

The instruction correction makes required completion obligations explicit across implementation, review and acceptance verification.
Behavioral improvement remains INCONCLUSIVE.
The authorized follow-up stopped after its first scenario encountered infrastructure failures; it produced no completed baseline/candidate comparison.

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
