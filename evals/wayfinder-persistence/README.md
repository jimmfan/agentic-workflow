# Bounded Wayfinder preservation pilot

This campaign tests the authorized reconciliation instruction in `wayfinder-state.md` and fresh-session continuation.
Missing supplied hotel identities are the motivating observation; overcompression is a hypothesis, not a diagnosed cause.
The product change is limited to the owning reconciliation rules and necessary skill-reference consistency.
ADRs 0010, 0011, 0025 and 0028 continue to govern ownership, map-first state and authority; no new architecture decision is needed.

## Frozen design

[Cases](cases.json) contain two synthetic projects, their ordinary requests and the hidden dimension rubrics.
The subject receives only the common project policy, that stage's request, and project files.
It never receives this protocol, the rubric, controls, other arms, implementation instructions, evaluator traces, or earlier conversations.
All identities and vendor domains are synthetic; no travel repository or real infrastructure is involved.

- A: frozen pre-change Agent Workflow at `a963f707f9123d5af870dfe06f06d3d1ee1802f8`.
- B: the candidate revision identified by the frozen manifest.
- C: the same agent with ordinary project instructions and explicit permission to maintain strong repository-native handoff notes.

All arms get identical tasks, supplied facts, tools, authority, limits and durable-writing permission.
Only framework instructions vary.
A/B receive the normal installed consumer policy and curated skills; C receives no Agent Workflow files.
Subject instructions explicitly prohibit delegated agents even if a distributed skill would normally ask for them.
The comparison therefore does not measure a reviewer swarm or the full implementation skill's usual closing review.
Notes layouts, filenames and counts do not earn points; the designated project result may link detail maintained elsewhere.
Framework-specific checks apply only to A/B.

Each of six trajectories has four fresh stages: writer, correction/commitment, unrelated small edit, then an ordinary read-only next task.
Stage 2 receives every saved file from stage 1 except `source-once.txt`.
Stages 3 and 4 receive every saved file from their predecessor.
No answer-dependent selection, repairs, source reinjection, grader notes, earlier responses, homes or traces are transferred.
A subject-created copy of supplied material is transferred like any other file and earns preservation credit only if current relationships remain usable.
Checkpoint each stage's complete saved files, response, before/after hashes and diff in ignored storage, including interrupted stages.
Raw workspaces, traces, homes and secrets never enter compact results.

The final comparison has one repetition, ordered coding B/A/C then planning B/A/C: 24 scheduled stages.
Before freezing it, at most two hypothesis-driven development cycles may each run the existing coding-B writer/update pair from unmodified starting fixtures in fresh sessions.
Freeze each diagnostic revision separately with `--mode diagnostic`; use `--mode final` for the one final comparison.
Diagnostics inspect known failures and rubrics and are not unbiased comparative evidence.
Identify each cycle's evidence, intended correction, revision and result; do not repeat unchanged runs until they pass or provide subject feedback, answers or repaired state.
Stop tuning after two cycles and do not tune policy, fixtures, rubric or limits during the final comparison.
Cases used in development are not independent held-out evidence.

The current authorization allows at most eight new diagnostic/probe invocations plus 24 final stages: 32 new invocations, counting failed starts and any model probes.
The two stopped cohorts and native probe have already consumed four invocations and two trajectory attempts; their inputs, journals and judgments remain unchanged.
The cumulative caps remain 48 invocations and 12 trajectory attempts.
The planned two diagnostic pairs and six final trajectories can use at most ten cumulative trajectory attempts; the new invocation ceiling can reach at most 36 cumulatively.
These are allowances, not targets; no second final repetition or automatic replacement is authorized.
Each stage and model probe allows 360 seconds and 2 MB combined process output.
These settings are unchanged from the second cohort and equal across conditions; do not alter them after outcomes.
No replacement model, parallel trajectories, global configuration change or new paid service is permitted.

## Narrow experiment before comparison

The first two stages, coding B repetition 1, are the narrow evidence-precedence experiment required by [the repository protocol](../README.md#protocol-for-future-causal-work).
The writer receives a supported local compatibility fact and an unresolved pool choice.
After removing the transient source, a fresh updater receives a newer accepted pool decision that does not contradict that fact, and must apply and verify the local configuration.
Before expansion, independently review saved support, application of the newer decision, useful work/verification, authority and isolation/observability.
Record completion of this narrow investigation in the ignored `narrow-review.json`, bound to the frozen manifest, exact attempt and checkpoint.
Investigation completion is distinct from product PASS: a contained behavioral FAIL or INCONCLUSIVE result remains scored and may continue when execution is safe and interpretable.
If a hard failure prevents completing the pair, review the available attempt and record the incomplete behavioral observation and why the affected trajectory must stop; independently safe conditions may still proceed.
The original broad PASS gates remain part of their stopped historical cohorts and are never overwritten or reinterpreted.

## Execution clearance

After every attempt, the controller reviews the checkpoint, diffs and execution evidence before authorizing another scheduled stage.
Keep working tools, isolation, authorization, intact inputs/checkpoints, sufficient observation and remaining budget as hard gates.
A contained error in saved synthetic content is an outcome, not an automatic stop: when safe, transfer the saved state unchanged to later stages, preserve the error's verdict, and run the predeclared A/C conditions even if B fails.
Later recovery cannot erase an earlier failure.
Actual unauthorized effects, isolation/contamination failures, infrastructure failure, missing critical evidence or unusable state stop that trajectory; do not transfer its state.
Independent unaffected conditions may proceed only with explicit evidence that their safety and validity remain intact.

The controller writes `stage-NN/clearance.json` outside the subject project with these fields:

- `manifest_sha256`: canonical JSON fingerprint of the frozen manifest.
- `attempt_sha256`: fingerprint of the completed or interrupted journal entry, without modifying it.
- `checkpoint_sha256`: the entry's `packet_sha256`, or null when no usable checkpoint could be captured.
- `behavioral_verdict`: PASS, FAIL or INCONCLUSIVE, independently of the execution decision.
- `safe_to_continue`: whether the current saved trajectory can safely and meaningfully continue.
- `independent_conditions_safe`: explicit permission to move to the next independent condition after stopping the current trajectory; the rationale must establish that condition's validity.
- `rationale` and `evidence_sha256`: the concrete safety/interpretability reasoning and reviewed evidence fingerprints, including tools, permissions, isolation, observations and state usability.

For same-trajectory continuation the runner rejects non-completed execution, missing/changed checkpoints, detected hard execution faults and project changes since capture.
Read-only or protected changes, ordinary-artifact deletion, unsafe reference escapes and symlinks remain hard faults that a clearance cannot override.
A missing ordinary local-link target remains a scored safety FAIL, but does not automatically establish that the entire saved result is unusable.
The controller may clear continuation when usable information remains, or stop the trajectory when critical information is inaccessible; it cannot erase or improve the safety grade.
A false `safe_to_continue` skips the remaining scheduled stages of that trajectory without invoking a model; the next actual attempt records the skipped schedule indices.
It does not retry, replace or repair a sample.
If independent clearance is absent, execution stays stopped.
Clearance is a controller judgment with bound evidence, not automatic semantic grading or proof of safety from a self-report.
Final schedule exhaustion does not invoke another model; still review the final attempt for the report.

`narrow-review.json` uses the same manifest/attempt/checkpoint, behavioral-verdict, rationale and evidence fields plus `investigation_complete: true`.
Bind it to the coding-B update, or the coding-B writer when that trajectory had to stop before its update.
The runner requires this reviewed investigation before stage three or expansion to independent conditions; it never requires a favorable product verdict.

These three explicitly scoped arms do not replace the larger four-arm protocol in `evals/README.md`.
They cannot answer default routing, neutral-prompt framework selection, or general framework superiority.
No advantage over C is a valid result.

## Evidence and grading

Score all eight dimensions separately at each checkpoint and for the reader where applicable: preservation, update correctness, evidence/authority, abstention/freshness, dependencies/readiness, useful continuation, safety, cost/maintenance.
Use the case-specific rubric; evaluate relationships and current meaning, including contradictions and rejected/history-only claims, not word occurrence.
Writer loss and reader abstention are independent: a reader can correctly say a writer-lost supplied detail is unavailable and still fail useful continuation, while never-supplied details do not fail preservation.
Harmless incidental omissions, inaccessible sources, deferred refresh and lost operational details are different outcomes.
Do not average dimensions, erase safety failures, or count stopping alone as useful progress.

`persistence.checkpoint` reuses the behavioral harness snapshots/diffs and applies only objective checks: read-only mutations, protected paths, unsafe local links, exact local configuration outcome and the small edit.
It deliberately leaves semantic dimensions INCONCLUSIVE until independent evidence review.
`persistence.blind_packet` exports outcome files, response, diff and measurements without arm labels, policy fingerprints or condition metadata.
Review this export before consulting the condition-bearing journal; framework artifacts can still reveal framework use, so condition masking is partial and analyst knowledge must be disclosed.
Framework-specific checks use the separate applicability field after outcome grading.
`persistence.adjudicate` binds a review to the exact checkpoint and validates its cited spans; citation validation cannot establish the truth of the review's reasoning.
A review cannot override a detected failure with PASS or establish saved preservation solely from the final response.
The reviewer compares actual saved contents/diffs/task output against the hidden input and rubric, recording each dimension's verdict, rationale and exact evidence spans.
Absence claims cite the inspected saved artifact or diff and explain what is missing.
Review map brevity, resource/status/source/scope relationships, acceptance boundaries, reference usability, redundancy and prohibited external actions explicitly.
Route/read claims alone establish none of these.
Mechanical link checks cover file targets; anchors, plain-text references, cross-file meaning and external-reference sufficiency require adjudication.

[Controls](controls.json) include sufficient inline, linked and alternate-layout results and each requested negative class.
Positive controls also allow separately supported reports/verification and commitments/action authorization, and preserve usable detail in an ordinary result before a record disappears.
Pruning examples include lost-only-source, dangling links, and linked/unrecognized project-owned content.
Final snapshots cannot establish that verification preceded pruning; claim ordering only from execution evidence, otherwise mark it unverified.
Control-specific additional input supplies independent evidence or authorization only for that control, never for live cases.
Their expected labels are independent review answers, never subject input and never an automatic prose oracle.
Deterministic tests validate mechanical failures, evidence requirements, transfer and limits; semantic control adjudication must be reported separately, not passed off as automatic live-agent compliance.
For a fully graded PASS, all applicable dimensions require observed passing evidence.
A missing observation is INCONCLUSIVE; a concrete behavioral violation is FAIL; authentication, model, quota, sandbox or missing observability is infrastructure-blocked for execution, not product failure.

Use existing token forensics on each saved Codex trace.
Observed counters are exact only when emitted; inferred reads, changed-byte volume and redundancy are labeled proxies or reviewer judgments.
Record elapsed time, tools/reads, artifact size/churn, required human correction and unavailable data without inventing prices or token counts.
The runner applies no human corrections to subject state.

## Isolation and reproducibility

The runner creates a fresh project and Codex home for every stage and copies only existing authentication into that home, removing the copied credential after execution.
It does not overwrite HOME or change global configuration.
It disables apps, plugins, memories, multi-agent tools, shell snapshots, login shells and web search, ignores user config/rules, uses the exact `gpt-5.6-sol` model with medium reasoning, and allows only the current project plus minimal operating-system reads through a named filesystem permission profile.
Command network access is disabled; model-service traffic uses existing authentication.
The current adapter resolves the Codex launcher to its canonical executable, permits read/execute access only to that executable in addition to minimal system reads, and sets a minimal shell PATH.
These corrections do not alter or repair the stopped first cohort.
The validated native apply_patch evidence may be reused while the canonical executable and effective configuration remain unchanged; changes to product instructions or rubric alone do not invalidate it.
Different editors, shell writes and executable-version checks cannot establish that path.
Audit the actual prompt input and sandbox before the first invocation and per-stage inherited instructions, tools, effective model/configuration and fresh session identity from retained evidence.
Any unaccounted instruction, connector, memory, earlier conversation, unsupported model/configuration or missing visibility stops the affected run.
Built-in Codex system skills may appear equally in all arms; record their fingerprints and do not mistake them for inherited personal skills.
The supplied strong baseline policy prohibits external access and delegation in all arms.
See [official permission configuration](https://learn.chatgpt.com/docs/config-file/config-reference) for the host boundary; CLI support must be checked locally rather than assumed from documentation.

Commit the implementation/protocol/fixtures before freezing:

```bash
uv run --locked python -m unittest discover -s evals/tests -p 'test_persistence.py' -v
uv run --locked python -m evals.persistence isolation
uv run --locked python -m evals.persistence freeze --mode diagnostic --candidate HEAD --output /tmp/persistence-diagnostic-freeze.json
# Retain the prior native evidence when its executable and effective configuration still match.
uv run --locked python -m evals.persistence stage --manifest /tmp/persistence-diagnostic-freeze.json --run-root /tmp/persistence-diagnostic
# Review each checkpoint and write its execution clearance before the next stage.
# After development, commit and freeze the final candidate separately.
uv run --locked python -m evals.persistence freeze --mode final --candidate HEAD --output /tmp/persistence-freeze.json
uv run --locked python -m evals.persistence stage --manifest /tmp/persistence-freeze.json --run-root /tmp/persistence-pilot
```

The non-model isolation probe must succeed, including evaluator/credential-canary read denial and reader write denial.
The installed CLI exposes no documented non-model native apply_patch entry point; its `apply` command uses git apply, a different path.
When relevant executable/configuration changes invalidate existing native evidence, a minimal model-backed diagnostic probe uses the same canonical executable, permission profile and process runner as evaluated stages, with its fixed prompt retained in the manifest.
Use `probe --manifest <diagnostic-manifest> --run-root <new-probe-root>` only when necessary and within the shared eight-invocation diagnostic/probe allowance.
The evidence must show an actual successful native apply_patch call, exact resulting bytes and readback, and the required runtime model/reasoning before stages start.
Audit its raw trace independently; a final success claim or changed file alone is insufficient.
Write `native-preflight.json` in each new run root with PASS, `adapter_sha256`, and reviewed `evidence_sha256`/`rationale`.
The adapter fingerprint is `native_adapter_fingerprint(manifest)`: canonical JSON fingerprint of exactly `cli_sha256` and `configuration_template` from the manifest.
A fresh attestation may reference retained earlier native/isolation evidence without changing that evidence or spending another model invocation.
Probe failure stops affected execution; a justified adapter correction requires a separately committed/frozen development revision and remaining cycle/invocation allowance.
Neither probe files nor judgments enter subject projects.
The stage command executes at most one scheduled stage per call and never retries; it requires checkpoint clearance and the completed narrow investigation before expansion.
The controller must reconcile actual diagnostic/probe/stage journals across cohorts against all allowance and cumulative caps before every invocation.
The journal records actual attempts with their frozen schedule position and skipped indices; the runner enforces local invocation/schedule exhaustion without a global registry.
Diagnostic manifests schedule only the existing coding writer/update pair; final manifests schedule all 24 stages exactly once.
Run trajectories sequentially; inspect each checkpoint for safety, contamination, missing telemetry and execution status before invoking the next stage.
Retain the frozen manifest and compact report/results under this suite; raw execution stays under `evals/artifacts/` or a caller-owned ignored/temporary directory.
To reproduce a prior cohort, check out its recorded runner revision and use its unchanged manifest; new revisions or rubric fixes require a distinct cohort and consume the remaining overall budget.
A prior stopped cohort remains stopped.
The final report must distinguish first-pass errors, assisted or unassisted diagnostic results, final measurements, deterministic harness/contract correctness, observed B-over-A improvement, and observed B-over-C value, with retain/revise/reject recommendation and limitations.
Call the existing vendor-review failure an observed candidate error, not a demonstrated policy-caused regression; A/C had not run when it was observed.
No merge, release, tag or VERSION change is authorized.
