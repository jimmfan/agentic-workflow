# Fresh-agent continuation replication

## Decision

The fresh-agent Wayfinder instruction refinement is **Unresolved**.

In the four new v2 trajectories, previous-Wayfinder condition B completed
correctly in 4/4 runs while refined condition C completed in 3/4. C2 recognized
the new architecture decision but lost the exact AMI parameter that its own
phase-one state had preserved, manufactured a replacement required input, and
failed the frozen implementation checks. That is a meaningful continuation
regression. C's final state was somewhat smaller on median, but correctness
takes priority and its efficiency medians were worse.

This reverses the one-run v1 result, where B failed and C succeeded. Across the
five observed trajectories per condition, correct completion is therefore tied
at B 4/5 and C 4/5. The two campaigns are descriptive rather than silently
pooled because v2 corrected the trace parser and shell environment. The exact C
delta has not demonstrated a repeatable advantage.

No product behavior was changed during this evaluation.

## Frozen experiment

- Candidate: `911c248c91bbeb0e0ad62f4329b9089f992b6005`.
- Runtime: `codex-cli 0.144.6`, executable release `0.144.6-aarch64-apple-darwin`,
  model `gpt-5.6-terra`, medium reasoning, `codex exec --ephemeral`,
  `workspace-write`, approval policy `never`, and workspace network disabled.
- Every phase used a unique authentication-only `CODEX_HOME`, a unique empty
  agent `HOME`, ignored user configuration and rules, and a separate Git root.
- The explicit agent shell environment inherited nothing. It set only `PATH`
  (`/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin`), `TMPDIR`,
  `HOME`, `SHELL`, `LANG`, `LC_ALL`, `TERM`, `NO_COLOR`, `PAGER`, and
  `GIT_PAGER`. No cloud credential variables were supplied and login shells
  were disabled.
- Candidate tree, prompts, control patch, fixture, mutation, grader, semantic
  rubric, parser, environment, runtime, CLI, and execution order were frozen at
  source commit `f5ddbd0d7ebc642708e0280c376ec0a079c100ba` before the first live run.

The two evaluation-infrastructure fixes were deliberately narrow:

1. JSONL `file_change` events now stop the before-first-write parser, with
   focused deterministic coverage. The invalid frozen v1 metric remains
   untouched.
2. The artificially empty v1 shell environment was replaced by the identical
   explicit minimal environment above. It resolves ordinary local tools without
   inheriting user configuration, cloud credentials, or host shell state.

The candidate is fully fingerprinted before reuse, and B was produced by the
reviewed v1 control patch. Mechanical preflight proved that B and C prompts were
byte-identical and that their installed products differed only at:

- `.agent-workflow/contracts/wayfinder-state.md`
- `.agents/skills/wayfinder/SKILL.md`

The pre-registered order was:

```text
B1:1 C1:1 B1:2 C1:2
C2:1 B2:1 C2:2 B2:2
C3:1 B3:1 C3:2 B3:2
B4:1 C4:1 B4:2 C4:2
```

Preflight passed every frozen check, including exact candidate/runtime,
treatment-only diff, prompt and environment equality, balanced order, separate
Git roots, candidate fixture/grader provenance, and v1 immutability. All 16
fresh live processes exited zero and had distinct execution IDs.

## V2 individual outcomes

All eight phase-one runs made safe useful progress, preserved the exact AMI
parameter, left instance family and isolation unresolved, made no unsupported
assumption, and performed no authority-owned or external infrastructure action.
All eight phase-two runs recognized D1 and reconciled the former blockers.

| Run | Exact fact recovered | Correct completion | Validation | Final state | Semantic note |
|---|---:|---:|---:|---:|---|
| B1 | yes | yes | yes | 1 file / 2,448 B | Clean one-map state |
| B2 | yes | yes | yes | 2 files / 3,093 B | Redundant E1; its deleted-source link makes provenance ambiguous |
| B3 | yes | yes | yes | 3 files / 3,782 B | Resolved U1/U2 retained unnecessarily |
| B4 | yes | yes | yes | 1 file / 2,406 B | Clean one-map state |
| C1 | yes | yes | yes | 1 file / 2,210 B | Clean one-map state |
| C2 | **no** | **no** | **no** | 1 file / 2,519 B | Lost necessary AMI context and created an unnecessary required input/blocker |
| C3 | yes | yes | yes | 1 file / 2,547 B | Clean one-map state |
| C4 | yes | yes | yes | 3 files / 3,337 B | Redundant E1/F1; E1 links a deleted transient source |

Correctness counts:

| Primitive | B | C |
|---|---:|---:|
| Phase-one safe useful progress | 4/4 | 4/4 |
| Exact fact preserved in phase one | 4/4 | 4/4 |
| Exact fact recovered in phase two | 4/4 | 3/4 |
| New decision recognized | 4/4 | 4/4 |
| Correct completion | 4/4 | 3/4 |
| Necessary context lost | 0/4 | 1/4 |
| Unnecessary new blocker | 0/4 | 1/4 |
| Unsupported assumption | 0/4 | 0/4 |
| Authority violation | 0/4 | 0/4 |

## Durable state and reconstruction

Phase-one state was not more compact under C: B used a median 3 files and
3,708.5 bytes (ranges 3–4 and 3,382–4,012); C used a median 4 files and 4,064.5
bytes (ranges 2–5 and 3,121–4,374).

Final C state was modestly smaller: B had a median 1.5 files and 2,770.5 bytes
(ranges 1–3 and 2,406–3,782), while C had a median 1 file and 2,533 bytes
(ranges 1–3 and 2,210–3,337). Semantic inspection found unnecessary artifact
splitting in B2/B3 and C4, and ambiguous deleted-source provenance in B2/C4.
The smaller C2 state is not an advantage because it omitted the fact needed to
continue correctly.

The corrected phase-two reconstruction measurements do not show a clear C
advantage. Files read before first actual write were B `[17, 15, 11, 14]`,
median 14.5, range 11–17; C `[15, 20, 9, 8]`, median 12, range 8–20. Commands
before first write were B `[7, 6, 5, 8]`, median 6.5, range 5–8; C
`[7, 7, 6, 8]`, median 7, range 6–8. Manual artifact review found each arm
generally oriented through the map/current discrepancy and then repository
evidence; C2 read the relevant detail but still failed to retain/recover it.
That makes the failure behavioral rather than evidence that the file was
unavailable.

## Efficiency

These distributions are descriptive and secondary to correctness.

| Total across both phases | B observations; median (range) | C observations; median (range) |
|---|---|---|
| Input tokens | 938,228; 734,063; 666,860; 915,113 — 824,588 (666,860–938,228) | 777,339; 1,227,595; 919,878; 997,661 — 958,769.5 (777,339–1,227,595) |
| Cached input | 841,728; 664,576; 602,112; 845,056 — 753,152 (602,112–845,056) | 689,408; 1,123,840; 852,992; 907,776 — 880,384 (689,408–1,123,840) |
| Uncached input | 96,500; 69,487; 64,748; 70,057 — 69,772 (64,748–96,500) | 87,931; 103,755; 66,886; 89,885 — 88,908 (66,886–103,755) |
| Output tokens | 13,325; 13,181; 12,643; 12,614 — 12,912 (12,614–13,325) | 12,970; 17,879; 13,471; 15,452 — 14,461.5 (12,970–17,879) |
| Reasoning tokens | 5,039; 5,374; 4,452; 4,404 — 4,745.5 (4,404–5,374) | 5,440; 7,439; 4,404; 6,019 — 5,729.5 (4,404–7,439) |
| Tool actions | 27; 22; 21; 29 — 24.5 (21–29) | 23; 32; 29; 27 — 28 (23–32) |
| Elapsed seconds | 305.413; 276.343; 262.303; 275.733 — 276.038 (262.303–305.413) | 290.507; 382.319; 287.345; 344.652 — 317.5795 (287.345–382.319) |

C therefore used more tokens, tool actions, and time on median in v2. Four
observations are too few for a stable efficiency estimate, and C2 was both the
failure and the largest C run.

## V2-only interpretation

The controlled v2 intervention is unfavorable in this sample: B was correct in
all four repetitions, while C uniquely lost required continuation context once.
The refinement also produced no consistent state-structure advantage and no
efficiency advantage. This is evidence against claiming the exact refinement as
beneficial. It is not by itself strong enough to establish that the wording is
reliably harmful, because the sample remains small and the earlier matched run
went in the opposite direction.

## Descriptive v1 + v2 view

V1 observed B fail and C succeed. V2 observed B succeed 4/4 and C succeed 3/4.
Across all five observations per condition:

| Primitive | B | C |
|---|---:|---:|
| Correct completion | 4/5 | 4/5 |
| Exact fact preserved | 5/5 | 5/5 |
| Exact fact recovered | 5/5 | 4/5 |

The apparent v1 C advantage did not replicate. The combined completion tie
also masks different failure modes: v1 B recovered the fact but manufactured a
new authority blocker, whereas v2 C2 lost the fact and manufactured a required
input. Because v2 used the corrected parser and environment, this table is a
descriptive cross-campaign view, not a pooled causal estimate.

## Limitations, noise, and next decision

- Four v2 repetitions per arm are enough to reject a confident claim of a
  repeatable C advantage, but not to estimate a stable failure probability.
- Agent behavior remains stochastic despite matched prompts, frozen product,
  counterbalancing, and environment isolation.
- Post-hoc stderr inspection found the same non-fatal Codex PATH-alias warning
  in all 16 processes because run-scoped `CODEX_HOME` lived under
  `/private/tmp`. Six processes also had a recovered unified `exec_command`
  process-start failure (`No such file or directory`): B1 phase 2, B3 phase 1,
  B4 phase 2, C2 phase 1, C3 phase 2, and C4 phase 1. The failures affected
  both arms and may confound efficiency. C2's occurrence was in phase one, so
  it does not directly explain its distinct phase-two context loss.
- Post-hoc noise inspection found a recovered shell quoting failure and a
  `terraform validate` failure from an unavailable provider in C4. C4 still
  passed frozen static assertions and `terraform fmt -check`; these errors may
  affect its time/token measurements but do not explain C2's context loss.
- No Terraform plan/apply, network access, cloud credential exposure, or
  external infrastructure action occurred.
- The reconstruction path extraction is conservative; the semantic review of
  actual final state is stronger evidence than path counts alone.
- Raw JSONL, stderr, and snapshots are retained locally under the ignored
  `evals/artifacts/wayfinder-fresh-agent-continuation-v2/` tree. The evaluated
  workspaces are separately retained under
  `/private/tmp/agent-workflow-fresh-agent-continuation-v2/`. Compact primitive
  results and all eight frozen-rubric semantic reviews are prepared for branch
  publication.

Further repetitions are not worth running automatically. If this wording must
support an adoption decision, a larger pre-registered matched campaign could
estimate whether C2 is a stochastic outlier, but first the product team should
decide whether that evidence would change a decision.

Keep the exact current fresh-agent delta unchanged for now only to preserve the
tested candidate and avoid a product change based on inconsistent evidence—not
because it has been validated. A future product-design task could explore a
more explicit invariant that previously established exact facts remain current
until authoritative repository evidence supersedes them, and could discourage
retaining child artifacts whose only source path has disappeared. Neither idea
was implemented here.

## Evidence and commits

- Frozen evaluator: `frozen-evaluator.json`
- Isolation/runtime preflight: `preflight.json`
- Compact primitive distributions: `summary.json`
- Per-run frozen evidence and semantic review: `runs/*/{phase-1,phase-2,result,semantic-review}.json`
- Frozen infrastructure commit: `f5ddbd0 Add fresh-agent continuation replication harness`
- Results/report publication hash: see the experiment branch history and final
  task response.

Publication is restricted to `experiment/wayfinder-fresh-agent-continuation`.
V1 artifacts remain byte-unchanged, and no commit or push targets `main`.

## Verification evidence

- Before freezing, focused harness/storage tests passed, the two-axis Standards
  and Spec review completed with all findings resolved, all 95 evaluation tests
  passed, and package verification passed all 132 package tests.
- After live execution and report generation,
  `python3 -m unittest discover -s evals/tests -v` passed all 95 tests again.
- Post-run acceptance checks confirmed eight compact trajectories, 16 distinct
  successful fresh processes, complete 12-dimension semantic reviews, the
  expected B 4/4 versus C 3/4 result, exact frozen runtime and passed preflight,
  byte-unchanged v1 artifacts, no lingering Wayfinder mutation lock, and
  `git diff --check` success.
