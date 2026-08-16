# ARC Wayfinder state-complexity v1 smoke

- Campaign ID: `arc-wayfinder-state-complexity-v1`
- Status: **completed; final W4 comparison confounded by a frozen-fixture defect; repetitions stopped**
- Authorized program ticket: [T4 — Run branching-state complexity smoke](../../../.ai-workflow-state/wayfinder/evaluation-program/tickets/T4-branching-state-complexity-smoke.md)
- Repetitions: one six-phase trajectory per condition; no repetitions authorized
- Product scope: evaluation state, fixture, harness, evidence, and reports only

## Purpose

This campaign tests whether explicit Wayfinder provides net value over a strong
repository-native handoff when a project has four parallel workstreams,
selective blockers, disappearing exact facts, decisions that resolve only part
of the state, a later partial supersession, existing implementation that must
remain valid, and a newly actionable branch. It is a distinct state-complexity
scenario, not an ARC Wayfinder v3 correction.

## Conditions and execution

- **A — Vanilla Codex + strong neutral durable handoff:** no Agentic Workflow;
  agents were explicitly asked to leave useful repository-native continuation
  state and chose one cohesive handoff document.
- **B — Agentic Workflow + explicit Wayfinder:** the frozen Agentic Workflow
  installation; mapping phases explicitly invoked `$wayfinder`, and
  implementation phases used normal downstream routing.

Both conditions used `gpt-5.6-terra`, medium reasoning, workspace-write,
approvals `never`, disabled shell-environment inheritance, identical network
policy, and six sequential fresh `codex exec --ephemeral` processes with no
resume. The completed runs are:

- A: `arc-state-a-1-174f804555`
- B: `arc-state-b-1-de289d15a9`

All twelve processes exposed unique execution IDs and exited 0.

## Frozen evidence boundary

The machine campaign definition, harness, fixture, phase mutations, prompts,
and semantic-review rubric were frozen before live execution. The freeze:

- was recorded at `2026-08-16T00:13:43.731968+00:00`;
- contains 24 critical-file SHA-256 digests;
- records source Git SHA `205989bd81008c75e6f216cd97c7202eb0ac40e0`;
- has manifest SHA-256
  `120a1796d01a4689e8e7820acad40dafbc8d27dd34a399829deaf2cf89cd8668`;
- records Agentic Workflow `0.11.1` and installed-artifact SHA-256
  `c5527e63b68a5f25cc70202c68a246dc8b0e61afcb798c90a83699a6052b70f8`
  for B.

Deterministic grading is limited to objective repository, Terraform, diff,
command, and explicit Wayfinder-contract fields. Arbitrary prose produces exact
path/line/snippet evidence with `manual_review_required`; no broad
keyword-window classifier is used.

## Isolation gate

The final audit passed before workspace preparation or evaluated execution. It
verified two disposable Git roots outside the controller hierarchy, no parent
`AGENTS.md` leakage, auth-only temporary `CODEX_HOME`, ignored user config and
rules, empty inherited shell environment, no cloud credentials, no
controller/sibling canary, unique ephemeral execution IDs, no resume, grader
and raw capture outside the workspaces, no Agentic Workflow in A, and the exact
frozen installation in B.

The first preserved preflight attempt failed only because the controller
sandbox denied network name resolution; no evaluated agent ran. The identical
frozen audit was then rerun with authorized network access and passed. That
failed attempt remains under `preflight/attempt-1/` rather than being hidden.

## Result boundary

The campaign cleanly exercised branching state and produced valid comparisons
through Phase 5 and for Phase 6's selective W1 supersession. Both arms:

- preserved, found, trusted, and implemented `/platform/arc/runner-ami`;
- completed safe W2 IAM/SSM work before W1 resolution;
- incorporated D1 without reviving stale `m6i`;
- completed the authorized W1/W2 slice while W3 and W4 stayed isolated;
- incorporated D2 as an instance-size-only supersession;
- changed `m7i.large` to `m7i.xlarge` without invalidating the remaining D1
  choices or unrelated W2 code;
- left W3 blocked and untouched; and
- made no external infrastructure change.

The apparent Phase 6 W4 result is **not a valid Wayfinder advantage**. The
frozen fixture described the SNS destination as W4's only missing input, but it
never supplied the alarm namespace, metric name, dimensions, threshold,
comparison operator, period, statistic, or evaluation window. A's fresh agent
noticed those missing semantics and safely declined to invent them. B's Phase
5 reconciliation dropped its earlier missing-input note, marked W4 ready, and
B's fresh implementation agent invented those values. The frozen grader checked
only for an alarm and the supplied ARN, so it rewarded unsupported
implementation. The result and grader output remain unchanged; the defect is
interpreted in the report and manual review.

Because that defect affects the campaign's intended newly-unblocked branch and
headline Phase 6 completion vector, the experiment is not clean enough to
repeat unchanged or to support a causal product conclusion. No overall score,
statistical claim, automatic-routing change, Wayfinder change, or product
behavior change is made.

## Evidence

- [Final report](../../reports/2026-08-15-arc-wayfinder-state-complexity-v1.md)
- [Manual semantic review](manual-review.md)
- [Product and tooling issues](product-issues.md)
- [Frozen evaluator](frozen-evaluator.json)
- [Final isolation audit](context-isolation-audit.json)
- [Condition A result](runs/arc-state-a-1-174f804555/result.json)
- [Condition B result](runs/arc-state-b-1-de289d15a9/result.json)
- [Preserved failed preflight](preflight/attempt-1/context-isolation-audit.json)

The result namespace also retains 12 phase JSON files, 12 raw JSONL/stderr
pairs, 12 repository snapshots, and the successful audit probes. Temporary
evaluated workspaces may be removed only after this evidence is persisted;
cleanup never removes these artifacts.

Guarded cleanup completed after report persistence. It removed only the two
completed disposable run directories, reclaiming 1,776 KiB of actual filesystem
blocks (648 KiB for A and 1,128 KiB for B). All durable evidence listed above
remains present.
