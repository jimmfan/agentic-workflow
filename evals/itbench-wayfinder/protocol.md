# ITBench Wayfinder controlled evaluation protocol

Status: preregistered; no evaluated agent outputs examined

Campaign ID: `itbench-wayfinder-v1`

## Research question

Does the frozen current Agent Workflow improve Codex diagnosis of Kubernetes
incidents under causal uncertainty, and does explicit Wayfinder invocation add
value beyond the workflow's normal routing?

The three primary conditions are:

- A — vanilla Codex, with no Agent Workflow instructions, skills, routing, or
  durable state exposed;
- B — the frozen current Agent Workflow and complete capability projection,
  with no explicit Wayfinder or Domain Modeling request; and
- C — the byte-identical frozen workflow installation used by B, with explicit
  `$wayfinder` invocation and no independent Domain Modeling request.

Domain Modeling, Debugging, Research, and every other current capability remain
available naturally in B and C. Their actual invocation is observed, not
assigned as a treatment.

## Benchmark boundary

Use the six public offline snapshots in the Artificial Analysis ITBench-AA SRE
dataset: Scenario-102, Scenario-34, Scenario-83, Scenario-17, Scenario-24, and
Scenario-80. The dataset revision and every selected file hash must be frozen in
the generated manifest before execution. `ground_truth.yaml` is controller-only
and must not appear in an evaluated workspace or agent-visible snapshot tree.

The snapshots are read-only evidence captures, not live clusters. Agents have
ordinary local shell/file inspection but no benchmark-specific MCP tools and no
network. This preserves treatment equivalence and makes runs reproducible, but
cannot establish live state, run new Kubernetes queries, or test remediation.

The current upstream ITBench, ITBench SRE Agent, ITBench Evaluations, Stirrup,
and dataset commits are provenance. When a current live-scenario definition
differs from the published ITBench-AA snapshot, the frozen ITBench-AA snapshot
and its `ground_truth.yaml` govern this campaign.

## Agent prompt

The neutral prompt template for A and B is:

```text
Diagnose the Kubernetes SRE incident represented by the read-only offline
snapshot at:

{snapshot_path}

Use local shell and file-inspection tools to investigate the snapshot. It is a
recording, not a live cluster: do not use the network, alter the snapshot, or
attempt remediation.

Identify the smallest set of independent root-cause Kubernetes entities that
explains the incident. Write the final diagnosis as valid JSON to:

{output_path}

Use this schema:
{
  "root_causes": [
    {
      "kind": "Kubernetes kind",
      "name": "observed entity name",
      "namespace": "observed namespace or null",
      "condition": "concise explanation of the causal fault"
    }
  ],
  "summary": "concise diagnosis and causal propagation explanation"
}

Use entity kind, name, and namespace exactly as supported by the snapshot.
Do not include a downstream symptom merely because it is unhealthy.
```

Condition C receives exactly the same text prefixed by:

```text
$wayfinder
```

The minimal-cause and symptom distinction are part of ITBench-AA's published
task definition and scoring target. The prompt deliberately does not mention
hypothesis tracking, unknown preservation, evidence categories, ownership,
visibility boundaries, Domain Modeling, Debugging, Research, or the reasoning
rubric.

## Frozen execution policy

- Model: `gpt-5.6-terra`.
- Reasoning effort: `medium`.
- Codex CLI: exact version recorded at freeze time.
- One fresh `codex exec --ephemeral` process and unique minimal `CODEX_HOME` per
  run; only the existing authentication material is copied.
- Ignore user config and user rules; inherit only a minimal non-secret shell
  environment; approval policy `never`; workspace-write sandbox; no network in
  the task contract.
- Timeout: 1,800 seconds per run.
- No automatic retry for a completed or timed-out agent run. Infrastructure
  launch failure before model execution may be retried once and must be marked.
- Each run gets a fresh Git workspace. A contains no Agent Workflow files.
  B and C receive byte-identical installations made from the frozen working-tree
  product snapshot.
- Raw JSONL, stderr, workspace snapshot, final diagnosis, elapsed time, token
  usage, and tool events are captured outside the evaluated workspace.

## Ordering and repetitions

Use deterministic seed `20260816`. For repetition 1, generate a balanced
scenario-blocked order: every scenario receives one A/B/C permutation, with the
six permutations used once before repetition. The manifest records the exact
order before execution. Runs are sequential to avoid resource contention and
cross-run environmental drift.

First run one complete A/B/C pass over all six scenarios (18 runs). From those
runs, calculate observed elapsed time and token usage. Proceed to repetitions 2
and 3 only if both are true:

1. the additional 36 runs are operationally practical under the remaining
   execution window and local storage; and
2. the first pass has no fairness or infrastructure defect that would make
   repetition invalid.

If either condition fails, stop at 18 rather than selectively repeating a
favorable subset. Preserve A/B/C and all six scenarios. Record the reduction as
preregistered resource methodology, not an experimental result.

## Native scoring

Implement a deterministic **ITBench-AA public-data derivative** of the
published average-precision-at-full-recall rule over the frozen public ground
truth:

- map every submitted `(kind, name, namespace)` to ground-truth groups using the
  frozen group filters and aliases;
- record true-positive, false-positive, and missing root-cause entities;
- if any ground-truth root cause is missing, native score is `0`;
- otherwise native score is `TP / (TP + FP)`; and
- success means full recall with no false positives (native score `1`).

Preserve prediction order and raw submitted entities. Do not use the
reasoning-quality rubric to alter native entity matches. Any ambiguous entity
normalization requires a blinded manual adjudication packet and cannot be
silently guessed.

The exact private ITBench-AA evaluator and agent prompt are not published, so
this campaign is not an exact leaderboard reproduction. The label above must be
used in artifacts and reports; comparisons are internal across A/B/C under the
same frozen matcher.

## Reasoning and capability evaluation

Use the separately frozen `reasoning-rubric.md`. Grade observable transcripts,
tool outputs, and final diagnoses after all evaluated runs in the authorized
pass complete. Never expose the rubric, ground truth, other runs, scenario
summaries, or reference trajectories to an evaluated agent.

For B and C, infer capability invocation from direct evidence: skill reads,
provider artifacts, route markers, and material skill-specific actions. A mere
installed skill name is not invocation. Record Wayfinder, Domain Modeling,
Debugging, Research, and any other material capability separately, including
interactions and apparent overhead.

## Analysis commitments

Report A versus B, B versus C, and A versus C separately. Do not combine native
correctness and reasoning quality into an opaque score. Distinguish evidence,
interpretation, and possible future experiments. Do not modify the product,
benchmark inputs, native rule, or frozen rubric in response to any run.
