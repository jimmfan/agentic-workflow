# ARC Wayfinder end-to-end v2: corrected three-condition smoke

## Conclusion

The v2 smoke is informative but not ready for repetitions. Isolation and
execution controls were clean at the audited boundary, all twelve fresh phases
completed, and the corrected fixture made phase 4 unequivocally executable.
All three conditions preserved, located, consumed, and implemented the exact
`/platform/arc/runner-ami` fact; respected the decision boundary; kept legacy
ownership unresolved but non-blocking; and completed every required Terraform
component without external mutation.

No engineering-outcome advantage for explicit Wayfinder appeared. The vanilla
durable handoff matched both Agentic Workflow arms on every headline primitive
while using the least elapsed time, tokens, tool actions, and pre-write reads.
The v1 continuity advantage did not reproduce.

The intended B-versus-C comparison is potentially confounded because neutral
condition B automatically selected Wayfinder in phase 1 and used its state in
every later phase. B and C therefore compare two Wayfinder trajectories with
different invocation prompts, not Agentic Workflow without versus with
Wayfinder. The frozen semantic classifier also retained several material
misclassifications despite its improved evidence capture. Repair treatment
separation and semantic classification before repetitions. Do not change
automatic routing from this one smoke.

## Campaign and evidence quality

- Campaign: `arc-wayfinder-e2e-v2`
- A: `arc-v2-a-1-f3d63c2258` — vanilla, neutral durable handoff
- B: `arc-v2-b-1-0cdb658fca` — Agentic Workflow, neutral prompt
- C: `arc-v2-c-1-cde5e0d86f` — Agentic Workflow, explicit `$wayfinder`
- Model/runtime: `gpt-5.6-terra`, medium reasoning, workspace-write,
  approvals `never`, empty shell-environment inheritance
- Execution: 12 sequential `codex exec --ephemeral` processes; 12 unique
  execution IDs, no resume, no parent task context, and no control-check failure
- Installation: Agentic Workflow `0.11.1`; source Git SHA
  `7eacd2ef8139251d31fc8f38bd39aeee9ca39134`; Wayfinder `v1.2.3`; B/C
  installed-artifact SHA-256
  `c5527e63b68a5f25cc70202c68a246dc8b0e61afcb798c90a83699a6052b70f8`
- Frozen-evaluator SHA-256:
  `5becb582140f1a6c2b1d9cd63b11f1df238a391c58943c51dddaeb4b1428824e`
- Overall isolation/execution evidence: **known limitation**, not confirmed
  contamination. The final audit passed before live execution and references
  the exact freeze, but it ran 33 seconds after rather than before that freeze.
- A-versus-B evidence: clean for the effect of normal installed Agentic
  Workflow behavior, including its observed automatic Wayfinder selection.
- B-versus-C evidence: **potentially confounded** for incremental explicit
  Wayfinder because B crossed over in every phase.
- A-versus-C evidence: clean at the audited boundary, with one trajectory per
  condition and no repeatability or statistical claim.
- Semantic-classifier evidence: known limitation; exact evidence remains
  inspectable and manual interpretations below supersede incorrect labels only
  in this report, not in frozen JSON.

## Frozen primitive summary

| Independent observation | A | B | C |
| --- | ---: | ---: | ---: |
| Phase 1 exact fact preserved | 1/1 | 1/1 | 1/1 |
| Phase 1 mapping-only boundary respected | 1/1 | 1/1 | 1/1 |
| Phase 2 exact fact located/read | 1/1 | 1/1 | 1/1 |
| Phase 2 exact fact trusted/consumed | 1/1 | 1/1 | 1/1 |
| Phase 2 exact fact correctly implemented | 1/1 | 1/1 | 1/1 |
| Phase 2 SSM progress | 1/1 | 1/1 | 1/1 |
| Phase 2 IAM/boundary progress | 0/1 | 0/1 | 0/1 |
| Phase 3 mapping-only boundary respected | 1/1 | 1/1 | 1/1 |
| Phase 4 complete bounded slice | 1/1 | 1/1 | 1/1 |
| Phase 4 exact fact implemented | 1/1 | 1/1 | 1/1 |
| Speculative rework | 0 lines | 0 lines | 0 lines |
| Wayfinder crossover in neutral B | n/a | 4/4 phases | n/a |

No aggregate score is computed.

## 1. A versus B: normal Agentic Workflow behavior

B changed the durable-state representation, not the engineering outcome. A
wrote a README pointer and one detailed handoff document. B's router selected
Wayfinder despite the neutral prompt and created a map, tickets, and unknowns.
Both represented the exact AMI fact, stale `m6i`, unresolved compute choices,
legacy ownership, actionable safe work, and exact continuation context.

In phase 2, both recovered and implemented the exact SSM lookup while avoiding
premature compute architecture. In phase 3, both retired the now-resolved
compute choices, kept later integration concerns non-blocking, and named the
same executable slice. In phase 4, both completed all required resources and
checks. Normal Agentic Workflow therefore added structured, linked state but no
observed correctness or completion benefit in this trajectory.

B cost more: 751.057 seconds versus A's 515.860 (+45.6%), 1,936,136 versus
1,004,891 recorded input tokens (+92.7%), 36,210 versus 24,302 output tokens
(+49.0%), and 52 versus 37 tool actions (+40.5%). These are single-run
descriptive measurements, not stable performance estimates.

## 2. B versus C: incremental explicit Wayfinder

The planned contrast is not identified. B read the Wayfinder skill and created
canonical Wayfinder state in phase 1, then fresh B agents used or modified that
state in phases 2 through 4. C was explicitly invoked in phases 1 and 3, but
both repositories ultimately used the same product representation.

Qualitatively, C created a somewhat smaller initial map (one ticket and four
unknowns) than B (three tickets and four unknowns). After new evidence, B
resolved its compute and node-IAM unknowns and made its existing T1 the ready
slice; C recorded a D1 and created T2 as the ready slice. Both correctly left
controller/integration and legacy-ownership concerns outside the ticket's
blocking path. Both completed phase 4 with no rework.

C happened to use less time and fewer tokens than B—621.984 versus 751.057
seconds and 1,612,913 versus 1,936,136 input tokens—but one stochastic pair of
two crossed-over Wayfinder trajectories cannot attribute that difference to the
explicit invocation.

## 3. A versus C: vanilla versus the explicit Wayfinder system

A and C achieved the same frozen functional result in all four phases. C made
state relationships more explicit through a map, D1, T1/T2, and U1-U4 records;
A expressed the same readiness boundary in one cohesive handoff. The structured
graph did not create a measurable continuity or completion advantage here.

C required 106.124 more seconds (+20.6%), 608,022 more input tokens (+60.5%),
4,653 more output tokens (+19.1%), nine more tool actions (+24.3%), and 37 more
files observed before first writes. The read extractor is directional, and
this one trajectory cannot establish typical overhead, but the observed cost
was not offset by a better engineering outcome.

## 4. Phase 1 state quality

All three conditions produced good durable state and changed no infrastructure.
Manual snapshot review found that each:

- preserved the exact SSM path and externally managed EKS constraint;
- marked the old `m6i` recommendation stale;
- retained instance family, shared/dedicated, and Karpenter/MNG as unresolved;
- retained legacy security-group ownership as unresolved and prohibited
  adoption or mutation;
- identified SSM, permissions-boundary, interfaces, tests, and validation as
  useful work that could proceed; and
- left a usable fresh-agent continuation point.

A used a single 138-line handoff plus README pointer. B used one map, three
tickets, and four unknowns. C used one map, one ticket, and four unknowns. B/C
made dependencies easier to navigate as links; A kept the full context cheaper
to reconstruct in one place.

The frozen classifier incorrectly labeled B's unresolved shared/dedicated
choice and C's unresolved Karpenter/MNG choice as `explicit_negative`. Exact
snapshot text shows both were open. These are evaluator defects, not product
findings.

## 5. Phase 2 continuity and safe progress

The deleted original source did not break any arm. Every fresh agent found the
exact AMI path in its phase-1 durable state, treated it as settled enough to
use, created the correct Terraform SSM lookup, and added/updated local tests.
The exact fact was therefore preserved, located/read, consumed, and correctly
implemented in A, B, and C.

All three intentionally stopped short of the unresolved compute choices and
made no external change. SSM progress was 1/1 per arm. IAM/permissions-boundary
implementation progress was 0/1 per arm; each deferred role creation until the
fixture later supplied the exact role contract. Other reversible progress
included safety tests, variables/interfaces, documentation, and in B/C durable
ticket/map updates. No arm recreated EKS, chose compute prematurely, assumed
legacy ownership, enabled public IPs, or ran Terraform apply.

This fails to reproduce v1's specific continuity gap: v2 A operationalized the
preserved literal just as B and C did. The difference could be agent variance,
the v2 handoff's wording/quality, or the v1 trajectory; this single smoke cannot
identify Wayfinder or broader Agentic Workflow as the cause.

## 6. Decision boundaries and phase 3 state evolution

Before D1, every arm correctly left compute architecture open. After the
identical phase-3 mutation, every arm incorporated the approved dedicated
`m7i.large` managed-node-group decision, no-Karpenter boundary, 2/2/6 scaling,
and benchmark consequence. Each recognized that cold p95/p99 missed the
60-second target while two warm nodes met the supplied observations.

A updated its handoff with an exact four-step implementation slice. B resolved
U1 and U5, completed its SSM/safety tickets, and made T1 ready. C recorded D1,
resolved its capacity choice, and created ready T2. None revived `m6i` or left a
contradictory compute tracker.

All three retained the legacy security-group ownership unknown. A said it was
“still ownership-unknown, but not a blocker for this slice.” B said U4 blocks
only work using or altering that group. C left U2/U3/U4 open with `Blocked by:
none` and explicitly said those questions do not block T2. B's U3 remained
blocked by U2 for a later end-to-end capacity proof, which was accurate and did
not block current implementation.

The frozen blocker extractor marked B/C for manual interpretation merely
because it found structured `Blocked by` lines; inspection found no improper
current-ticket blocker. The semantic classifier also made several incorrect or
ambiguous labels (notably C's resolved instance choice as `ambiguous`). Raw
path/line/snippet evidence preserved enough information for this manual result.

## 7. Did C over-block phase 4?

No. C preserved genuine later unknowns but scoped them away from the authorized
ticket, then the fresh phase-4 agent implemented the entire ticket. The v1
whole-ticket stall did not reproduce under unequivocal readiness information.
B's automatically created Wayfinder state behaved the same way, and A's prose
handoff also drew the boundary correctly.

This is evidence that explicit readiness facts can prevent over-blocking; it is
not proof that Wayfinder reliably derives that boundary when repositories are
less explicit.

## 8. Phase 4 component comparison

Every condition passed every independently frozen component check:

| Required or prohibited component | A | B | C |
| --- | ---: | ---: | ---: |
| Existing cluster data reference; no `aws_eks_cluster` | yes | yes | yes |
| Exact SSM lookup and launch-template consumption | yes | yes | yes |
| EC2 node-role trust and permissions boundary | yes | yes | yes |
| All three exact managed-policy attachments | yes | yes | yes |
| Node group waits for policy attachments | yes | yes | yes |
| Launch template created and consumed | yes | yes | yes |
| Dedicated EKS managed node group | yes | yes | yes |
| Private subnet inputs | yes | yes | yes |
| `m7i.large`, `ON_DEMAND`, 2/2/6 | yes | yes | yes |
| Required workload label and dedicated taint | yes | yes | yes |
| No Karpenter, hard-coded AMI, public IP, or legacy-resource use | yes | yes | yes |
| No Terraform apply or external mutation | yes | yes | yes |

The evaluator's nine repository safety tests passed for all three final
snapshots, and `terraform fmt -check -recursive terraform` passed. No condition
ran `terraform validate` because the fixture intentionally lacked an initialized
provider directory and initialization/network download was unauthorized. Agents
reported that limitation accurately.

Raw events show validation commands in all 12 phases. C phase 3 had one failed
bytecode-cleanup command due to a Python-version filename mismatch, then
recovered and completed its final checks. Host safety rejected recursive `rm`
attempts in 11 phases; agents used targeted `unlink`/`rmdir` cleanup instead.
Those recoverable tool errors did not change the graded repositories.

## 9. Speculative rework

Frozen rework was zero files and zero approximate lines for A, B, and C. No arm
implemented an unsupported architecture before D1, so the phase-3 decision did
not require reversal. Phase-4 changes were additive within the authorized
slice.

## 10. Runtime and reconstruction overhead

| Four-phase total | A | B | C |
| --- | ---: | ---: | ---: |
| Elapsed time | 515.860 s | 751.057 s | 621.984 s |
| Input tokens | 1,004,891 | 1,936,136 | 1,612,913 |
| Cached input tokens | 878,848 | 1,772,288 | 1,462,784 |
| Output tokens | 24,302 | 36,210 | 28,955 |
| Reasoning tokens | 3,944 | 8,474 | 6,904 |
| Tool actions | 37 | 52 | 46 |
| Files observed before first writes | 40 | 78 | 77 |
| Repeated-read path observations | 64 | 118 | 119 |

| Phase elapsed time | A | B | C |
| --- | ---: | ---: | ---: |
| Phase 1 | 103.269 s | 143.971 s | 170.571 s |
| Phase 2 | 152.156 s | 230.133 s | 137.280 s |
| Phase 3 | 134.317 s | 201.058 s | 148.467 s |
| Phase 4 | 126.118 s | 175.895 s | 165.666 s |

Input/cached/output/reasoning usage and elapsed time come directly from Codex
JSONL/runtime evidence. Tool and read counts are conservative extractions; the
same command can appear in start/completion events, and path parsing is not
complete filesystem telemetry. One run per condition precludes variance or
significance claims.

Each process used and removed an auth-only temporary `CODEX_HOME`. The twelve
phase processes removed 512,011,180 logical bytes in total; the three final
isolation probes removed another 114,081,260 logical bytes. Source credentials
were unchanged.

## 11. Evidence for and against Wayfinder

The strongest favorable evidence is qualitative state explicitness. B and C
made ready work, retained unknowns, and dependency boundaries navigable through
canonical maps and linked U/D/T artifacts. Both correctly narrowed broad
unknowns to non-blocking later work and completed the bounded slice, directly
answering the v1 over-blocking concern under a stronger fixture.

The strongest contrary evidence is the absence of incremental outcome value.
A matched every continuity, safety, state-evolution, implementation,
verification, and rework result with substantially lower observed overhead.
Moreover, automatic B crossover prevents attributing any B/C difference to
explicit invocation. Structured state increased reconstruction surface without
an observed payoff in this trajectory.

Generic durable handoff therefore appears to capture most—and in this smoke all
measured—Wayfinder value. That conclusion is fixture- and trajectory-limited:
the scenario had one cohesive decision stream and a strong explicit handoff
prompt, which may favor a single-document representation.

## 12. Does broader Agentic Workflow explain v1?

V2 does not support a unique explanation. A, B, and C all passed the continuity
test, so the v1 A/C difference was not reproduced. B's automatic Wayfinder use
also means v2 contains no broader-Agentic-Workflow-without-Wayfinder trajectory.
The evidence is consistent with generic handoff quality or run variance
explaining v1, but cannot rule in or out broader routing/contracts or Wayfinder
state as the cause.

## 13. Repetition readiness and next decision

Do not repeat this evaluator unchanged. It is sound enough to show that the
corrected phase-4 fixture works and that the over-blocking failure is not
inevitable, but two design defects remain material:

1. normal B routing selected Wayfinder, so explicit Wayfinder's incremental
   effect is not isolated; and
2. the semantic classifier still misclassifies clear unresolved/resolved text,
   even though its exact evidence makes manual correction possible.

A future campaign should repair those boundaries before repetitions. Any clean
non-Wayfinder Agentic Workflow condition must be established through an
explicitly supported product/routing treatment decided in advance, not by
silently suppressing normal behavior after observing crossover. Semantic
grading should use structured fixture truth or narrowly parsed record fields,
leaving free prose entirely manual where deterministic interpretation is not
reliable.

The v1 blocker-discipline issue deserves future design evidence but not a
product change now. The newly observed automatic-selection behavior is a
separate product question. Automatic routing changes remain deferred for human
review.

## 14. Independent verification and cleanup

Post-report verification used Python 3.14.6. All 40 evaluator tests and all 46
Agentic Workflow package tests passed; both the preserved v1 freeze and final v2
freeze matched their critical files. A separate artifact audit confirmed three
result JSON files, twelve unique fresh execution IDs, twelve raw JSONL/stderr
pairs, twelve phase snapshots, exit status zero and isolation invariants for
every phase, byte-identical B/C installations, no observed Terraform apply, and
all frozen phase-4 component checks true. `git diff --check` passed, and no v1
campaign, fixture, harness, result, or report path has a diff.

After evidence persistence, guarded harness cleanup removed only the three
completed disposable workspaces (1,928 KiB of actual filesystem blocks). Raw
evidence and snapshots remain reconstructable under the v2 result namespace.
No source credentials, external infrastructure, product behavior, or v1
artifact was changed.

## Evidence pointers

- Campaign record: [`campaign.md`](../results/arc-wayfinder-e2e-v2/campaign.md)
- Frozen evaluator: [`frozen-evaluator.json`](../results/arc-wayfinder-e2e-v2/frozen-evaluator.json)
- Isolation audit: [`context-isolation-audit.json`](../results/arc-wayfinder-e2e-v2/context-isolation-audit.json)
- Isolation review: [`review.md`](../results/arc-wayfinder-e2e-v2/isolation-audit/review.md)
- Condition A result: [`result.json`](../results/arc-wayfinder-e2e-v2/runs/arc-v2-a-1-f3d63c2258/result.json)
- Condition B result: [`result.json`](../results/arc-wayfinder-e2e-v2/runs/arc-v2-b-1-0cdb658fca/result.json)
- Condition C result: [`result.json`](../results/arc-wayfinder-e2e-v2/runs/arc-v2-c-1-cde5e0d86f/result.json)
- Product and tooling issues: [`product-issues.md`](../results/arc-wayfinder-e2e-v2/product-issues.md)
- Preserved preflight attempts: [`preflight/`](../results/arc-wayfinder-e2e-v2/preflight/)
