# Manual semantic review

## Review rule

This review answers semantic questions from exact snapshot and result evidence.
It does not rewrite frozen JSON or convert arbitrary prose into deterministic
labels. Explicit Wayfinder `Status`, `Blocked by`, `Related`, and `Resolves`
fields are treated as structured evidence only where the product contract gives
them clear meaning. All other interpretations below are manual.

Snapshot archives under each run's `snapshots/` directory preserve the cited
repository version. Phase JSON stores the corresponding exact path, line, and
snippet packets.

## Phase review

| Question | A — vanilla handoff | B — explicit Wayfinder | Review |
| --- | --- | --- | --- |
| Phase 1 preserved settled facts | Yes | Yes | Both retained the exact SSM path, external EKS, private networking, and permissions boundary. |
| Phase 1 separated stale/open/blocked/actionable state | Yes | Yes | Both marked `m6i` stale, W1 open, W3 and W4 blocked, and W2 actionable. |
| Phase 1 avoided implementation | Yes | Yes | Frozen mapping-only checks passed. |
| Phase 2 found and consumed the deleted-source SSM fact | Yes | Yes | Both read durable state, used the exact SSM parameter, and implemented the safe IAM/SSM slice. |
| Phase 2 guessed W1, W3, or W4 | No | No | Neither selected compute, touched the legacy resource, nor invented observability input. |
| Phase 3 retired W1 unknowns after D1 | Yes | Yes | Both made dedicated MNG, `m7i.large`, no Karpenter, and 2/2/6 active while keeping W3/W4 blocked. |
| Phase 4 completed independently actionable W1/W2 | Yes | Yes | Both completed the frozen production-readiness vector and passed validation. |
| Phase 5 represented D2 as partial supersession | Yes | Yes | Both replaced only instance size and retained dedicated MNG, no Karpenter, and 2/2/6. |
| Phase 5 kept W3 blocked | Yes | Yes | Both retained the ownership blocker without blocking other work. |
| Phase 5 made W4 ready on complete project truth | No | No | Both followed the fixture's assertion that destination was the sole blocker, but the fixture did not actually contain enough alarm semantics. A also warned not to infer undocumented inputs; B dropped its earlier explicit missing-metrics concern. |
| Phase 6 limited W1 supersession rework | Yes | Yes | A changed two approximate runner lines; B changed four. Neither changed unrelated pre-existing Terraform files. |
| Phase 6 completed a justified W4 implementation | No | No | A correctly declined unsupported implementation. B created an alarm, but its metric semantics were invented and therefore not justified. |
| Phase 6 preserved W2 and W3 | Yes | Yes | Existing SSM/IAM remained valid and the legacy resource stayed untouched. |

## Key exact evidence

### A — Phase 5 and Phase 6

The Phase 5 handoff accurately captured partial supersession in
`docs/migration-continuation.md`: D1 remained authoritative for dedicated
placement, managed node groups, no Karpenter, and 2/2/6, while D2 supplied
`m7i.xlarge`. It also called the destination artifact authoritative, but warned
the next engineer not to infer other undocumented alarm inputs.

The fresh Phase 6 agent re-read `docs/observability-requirements.md` and
`docs/observability-destination.md`, changed only W1's instance size in
`terraform/runners.tf`, and documented that namespace, metric name,
dimensions, threshold, operator, period, statistic, and evaluation window were
still absent. The frozen result therefore records
`selective_continuation_complete: false`, solely because the expected alarm was
absent. That is safe behavior under the repository truth, not a continuity
failure.

### B — Phase 3, Phase 5, and Phase 6

B's Phase 3 map explicitly listed the alarm's namespace, metric name,
dimensions, threshold, period, statistic, and evaluation window as not yet
specified. During Phase 5, B resolved U3 and created ready T3 after receiving
only the SNS destination; the missing-metric list disappeared from active
state. The structured map/U/T set was internally aligned with itself, but no
longer complete relative to the repository's implementation needs.

B's fresh Phase 6 agent trusted ready T3 and created
`aws_cloudwatch_metric_alarm`. It used the supplied SNS ARN but invented
`ARC/Runner`, `FailedRunnerJobs`, threshold `1`,
`GreaterThanOrEqualToThreshold`, 60-second `Sum`, one evaluation period, and
`notBreaching`. None of those choices appeared in evaluator-controlled project
truth. The frozen result records `selective_continuation_complete: true`
because the grader asserted only alarm existence and ARN wiring. Manual review
overrides the product interpretation, not the frozen machine value: B did not
complete a *justified* W4 implementation.

## Contradiction and staleness review

- Neither final representation kept `m7i.large` as active alongside
  `m7i.xlarge`. Historical and supersession references are appropriate.
- Neither revived the stale `m6i` recommendation.
- Neither allowed W3 to block W1, W2, or W4; W3 remained open and blocked.
- A's Phase 5 handoff was internally tense—W4 was labeled actionable while the
  same document prohibited inferring missing alarm inputs—but its Phase 6
  reconciliation restored safe truth.
- B's Phase 5 map/U/T artifacts were mutually coherent on their explicit
  statuses, yet semantically incomplete because the earlier missing-metrics
  concern vanished. This is a synchronization/coverage failure, not a
  deterministic contract-field contradiction.

## Durable-state maintenance review

| Mapping point | A files / lines / reconciled | B files / lines / reconciled |
| --- | ---: | ---: |
| Phase 1 | 1 / 109 / 1 | 6 / 166 / 6 |
| Phase 3 | 1 / 108 / 1 | 8 / 239 / 4 |
| Phase 5 | 1 / 123 / 1 | 9 / 289 / 6 |

B's links and typed records made decisions, unknowns, and ready tickets easier
to navigate, and B left no active stale W1 field after D2. That structure also
required six state-file reconciliations at Phase 5 and substantially more
pre-write reading. The dropped W4 semantic gap shows that mutually consistent
statuses across distributed artifacts do not guarantee completeness. One
trajectory cannot establish whether normal Wayfinder reconciliation reliably
controls that risk.

