# Fresh-agent continuation instruction smoke

## Result

The fresh-agent continuation refinement produced the best continuation outcome
in this one controlled smoke, but the evidence is **positive and provisional**,
not sufficient to claim a reliable causal improvement.

Condition C (current instructions) was the only arm that preserved and recovered
the disappearing AMI parameter, reconciled the newly resolved architecture
blockers, implemented the now-justified runner node group, and passed the frozen
static and Terraform validation checks. Condition B (the matched instruction-only
control) preserved and recovered the exact AMI parameter but replaced the
resolved blockers with a new launch-contract blocker and did not implement the
node group. Condition A (generic durable handoff) failed to preserve the exact
parameter and prematurely chose an isolation model in phase one.

This is the observed effect of the controlled intervention in this sample. One
stochastic agent per condition cannot establish that the effect is repeatable,
and transient CLI failures add noise. Additional matched repetitions are
warranted before adopting the wording as causally validated.

## What was tested

- Candidate product: `911c248c91bbeb0e0ad62f4329b9089f992b6005`.
- A — generic repository-native durable handoff, with no Agent Workflow install.
- B — the same candidate and explicit Wayfinder prompt as C, with only the fresh-
  agent persistence-admission and progressive-loading instruction delta removed.
- C — the current candidate fresh-agent Wayfinder instructions.
- Fixture: the existing two-phase `resume` scenario. Phase one exposes
  `/platform/eks/runner/ami/latest` while instance family and isolation remain
  unresolved. The controller then deletes that source and commits the approved
  `m7i`/dedicated-node-group/private-networking decision before a fresh phase-two
  agent starts.
- Runtime: `codex-cli 0.144.6`, `gpt-5.6-terra`, medium reasoning,
  `workspace-write`, approval policy `never`, one run per condition.

The B/C prompts are byte-identical. Their installed products differ on exactly
two reviewed files: the Wayfinder skill and Wayfinder state contract. The
campaign, prompts, control patch, fixture, mutation, grader dependencies, and
instruction sources were frozen before execution.

## Correctness and continuation

| Primitive outcome | A: generic | B: matched old | C: current |
|---|---:|---:|---:|
| Phase-one safe useful progress | no | yes | yes |
| Exact AMI fact persisted | no | yes | yes |
| Instance family left unresolved | yes | yes | yes |
| Isolation left unresolved | no | yes | yes |
| Exact AMI fact recovered in phase two | no | yes | yes |
| New architecture decision applied | yes | no | yes |
| Frozen implementation assertions passed | no | no | yes |
| Validation passed | no | no | yes |

A made substantial Terraform changes during phase one despite the unresolved
isolation decision, stored no exact AMI parameter, and converted the parameter
to a caller-provided value. In phase two it applied the new architecture decision
but still could not recover the exact parameter.

B created safe durable state and recovered the exact parameter. On resume it
correctly noticed that the map was stale and that D1 resolved the original
blockers, but it then promoted deployment-time inputs (exact `m7i` size, IAM
role, capacity, and bootstrap values) into a new authority-owned blocker. Those
values could safely remain explicit Terraform inputs, as C demonstrated.

C resumed from its map, checked the directly relevant unknowns and D1, retired
the resolved U1/U2 records, represented deployment-specific values as inputs,
implemented the node group, and passed `terraform validate`,
`terraform fmt -check`, and `git diff --check` in the agent trace. The frozen
grader independently passed all static assertions and `terraform fmt -check`.

## Durable state quality

| State measure | A | B | C |
|---|---:|---:|---:|
| Phase-one files | 1 | 4 | 3 |
| Phase-one lines | 19 | 84 | 93 |
| Phase-one bytes | 1,450 | 3,812 | 3,277 |
| Final files | 1 | 3 | 1 |
| Final lines | 19 | 71 | 61 |
| Final bytes | 1,507 | 4,295 | 2,331 |
| Lexical procedural-history lines in phase one | 0 | 0 | 0 |

C stored the exact fact directly in its map instead of allocating B's separate
evidence record. After reconciliation C retired both resolved unknown children
and ended with one current map. B retired its original unknowns but retained a
separate evidence record and added U3, ending with three files and 84% more
bytes than C. This is meaningful evidence of higher current-state density, even
though C's wrapped prose produced more phase-one lines.

The procedural-history check is deliberately weak: it is a conservative lexical
indicator, not a semantic grader. No arm wrote obvious agent-action narration.
B's evidence provenance (including the source-removal commit) is legitimate
provenance rather than procedural history, but C showed it was not necessary as
a separate child for correct continuation.

## Reconstruction and efficiency

| Total across both phases | A | B | C |
|---|---:|---:|---:|
| Input tokens | 518,178 | 1,198,655 | 1,028,956 |
| Cached input tokens | 446,976 | 1,099,520 | 948,992 |
| Uncached input tokens | 71,202 | 99,135 | 79,964 |
| Output tokens | 15,463 | 15,809 | 14,518 |
| Reasoning tokens | 4,237 | 5,498 | 4,218 |
| Tool actions | 20 | 28 | 29 |
| Elapsed seconds | 318.512 | 338.866 | 313.736 |

Relative to B, C used 14% fewer total input tokens, 19% fewer uncached input
tokens, 8% fewer output tokens, 23% fewer reasoning tokens, and 7% less elapsed
time. C used one more tool action. These are descriptive observations from one
run, not stable efficiency estimates.

Both Wayfinder arms followed the intended broad resume order: contract, effort
discovery, low-resolution map, relevant state/detail, then repository evidence.
A corrected post-hoc event-order read found 11 completed shell commands before
B's first file change and 10 before C's. Conservative path extraction found 18
unique path-like reads for B and 16 for C. The frozen summary's
`files_read_before_first_write` field is not valid because its parser did not
treat JSONL `file_change` events as writes; it counted later reads. That field is
retained in raw evidence but must not be used for conclusions.

## Isolation and limitations

Preflight passed all frozen checks: three separate Git roots, no framework in A,
only the two treatment surfaces changed in B, identical B/C prompts, controller
and grader artifacts outside workspaces, and reuse of the previously passed live
isolation protocol. All six executions had unique thread IDs. Each phase used
`codex exec --ephemeral`, a unique authentication-only `CODEX_HOME`, ignored
user config/rules, no inherited controller `CODEX_*` context, and no phase-one
summary.

Important limitations:

- This is one run per arm, so model variance can explain some or all B/C
  divergence despite the controlled product intervention.
- Raw stderr contains recovered unified-exec and absolute-path patch failures.
  B and C both encountered this noise in phase two; B also encountered a phase-
  one process-start failure while C did not. This is a potential confound for
  timing, token, and possibly behavioral comparisons.
- A's bare environment could not resolve several ordinary shell tools that the
  installed-framework arms later resolved. That weakens A-vs-Wayfinder cost and
  validation comparisons, though it does not affect the matched B-vs-C product
  intervention.
- The lexical procedural-history classifier and conservative path parser do not
  measure semantic current-state density on their own; the final artifact
  inspection supplies the stronger evidence above.
- No external infrastructure action, Terraform plan, or apply was run.

## Recommendation

Do not change the candidate instructions based on this smoke. Keep the exact C
delta as the treatment for a repetition campaign because it showed no observed
correctness regression and produced the only complete continuation here.

Run at least four additional matched repetitions per condition (five total),
randomizing or counterbalancing condition order. Before those repetitions, fix
the runner's minimal shell environment/absolute-path noise and update the trace
parser to recognize `file_change` events. Add a semantic final-state-density
check, but keep the current frozen campaign and raw smoke immutable. If C's
correctness and state-retirement advantage repeats, adopt the exact instruction
delta; if only efficiency varies, treat that as noise rather than a product
claim.

## Evidence locations

- Frozen inputs: `frozen-evaluator.json`
- Isolation preflight: `preflight.json`
- Compact primitive metrics: `summary.json`
- Per-condition phase evidence: `runs/*/phase-1.json`,
  `runs/*/phase-2.json`, and `runs/*/result.json`
- Raw JSONL, stderr, and snapshots (repository-ignored but retained locally):
  `evals/artifacts/wayfinder-fresh-agent-continuation-v1/`
