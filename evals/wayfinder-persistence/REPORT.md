# Wayfinder persistence quality: bounded pilot report

The focused reconciliation change is implemented and deterministic verification passes.
The live comparison is **INCONCLUSIVE**: the first writer encountered a sandboxed file-edit helper failure and reached the frozen time limit without saving a result.
There is no observed improvement over A and no observed value over C.
Recommend **retain the instruction provisionally**, and hold a merge recommendation pending a successful, separately reported continuation cohort.
No merge, release, tag or VERSION change was performed.

## Revisions and conditions

- Frozen pre-change A: `a963f707f9123d5af870dfe06f06d3d1ee1802f8`, fetched `origin/main` at task start.
- Frozen B and evaluated harness: `d0b0d9b4c7b549cf9cc122d50e7d46cc413a776a`.
- Offline adapter correction after the stopped cohort: `5e0ef7215ddd14dc537ee39b74e32badb88db4b1`.
  The Wayfinder policy is unchanged from evaluated B; the corrected adapter has no evaluated model run.
- Offline evaluator/rubric correction: `7432b2a9a03a81a791c2a4fb4415e30771aeda9e`.
  It removes an unrequested exact JSON-field requirement for the runtime-pool choice; no evaluated update used either rubric.
- CLI: `codex-cli 0.144.6`; runtime turn context confirms `gpt-5.6-sol`, reasoning `medium`, approval policy `never`.
  No inherited implementation model or substitution was used.
- Frozen manifest fingerprint: `9a316adf727e6b823ee261996dd8b37c86db38903ad9b73d63b2d7a0fb7d996d`.
  [Manifest](results/cohort-1-freeze.json) retains exact source, dependency, CLI, policy and input fingerprints, fixed order and limits.
  The A/B policy inventories differ only in `.agent-workflow/contracts/wayfinder-state.md`.
- [Compact result](results/cohort-1-result.json) retains commands, actual input/turn-context fingerprints, delivered-file identities, checkpoint evidence, dimensional judgments, overhead and execution status.
  Raw traces, workspaces and homes remain outside Git at `/tmp/persistence-quality-cohort-1`; copied authentication was removed.

## What changed

`Reconcile affected state` now requires preservation of consequential newly supplied, corrected and still-valid details in the designated result artifact or a usable durable reference.
It retains identity/status/source/scope relationships, reconciles established dependency consequences, and requires bounded readback before claiming a material authorized update complete.
Maps stay brief; optional records, recognition, pruning, concurrent-edit checks, authorization and lifecycle ownership are unchanged.
A linked ordinary artifact remains outside Wayfinder record recognition and does not gain write authorization.
The existing ADRs own these boundaries; no additional ADR or state machinery was introduced.

The harness adds two synthetic cases with four fresh stages and a strong repository-native handoff baseline.
It reuses snapshots/diffs and token forensics, keeps rubrics away from subjects, exports condition-masked review packets, and requires explicit semantic adjudication.
It does not interpret or mutate Wayfinder state for the subject.

## Execution and dimensional evidence

Planned: 12 trajectories / 48 stages, in the frozen order.
Executed: **1 evaluated stage attempt, 0 completed stages, 0 completed trajectories**.
The coding B/repetition-1 writer was the first half of the required narrow evidence-precedence preflight.
Its fresh update never ran, so the gate remained closed and all 47 remaining stages were unexecuted.
The no-retry journal guard was exercised afterward and refused before another model invocation.
Non-model sandbox probes are separately reported setup checks, not evaluated subject stages.

| Dimension | Attempt result | Evidence and limit |
|---|---|---|
| Preservation | INCONCLUSIVE | Writer did not finish; saved rollout remained the original 43-byte title/owner stub. The transient source still existed; no post-removal preservation claim is possible. |
| Update correctness | INCONCLUSIVE | No update stage ran and no project bytes changed. |
| Evidence/authority | INCONCLUSIVE | No completed maintained result; attempted patch text is not a saved result. |
| Abstention/freshness | INCONCLUSIVE | No completed reader or final response. |
| Dependencies/readiness | INCONCLUSIVE | No completed result or continuation task. |
| Useful continuation | INCONCLUSIVE | No usable new output; stopping is not counted as progress. |
| Safety | PASS for this observed attempt | Before/after project fingerprints agree, trace contains no external/connector operations, and copied auth was removed. Later-stage/reader safety is untested. |
| Cost/maintenance | PASS for available measurement | Observations and unavailable fields are recorded; this is not an acceptable-cost or comparative-value verdict. |

The terminal runner status is `timeout` at **180.024 seconds**, exit `-9`.
The causal evidence available is narrower: `apply_patch` failed because its filesystem sandbox helper could not execute the Codex launcher path, followed by the hard deadline.
Earlier shell attempts also lacked `sed` and `git` under the isolated PATH.
This is an **infrastructure-blocked execution**, not a demonstrated product preservation failure.
Overcompression remains unproven.

The attempt recorded 228,988 input tokens, including 180,480 cached input, and 4,368 output tokens; 1,228 reasoning-output tokens are a subset, not added again.
Uncached input is the derived 48,508 tokens.
These come from the final observed cumulative rollout counter; usage after that observation is unavailable.
The interrupted exec stream had no completed-turn usage, so its null totals were not treated as zero or added to rollout totals.
Exec trace analysis observed 9 shell calls, 2 shell failures and 100,133 bytes of shell output; separate runtime evidence records the failed native patch call.
Artifact bytes remained 1,540 including the supplied transient source; change churn and subject-state human corrections were zero.
Read attribution is a command-text proxy, internal model-call counts and prices are unavailable, and there is no comparative redundancy/maintenance estimate.
The large cumulative input count alone cannot establish instruction bloat or compression as a cause.

## Isolation, controls and verification

The subject had a fresh project, fresh Codex home, no previous conversation, and only its stage request and saved/input project files.
No rubric, control answers, other arm or source-maintenance instructions were supplied.
Five bundled system-skill fingerprints were recorded; no personal skills or memory were detected in the prompt audit.
Apps/plugins/memory/web/delegation were disabled in the per-run configuration; tool network access was disabled.
Runtime evidence confirms the requested model/settings and only local attempted operations.
This is prompt/trace evidence plus sandbox probes, not a complete operating-system or remote-service audit.
The unavailable complete tool-catalog observation is not inferred from the absence of tool use.

The original non-model read/write isolation probe passed but did not exercise the native edit helper: that was an inadequate preflight.
The offline correction resolves and permits only the canonical Codex executable and sets a minimal shell PATH.
The new `isolation` command proved executable invocation, project read/write, hidden evaluator/credential denial, and reader write denial.
It does not prove the complete model-driven edit path, and no second evaluated cohort was run.
No global configuration, authentication, billing or sandbox-bypass change was made.

Four sufficient controls cover inline detail, a linked artifact, an alternate layout and honest uncertainty about a never-supplied answer.
Sixteen negative controls cover missing or misassociated details, rejected/history-only text, incompatible appended corrections, later loss, authority promotion, invention, false blocking, dangling references, read-only mutation, unrelated changes and pruning ordinary artifacts.
An independent Spec reviewer found no clearly mislabeled semantic control; the implementing analyst also checked them against the frozen case inputs.
These qualitative checks were not blind to control labels.
The deterministic tests intentionally leave semantic prose outcomes INCONCLUSIVE without adjudication, rather than implement a keyword-based semantic oracle.
Review exports hide arm metadata, although framework artifacts can reveal framework use; no completed live outcome was semantically graded under that masking.

Verified on macOS/Python 3.14.6:

- `uv run --locked ruff format --check .` and `uv run --locked ruff check .` — PASS.
- `uv run --locked python agent_workflow/verify_package.py --tests` — PASS, 148 tests.
- `uv run --locked python -m unittest discover -s evals/tests -p 'test_*.py' -q` — PASS, 50 tests including 15 focused persistence tests.
- `uv run --locked python tests/wheel_smoke.py` — PASS, sdist/wheel and disposable-consumer lifecycle/lockfile checks.
- `git diff --check` — PASS.
- `uv run --locked python -m evals.persistence isolation` — PASS after the separately committed offline correction; no model call.

Closing Standards review identified cleanup, output-cap and valid-reference defects; Spec review additionally identified unmasked review metadata and incomplete dependency fingerprints.
The changes address those findings, with focused regression evidence.
Meaningful semantic behavior, hosted Linux/Python 3.11 checks and the corrected model-driven helper path remain unverified.

## Reproduction and next decision

To reproduce the recorded failed cohort, use a disposable checkout of the frozen harness revision and [its manifest](results/cohort-1-freeze.json), then the `stage` command in [the protocol](README.md#isolation-and-reproducibility).
Do not resume or repair the stopped journal, mix its observations with a later revision, or present a new attempt as the original cohort.

For a new cohort, first use the current offline isolation probe and explicitly validate the full native file-edit path.
Freeze the revised runner/configuration with the recorded task inputs and explicitly revised rubric, preserve the failed cohort, and account for its one consumed invocation.
At most 47 evaluated stages remain under this request's budget; at most 11 further complete four-stage trajectories fit without exceeding either cap.
The original cohort's fresh update cannot be run as if its writer succeeded.
No external account action is needed; the remaining prerequisite is validating the corrected adapter in a separately reported live cohort.
The three-arm pilot still does not replace `evals/README.md`'s larger four-arm protocol or establish default-routing/general superiority.

**Delivery recommendation:** retain the focused instruction and offline tests; defer behavioral endorsement and merging until the narrow continuation check succeeds.
No advantage over the old policy or strong baseline has been established.
