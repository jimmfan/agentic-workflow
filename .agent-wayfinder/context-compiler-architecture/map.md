# Fresh-agent continuation evaluation

- Status: current

## Destination

Produce and push a frozen, controlled A/B/C smoke that causally tests whether
the fresh-agent Wayfinder instruction delta improves continuation, without
changing product behavior or contaminating the current dirty worktree.

## Territory

- Product delta: exact candidate commit and matched instruction-only control.
- Existing evidence: prior continuation experiments, fixtures, harnesses,
  graders, isolation, and metrics that can be reused.
- Experiment: frozen prompts, one multi-phase scenario, ephemeral agents, and
  independent A/B/C artifacts.
- Interpretation: correctness and state quality first; efficiency metrics stay
  separate and causal B-vs-C remains distinct from A-vs-C.
- Delivery: raw evidence, report, verification, commit, and push only to
  `experiment/wayfinder-fresh-agent-continuation`.

## Current state

Candidate is `911c248c91bbeb0e0ad62f4329b9089f992b6005`; local `main`, the
experiment branch, and both remote refs resolved to it before evaluated work.
Commit `9e4574d` contains the fresh-agent wording plus unrelated migrations, so
an older revision is not a valid control. The control must remove only the exact
instruction delta from the candidate.

The existing `resume` fixture is the minimal causal scenario: phase one exposes
the exact AMI parameter `/platform/eks/runner/ami/latest` while instance family
and isolation remain unresolved; the controller then deletes that source and
commits the missing decisions before a fresh phase-two process. Prior resume and
ARC campaigns establish useful infrastructure and historical context, but none
compare this exact instruction delta against a matched control.

The new campaign freezes one run per condition using `gpt-5.6-terra`, medium
reasoning, `codex exec --ephemeral`, an auth-only per-process `CODEX_HOME`, and
separate Git roots. B and C use identical prompts and candidate `911c248`; B
applies a reviewed patch to only the installed Wayfinder skill and state
contract. Deterministic campaign, treatment, fixture, grading, and storage tests
pass.

The one-run smoke is positive but provisional. A lost the exact AMI path and
crossed the unresolved isolation boundary. B preserved and recovered the path
but replaced the newly resolved blockers with an unnecessary launch-contract
blocker, so it did not implement. C preserved/recovered the path, reconciled and
retired the resolved unknowns, implemented the node group, and passed the frozen
implementation and validation checks. Final C state is one 2,331-byte map; B is
three files totaling 4,295 bytes. C also used fewer tokens and less elapsed time
than B, but one run and recovered CLI errors make efficiency inconclusive.

All six processes have distinct execution IDs and preflight passed. The frozen
reconstruction parser failed to stop at JSONL `file_change` events, so its
reported pre-write file count is excluded. Post-hoc event ordering gives 11
commands / 18 conservative path-like reads for B and 10 / 16 for C before the
first file change. Raw stderr also records asymmetric recovered process/patch
failures, so additional matched repetitions are warranted after fixing runner
noise.

## Blockers and dependencies

No experiment blocker remains. Product adoption remains intentionally unsettled:
one stochastic run does not prove repeatable causality, and the user authorized
recommendations rather than product changes.

## Next work

Verify the frozen evidence package and report, commit only experiment artifacts,
and push the detached commit to `experiment/wayfinder-fresh-agent-continuation`.
Recommend four additional randomized/counterbalanced repetitions after runner
noise and the trace parser are fixed; do not run them in this campaign.

## Notes

- The current primary worktree contains an unrelated, apparently interrupted
  workflow-implementation simplification; it remains untouched.
- Do not create a context compiler, modify candidate behavior, or start a large
  repetition campaign.

## Out of scope

Product fixes, routing changes, release work, `main` mutation, and merge work.
