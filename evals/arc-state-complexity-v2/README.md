# ARC state complexity, protocol v2

This adapts the recovered six-phase branching-state test for the current campaign runner and current workflow versus vanilla.
The historical [report](https://github.com/jimmfan/agentic-workflow/blob/37e35b0be95b1b835f460af15187c91d915ca4dc/evals/reports/2026-08-15-arc-wayfinder-state-complexity-v1.md), campaign, evaluator and their outcomes remain evidence of the original protocol only.
[Provenance](provenance.json) binds the exact historical source hashes and current product commit.
No model run has been performed by preparing these files.

| Phase | Inputs and task | Required outcome |
|---|---|---|
| 1 | Four parallel workstreams; map only | Preserve exact AMI source; W1 unknown, W2 ready, W3 ownership blocked, W4 destination blocked |
| 2 | Delete transient platform-facts document; fresh implementation session | Consume preserved source and implement ready IAM/SSM without guessing compute |
| 3 | Add D1, benchmark and readiness contract; fresh reconciliation session | Approve dedicated m7i.large managed nodes, 2/2/6; distinguish cold versus warm evidence |
| 4 | Fresh implementation session | Implement authorized D1 slice; preserve independent W3/W4 blockers |
| 5 | Add D2, capacity evidence and SNS destination; fresh reconciliation session | Supersede instance size only; W4 becomes ready, W3 remains blocked |
| 6 | Fresh implementation session | Change size to m7i.xlarge, preserve valid work, implement complete alarm contract |

Both arms receive one identical frozen scenario and fixture, including every public prompt and transition.
The current arm installs commit `deb91942ac45373111a6bc615b359b2bbb230a68`; vanilla has an empty project workflow payload.
Native instructions and bundled system skills remain available identically through the same CLI and sandbox grants; no personal skill or configuration is copied.
The adapter records bundled skill content hashes for post-run comparison.
Unlike v1, there is no arm-specific `$wayfinder` prompt or map-syntax reward.
This measures the current workflow under neutral task requests, not adherence to the former explicitly invoked treatment.

## Fixture and grading repair

V1 supplied an SNS destination but omitted metric, dimensions, statistic, period, threshold, comparison, evaluation, missing-data and action semantics.
Its alarm-presence heuristic could reward invented requirements.
V2 supplies a complete synthetic [alarm contract](fixture/docs/observability-requirements.md) before the run and reveals the destination in phase 5.
The phase 6 rubric requires every field and rejects invented semantics.
If a requirement is missing or contradictory, asking or blocking the affected work is appropriate; missing implementation does not earn completion credit.
All judgments concern source fidelity, scoped blocking, safe progress, selective preservation and actual evidence, regardless of note format or workflow syntax.

The [ARC calibration corpus](calibration.json) has two valid layouts and six deliberate defects, with 48 expected judgments.
Every control includes an actual alarm Terraform resource, and the wrong-metric control changes that implemented resource.
State notes or intended settings alone cannot pass alarm completion.
The calibration request makes the approved destination explicitly satisfy the previously conditional blocker.
The common initial fixture supplies the formatting-check obligation before phase 2.
Export only its blind packet to an independent reviewer using `evals.campaign calibration-packet`, then assess the returned review before scoring subjects.
The scenario rubric and calibration answers never enter the subject prompt, workspace or granted read roots.
A calibrated independent semantic review is still required for a behavioral PASS.

## Runner changes and budget

Frozen `before_turn` creates/deletes are limited to supplied documents, refuse collisions, and retain separate controller-before snapshots plus hashed transition evidence.
Each phase has its own session label/home and must start with a new native session ID.
Both arms receive the same explicit continuation-file permission: `.md`, `.txt`, `.json`, `.yaml`, `.yml`, or `.toml` files under arbitrary names and directories outside infrastructure, tests, installed framework locations and supplied source documents, including reserved decision/benchmark locations.
New parent directories are permitted only for allowed regular files; symlinks and empty ungranted directories remain rejected.
Existing continuation files may be updated; mapping phases protect all Terraform files, and implementation phases allow only the five declared `.tf` paths.
The interrupted revision-3 attempt exposed a mismatch between broad public format permission and a narrow hidden filename allowlist.
Revision 4 repairs that mismatch prospectively; retained old artifacts and mechanical outcomes are not changed.
Protected supplied documents and tests cannot be changed for grading credit.
The explicit vanilla payload, subscription-only authentication overrides and explicit Fast-disabled setting are frozen before execution.
The native interpreter retains the canonical-path fix from `4a2b5be`.

Proposed budget: one six-phase trajectory per arm, 12 subject calls maximum, 300 seconds per phase, a 3900-second campaign launch window, and no automatic retry.
Use `gpt-6.1-sol`, medium reasoning, subscription authentication, standard/default service with Fast disabled, and no subject subagents for both arms.
These limits cap invocation count and time, not subscription tokens or credits.
The disabled-subagent setting is a restricted host condition and may prevent workflow-required independent review; record that separately from common outcomes.
The two arms are serialized in a seeded order; one pair is a feasibility observation, not a reliability estimate or causal attribution to an individual instruction.

Preparation revision 5 uses the explicitly approved full 3900-second campaign budget with standard/default service with Fast disabled and no additional absolute wall-clock cutoff.
It supersedes the earlier 03:30 UTC limit only for a new unstarted preparation; earlier freezes remain retained and unchanged.
The 12-call limit, 300-second phase deadline and no-retry rule remain active.
The Terminal launcher supervises the full controller for 3900 seconds, stops only its owned descendant process groups on timeout/interruption, and removes only credential copies whose session ownership matches this campaign.
The launcher prints a flushed start banner, log locations, phase starts/completions and a heartbeat at most 30 seconds apart; completion counts describe execution, with semantic grading pending.
It prints the retained audit path on interruption, timeout or exit and refuses every reused campaign before tooling-drift checks.
Shutdown may take up to 15 seconds after model work is stopped; abrupt untrappable termination still requires manual inspection of retained state.
An optional `--launch-before` can freeze an absolute launch cutoff for separately constrained preparations.

## User-operated handoff

Run from the retained tooling checkout in a normal Terminal because nested macOS Seatbelt initialization may fail inside an agent shell.
Use a fresh independent canonical output location and the selected native binary.
Preparation is model-free; preflight uses only synthetic canaries and never copies authentication.
Only the explicitly invoked `run` command consumes model allowance and temporarily uses the user's existing authentication through the adapter.
The launcher refuses failed preflight, reused campaigns, mismatched frozen inputs, or an expired optional launch cutoff.

```bash
python3 -m evals.campaign.arc_launch prepare --out <canonical-output> --binary <native-binary>
python3 -m evals.campaign.arc_launch preflight --out <canonical-output>
python3 -m evals.campaign.arc_launch run --out <canonical-output>
```

Retain raw requests, traces, snapshots, session homes and native results outside the subject read roots and Git.
Sanitize machine paths and identifiers before publishing evidence.
Do not weaken isolation or fall back to API authentication if native setup fails.
An ungraded completed run normally remains INCONCLUSIVE and may exit 2.

## Evidence limits and prereview

The unchanged offline safety suite checks a few forbidden-resource patterns; it does not prove Terraform validity or cloud readiness.
Provider downloads, init, plan, apply and external changes are prohibited.
Transient-source deletion removes the current file, not its original Git history; a subject may recover it from the baseline, which must be reported when interpreting continuity.
Final snapshots cannot establish absence of transient writes; retained native traces may have observation gaps.
System-skill hashes must be compared after both arms, and an observed mismatch is a confound rather than product evidence.
The latest user request disables Fast for prospective tests.
Both isolated sessions set `features.fast_mode=false` and omit `service_tier`, using the standard/default request rather than guessing a literal `"default"` value.
The [official configuration reference](https://learn.chatgpt.com/docs/config-file/config-reference) describes service tiers as optional model-advertised selections.
Actual response service tier remains unverified until execution metadata is available; historical Fast evidence is unchanged.

Contextual prereview checked the six recovered stages, exact D1/D2 boundaries, complete W4 semantics, neutral requests/rubric, protected inputs, fresh sessions, no retry, and the approved full campaign budget.
Deterministic controls exercise all six phases with synthetic response envelopes, transition drift, collision rejection, escaped paths, subscription and Fast-on/Fast-off overrides, keyless child environment and cutoff behavior.
These controls do not constitute live behavior or independent grading.
Native preflight and independent reviewer calibration remain required before launch and scoring respectively.
