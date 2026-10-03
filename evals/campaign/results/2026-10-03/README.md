# Framework acceptance evidence, October 3, 2026

The reusable campaign framework passed deterministic verification, blind grader calibration, and two actual manual-host boundary controls.
Native Codex execution remains infrastructure-blocked in this Work Mode host.
No historical release ranking, multi-turn native persistence result, or skill-combination improvement is established by this delivery.

## What actually ran

| Check | Observed result | Evidence and limit |
|---|---|---|
| Campaign deterministic controls | 80 tests passed | Revision preparation, adapter protocol, evidence binding, recovery, grading, calibration, and CLI preservation controls; synthetic responses are not product behavior. |
| Complete package gate | 220 tests passed | `uv run --locked python agent_workflow/verify_package.py --tests` ended with the package verification success message. |
| Complete evaluation-tooling suite | 174 tests passed | Includes the 80 campaign controls and existing evaluation tooling. |
| Python style | Passed | `uv run --locked ruff format --check .` and `uv run --locked ruff check .`. |
| Distribution smoke | Passed | `uv run --locked python tests/wheel_smoke.py` built sdist/wheel, installed an isolated CLI, exercised install/update/status/remove, and passed two lockfile checks. |
| Semantic grader calibration | 48 of 48 expected judgments matched | Independent fresh grader saw only the blind packet: 42 valid dimensions accepted and six planted defects detected. |
| Actual manual boundary smoke | 2 of 2 turns PASS | Separate fresh subjects completed the typo edit and read-only choice discussion; mechanical checks and independently cited semantic judgments passed. |
| Native no-model sandbox probe | Infrastructure-blocked | Codex CLI 0.160.0 probe timed out after 30.06454 seconds with exit -9 and no diagnostic output; no credential copy or model launch. |
| Historical preparation | All selected payloads prepared offline | v0.33.2, v0.35.1, v0.35.3, v0.41.2 and optional v0.31.0/v0.37.0 installed and matched retained file hashes in disposable consumers; no performance result. |

Verification used the Linux host's Python 3.12 environment.
The source-only change leaves distributed instructions, package resources, and VERSION unchanged.
Independent Standards and Spec reviews found no remaining material issues after correction of evidence recovery, output preservation, host capability, Git setup, and rubric problems.
The existing baseline-comparison session and its branch were not modified.

## Retained artifacts

- [Calibration result](calibration-result.json) contains the actual 48 judgments, exact citations, authored expectations, and agreement totals.
- [Manual spec](manual-spec.json) freezes the two requested cases, current framework commit, host setting claims, seed and limits.
- [Manual manifest](manual-manifest.json) records installed hashes, scenario inputs, tooling hashes and schedule.
- [Manual evidence](manual-evidence.json) retains the public requests, saved project content, changes, final responses and available observations.
- [Manual review](manual-review.json) contains the calibrated independent review bound to that evidence packet.
- [Manual report](manual-report.md) and [JSON report](manual-report.json) show the complete two-turn result.
- [Native preflight record](native-preflight.json) retains the failed probe, explicit host configuration and its evidence limits.

The manual subjects were created with `fork_turns="none"`, one new subject per run, and received only their consumer directory, an instruction to follow its installed AGENTS.md, a boundary against inspecting ancestor/sibling projects, and the exact public request.
They did not receive hidden criteria, future turns, other subjects' results, or the comparison rationale.
The two tasks use Direct behavior and do not establish native discovery or invocation of the installed skill catalog.
The user selected Astra/Ultra, but the host did not expose an independent model identifier, usage totals, active context occupancy, or native command trace to this controller.
Recorded elapsed time includes controller scheduling and evidence collection, rather than pure model runtime.

The same independent grader first completed the blind calibration, then judged the two subject outcomes from their packet.
That establishes successful calibration for this reviewer and rubric on these controls; it does not guarantee correctness for every future semantic judgment.
No transient action or external-system claim was treated as independently observed.

Raw consumers and checkpoint ZIPs remain outside Git under `/tmp/aw-manual-controls-001` in the execution workspace.
Native probe exhaust remains under `/tmp/campaign-native-preflight-subagents`.
Those temporary locations are not durable storage guarantees; the compact material above preserves the conclusions and their declared limits.

## Repeat or extend

Use the [runbook](../../README.md) from the exact delivered tooling revision.
Recreate calibration with `calibration-packet` and compare a fresh independently supplied review with `calibration-assess`.
To repeat these controls, freeze `evals/campaign/results/2026-10-03/manual-spec.json` into a new external directory and follow the manual `begin`/`record` protocol.
Never replace the observations in this retained run.

On a host where `python -m evals.campaign.codex --preflight` succeeds, freeze the 18-turn [smoke template](../../examples/smoke.json) using that host's actual model settings, then explicitly launch and grade it.
The next comparative screen uses the four candidates justified in [VERSIONS.md](../../VERSIONS.md), with matched settings and fresh trajectories.
That screen, long-context/compaction validation, and possible instruction adoption remain unexecuted experiments; they are not required to claim the source-only harness and the observed controls passed.
