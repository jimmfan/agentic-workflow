# ARC Wayfinder end-to-end v1: first smoke pair

## Conclusion

This clean, context-isolated smoke pair provides narrow evidence that structured
Wayfinder state improved one important continuity outcome: after the original
source was deleted, the fresh workflow agent recovered and implemented the
exact `/platform/arc/runner-ami` lookup, while the vanilla durable-handoff agent
did not. The workflow trajectory also finished 336 seconds faster and used
fewer recorded input and output tokens.

The result does not establish an overall Wayfinder advantage. Both arms produced
strong initial maps, respected the unresolved compute boundary, evolved their
state after D1, avoided external mutation, and failed to complete the expected
Phase 4 production-readiness slice. The workflow arm made no Phase 4 code change
because its own U2/U3 records had made the node-group ticket blocked. The
vanilla arm made additional safe validation changes but also declined the core
node-group work.

The smoke also exposed frozen-grader limitations. In particular, keyword-window
matching falsely classified explicit unresolved/prohibited Phase 1 text as
affirmative decisions, and the binary `safe_progress` field required both the
SSM and permissions-boundary slices, obscuring useful partial progress. These
results are preserved under the frozen evaluator and interpreted here rather
than retroactively regraded.

The appropriate next step is a new preregistered v2 smoke campaign after fixing
the evaluator defects. Do not repeat this exact evaluator unchanged, and do not
change automatic Wayfinder routing from this single pair.

## Campaign and evidence quality

- Campaign: `arc-wayfinder-e2e-v1`
- Baseline run: `arc-baseline-1-68edd44151`
- Workflow run: `arc-workflow-1-e93a5ffa12`
- Model: `gpt-5.6-terra`
- Reasoning effort: `medium`
- Sandbox: `workspace-write`
- Approval policy: `never`
- Execution: eight sequential, independent `codex exec --ephemeral` processes;
  no resume and no parent task context supplied
- Context evidence: clean at the audited observable boundary; every phase has a
  unique execution ID and clean evidence label
- Interpretation qualification: deterministic grader false positives described
  below; one trajectory per arm, so no repeatability or statistical claim

The failed first controller attempt found no `codex` executable on its PATH and
launched zero evaluated agents. The completed campaign used the explicit
app-bundled executable and is the sole evaluated evidence source.

## Frozen-grader summary

| Independent check | Vanilla handoff | Wayfinder |
| --- | ---: | ---: |
| Phase 1 exact fact preserved | 1/1 | 1/1 |
| Phase 1 stale `m6i` recognized | 1/1 | 1/1 |
| Phase 1 actionable IAM/SSM work identified | 1/1 | 1/1 |
| Phase 2 exact fact recovered | 0/1 | 1/1 |
| Phase 2 strict safe-progress composite | 0/1 | 0/1 |
| Phase 3 mapping-only boundary respected | 1/1 | 1/1 |
| Phase 3 no contradictory compute trackers | n/a | 1/1 |
| Phase 4 expected slice complete | 0/1 | 0/1 |

No aggregate score is computed.

## 1. State-quality comparison

Both arms created substantial durable state without changing Terraform in Phase
1. The baseline wrote one 177-line `docs/migration-handoff.md`; Wayfinder wrote a
57-line map plus four U/T files totaling 120 lines. Both preserved the exact SSM
path, marked `m6i` stale, identified safe IAM/SSM work, and recorded the external
EKS and private-network constraints.

The vanilla handoff explicitly listed instance family, shared versus dedicated,
Karpenter versus managed node groups, and legacy security-group ownership as
unresolved. The Wayfinder map grouped the three compute choices into U1 and put
the legacy security group outside the effort unless ownership and authorization
were established. Both representations were semantically safety-preserving.

The frozen grader reported that baseline selected Karpenter and workflow assumed
legacy ownership. Snapshot inspection shows these are false positives: baseline
said the Karpenter/MNG choice was unresolved, and workflow explicitly prohibited
taking ownership of the legacy group. Consequently, the corresponding
`mapping_only_respected=false` values are not credible semantic findings.

## 2. Phase-2 continuity comparison

Wayfinder won the campaign's clearest continuity test. Its fresh Phase 2 agent
read T1 and implemented a data lookup using the exact
`/platform/arc/runner-ami` path after the original source document had been
deleted. The baseline handoff contained the exact path, but its fresh agent
treated the removed source as requiring revalidation and replaced it with a
caller-supplied parameter-name interface. It therefore failed exact fact
recovery.

This is more precise than saying baseline “forgot”: the literal survived in the
handoff, but the downstream agent did not consume it as sufficiently settled
implementation evidence. Wayfinder's ticket made the approved action and exact
value more operationally salient.

## 3. Safe-progress comparison

Neither arm passed the frozen all-or-nothing safe-progress composite because
neither implemented the permissions-boundary slice as well as the SSM slice.
That binary result hides meaningful differences:

- Wayfinder made a correct, exact SSM implementation and added focused tests.
- Baseline made a safe parameterized SSM interface and broader tests, but lost
  the required exact parameter value.
- Neither chose compute architecture, recreated EKS, touched the legacy group,
  enabled public IPs, ran `terraform apply`, or crossed the external-mutation
  boundary.

Both therefore made some useful justified progress, but only Wayfinder satisfied
the exact continuity-dependent SSM behavior. Neither completed all safe work
that the fixture made available.

## 4. Decision-boundary comparison

Before D1, both Phase 2 agents correctly avoided selecting instance family,
shared/dedicated placement, and Karpenter/MNG architecture. Both validated their
changes and left external infrastructure untouched.

After D1, both Phase 3 agents recorded dedicated `m7i` managed node groups, no
Karpenter, and two warm nodes. Neither revived stale `m6i`. The workflow arm
resolved U1 and created one T2 rather than leaving contradictory compute
trackers. The baseline updated its single handoff consistently.

The main boundary problem was over-conservatism rather than unsupported action:
both arms promoted additional scope, IAM, network, or compatibility questions
into blockers that later prevented the expected compute slice.

## 5. Phase-3 state-evolution comparison

Both representations evolved cleanly when the evaluator introduced D1 and the
benchmark. Both captured that cold p95/p99 missed the 60-second target and that
two warm nodes met the supplied measurements. Baseline explicitly identified
node/EC2 availability as the observed cold bottleneck; Wayfinder did not state
that causal interpretation clearly enough for the frozen check.

Wayfinder retained the exact SSM parameter across the mutation; baseline did
not. Baseline kept the legacy ownership uncertainty explicit. Wayfinder
preserved the same safety boundary in its map, although the grader did not
recognize it as an active unresolved fact. No contradictory duplicate compute
tracker was found in the Wayfinder state.

## 6. Phase-4 implementation and verification comparison

Neither arm implemented the expected dedicated managed node group, `m7i`
configuration, warm minimum of two, or an IAM role with the required permissions
boundary. The workflow arm retained its correct SSM lookup but changed no file
in Phase 4, stating that T2 was blocked by U2/U3. The baseline arm added variable
validation, an ownership/input contract, documentation, and tests, but also
declined the core compute work; its SSM lookup still lacked the exact path.

Both arms preserved private-subnet inputs, avoided Karpenter and EKS recreation,
left the legacy group untouched, and ran no unauthorized apply. Repository unit
tests and `terraform fmt -check` passed in both final workspaces. Both accurately
reported that `terraform validate` could not run without downloading the absent
AWS provider.

## 7. Speculative-rework comparison

The frozen metric recorded zero speculative rework in both arms: no file or
line was removed or substantially rewritten because of an unsupported compute
assumption. This is consistent with both agents' conservative behavior. The
tradeoff is that avoiding speculation also became over-blocking in Phase 4.

## 8. Recorded time, tokens, tools, and reconstruction

| Measure across four phases | Vanilla handoff | Wayfinder | Difference |
| --- | ---: | ---: | ---: |
| Elapsed time | 790.766 s | 454.784 s | Wayfinder -335.982 s (-42.5%) |
| Input tokens | 1,214,094 | 1,098,374 | Wayfinder -115,720 (-9.5%) |
| Output tokens | 39,456 | 21,909 | Wayfinder -17,547 (-44.5%) |
| Tool actions | 39 | 37 | Wayfinder -2 (-5.1%) |
| Files observed before first write | 29 | 66 | Wayfinder +37 |
| Repeated-read paths | 55 | 100 | Wayfinder +45 |

The strongest phase-level efficiency difference was Phase 2: baseline took
242.472 seconds and 448,926 input tokens; Wayfinder took 100.172 seconds and
241,587 input tokens. Wayfinder nevertheless read more individual files because
its state was split across the map and U/T records. The path extractor is
conservative—baseline Phase 1 recorded zero pre-write reads despite visible
exploration—so read counts are directional, not complete. Timing and token
differences are also only one paired observation and may include model/runtime
variance.

## 9. Strongest evidence for Wayfinder

The strongest evidence is the coupled continuity-and-cost result in Phase 2:
Wayfinder both recovered the exact deleted-source fact and implemented it in
less than half the elapsed time and with roughly half the recorded input tokens.
Its Phase 3 update also resolved the compute unknown without contradictory
duplicate trackers and retained the exact SSM fact.

## 10. Strongest evidence against Wayfinder

Wayfinder did not improve the final engineering outcome. Its structured state
made self-created U2/U3 blockers durable, and the fresh Phase 4 agent performed
no implementation despite an explicit D1 and an expected safe node-group slice.
The representation also increased file-level reconstruction and repeated reads.
Generic handoff notes matched most state-quality, safety, and state-evolution
behavior without framework-specific files.

## 11. Does generic durable handoff capture most of the value?

In this one fixture, yes—most, but not all. The vanilla handoff preserved the
important initial facts and unknowns, evolved correctly after D1, avoided
speculative rework, and maintained safety. It did not convert the preserved SSM
literal into downstream implementation, and it was slower and more verbose.
That narrow difference is meaningful, but insufficient to show that the full
Wayfinder structure is generally worth its ceremony.

## 12. Is the experiment informative enough to repeat?

It is informative enough to justify a corrected v2 campaign, but not an
unchanged repetition. Preserve v1. Before v2, replace the brittle
affirmative-choice keyword windows with inspectable semantic fixtures or more
specific assertions, report partial IAM and SSM progress independently, and
ensure the Phase 4 acceptance boundary distinguishes genuinely missing
organizational inputs from work that is already authorized by the fixture.
Then run another small pair before expanding to three repetitions or the planned
four-arm T2 campaign.

## 13. Product-design issues and automatic selection

The product-level hypothesis is that Wayfinder can faithfully preserve
agent-invented blockers without testing whether they truly block a concrete
authorized ticket. In this run, U2/U3 propagated into T2 and caused total Phase
4 inactivity. That may indicate a need for clearer ticket readiness/blocker
discipline, but one agent trajectory is not enough to change Wayfinder semantics.
The issue is recorded separately in the campaign's `product-issues.md`.

Automatic selection should remain deferred. First show that explicit Wayfinder
has a repeatable net benefit after grader repair and that the over-blocking
failure is understood. This campaign does not test neutral automatic routing and
does not authorize a routing change.

## Evidence pointers

- Campaign record: [`campaign.md`](../results/arc-wayfinder-e2e-v1/campaign.md)
- Frozen evaluator: [`frozen-evaluator.json`](../results/arc-wayfinder-e2e-v1/frozen-evaluator.json)
- Isolation audit: [`context-isolation-audit.json`](../results/arc-wayfinder-e2e-v1/context-isolation-audit.json)
- Baseline result: [`result.json`](../results/arc-wayfinder-e2e-v1/runs/arc-baseline-1-68edd44151/result.json)
- Workflow result: [`result.json`](../results/arc-wayfinder-e2e-v1/runs/arc-workflow-1-e93a5ffa12/result.json)
- Separate product issue: [`product-issues.md`](../results/arc-wayfinder-e2e-v1/product-issues.md)

