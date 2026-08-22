# Fresh-agent continuation replication

- Status: completed

## Destination

Determine whether the fresh-agent Wayfinder instruction refinement has a
repeatable advantage over the matched previous-Wayfinder behavior by running a
frozen four-trajectory B/C replication, reporting v2 independently before a
separate descriptive v1+v2 view, and pushing the evidence only to
`experiment/wayfinder-fresh-agent-continuation`.

## Territory

- Frozen product: candidate `911c248c91bbeb0e0ad62f4329b9089f992b6005`,
  with no product, routing, or state-architecture changes during the campaign.
- Treatment isolation: B removes only the reviewed fresh-agent continuation
  instruction delta; C uses the candidate unchanged; prompts and runtime remain
  identical.
- Evaluation infrastructure: preserve v1, correct JSONL `file_change` write
  detection, and replace the empty inherited environment with one minimal
  explicit functional shell environment shared by B and C.
- Execution: preregister a balanced B/C order, freeze before the first live
  run, then execute four independent two-phase trajectories per condition with
  fresh ephemeral agents and isolated workspaces.
- Evidence and interpretation: grade correctness, durable-state quality,
  reconstruction behavior, authority safety, and efficiency without an opaque
  overall score or overstated significance.

## Current state

The completed v1 smoke and its qualified positive result are preserved in
[`../context-compiler-architecture/map.md`](../context-compiler-architecture/map.md).
Its artifacts under `evals/results/wayfinder-fresh-agent-continuation-v1/` and
the v1 campaign, prompt, fixture, treatment, grader, and raw evidence are
immutable historical evidence.

The frozen v2 campaign completed all 16 fresh live phases in the preregistered
B/C order. Preflight passed exact candidate/runtime, treatment-only diff,
byte-identical prompts, identical explicit environments, separate Git roots,
candidate fixture/grader provenance, and v1 immutability. Raw evidence remains
locally preserved; compact results and frozen-rubric semantic reviews are under
`evals/results/wayfinder-fresh-agent-continuation-v2/`.

V2 observed correct completion in B 4/4 and C 3/4. C2 lost the exact AMI fact
that phase one had preserved and manufactured a replacement required input.
Across the separate descriptive v1+v2 view, completion is tied B 4/5 and C 4/5,
while exact fact recovery is B 5/5 and C 4/5. Because v2 reverses the one-run v1
direction, the classification is **Unresolved**: the exact refinement has not
shown a repeatable advantage. No product behavior changed.

## Blockers and dependencies

None. Harness and result commits were pushed only to
`experiment/wayfinder-fresh-agent-continuation`.

## Next work

No further action is required for this campaign. Do not automatically run
further repetitions. If a later adoption decision needs a more stable failure
estimate, preregister a larger matched campaign as a separate effort.

## Notes

- Required runtime: `gpt-5.6-terra`, medium reasoning,
  `codex exec --ephemeral`, workspace-write sandbox, approval policy `never`,
  and a unique auth-only `CODEX_HOME` for every phase.
- B and C prompts must be byte-identical and explicitly invoke Wayfinder.
- Run exactly B x4 and C x4 additional trajectories; do not add A or
  automatically expand the sample.
- Preserve machine-reviewable treatment and environment equality evidence,
  unique execution/thread identifiers, raw evidence, primitive per-run results,
  and the preregistered order.

- Canonical report:
  [`evals/results/wayfinder-fresh-agent-continuation-v2/report.md`](../../evals/results/wayfinder-fresh-agent-continuation-v2/report.md).
- Frozen evaluator, preflight, summary, and per-run evidence sit beside the
  report. The harness is frozen at commit `f5ddbd0`.

The preregistered leading order is B, C, C, B across four paired repetitions;
within each pair both phase-one processes precede phase two and phase-two order
matches phase one. The exact order is canonical in the v2 campaign manifest.

## Out of scope

Product behavior changes, changes to v1 artifacts, generic A-condition runs,
additional automatic repetitions, main-branch mutation, merging, and product
adoption based on the result.
