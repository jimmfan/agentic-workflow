# Bounded Wayfinder preservation pilot

This campaign tests the authorized reconciliation instruction in `wayfinder-state.md` and fresh-session continuation.
Missing supplied hotel identities are the motivating observation; overcompression is a hypothesis, not a diagnosed cause.
The product change is limited to the owning reconciliation section.
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

Each of 12 trajectories has four fresh stages: writer, correction/commitment, unrelated small edit, then an ordinary read-only next task.
Stage 2 receives every saved file from stage 1 except `source-once.txt`.
Stages 3 and 4 receive every saved file from their predecessor.
No answer-dependent selection, repairs, source reinjection, grader notes, earlier responses, homes or traces are transferred.
A subject-created copy of supplied material is transferred like any other file and earns preservation credit only if current relationships remain usable.
Checkpoint each stage's complete saved files, response, before/after hashes and diff in ignored storage, including interrupted stages.
Raw workspaces, traces, homes and secrets never enter compact results.

The fixed order is coding B/A/C then planning B/A/C for repetition 1; coding C/A/B then planning C/A/B for repetition 2.
This offers limited order variation, not statistical counterbalancing.
There are at most 48 evaluated stage invocations, including failed starts and preflight attempts.
Each stage allows 180 seconds and 2 MB combined process output; these are hard runner limits, not inferred token limits.
No retry-to-green, replacement model, parallel trajectories, extra pilot, global configuration change or new paid service is permitted.

## Narrow experiment before comparison

The first two stages, coding B repetition 1, are the narrow evidence-precedence experiment required by [the repository protocol](../README.md#protocol-for-future-causal-work).
The writer receives a supported local compatibility fact and an unresolved pool choice.
After removing the transient source, a fresh updater receives a newer accepted pool decision that does not contradict that fact, and must apply and verify the local configuration.
Before continuing even this trajectory, independently adjudicate that saved support survived, the newer decision was applied, useful work and verification occurred, authority stayed scoped, and isolation/observability held.
Record the exact stage-2 checkpoint fingerprint and rationale in the ignored `preflight.json`; only PASS opens the remaining runs.
A failure or inconclusive narrow result is retained and stops expansion, not silently tuned away.

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
`persistence.adjudicate` binds a review to the exact checkpoint and validates its cited spans; citation validation cannot establish the truth of the review's reasoning.
A review cannot override a detected failure with PASS or establish saved preservation solely from the final response.
The reviewer compares actual saved contents/diffs/task output against the hidden input and rubric, recording each dimension's verdict, rationale and exact evidence spans.
Absence claims cite the inspected saved artifact or diff and explain what is missing.
Review map brevity, resource/status/source/scope relationships, acceptance boundaries, reference usability, redundancy and prohibited external actions explicitly.
Route/read claims alone establish none of these.
Mechanical link checks cover file targets; anchors, plain-text references, cross-file meaning and external-reference sufficiency require adjudication.

[Controls](controls.json) include sufficient inline, linked and alternate-layout results and each requested negative class.
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
Audit the actual prompt input and sandbox before the first invocation and per-stage inherited instructions, tools, effective model/configuration and fresh session identity from retained evidence.
Any unaccounted instruction, connector, memory, earlier conversation, unsupported model/configuration or missing visibility stops the affected run.
Built-in Codex system skills may appear equally in all arms; record their fingerprints and do not mistake them for inherited personal skills.
The supplied strong baseline policy prohibits external access and delegation in all arms.
See [official permission configuration](https://learn.chatgpt.com/docs/config-file/config-reference) for the host boundary; CLI support must be checked locally rather than assumed from documentation.

Commit the implementation/protocol/fixtures before freezing:

```bash
uv run --locked python -m unittest discover -s evals/tests -p 'test_persistence.py' -v
uv run --locked python -m evals.persistence freeze --candidate HEAD --output /tmp/persistence-freeze.json
uv run --locked python -m evals.persistence stage --manifest /tmp/persistence-freeze.json --run-root /tmp/persistence-pilot
```

The stage command executes exactly the next stage, never retries or automatically expands past the narrow gate.
Run trajectories sequentially; inspect each checkpoint for safety, contamination, missing telemetry and execution status before invoking the next stage.
Retain the frozen manifest and compact report/results under this suite; raw execution stays under `evals/artifacts/` or a caller-owned ignored/temporary directory.
To reproduce a prior cohort, check out its recorded runner revision and use its unchanged manifest; new revisions or rubric fixes require a distinct cohort and consume the remaining overall budget.
A prior stopped cohort remains stopped.
The final report must distinguish deterministic harness/contract correctness, observed B-over-A improvement, and observed B-over-C value, with retain/revise/reject recommendation and limitations.
No merge, release, tag or VERSION change is authorized.
