# Fresh-agent continuation replication

- Status: current

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

The v2 harness is implemented on
`experiment/wayfinder-fresh-agent-continuation`. It archives the product and
fixture from `911c248c`, creates eight separate Git roots, reuses the reviewed
v1 control patch, and mechanically rejects any B/C difference outside the two
treatment paths. V1 paths are checked against branch baseline `46a08a9` and
remain unchanged.

The corrected JSONL parser ends the reconstruction window on the first
`file_change` event. Each Codex process receives a unique auth-only
`CODEX_HOME`; spawned agent shells inherit nothing and receive only an explicit
fixed PATH, empty run-scoped HOME, locale, terminal, and pager values. Login
shells and workspace-write network access are disabled. The frozen semantic
rubric keeps correctness and state-quality review separate from efficiency.

Focused v2/storage tests, all 92 evaluation tests, and all 132 package tests
pass. No live evaluated process has started and no frozen v2 result exists yet.

## Blockers and dependencies

- Live execution remains blocked on the pre-live two-axis review, committing the
  reviewed harness, freezing all inputs, and passing recorded preflight.
- Once the first evaluated run starts, the campaign is immutable. Any further
  harness defect must be recorded rather than repaired unless it invalidates
  the campaign, in which case execution stops.

## Next work

Complete the Standards and Spec review. Resolve any findings, commit the
reviewed harness, freeze the candidate/treatment/prompts/fixture/mutation/grader/
rubric/parser/environment/runtime/order, and run recorded preflight immediately
before the first trajectory.

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

The preregistered leading order is B, C, C, B across four paired repetitions;
within each pair both phase-one processes precede phase two and phase-two order
matches phase one. The exact order is canonical in the v2 campaign manifest.

## Out of scope

Product behavior changes, changes to v1 artifacts, generic A-condition runs,
additional automatic repetitions, main-branch mutation, merging, and product
adoption based on the result.
