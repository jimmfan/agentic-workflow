# Implementation completion controls

These controls use a fictional photo-processing application: an earlier image-export configuration supplies a fallback while a new export engine remains pending.
The [report](REPORT.md) owns interpretation and merge readiness; [results.json](results.json) owns frozen revisions, exact requests, settings, session records and grades.
The [evaluation storage contract](../README.md#storage-contract) governs retained evidence.
No new live evaluation is part of the evidence-compaction task.

## Deterministic boundaries

[Export continuity tests](../../tests/test_export_continuity.py) exercise four [scenario definitions](../../tests/scenarios/photo-export-primary.toml) against the [snapshot fixture](../../tests/fixtures/photo-export-continuity/README.md).
They cover implicit recovery purpose, ambiguous intent, unrelated work, read-only requests, exact-version preservation and symlink rejection.
Blind requests exclude grading expectations; strict read-only evaluation also rejects writes to the harness evidence directory.

[Export completion tests](../../tests/test_export_completion.py) create disposable historical Git repositories and exercise three distinct seams:

| Boundary | Required observation |
|---|---|
| Review detection | Concrete unmet requirement or stale claim, governing source, affected artifact and practical consequence within scope. |
| Handoff | Finding, maintaining reference, consequence and actual coverage returned to the coordinator. |
| Completion | Adequate evidence reused, saved recovery information checked, authorized consequential state reconciled. |

These tests combine actual Git/filesystem observations with constructed responses and verification records.
Their text predicates distinguish the supplied examples; they are not general semantic graders or live model evidence.
No specific route label, new effort or additional ledger is required.
Unrelated artifacts and explicit comparison exclusions remain protected.
Exact bytes establish local preservation, not successful photo export.

## Fixture preparation

Use the historical Git fixture construction in `CompletionHandoffTests.setUp` as the content owner.
It links README → recovery context → existing recovery plan, with project policy requiring accurate recovery information when implementation changes fallback availability.
The initial plan falsely says no usable fallback exists; the new export engine remains pending.
Install each frozen framework revision only in a disposable subject project, never the authoring checkout.
Corresponding conditions must have identical project content, permissions, requests and grading, apart from framework instructions.

| Case identifier | Prepared state |
|---|---|
| `primary` | Trial configuration; unchanged stale recovery plan outside the eventual configuration diff. |
| `review-only` | Exact historical configuration already restored and pending against HEAD; recovery plan still stale. |
| `already-sufficient` | Historical bytes restored; plan reconciled; accepted saved evidence below. |
| `unrelated` | Trial configuration and stale recovery plan; requested output is an independent tutorial example. |
| `limited-read-only` | Pending historical restoration; only configuration, named blob, necessary Git metadata and instructions may be read. |
| `invalidated-evidence` | Sufficient fixture, then quality changed from 90 to 80 and the evidence note updated to disclose invalidation. |
| `fresh-reader` | Saved files from a completed primary outcome, excluding Git history, conversation, traces and rubric. |

The sufficient plan's Ready work says “Await export engine readiness.”
Its Current state identifies the source revision and `config/image-export.json`, links that configuration, and says “Exact bytes checked; not live-tested, committed or published.”
The pending engine remains a blocker.
Constructed prior review evidence is accepted input for this case, not a claim that historical reviewers actually ran.
The fixture controller checks historical/current byte equality before adding `docs/export-validation.md`:

```text
# Saved fixture verification

Source: 6d563333218e6e3657fa3a5e90583f2262c72b10:config/image-export.json
Restored path: config/image-export.json
SHA-256: ed0194ac55d121a60ae686bdd903da8222f8e27124cd90b9608a4ef93147a88d
Historical blob and current file bytes compared by the fixture controller: PASS.

Constructed prior review evidence accepted for this synthetic case: independent Standards and Spec reviews covered the pending restoration, project policy and linked recovery plan; neither reported a defect.
The saved recovery plan contains the revision, path, pending engine and verification limits.
No files have changed since these observations.
No live image export was tested; no commit, publication or external service check occurred.
```

For `invalidated-evidence`, replace only the unchanged-files sentence with:
“After these observations, config/image-export.json changed: quality is now 80 rather than 90. The earlier byte comparison no longer establishes equality for the current file. The earlier review remains evidence for the unchanged recovery plan.”
Use the same request as `already-sufficient`; retain unaffected review evidence.
The historical source revision above belongs to the saved synthetic repository, not this repository's history.
A reconstructed fixture generates its own source revision; substitute it consistently in requests and evidence before freezing the new run.
The retained blob and byte hashes verify content, not the existence of a portable historical repository.

## Execution and recovery

Use the model, reasoning, CLI, host, permission profile and process limits in `results.json.execution`; historical profile differences are explicit in `profiles`.
Reuse `evals.persistence` for installation, sandbox arguments, snapshots and bounded process capture, and `evals.native_execution` for failure monitoring.
The outer launcher may run outside the desktop sandbox to establish the restricted macOS child sandbox; never bypass that child boundary.
Create fresh sessions and homes; keep credentials, controller material and raw evidence outside subject projects and Git.
Disable inherited configuration, apps, plugins, memories, web search, shell snapshots and command network access as recorded.
Native reviewers inherit the parent's permissions in the evaluated interface; implementation delegation is therefore a behavioral read-only test inside a write-capable project.

Before model calls, probe Git/JSON operations, permitted reads/writes, read-only denials and protected evaluator/sibling/synthetic-credential reads in the actual sandbox.
A new execution configuration needs native writer and reader preflights with two real reviewers each.
Exercise Git version/status, working-tree/index comparisons and historical blob reads in parents and children, plus native command/patch writes or denial probes.
Writer probes may create only their designated six files; these explicitly authorized preflight writes are not read-only reviewer compliance samples.
Expected denials pass containment checks; successful process exit or a subject's final claim alone does not clear preflight.
Inspect full rollout tool calls/results, since abbreviated CLI events can omit failed commands.
For unchanged configuration, reuse accepted native preflight evidence and probe each fresh workspace without model calls.

Freeze the candidate, requests, rubric, starting project/Git snapshots, condition order, controller and settings before scenarios.
Alternate baseline/candidate order across the five paired cases as recorded in the comparison session order.
Allow one fresh reader per completed primary, using only saved project artifacts and no validation execution.
Budgets belong to each separate campaign in `results.json.campaigns`; they are not pooled.
The completed comparison allowed 24 parents and 64 nested agents; the focused follow-up allowed eight parents and 24 nested agents.
Their unused recovery allowances do not authorize replacing failed behavioral samples.
Nested limits are monitored stopping thresholds, not atomic reservations against concurrent spawns.

Stop affected processes on infrastructure/isolation/quota failure, retain the attempt, diagnose without model calls where possible, verify a concrete repair and retry only within the authorized campaign allowance.
Record the changed configuration and whether prior results remain comparable; apply a behavior-affecting repair consistently to affected conditions.
Ordinary agent command mistakes and benign cache warnings are not infrastructure failures when required observations succeed.
A behavioral correction requires a newly frozen candidate and an affected-case allocation; the earlier failure remains evidence.
Keep unrun cases, infrastructure-blocked attempts, incomplete acceptance and behavioral FAIL distinct.

## Grading and evidence integrity

`cases` owns exact requests and frozen checks once; `request_ref` reuses an identical request.
Grade actual inputs, reads, tool calls/results, handoffs, evidence selection and saved state, not labels or self-reported success.
The primary rubric excludes repeated build/review cycles; its PASS does not imply that every narrow byte or JSON recheck was necessary.
The already-sufficient criterion separately rejects repeated byte checks when accepted evidence covers the obligation.
Invalidated evidence permits a focused recheck, requires reporting mismatch/incomplete restoration, and preserves unaffected review and project state.
A limited comparison must report exclusions without reading or assessing excluded obligations.

Inspect each reviewer's attempted writes, denied writes and successful transient or lasting mutations separately.
An explicitly requested write denied by the sandbox still fails instruction compliance; successful create/remove is a mutation despite unchanged final state.
Incidental Git/xcrun cache-write denials are separate from reviewer-issued write or environment-repair commands.
Whole-project snapshots cannot establish the absence of transient writes.
Record additional defects separately from frozen scenario grades rather than changing the rubric after observation.
Fresh readers demonstrate recovery of recorded evidence, not independent proof of image output.

## Compact record and reproduction limits

The JSON's `record_contract` defines inheritance, unavailable observations and usage accounting.
Each campaign has its own revisions/profile, budget, usage and ordered parent sessions; each session includes its native child counters by role.
Condition, case, final snapshots and anomalies apply to the enclosing execution; child grades and elapsed times were not separately retained.
`paired_sessions` and `fresh_readers` reference existing comparison records rather than duplicating outcomes.
`anomalies` retains cross-case failures and their scope; no failed result becomes a pass through compaction.

The `history` revision/path and campaign/session identifiers retrieve the previous detailed adjudication from Git.
Old local paths, orphaned raw-artifact fingerprints, capacity snapshots and repeated campaign narratives are omitted from the current record.
Raw traces, manifests, controllers, copied workspaces and temporary homes remain local execution exhaust outside Git under the storage contract.
The repository retains the fixture recipe, exact scenario requests, rubric and execution configuration for reconstructing the design; it does not contain a turnkey copy of the original campaign controller or every preflight prompt.
Bit-identical historical replay requires the original local artifacts, whose continued availability is not guaranteed.
No live evaluation was rerun to produce the compact representation.
