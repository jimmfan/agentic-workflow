# T3: Run the smallest valid long-lived A/B/C smoke

- Status: done
- Blocked by: none
- Related: D1

## Outcome

Freeze and run one treatment-isolated, interruption-heavy infrastructure scenario across vanilla Codex, normal Agent Workflow routing, and explicit Wayfinder, with a true fresh-process resume and later authoritative evidence that conflicts with an earlier assumption.

## Acceptance

- The frozen rubric rewards equivalent vanilla behavior and separates engineering correctness, epistemic quality, continuity, Wayfinder mechanics, and cost.
- B demonstrably exercises justified automatic escalation; C exercises explicit Wayfinder; selected arms create and evolve useful local state.
- Specialized capability composition, fresh-session re-entry, stale-evidence reconciliation, and treatment isolation are observed.
- If the smoke does not exercise these mechanisms, stop instead of multiplying runs.

## Current blocker

The protocol, rubric, harness, scenario, treatment payload, and provider
projection are frozen. Deterministic self-checks pass. The first isolation audit
attempt proved the static separation checks but could not reach the model
service from the sandbox. Network escalation was denied because the synthetic
fixture and prompts would be sent to the external Codex service without a
separate explicit disclosure approval.

Recovery condition satisfied: the user explicitly authorized sending the
synthetic ARC fixture and frozen evaluation prompts to the Codex model service
for the three isolation probes and twelve fresh-process smoke phases. Resume by
rerunning the unchanged isolation audit; do not refreeze or edit critical files.

## Result

The frozen A/B/C smoke completed with clean isolation and all required
mechanisms exercised. Automatic B and explicit C created only canonical local
state, resumed in fresh processes, reconciled later evidence, and composed with
Implementation + Verification. B completed the final slice and respected every
phase boundary. A completed it but implemented prematurely during the mapping
phase. C's implementation is correct on manual inspection, but the frozen
grader missed its one-hop Terraform local indirection; no repetitions were run.
The original evaluation report and machine bundle remain available from Git
history at `911c248`; the current-tree bundle was removed by a later
user-authorized pre-1.0 repository cleanup.
