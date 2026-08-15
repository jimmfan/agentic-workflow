# ARC Wayfinder end-to-end v2 smoke

- Campaign ID: `arc-wayfinder-e2e-v2`
- Status: **completed; report issued; repetitions stopped**
- Authorized program ticket: [T3 — Run corrected ARC Wayfinder v2 smoke](../../../.ai-workflow-state/wayfinder/evaluation-program/tickets/T3-corrected-arc-wayfinder-v2-smoke.md)
- Repetitions: one trajectory per condition; stop after the smoke report
- Product scope: evaluation infrastructure and fixture only

## Purpose and expected outcome

V1 found a promising exact-fact continuity/actionability signal for explicit
Wayfinder, but it conflated explicit Wayfinder with broader Agentic Workflow,
used brittle keyword-window semantic grading, hid partial safe progress in one
composite, and left Phase 4 too ambiguous to establish over-blocking.

V2 corrects those experimental defects without changing Agentic Workflow or
Wayfinder product behavior. A successful campaign yields twelve isolated raw
phase records, three completed trajectories, primitive machine observations,
inspectable semantic evidence, a treatment-crossover audit, and a report that
compares A-vs-B, B-vs-C, and A-vs-C separately. It does not yield an automatic
routing decision or authorize repetitions.

## Conditions

- **A — Vanilla + neutral durable handoff:** no Agentic Workflow installation;
  the agent is explicitly asked for repository-native durable continuation.
- **B — Agentic Workflow + neutral durable handoff:** the same semantic prompts
  as A, with Agentic Workflow installed normally and no explicit Wayfinder
  request. Normal routing remains enabled; any Wayfinder use is recorded as
  treatment crossover rather than suppressed.
- **C — Agentic Workflow + explicit Wayfinder:** the same installation as B;
  Phases 1 and 3 explicitly invoke `$wayfinder`.

The primary comparisons are A-vs-B (broader Agentic Workflow), B-vs-C
(incremental explicit Wayfinder), and A-vs-C (total system difference). No
overall score is computed.

## Frozen execution controls

The machine preregistration is
[`evals/campaigns/arc-wayfinder-e2e-v2.json`](../../campaigns/arc-wayfinder-e2e-v2.json).
It fixes:

- GPT-5.6 Terra with medium reasoning;
- workspace-write sandbox and approvals `never`;
- identical environment/network policy;
- twelve sequential `codex exec --ephemeral` processes with no resume;
- phase-interleaved A/B/C ordering;
- exact prompts;
- one smoke trajectory per condition; and
- the evidence-quality and semantic-classification vocabularies.

Every process gets a unique temporary `CODEX_HOME` containing only a mode-0600
copy of the existing authentication file. User config, user rules, global
skills, controller `CODEX_*` variables, cloud environment variables, and
controller/sibling paths are not inherited by model-generated shells. The
temporary home is removed after the process; source credentials are never
modified or recorded.

## Fixture and mutation contract

The initial fixture preserves the v1 scenario: external EKS, exact SSM AMI
path, private networking, permissions boundary, stale `m6i`, unresolved compute
architecture, ambiguous legacy-resource ownership, and safe SSM/IAM work.
Phase 2 deletes only `docs/platform-facts.md` after Phase 1 evidence is captured.

Phase 3 adds the same benchmark plus an approved decision/readiness artifact
that supplies every project-specific input for a bounded implementation:
dedicated `m7i.large` managed-node-group capacity, 2/2/6 scaling, private
subnets, exact SSM lookup, EC2 trust and required policy ARNs, permissions
boundary, authorized new IAM/launch-template/node-group resources, and no
Karpenter. Legacy ownership stays unresolved but is explicitly non-blocking for
the isolated new resources. No external plan or apply is authorized.

## Corrected evidence model

Deterministic checks are limited to inspectable primitive state or code, such as
exact literals, resource types, attributes, dependencies, policy ARNs, changed
files, command exit statuses, and raw runtime usage.

Semantic questions retain exact `path`, `line`, and `snippet` evidence. Their
classification is one of `explicit_affirmative`, `explicit_negative`,
`unresolved`, `absent`, or `ambiguous`. The grader does not infer a positive
decision from nearby keywords. Ambiguous cases stay ambiguous for manual report
interpretation.

Fact preservation, location/read, trusted consumption, and final
implementation are separate. SSM, IAM/boundary, other reversible progress,
premature architecture, external violations, every Phase 4 component,
verification, rework, and overhead are also independent observations.

For Condition B, each phase records explicit-invocation evidence, Wayfinder
skill reads, Wayfinder-state creation/modification/read, and self-reported route
markers. Raw JSONL remains authoritative where hidden provider dispatch is not
exposed.

## Freeze and isolation gate

The evaluator-critical inventory consists of the v2 harness, machine campaign,
fixture, and mutations. A freeze records their SHA-256 digests plus the current
source Git SHA. Once live evidence exists, it must never be overwritten; a new
defect requires a new campaign.

After freezing, the three-condition audit creates independent disposable Git
roots under `/private/tmp`, verifies A and byte-identical B/C installations,
runs one fresh read-only canary probe per condition, and records raw probe JSONL
and stderr. It checks unique execution IDs, no resume, auth-only `CODEX_HOME`,
empty inherited shell environment, no parent/sibling/controller canary, no
unexpected Agentic Workflow in A, no repository mutation, and grader/raw
evidence outside evaluated repositories. Any failed check stops live execution.

## Verification completed for the final freeze

From the source repository root on the macOS host:

```text
python3 -B -m unittest evals.tests.test_arc_wayfinder_v2 -v
python3 -B -m unittest discover -s evals/tests -v
python3 -B -m evals.arc_wayfinder --verify-freeze
python3 skills/agentic-workflow/scripts/verify_package.py --tests
```

Observed results: 13 v2 tests passed, 40 total eval tests passed, the v1 freeze
matched, and the 46-test package gate ended with
`OK: Agentic Workflow package verification passed.`

## Completed smoke

- Condition A: `arc-v2-a-1-f3d63c2258`
- Condition B: `arc-v2-b-1-0cdb658fca`
- Condition C: `arc-v2-c-1-cde5e0d86f`
- Live phase interval: 2026-08-15; twelve unique fresh execution IDs; every
  evaluated process exited 0
- Result: all three arms preserved, located, consumed, and implemented the exact
  AMI fact and completed every frozen phase-4 component
- Treatment crossover: condition B selected Wayfinder automatically and used or
  modified its state in all four phases
- Interpretation: informative smoke, but B-versus-C is potentially confounded
  and the semantic classifier retains material known limitations
- Report: [`../../reports/2026-08-15-arc-wayfinder-e2e-v2.md`](../../reports/2026-08-15-arc-wayfinder-e2e-v2.md)
- Product/tooling issues: [`product-issues.md`](product-issues.md)

The final corrected isolation audit passed before any evaluated agent ran and
recorded the exact frozen evaluator hash. It completed 33 seconds after the
final freeze rather than before it; this procedural reversal is retained as a
known limitation. Two earlier preflight attempts are preserved under
[`preflight/`](preflight/): the first was blocked by the controller sandbox's
network policy before inference, and manual inspection rejected the second
audit's grader because it missed an ambiguous underscored JSON field. No
evaluated agent ran in either attempt.

## Persistent artifacts and cleanup

The campaign persists its freeze, audit, raw probe evidence, raw phase JSONL and
stderr, phase JSON, snapshots, result JSON, report, and separate product issues
under `evals/results/arc-wayfinder-e2e-v2/`. Evaluated repositories and control
state live only under the guarded campaign temp root.

After all three results are safely persisted, the harness may remove each
completed temporary run with `--cleanup RUN_ID`. Cleanup refuses incomplete or
out-of-root targets and never removes result evidence. Temporary authentication
copies are removed after every individual Codex process. No source auth file,
Keychain item, credential volume, v1 artifact, or external infrastructure is
modified.

Cleanup completed after report persistence and before final verification. The
three guarded run directories occupied 1,928 KiB of actual filesystem blocks
and were removed; raw evidence and all twelve snapshot archives remain under
this result namespace. The twelve per-process temporary homes had already been
removed immediately after use (512,011,180 logical bytes recorded).

## Interpretation boundary

One trajectory per condition is smoke evidence, not a distribution. The final
report must preserve any frozen grader defect, disclose every isolation
limitation, stop before repetitions, record product issues separately, and
leave automatic Wayfinder routing deferred for human review.
