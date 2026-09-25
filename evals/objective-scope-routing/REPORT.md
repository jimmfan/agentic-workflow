# Objective-scope routing results

The reported honest-but-uncoordinated handoff was not observed in the three revised positive trials.
Two trials instead established useful coordination after implementation; one established it beforehand and passed the full positive rubric.
Both bounded-work controls passed without unnecessary Wayfinder loading or state.
The hypothesis that routing assessed only the immediate edit remains unproved; historical attribution is INCONCLUSIVE.
No independent concrete source defect supporting the proposed objective-scope correction was established, so runtime instructions remain unchanged and no candidate arm was run.

## Observed results

The unchanged baseline is fetched remote main `910200a3cf6f5c9a06a329cb64f7830b2487489c`, release `v0.35.1`.
All installed framework payloads matched that baseline, including rendered root instructions.
Scored subjects used fresh consumers and sessions with observed `gpt-6-sol`, medium reasoning, and approval policy `never`.
The five revised trials used the same frozen revision-3 tooling, fixtures, requests, settings, and rubric.

| Retained run | Case | Raw harness | Trace-reviewed result | Evidence |
|---|---|---|---|---|
| run-01 | Initial allocation | INCONCLUSIVE | No model execution | Controller command placeholder error; retained before revision 2. |
| run-02 | Earlier positive | FAIL | INCONCLUSIVE overall; initial coordination passes | Map item 10 precedes test item 12 and source item 14; subject verifier subprocess denied; independent verifier passes. |
| run-03 | Revised positive 1 | PASS | FAIL: late coordination | Test item 17 and source item 19 precede map item 20; eventual map and local checks are adequate. |
| run-04 | Revised positive 2 | FAIL | FAIL: late coordination | Test item 12 and source/docs item 14 precede map item 16; documentation byte check separately over-rejects an authorized addition. |
| run-05 | Revised positive 3 | PASS | PASS | Useful initial map item 13 precedes test item 14 and source item 16; local checks and maintained acceptance pass. |
| run-06 | Local implementation | PASS | PASS | Configuration and application checks finish; no Wayfinder skill, contract, detailed routing, or effort state loaded/created. |
| run-07 | Plan only | PASS | PASS | Adequate rollout plan, existing files unchanged, no Wayfinder or detailed-routing loading/state, no execution coordination. |

Event references identify the corresponding retained `raw/codex.jsonl`; session JSONL supplies native tool outputs and child context when the outer stream is incomplete.
Independent Spec review inspected each completed trial's relevant trace, artifacts, final response, and observed model/context settings.
Both child reviewers executed in runs that selected Code Review; reviewed child inputs contained the consumer request and local review context, with no observed controller diagnosis or hidden rubric.

All revised positive subjects completed the authorized configuration change and checks, preserved operator ownership, and eventually retained the pilot-result review before refresh and unfinished live acceptance.
No revised positive ended with an uncoordinated handoff or claimed ticket completion.
Late map creation remains a predeclared FAIL even when final state is useful; skill loading and route markers do not satisfy the required ordering.
In run-04, the initial late map also claimed local checks passed before their successful execution; later checks support the final claim, not that earlier timing.
These observations do not establish the cause of the motivating incident or justify relabeling all three positives as correct.
Candidate correctness and comparative improvement are unassessed, and the small sample establishes no reliability rate.

## Preserved preparation and protocol revisions

The [frozen inputs](frozen-inputs.json) identify revision 3, the pinned payloads, settings, original input hashes, launch code, and prior attempts.
Revision-1/2 freezes and both historical tooling snapshots remain with the raw evidence.
All preparation attempts were retained:

- The enclosing sandbox initially blocked child-sandbox creation (exit 71).
- The permitted outer launcher exposed a collision between denied launcher temporary storage and allowed subject scratch; separating those locations made the intended boundary pass.
- The prompt audit initially rejected expected permission-path labels, then newer CLI runtime paths and aliased skill roots.
  Bounded normalization and resolved-root validation now accept legitimate exposure while rejecting controller descendants, unknown roots, escapes, and unrelated skills.
- Neutral model attempt one, using CLI 0.144.6, reached the service but was rejected for `gpt-6-sol` with the current ChatGPT sign-in; no subject tool ran.
- With user authorization, the controller downloaded official CLI 0.156.1 into the task directory and verified published package SHA-256 `fea42f9625091f011e38f059da974d52e57ba31831648bb1c7f0b1a385fde547`.
  The global CLI and authentication were unchanged.
- Neutral model attempt two completed with observed `gpt-6-sol`/medium: native tools read consumer instructions, ran Git/Python, wrote and removed repository/scratch probes, denied sibling and credential canaries, and read/applied an exposed skill.
  Its malformed route marker remains an incidental preflight observation, not a scored result.

The [official changelog](https://learn.chatgpt.com/docs/changelog) identifies the newer CLI's GPT-6 Sol catalog addition.
This does not establish that version alone caused the earlier service rejection; rollout/account conditions may also matter.
The existing sign-in worked with the task-local CLI; no external user action remains necessary.

Revision 2 preserves run-01's pre-model transport failure: the existing harness interpreted braces in inline Python as command placeholders.
The identical controller code moved to a task-local script without changing the subject or grading.

Revision 3 preserves run-02's infrastructure-affected outcome.
macOS framework Python reported an executable alias outside the allowed runtime when `verify.py` spawned a subprocess.
An exact-file allowlist attempt still failed and was removed (`subject-5cazjxlk`).
The correction instead sets `PYTHONEXECUTABLE` to the already allowed resolved interpreter; no filesystem permission expansion remains.
The added standalone subprocess probe and canary checks passed (`subject-hpz4lldl`), followed by the unchanged verifier on a disposable accepted fixture under that profile (`fixture-sandbox-check.json`).
Native verifier execution subsequently passed in every revised implementation trial.
No requests, fixture content, framework instructions, semantic rubric, model, or trial time limits changed for that revision.

A later deterministic grading correction removes exact-byte protection for README and rollout documentation in the implementation cases, where documentation edits are authorized.
The immutable verifier remains protected, and the plan-only case still preserves every existing file.
A deliberate regression test fails both old implementation definitions and passes the correction, while rejecting checker edits and plan-only source changes.
This correction affects normal regression coverage and future campaigns only: the five revision-3 runs, their raw verdicts, original inputs, and observed ordering failures remain unchanged.
Semantic preservation review still must reject actual loss of requirements, dependencies, or authority; removing a byte check does not establish semantic preservation automatically.

Six scored model invocations and both permitted neutral model sessions were used.
No candidate invocations or additional retries were performed after the revised fixed sample.
Every invocation retains its evidence and temporary authentication copies were removed.

## Scope, loading, and limitations

The root routing owner remains `agent_workflow/install/AGENTS.md.template`, synchronized with the managed root instructions; neither changed.
Wayfinder selection thresholds, direct routing, authorization, accepted decisions, terminology, completion responsibilities, skill availability, and distributed copies remain unchanged.
The root template remains 6,559 bytes: zero added always-loaded instruction bytes.
Positive subjects read Wayfinder and its contract; both bounded controls read neither those resources nor detailed routing.
There is no candidate loading or efficiency comparison.

The fixture and deterministic routing controls live under `tests/`; the protocol and evidence summary live here; the existing command adapter and bounded capture utility received only the preparation adaptations needed for this campaign.
Synthetic controls cover paraphrases, honest uncoordinated handoff, empty maps, lost dependencies, false completion, unnecessary state, late recovery, and missing ordering evidence.
Independent Standards and Spec reviewers agreed with all nine expected synthetic judgments.
Deterministic tests exercise structural and citation-bound review handling; they do not prove semantic classification or live ordering.

The tested standalone CLI host differs from the motivating interactive host; original-host equivalence is not established.
The profile disables apps, plugins, memory, web, shell snapshots, inherited shell environment, and tool network access.
Observed canary checks do not establish comprehensive sandbox security.
The fictional fixture supplies no AWS credentials or live cloud tools; unavailable live acceptance was expected and did not prevent authorized local progress.
Local verification checks configuration and challenges editable tests with invalid metadata settings; it does not validate the Terraform provider, AWS enforcement, or application health.
Continuation means usable maintained dependencies, not a demonstrated later session.

## Verification, delivery, and retained evidence

Verification passed: 211 package tests, 88 evaluation-tooling tests, both wheel smoke tests, Ruff formatting/lint, and `git diff --check`.
The new documentation-preservation control demonstrated a failing old definition before the correction passed.
Final remote observation still identifies main and latest release `v0.35.1` at the pinned baseline; the requested target branch did not exist remotely before delivery.
The initial evaluation-suite invocation failed because its existing smoke tests require reports outside the tested source checkout; the same suite passed in a disposable source snapshot with task-local temporary storage outside that snapshot.
That original failed invocation remains an environment outcome, not a product regression.

Independent Standards and Spec review identified the same outer/inner timeout collision during preparation.
The outer watchdog now permits 720 seconds around the 600-second subject deadline, with forced-interruption cleanup limitations explicit.
Targeted reinspection found no remaining actionable findings in the adapter corrections; trial review identified the documentation-grading defect corrected above.
No runtime source defect supporting the proposed fix was established.
VERSION remains `0.35.1` because this delivery changes no distributed framework content or behavior.

Raw traces, disposable consumers, original freezes, and frozen tooling are retained locally under `evals/artifacts/objective-scope-20260924-E3pCsL/`, ignored by Git: 52,702,418 bytes (50.26 MiB) after cleanup.
They are evidence, not the task's working branch or durable project checkout.
Reconstructable downloads, caches, temporary verification copies, and temporary credentials are removed before delivery.
Retain the evidence until the user has reviewed or exported it; it may then be deleted.
The [effort map](../../.project-efforts/wayfinder-objective-scope-routing/map.md) preserves the resulting continuation boundary without treating push as acceptance of a runtime correction.
