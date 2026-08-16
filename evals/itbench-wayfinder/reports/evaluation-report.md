# Controlled ITBench Wayfinder evaluation

## Practical conclusion

This experiment found **no reliable improvement from the frozen Agentic
Workflow, and no incremental benefit from forcing Wayfinder**, on these six
bounded offline Kubernetes investigations.

The strict native result was 3/18 successes for vanilla Codex, 4/18 for normal
workflow routing, and 3/18 for explicit Wayfinder. The one-run workflow edge is
not persuasive: it came from a scenario 34 submission that named the expected
Valkey Pod but did not identify the ground-truth authentication fault. In the
same campaign, the native matcher rejected many diagnoses that identified the
right fault mechanism at a different Kubernetes entity layer. The primary
score is therefore reproducible but a poor measure of absolute diagnostic
correctness for this snapshot set.

The separately frozen reasoning rubric also showed no consistent treatment
gain. Normal workflow routing had small positive shifts in evidence labeling
and ownership reasoning, but equally small negative shifts in discriminating
evidence, unknown preservation, minimal attribution, and remaining-evidence
statements. Explicit Wayfinder did not improve any clear reasoning pattern over
normal routing and was slightly worse on several uncertainty-related measures.

Cost moved in the wrong direction. Relative to vanilla, normal workflow routing
used 58% more elapsed time and 42% more input tokens; explicit Wayfinder used
43% more elapsed time and 51% more input tokens. Wayfinder's specific net
contribution was rated `mixed` in 15/18 runs and `not_observable` in 3/18. No run
invoked Domain Modeling, so this experiment says nothing about its causal value.

This is a negative result for the tested workload, not proof that Wayfinder is
never useful. These were single-shot, read-only diagnoses with unusually direct
snapshot evidence; explicit Wayfinder never produced durable state and often
amounted to extra setup around ordinary debugging.

## What was tested

- 6 ITBench-AA public SRE snapshots: 102, 34, 83, 17, 24, and 80.
- 3 conditions: A vanilla Codex; B frozen Agentic Workflow with normal routing;
  C the byte-identical workflow with explicit `$wayfinder`.
- 3 repetitions per scenario and condition: **54 diagnostic runs total**.
- Model `gpt-5.6-terra`, reasoning effort `medium`, Codex CLI `0.144.6`.
- Agentic Workflow version `0.11.1`, source commit
  `c5bf31577c7523e31658ec0dd9b59ae7f5aeede0`.
- ITBench-AA revision `76df38a82288f75ba9e41dc8c515033332497473`.

This is an **ITBench-AA public-data derivative**, not an exact leaderboard
reproduction: the private benchmark prompt and exact evaluator are unpublished.
The public precision-at-full-recall formula and frozen entity filters were
implemented deterministically.

## Integrity and execution

- The manifest, prompt, native matcher, and reasoning rubric were frozen before
  evaluated output.
- All 727 agent-visible files were hash-verified and read-only; six
  `ground_truth.yaml` files remained controller-only.
- All 2,234 static preflight checks passed.
- The live isolation audit passed for A, B, and C.
- A saw no workflow instructions. B and C received byte-identical workflow
  installations; C differed only by the `$wayfinder` prefix.
- All 54 runs used fresh Git workspaces and ephemeral minimal `CODEX_HOME`s.
- All 54 exited normally, produced valid JSON, and required no retries.
- No evaluated command attempted `curl`, `wget`, `ssh`, `kubectl`, or a cloud
  CLI. Every workspace changed only `diagnosis.json`.
- The frozen product fingerprint remained unchanged after execution.

The first 18-run pass took 37.3 minutes. Because the estimated remaining runtime
was practical and there was no fairness defect, the preregistered decision rule
continued to the full 54 runs. Summed diagnostic elapsed time was 2.17 hours.

## Aggregate results

Higher reasoning scores are better on a 0–2 scale. `N/A` means the dimension
was not observable often enough to compare.

| Metric | A Vanilla | B Workflow auto | C Explicit Wayfinder |
| --- | ---: | ---: | ---: |
| Strict native mean | 0.167 | 0.222 | 0.167 |
| Strict native successes | 3/18 | 4/18 | 3/18 |
| Strict entity precision | 0.167 | 0.222 | 0.158 |
| Strict entity recall | 0.167 | 0.222 | 0.167 |
| Strict false-positive predictions | 15 | 14 | 16 |
| Evidence vs assumption | 1.667 | 1.722 | 1.667 |
| Premature root-cause assignment | 1.889 | 1.833 | 1.778 |
| Symptom vs cause | 2.000 | 2.000 | 1.944 |
| Unknown preservation | 1.389 | 1.333 | 1.278 |
| Discriminating evidence | 1.500 | 1.389 | 1.444 |
| Visibility-limit recognition | 0.625 (n=16) | 0.667 | 0.556 |
| Ownership/boundary reasoning | 1.889 | 2.000 | 1.944 |
| Unsafe-remediation avoidance | 2.000 | 2.000 | 2.000 |
| Minimal causal attribution | 1.944 | 1.833 | 1.833 |
| Remaining evidence requirements | 0.778 | 0.667 | 0.611 |
| Wayfinder invocation | N/A | 0/18 | 18/18 treatment; 17/18 direct skill-read/action evidence |
| Workflow Debugging invocation | N/A | 18/18 | 1/18 |
| Domain Modeling invocation | N/A | 0/18 | 0/18 |
| Mean elapsed seconds | 108.4 | 171.4 | 154.8 |
| Median elapsed seconds | 104.1 | 132.8 | 140.3 |
| Mean input tokens | 994,523 | 1,416,422 | 1,502,370 |
| Mean cached input tokens | 888,633 | 1,271,310 | 1,368,078 |
| Mean output tokens | 4,254 | 5,572 | 6,312 |
| Mean tool actions | 15.5 | 16.7 | 17.8 |

The native paired comparisons were almost entirely ties:

- A→B: B won 1 of 18 paired cells, tied 17, and lost 0; mean difference +0.056.
- B→C: C won 0, tied 17, and lost 1; mean difference −0.056.
- A→C: all 18 paired cells tied; mean difference 0.

There are only six independent scenario clusters, so these small ordinal-score
differences should not be treated as statistically established effects.

## Why the native score is misleading

The frozen matcher faithfully implements exact kind/name/namespace filters, but
those filters do not consistently correspond to the most defensible causal
entity in the snapshots, and they ignore the submitted `condition` text.

- Scenario 102 expects the Namespace, while every run identifies the concrete
  `ResourceQuota` and correctly explains how it blocks the ad replacement pod.
- Scenarios 17, 80, and 83 expect a base-name `NetworkChaos`; runs identify the
  parent `Schedule` or generated child chaos resources with suffixes while
  correctly describing the injected fault and propagation.
- Scenario 34 awards B repetition 1 for naming the expected Pod, even though it
  does not identify the password-authentication mismatch. Most other runs name
  the Valkey Deployment but incorrectly blame CPU throttling.
- Scenario 24 is clean: all nine runs identify the expected Deployment and bad
  Kafka port.

This means the 4/18 B result is not evidence of a workflow correctness gain.
The condition-blinded adjudication packet preserves these ambiguities for a
separate sensitivity review without rewriting the primary metric.

## Reasoning-quality result

No reasoning dimension shows a stable, meaningful treatment improvement.

For B versus A, the largest positive shift was ownership/boundary reasoning
(+0.111 on the 0–2 scale). The same treatment was −0.111 on discriminating
evidence, minimal attribution, and remaining-evidence requirements. For C versus
B, only discriminating evidence rose (+0.055); evidence labeling, premature
closure, unknown preservation, visibility limits, ownership reasoning, and
remaining-evidence statements each fell by 0.055–0.111. These are tiny effects
relative to run-to-run and scenario variation.

The clearest cross-condition strengths were shared by all arms: symptom/cause
separation was near-perfect, and no run attempted or recommended unsafe
shotgun remediation. The shared weakness was acknowledging snapshot visibility
limits and stating what evidence would still be needed.

Belief updating and safe continuation were usually genuinely unobservable, so
they were not compared. The rubric was not collapsed into a single score.

## Wayfinder and other capability behavior

Normal routing selected Workflow Debugging in all 18 B runs and never selected
Wayfinder. Fourteen B runs emitted `[route: router → debugging]`. This looks
reasonable for bounded incident diagnosis, and C did not outperform B, so this
experiment does not support a claim that the router missed a beneficial
Wayfinder opportunity.

Explicit C treatment caused observable Wayfinder use in the trajectory, but no
run created durable Wayfinder state; every evaluated workspace changed only the
required diagnosis file. The Wayfinder-specific grader found:

- net contribution: 15 `mixed`, 3 `not_observable`, 0 unambiguously `helpful`;
- duplicated debugging/process overhead: 7 `harmful`, 10 `mixed`, 1
  `not_observable`;
- material trajectory change: 17 `not_observable`, 1 `helpful`;
- symptom/cause distinction: 13 `helpful`, 2 `mixed`, 3 `not_observable`;
- uncertainty preservation: 3 `helpful`, 4 `mixed`, 3 `harmful`, 8
  `not_observable`.

The common pattern was useful causal language without evidence that Wayfinder
caused it. Agents often loaded routing/Wayfinder instructions, retried unavailable
shell utilities, then performed essentially ordinary snapshot debugging. That
explains why explicit Wayfinder could look disciplined yet show no incremental
score gain and materially higher token use.

Domain Modeling, Research, Discovery, and Verification were never materially
invoked. Domain Modeling therefore neither helped nor hurt these trajectories;
there is no basis here for a separate Domain Modeling recommendation.

## Per-scenario results

### Scenario 102 — namespace quota blocks ad pod creation

All nine runs found the `otel-demo-memory` ResourceQuota, tied it to rejected ad
pod creation, and traced the failure through the ad Service to frontend errors.
A, B, and C all received native zero only because ground truth requires the
Namespace entity. B's reasoning grader favored uncertainty preservation but was
weaker on discriminating evidence and visibility limits; C did not materially
change the trajectory. Practical interpretation: all treatments solved the
engineering problem at a concrete entity layer; Wayfinder added no useful
increment.

### Scenario 34 — Valkey authentication mismatch

This is the real diagnostic failure. Eight runs blamed CPU starvation in a
Valkey or cart Deployment; the remaining B run named the exact Valkey Pod but
only called it nonresponsive. None found the password-authentication mismatch.
B's one native success is therefore an entity-only grading artifact. Reasoning
scores were also weakest here, especially for preserving uncertainty and naming
remaining evidence. Practical interpretation: neither the router's Debugging
path nor explicit Wayfinder pushed the agent toward evidence that distinguished
authentication failure from resource saturation.

### Scenario 83 — checkout/email network partition

All nine runs found the checkout/email Chaos Mesh partition and correctly traced
timeouts through checkout to proxy failures. They named either the parent
Schedule or generated NetworkChaos child, so the exact base-name matcher gave
all zero. C had its clearest local reasoning uplift here, particularly in
unknown preservation, but correctness was unchanged and the effect did not
generalize. Practical interpretation: ordinary debugging was already sufficient
to separate healthy email pods from the network fault.

### Scenario 17 — product-catalog network delay

All nine runs found recurring Chaos Mesh delay against product-catalog and
treated dependent service failures as symptoms. They named the parent Schedule
or generated PodNetworkChaos instead of the frozen NetworkChaos group, yielding
native zero. B was locally stronger on evidence discipline and unknown
preservation; C was weaker on unknown preservation and discriminating evidence.
Practical interpretation: forced Wayfinder did not help on the multi-hop case it
was expected to favor.

### Scenario 24 — checkout Kafka port misconfiguration

All nine runs exactly identified `Deployment/checkout`, `KAFKA_ADDR=kafka:9999`,
and propagation through checkout availability. Every condition scored 1.0 in
every repetition. Practical interpretation: the evidence was direct enough that
workflow machinery had no correctness headroom; B and C only added cost.

### Scenario 80 — checkout/Kafka network partition

All nine runs found the checkout/Kafka partition and traced checkout and proxy
failures correctly. Again, Schedule/generated-child names failed the exact
base-name matcher. Reasoning differences were small: B improved visibility-limit
recognition locally, while C gathered slightly more discriminating evidence.
Practical interpretation: no treatment changed the substantive diagnosis.

## Evidence, interpretation, and next experiments

### Evidence

- Strict native correctness: A 3/18, B 4/18, C 3/18, with the B edge caused by
  one entity-only match whose condition was wrong.
- A and C tied in every native paired cell.
- No reasoning dimension showed a consistent workflow or Wayfinder advantage.
- B and C increased elapsed time and tokens substantially.
- B consistently routed to Debugging; C used Wayfinder but created no durable
  Wayfinder artifact.
- Domain Modeling was never invoked.

### Interpretation

For these bounded offline incidents, the current router's decision not to select
Wayfinder appears defensible. Explicit Wayfinder added instruction-processing
and setup overhead but did not prevent the shared scenario 34 misdiagnosis or
improve uncertainty handling overall. The experiment does not support changing
the product to invoke Wayfinder more aggressively.

The stronger immediate finding is about evaluation quality: exact entity
matching without condition validation confounds controller/child identity with
causal correctness. Absolute benchmark scores should not drive product changes
until that ontology boundary is adjudicated.

### Possible future experiments

1. Run the blinded adjudication packet and preregister a condition-aware semantic
   matcher before any new treatment comparison. Prefer the official evaluator if
   its exact contract becomes available.
2. Test Wayfinder on longer, interruptible investigations where multiple unknowns
   genuinely persist and durable re-entry state can be used. This campaign did
   not exercise that product contract.
3. If testing overhead, isolate workflow instruction loading from routing logic
   and ensure ordinary document-inspection utilities are available; do not infer
   a production latency regression solely from this sanitized harness.
4. Do not run a Domain Modeling isolation study yet. First choose scenarios with
   real terminology, ownership, or state-model ambiguity that would plausibly
   trigger it naturally.

## Limitations

- Only six unique scenarios were tested, with three stochastic repetitions.
- The exact private ITBench-AA prompt and evaluator are unavailable.
- Frozen ground truth contains entity-layer and scenario-17 consistency issues.
- Snapshots cannot support live follow-up queries or remediation validation.
- The reasoning grader used the same model family, one grade per trajectory, and
  could observe treatment behavior through skill reads even though condition
  labels and run IDs were hidden.
- To honor the approved data-transfer boundary, reasoning graders did not receive
  ground truth. Native correctness used it locally; reasoning grades assess only
  observable epistemic discipline.
- Token counts include large cached-input components and are not dollar cost.

## Artifacts

- Frozen manifest: `../frozen-manifest.json`
- Protocol: `../protocol.md`
- Reasoning rubric: `../reasoning-rubric.md`
- Scenario metadata: `../scenario-metadata.md`
- Source reconnaissance: `../source-reconnaissance.md`
- Static preflight: `../preflight.json`
- Context-isolation audit: `../context-isolation-audit.json`
- Machine-readable aggregate: `results-summary.json`
- Blinded adjudication packet: `manual-adjudication.md`
- Per-run execution records and raw transcripts: `../results/runs/`
- Per-run native and reasoning grades: `../results/grades/`

