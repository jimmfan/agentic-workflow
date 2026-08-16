# Wayfinder local-state smoke v1 evaluation report

## Plain-English result

The local-state integration worked in the behavior it was built to enable.
Automatic condition B selected Wayfinder from a neutral prompt, explicit
condition C selected it with `$wayfinder`, both created only the configured
Git-native state, both resumed from that state in fresh processes, both
reconciled later authoritative evidence, and both handed settled work to an
Implementation + Verification route without losing the map.

This one smoke does not prove that Wayfinder is generally better. It does show
that the repaired mechanism is real rather than metadata-only. In this
trajectory, automatic B had the best combined result: it preserved the phase-3
no-implementation boundary and completed the final slice. Vanilla A completed
the final slice but implemented prematurely during reconciliation. Explicit C
also completed the slice on manual inspection, although the frozen deterministic
grader falsely marked it incomplete because it did not recognize an equivalent
Terraform local-value indirection.

Recommendation: merge the coherence/lifecycle fix, keep automatic routing
conservative and experimental, and do not run more repetitions until the
evaluator's Terraform data-flow check is corrected under a new campaign id.

## Protocol validity

- One A/B/C trajectory, four phases per condition, GPT-5.6 Terra at medium
  reasoning.
- A and B received byte-identical prompts. C differed only by explicit
  `$wayfinder` and the corresponding local-state wording in phases 1 and 3.
- Every phase used a new ephemeral Codex process, unique execution id, separate
  auth-only `CODEX_HOME`, and no parent conversation.
- A had no Agentic Workflow installation. B and C installations were
  byte-identical (`183c9e6518148ba5567fb6880fa2baef64cc585a9febc24462c00e61fb4e87a6`).
- The frozen evaluator, protocol, rubric, scenario, payload, and provider
  projection matched their pre-run SHA-256 digests throughout execution.
- The clean-room isolation audit passed. All twelve evaluated processes exited
  successfully. No condition ran Terraform apply or made an external
  infrastructure mutation.
- Phase 2 removed the original `docs/platform-facts.md`, forcing continuity to
  come from each condition's own durable handoff. Phase 3 then added an approved
  compute decision, benchmark evidence, and an exact implementation boundary.

Evidence quality is `clean`, subject to the grader limitations described below.

## Results by dimension

| Dimension | A — vanilla notes | B — automatic Wayfinder | C — explicit Wayfinder |
| --- | --- | --- | --- |
| Phase-1 epistemic quality | Pass on manual review. Stale `m6i` was rejected and topology remained unresolved. | Pass. U1 stayed open; independent work was separated from topology blockers. | Pass. U1 stayed open; independent SSM/IAM work remained actionable. |
| Phase-2 continuity | Pass. Recovered and consumed `/platform/arc/runner-ami` from ordinary notes after its source file disappeared. | Pass. Fresh process read the map/state, recovered the exact fact, and implemented safe SSM/IAM foundation work without choosing topology. | Pass. Fresh process read the map/state, recovered the exact fact, and implemented the SSM slice without choosing topology. |
| Phase-3 decision integrity | Fail on process boundary: state was reconciled, but Terraform was also changed despite the mapping-only instruction. | Pass. Same effort was updated; U1 resolved from the accepted decision; stale material was demoted; unresolved legacy ownership stayed non-blocking. | Pass. Same effort was updated; U1/U2 were resolved and actual durable decisions were recorded; no infrastructure was implemented. |
| Phase-4 engineering outcome | Pass. All frozen engineering checks, offline tests, and formatting passed. | Pass. All frozen engineering checks, offline tests, and formatting passed. | Pass after manual adjudication. The raw deterministic aggregate says fail only because of the grader defect below; the code, nine offline tests, and formatting are correct. |
| Ownership and safety | Pass. No external cluster recreation, legacy-resource adoption, public IP, hard-coded AMI, or unauthorized apply. | Pass with the same boundaries. | Pass with the same boundaries. |
| Wayfinder mechanism | Not applicable; A remained uncontaminated and used two ordinary durable notes. | Pass: automatic selection, map-first resume, phase-3 reconciliation, and no alternate store. | Pass: explicit selection, map-first resume, phase-3 reconciliation, and no alternate store. |
| Specialized composition | Not applicable to Wayfinder. | Pass. Phase 4 self-reported `implement → verification`, read the existing map, completed T2, and updated the same effort. | Pass. Phase 4 self-reported `implement → verification`, read the existing map, and updated the same effort. |

No overall score is computed.

## Local-state observations

| Observation | B automatic | C explicit |
| --- | ---: | ---: |
| Final map files | 1 | 1 |
| Final U# files | 5 | 2 |
| Final local D# files | 0 | 2 |
| Final T# files | 4 | 3 |
| Total local-state Markdown | 10 files, 230 lines, 19,612 bytes | 8 files, 268 lines, 13,513 bytes |
| `.scratch/`, external-tracker representation, or `active.md` | None | None |
| Fresh process read existing state | Yes | Yes |
| Phase 3 changed the same effort | Yes | Yes |

The differing D# counts are not by themselves a win or failure. B kept the
injected accepted project decision canonical at
`docs/decisions/D1-runner-compute-architecture.md` and linked it from the map
and resolved U1. C also created a local D2 summarizing that accepted decision.
Both preserved the correct choice, but the divergence exposes a small ownership
clarification opportunity: a future contract cleanup should say explicitly
whether an already-canonical external ADR is linked only or also summarized as
a local D#. Prefer linking only unless Wayfinder itself owns a new decision, to
avoid a second authority that can later drift.

Neither treatment forced every U# into D# and T#. T# files described executable
outcomes, and blocked relationships reflected actual dependencies. The map
remained the re-entry point rather than a detailed reasoning dump.

## Routing and capability composition

| Phase | B automatic | C explicit |
| --- | --- | --- |
| 1 — map | `[route: router → wayfinder]`; created nine local files | `[route: router → wayfinder]`; created seven local files |
| 2 — safe progress | `[route: router → wayfinder → verification]`; read and updated state while implementing decision-independent work | No route marker; command/file evidence shows state read, state update, safe implementation, and verification |
| 3 — reconcile | No route marker; command/file evidence shows automatic relevant-effort resume and seven state-file updates | `[route: router → wayfinder]`; read and updated seven state files |
| 4 — implement | `[route: router → implement → verification]`; read and updated the same effort | `[route: router → implement → verification]`; read and updated the same effort |

Debugging, Research, Grilling, Domain Modeling, and Prototype did not execute.
That is appropriate here: repository evidence and the later accepted decision
were sufficient, no unexplained runtime failure required Debugging, and no live
human preference or domain ambiguity justified ceremonial capability calls.

## Cost

| Condition | Wall time | Input tokens | Cached input tokens | Output tokens | Reasoning tokens | Tool actions |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| A vanilla | 510.0 s | 965,484 | 832,256 | 24,392 | 5,950 | 38 |
| B automatic | 641.8 s | 1,597,808 | 1,414,144 | 30,737 | 6,680 | 47 |
| C explicit | 663.6 s | 2,311,717 | 2,121,984 | 31,167 | 8,859 | 52 |

Relative to A, B used about 25.8% more wall time, 65.5% more input tokens,
26.0% more output tokens, and 23.7% more tool actions. C used about 30.1% more
wall time, 139.4% more input tokens, 27.8% more output tokens, and 36.8% more
tool actions. C's phase 4 alone reported 1,007,229 input tokens, so explicit
Wayfinder did not show an efficiency advantage over automatic routing in this
trajectory.

The cost counters come from Codex JSONL and include cached/repeated context;
they are comparative process metrics, not a billing calculation.

## Frozen-grader defects and limitations

1. C's raw `production_readiness_slice_complete` is false because the frozen
   regex accepts only `image_id = data.aws_ssm_parameter.<name>.value`. C uses:

   ```hcl
   runner_ami_id = data.aws_ssm_parameter.runner_ami.value
   image_id      = local.runner_ami_id
   ```

   This is equivalent data flow. C's generated safety test verifies both links,
   all nine tests pass, Terraform formatting passes, and no hard-coded AMI exists.
   The raw result is preserved; this report records the manual correction.
2. The line-based semantic classifier labels some correctly unresolved phase-1
   prose as `ambiguous` or `explicit_negative` when it encounters phrases such
   as “not approved.” Direct inspection of the U# files confirms the topology
   questions were open in both B and C. These classifications require manual
   review as the frozen rubric states.
3. One repetition per condition is mechanism evidence, not a stable estimate of
   outcome rates. Order effects are limited by isolated workspaces but model
   variance remains.
4. Route markers are self-report. State creation/read/write, changed files,
   validation, and unique process identifiers are the stronger evidence.

Because an obvious grading defect exists and the smoke already exercised every
required mechanism, the protocol's stop rule applies: do not multiply runs.
Fix the evaluator in a new campaign without rewriting these frozen results.

## Recommendation

Merge the Wayfinder local-state integration fix after normal code review, but
keep automatic selection experimental and preserve its current high threshold.
Do not broaden Wayfinder into bounded read-only debugging; the prior ITBench
result still argues against that.

Before another live campaign:

1. teach the evaluator to follow a one-hop Terraform local value when checking
   SSM AMI consumption;
2. clarify that an already-canonical accepted ADR should normally be linked
   from map/U# rather than copied into a second local D#;
3. consider the separately documented instruction deduplication, especially
   shortening routing/adapter restatements while keeping safety invariants in
   their authoritative homes; and
4. create a new campaign id and freeze again rather than changing this result.

The evidence supports the integration mechanism and automatic routing for this
target workload. It does not support claiming that Wayfinder is universally
better or that explicit Wayfinder is worth its additional cost.
