# ARC Wayfinder state-complexity v1: six-phase smoke

## Conclusion

The campaign was clean at the observable isolation and execution boundary and
did exercise the intended branching, evolving project state. It produced useful
evidence through Phase 5 and for Phase 6's selective W1 update. On those valid
dimensions, the strong vanilla handoff matched explicit Wayfinder while using
substantially less observed time, tokens, tool activity, and reconstruction.

The apparent frozen Phase 6 win for Wayfinder is invalid as product evidence.
The fixture supplied an SNS destination but omitted the alarm's required metric
semantics. A noticed the repository was still insufficient and refused to
invent them. B's distributed state lost its earlier missing-input warning,
declared W4 ready, and the implementation agent invented the missing values.
The frozen grader rewarded alarm existence and ARN wiring without checking
those semantics. Results are preserved exactly and interpreted rather than
silently regraded.

Consequently, this one pair does not show that Wayfinder justifies its added
structure at this complexity. It also does not justify simplifying Wayfinder or
changing automatic routing. Do not repeat this campaign unchanged. If the line
of research continues, first create a new campaign whose W4 artifact supplies
and grades every required alarm input, then run one corrected smoke before
deciding whether repetitions are worthwhile.

## Campaign and evidence boundary

- Campaign: `arc-wayfinder-state-complexity-v1`
- A: `arc-state-a-1-174f804555` — vanilla Codex with a strong neutral durable
  handoff prompt
- B: `arc-state-b-1-de289d15a9` — installed Agentic Workflow with explicit
  Wayfinder in mapping/reconciliation phases
- Runtime: `gpt-5.6-terra`, medium reasoning, workspace-write, approvals
  `never`, identical network policy, no inherited shell environment
- Execution: twelve sequential fresh `codex exec --ephemeral` processes, six
  per arm, no resume; all exposed unique execution IDs and exited 0
- Source Git SHA: `205989bd81008c75e6f216cd97c7202eb0ac40e0`
- Agentic Workflow: `0.11.1`; B installed-artifact SHA-256
  `c5527e63b68a5f25cc70202c68a246dc8b0e61afcb798c90a83699a6052b70f8`
- Frozen manifest SHA-256:
  `120a1796d01a4689e8e7820acad40dafbc8d27dd34a399829deaf2cf89cd8668`
- Statistical boundary: one trajectory per condition; all differences are
  descriptive, not estimates of repeatable effects

The final isolation audit passed before any evaluated workspace was prepared.
One earlier audit attempt failed at network resolution before inference and is
preserved; it ran no evaluated agent. The successful audit verified out-of-tree
Git roots, no parent policy or controller/sibling context, auth-only temporary
Codex homes, no cloud credentials, no resume, external grader/raw capture, no
Agentic Workflow in A, and the exact frozen installation in B.

## Frozen primitive summary

| Independent observation | A | B | Interpretation |
| --- | ---: | ---: | --- |
| Phase 1 exact fact and constraints preserved | pass | pass | Valid comparison |
| Phase 1 mapping-only boundary | pass | pass | Valid comparison |
| Phase 2 fact located/read | pass | pass | Valid comparison |
| Phase 2 fact trusted/consumed | pass | pass | Valid comparison |
| Phase 2 exact fact implemented | pass | pass | Valid comparison |
| Phase 2 safe IAM/SSM slice | pass | pass | Valid comparison |
| Phase 3 D1 reconciliation | pass | pass | Valid comparison |
| Phase 4 complete W1/W2 slice | pass | pass | Valid comparison |
| Phase 5 D2 partial supersession | pass | pass | Valid for W1; W4 fixture premise defective |
| Phase 6 minimal W1 update | pass | pass | Valid comparison |
| Frozen Phase 6 complete vector | fail | pass | **Not a valid product comparison** |
| Justified Phase 6 W4 implementation | no | no | A stopped safely; B invented inputs |
| Speculative pre-D1 rework | 0 | 0 | Valid comparison |

No aggregate score is computed.

## 1. Was the campaign clean and uncontaminated?

Yes at the demonstrated context boundary. The final audit and all twelve phase
records show fresh ephemeral identities, no resume, no controller or sibling
context, matched runtime controls, and correct treatment installation. A had no
Agentic Workflow; B had the frozen installation. The grader and evidence store
were outside evaluated workspaces. All processes ran sequentially and exited 0.

“Clean” does not mean the fixture was valid in every respect. Isolation and
execution were clean, while W4's project truth and deterministic acceptance
were defective. That is a campaign-design confound, not context contamination.

## 2. Did the harder scenario exercise branching and evolving durable state?

Yes. Both trajectories managed four simultaneous workstreams across six fresh
agents: W1 compute began unresolved, W2 identity/image was safely actionable,
W3 legacy ownership stayed blocked throughout without blocking other work, and
W4 began blocked. D1 resolved W1; Phase 4 implemented W1/W2; D2 later replaced
only the instance size; W4 was purportedly unblocked; W3 remained blocked; and
Phase 6 had to preserve correct code while selectively revising stale code.

This is materially more complex than v1/v2's cohesive four-phase stream. The
fixture defect affects whether W4 was *actually* unblocked, but not whether the
agents had to model branching, selective blockers, D1, D2, and existing code.

## 3. Phase 1 state-quality comparison

Both were strong. A created one 109-line continuation document. B created six
typed map/U/D/T files totaling 166 lines. Both preserved the SSM path,
externally managed EKS, private networking, and permissions boundary; marked
the old `m6i` recommendation stale; left W1 unresolved; made W2 actionable;
and kept W3 and W4 selectively blocked. Neither implemented infrastructure.

B made relationships and ticket readiness explicit. A kept the same practical
truth in one cohesive read surface. No correctness advantage appeared.

## 4. Phase 2 exact-fact continuity and actionability

Both passed all four distinct continuity observations after the authoritative
source was deleted: the SSM fact remained preserved, the fresh agent found/read
it, trusted/consumed it, and implemented `/platform/arc/runner-ami`. Both made
meaningful IAM/SSM progress and validated it without selecting W1 architecture,
assuming W3 ownership, or inventing W4 input.

The exact-fact advantage observed in v1 therefore did not reproduce here, just
as it did not reproduce in v2.

## 5. Phase 3 selective-blocker and state reconciliation

Both accurately incorporated D1: dedicated runner compute, EKS managed node
groups, `m7i.large`, no Karpenter, and 2/2/6. Both retired the initial compute
questions as active blockers, retained W2's validity, kept W3 blocked only for
legacy cleanup, and kept W4 blocked. Both respected the mapping-only boundary.

A reconciled one document. B updated four of eight state files and added a
decision and implementation ticket. B's state was more explicitly navigable;
A's was cheaper to reconstruct. Neither over-blocked Phase 4.

## 6. Phase 4 parallel safe progress

Both completed the full frozen W1/W2 production-readiness slice: dedicated
managed node group, `m7i.large`, 2/2/6, exact SSM lookup, private networking,
fixture-owned runner resources, and permissions-boundary wiring. Neither added
Karpenter, recreated EKS, touched the legacy W3 resource, invented the W4
destination, enabled public networking, or ran apply. W3 and W4 did not stop
independently authorized work.

All evaluator tests and Terraform formatting checks passed for both arms.

## 7. Phase 5 partial-supersession reconciliation

For W1, both were correct. Each made `m7i.xlarge` current and retained dedicated
compute, managed node groups, no Karpenter, and 2/2/6. Neither treated D2 as a
replacement for all of D1, and neither left active contradictory old/new
instance truth. W2 remained valid and W3 remained blocked.

For W4, neither representation had a sound basis for declaring full readiness
because evaluator-controlled truth still lacked the alarm metric contract. A's
handoff labeled W4 actionable but also warned not to infer undocumented alarm
inputs. B resolved U3 and created ready T3, dropping its Phase 3 list of missing
metric semantics. The intended transition cannot be credited as a clean
success in either arm.

## 8. Phase 6 selective-update comparison

Both made the legitimate W1 change and preserved unaffected Terraform. A's
runner diff was approximately two changed lines; B's was four. Neither changed
an unrelated pre-existing Terraform file, invalidated W2, or touched W3.

A then re-read the observability artifacts, identified the missing alarm
semantics, and stopped rather than guess. B trusted its ready ticket and built an
alarm using the supplied ARN but invented namespace `ARC/Runner`, metric
`FailedRunnerJobs`, threshold `1`, comparison operator, 60-second `Sum`, one
evaluation period, and missing-data behavior. The frozen Boolean says A failed
and B passed; engineering review says neither completed a justified W4 slice.

## 9. Did either arm unnecessarily invalidate still-correct work after D2?

No. Both preserved the SSM lookup, IAM boundary, node-role relationships,
dedicated/MNG/no-Karpenter decisions, and 2/2/6 scaling. Frozen diff analysis
found no unnecessarily changed pre-existing Terraform files. B added W4 code,
but its problem was unsupported input selection, not invalidation of correct W1
or W2 work.

## 10. Did either arm fail to retire superseded `m7i.large` truth?

No. Both made `m7i.xlarge` active and retained `m7i.large` only in historical
or explicit supersession context. Neither final representation contained
contradictory active instance-size truth.

## 11. Did either arm incorrectly revive stale `m6i`?

No. Both consistently treated `m6i` as stale history, never selected it, and
never implemented it.

## 12. Did either arm let W3 block unrelated work?

No. W3 ownership remained unresolved and correctly prohibited import, deletion,
modification, or assumed ownership. Both arms nevertheless completed W1/W2 and
proceeded with the purported W4 transition. The legacy fixture stayed
untouched.

## 13. Did W4 correctly transition from blocked to actionable?

No clean success can be claimed. At the campaign's intended semantic level,
both Phase 5 agents treated the destination artifact as unblocking W4. At the
actual repository-truth level, W4 remained under-specified because the metric
contract was absent. A preserved that concern in a warning and recovered safe
behavior in Phase 6. B removed the concern from active state and treated W4 as
ready. The fixture, not just an agent, was wrong to define the destination as
the sole missing input.

## 14. Did either representation accumulate contradictory state?

Neither accumulated contradictory active W1 or W3 state. A's Phase 5 document
was internally tense: it called W4 actionable while forbidding inference of
undocumented alarm inputs. B's map/U/T set was internally consistent on status,
but semantically incomplete relative to the repository because the earlier
missing-metrics concern disappeared. This is better described as lost state
coverage than a direct structured-field contradiction.

## 15. Durable-state maintenance and synchronization cost

| Mapping point | A files | A lines | A reconciled | B files | B lines | B reconciled |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Phase 1 | 1 | 109 | 1 | 6 | 166 | 6 |
| Phase 3 | 1 | 108 | 1 | 8 | 239 | 4 |
| Phase 5 | 1 | 123 | 1 | 9 | 289 | 6 |

B's additional structure was not inherently waste: it exposed typed decisions,
unknowns, blockers, and implementation tickets. It also enlarged the
synchronization surface. At Phase 5, B reconciled six state files to A's one,
yet still lost an important W4 concern. Fresh B implementation agents read 20,
21, and 24 files before their first observed writes in Phases 2, 4, and 6;
A read 11, 6, and 12.

The real evaluation program's pre-campaign stale map/U/D/T incident reinforces
the relevance of this cost. One campaign cannot answer whether normal
reconciliation reliably offsets it, so U4 remains open.

## 16. Speculative rework

Frozen speculative rework before D1 was zero in both arms. Neither implemented
an unsupported compute architecture in Phase 2, so D1 required no reversal.

B's Phase 6 W4 alarm is unsupported implementation rather than rework already
measured by a later reversal; it would require correction or removal once the
real metric contract arrived. That risk should not be hidden inside the frozen
zero-rework value.

## 17. Necessary supersession rework

Both correctly performed the required `m7i.large` to `m7i.xlarge` change. A's
runner file changed by approximately two lines and B's by four. This is
legitimate supersession rework, not failure. Both limited it to the affected
slice and preserved the rest of D1 and W2.

## 18. Verification comparison

All twelve agents exited 0 and both arms observed validation in implementation
phases. Frozen evaluator unit tests and Terraform format checks passed after
Phase 4 and Phase 6, and repository safety tests passed. No `terraform init`,
`plan`, or `apply` command was observed. Some B implementation runs encountered
intermediate command failures and recovered; final validation passed.

The W4 acceptance gap illustrates the limit of passing tests: the tests proved
the properties they encoded, but those properties omitted required semantic
inputs. Verification was comparable in execution but incomplete in campaign
specification.

## 19. Token, time, tool, and reconstruction overhead

| Six-phase total | A | B | B relative to A |
| --- | ---: | ---: | ---: |
| Elapsed | 816.844 s | 1,336.394 s | +63.6% |
| Input tokens | 1,281,425 | 3,086,063 | +140.8% |
| Cached input tokens | 1,139,712 | 2,808,320 | +146.4% |
| Output tokens | 39,308 | 48,302 | +22.9% |
| Reasoning tokens | 5,969 | 9,983 | +67.2% |
| Tool actions | 51 | 85 | +66.7% |
| Files observed before first writes | 62 | 127 | +104.8% |
| Repeated-read path observations | 90 | 189 | +110.0% |

| Phase elapsed | A | B |
| --- | ---: | ---: |
| Phase 1 | 83.842 s | 130.447 s |
| Phase 2 | 120.407 s | 191.060 s |
| Phase 3 | 291.859 s | 459.116 s |
| Phase 4 | 113.440 s | 172.686 s |
| Phase 5 | 92.657 s | 235.098 s |
| Phase 6 | 114.639 s | 147.987 s |

Usage and elapsed time are direct runtime observations. Tool/read metrics are
conservative event-derived reconstructions, not complete filesystem telemetry.
One pair supplies no variance estimate, but the observed overhead is large and
was not offset by a valid engineering outcome advantage.

## 20. Strongest evidence for Wayfinder

The strongest favorable evidence is representational explicitness. B made D1,
D2, open W3 ownership, resolved compute uncertainty, and ready implementation
slices navigable as typed, linked artifacts. After D2, it preserved every
still-valid W1 choice and changed only the invalidated instance-size slice. The
fresh B agent could follow a ready ticket to implement both intended branches.

That is a real usability signal, but the W4 ticket was incomplete and the same
valid W1 behavior occurred in A. It is therefore not an outcome advantage.

## 21. Strongest evidence against Wayfinder

A single strong handoff matched B on every valid continuity, blocker,
state-evolution, safe-progress, selective-W1-update, and verification dimension
at much lower observed cost. More importantly, B's distributed reconciliation
dropped a valid missing-input concern and promoted an incomplete ticket, which
led a fresh agent to invent implementation semantics. The added structure did
not protect correctness in the most discriminating branch.

## 22. Does the single-document handoff remain sufficient here?

Yes for the valid measured dimensions in this one trajectory. A represented
all four workstreams, survived source deletion, reconciled D1 and D2, isolated
W3, implemented W1/W2, and made the minimal W1 update. Its Phase 6 refusal on W4
was the safer response to actual repository truth, not evidence that one
document failed to scale.

This does not prove one document is always sufficient; it shows this campaign
did not find its limit.

## 23. Does Wayfinder justify its structure only at this complexity level?

Not from this evidence. State complexity increased substantially, but no valid
engineering advantage appeared. B's higher maintenance and reconstruction cost
was not offset by better valid behavior. A corrected trajectory could still
find a benefit, so this is evidence against present justification, not a broad
product verdict.

## 24. Did distributed map/U/D/T state create synchronization problems?

It created a larger synchronization surface and one consequential loss of
state coverage: B's earlier missing alarm semantics were absent after the
Phase 5 map/U/T reconciliation. Yet its explicit fields were mutually coherent,
and W1 supersession stayed correct across nine files. The result supports U4 as
a real risk, but cannot establish that Wayfinder generally causes stale state
or that normal reconciliation cannot control it.

The evaluation program's own pre-campaign stale linked artifacts are separate
dogfooding evidence pointing in the same direction.

## 25. Is the experiment informative enough to repeat?

Not unchanged. It is informative about exact-fact continuity, selective
blockers, D1/D2 evolution, W1 rework, state surface, and overhead. It is not
valid for the intended newly-unblocked W4 branch or the headline Phase 6
completion comparison. Repetition would multiply evidence from a known false
readiness premise.

## 26. What should the next step be?

Human review should decide whether to fund one **new corrected smoke**. That
campaign should explicitly supply namespace, metric name, dimensions,
threshold, comparison operator, period, statistic, evaluation window, missing
data behavior, and destination, then freeze exact checks for them. Run one pair
before any repetitions.

Do not simplify Wayfinder from one confounded pair. Do not repeat this campaign.
Do not proceed automatically. Stopping this line of research is also reasonable
if the observed overhead and two consecutive no-advantage valid trajectories
already exceed the program's appetite for further evidence.

## 27. Does any evidence justify investigating automatic routing yet?

No new evidence does. This campaign explicitly invoked Wayfinder in B and
intentionally omitted a neutral Agentic Workflow arm, so it says nothing new
about automatic selection. V2's crossover remains the sole direct observation,
and U2 remains open. No routing behavior was changed.

## Independent verification and preservation

Before live execution, 12 campaign-specific tests, 52 total evaluator tests,
and 46 package tests passed; the package gate ended with
`OK: Agentic Workflow package verification passed.` The freeze matched all 24
critical files and `git diff --check` passed. Post-report verification repeats
those applicable checks and audits result completeness, unique IDs, snapshot
and raw-evidence counts, zero exit statuses, isolation, no external Terraform
operation, and preservation of v1/v2 paths.

No Agentic Workflow production behavior, routing, skill, provider, Wayfinder,
lifecycle, or installation semantics changed. V1 and v2 evidence remains
unchanged. Temporary run repositories are cleanup-only artifacts; frozen JSON,
raw logs, snapshots, reports, and audit records remain durable.

After evidence persistence, guarded harness cleanup removed only the two
completed disposable run directories and reclaimed 1,776 KiB of actual
filesystem blocks. The result namespace and all reconstructable evidence remain.

## Evidence pointers

- [Campaign record](../results/arc-wayfinder-state-complexity-v1/campaign.md)
- [Manual semantic review](../results/arc-wayfinder-state-complexity-v1/manual-review.md)
- [Product and tooling issues](../results/arc-wayfinder-state-complexity-v1/product-issues.md)
- [Frozen evaluator](../results/arc-wayfinder-state-complexity-v1/frozen-evaluator.json)
- [Isolation audit](../results/arc-wayfinder-state-complexity-v1/context-isolation-audit.json)
- [Condition A result](../results/arc-wayfinder-state-complexity-v1/runs/arc-state-a-1-174f804555/result.json)
- [Condition B result](../results/arc-wayfinder-state-complexity-v1/runs/arc-state-b-1-de289d15a9/result.json)
