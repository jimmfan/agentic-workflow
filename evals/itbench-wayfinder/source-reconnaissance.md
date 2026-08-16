# ITBench / ITBench-AA source reconnaissance

Date: 2026-08-16

## Decision

Use a **pinned offline snapshot corpus** for the controlled Wayfinder study, not a live Kubernetes deployment. Pin Artificial Analysis' public dataset at commit `76df38a82288f75ba9e41dc8c515033332497473`, selectively download only the chosen scenario directories, and grade against the `ground_truth.yaml` packaged with that same revision. This gives every condition identical, immutable evidence and avoids current-source drift in Scenarios 80 and 83.

Do **not** start evaluated runs yet. Two protocol decisions remain blocking:

1. Artificial Analysis has not published its exact ITBench-AA prompt, output schema, entity-normalization matcher, or grading adapter. Public artifacts support a faithful public-data derivative, not an exact leaderboard reproduction.
2. IBM's reproducible offline prompt cannot be used unchanged for this experiment: it prescribes much of the epistemic workflow being tested and its worked example directly gives away Scenario 102's root cause and causal chain.

The clean recommendation is to freeze a short, neutral, condition-identical task prompt and deterministic entity matcher, label the study **“ITBench-AA public-data derivative,”** and retain Scenario 102 only after verifying that prompt contains no quota example. If exact use of IBM's public prompt is required, replace Scenario 102 with Scenario 33, which preserves the platform/workload scheduling boundary without appearing in the prompt's worked examples.

## Exact source pins

| Artifact | Pin | Role and status |
|---|---|---|
| Artificial Analysis ITBench-AA | `76df38a82288f75ba9e41dc8c515033332497473` | Recommended data and native-score source. It contains 40 public SRE scenarios; 19 leaderboard scenarios are held out. [Dataset card](https://huggingface.co/datasets/ArtificialAnalysis/ITBench-AA/blob/76df38a82288f75ba9e41dc8c515033332497473/README.md), [metadata and ground truth](https://huggingface.co/datasets/ArtificialAnalysis/ITBench-AA/blob/76df38a82288f75ba9e41dc8c515033332497473/sre/data.jsonl) |
| IBM ITBench-Lite | `d0916b08ba421ce5e672e9ad68aa947d938dfef0`; snapshot family `v0.2-B96DF826-4BB2-4B62-97AB-6D84254C53D7` | Alternate official snapshot source and source of the documented offline limitations. The six selected ground truths match the AA copies, aside from final-newline differences in two files. [Dataset card](https://huggingface.co/datasets/ibm-research/ITBench-Lite/blob/d0916b08ba421ce5e672e9ad68aa947d938dfef0/README.md) |
| IBM ITBench trajectories | `c3093ee33b4f16a8eed97ade1266d0d7e88b2dec` | Historical GPT-OSS-120B executions, prompts, outputs, and judge results. Reference runs, not expert solutions. [Dataset card](https://huggingface.co/datasets/ibm-research/ITBench-Trajectories/blob/c3093ee33b4f16a8eed97ade1266d0d7e88b2dec/README.md) |
| IBM public SRE agent | `30673b23a7166fc53162b2e6c23a364e7c5f0197` | Reproducible IBM/Zero/Codex runner and task prompt. Its evaluator submodule is pinned to `ab2aac2f96a06ac32320ab4d53a25d2eb266351c`. [Repository](https://github.com/itbench-hub/ITBench-CISO-SRE-FinOps-Agent/tree/30673b23a7166fc53162b2e6c23a364e7c5f0197) |
| IBM evaluator, current main inspected | `14f026fc9cc348c4ecec5ab32714de954c95c1b1` | LLM-as-judge evaluator; this is not the same artifact as AA's unpublished matcher and is newer than the public agent's submodule pin. [Evaluator](https://github.com/itbench-hub/ITBench-Evaluations/tree/14f026fc9cc348c4ecec5ab32714de954c95c1b1) |
| ITBench source, current main inspected | `a4946db21052d40c6d67fce2179aae979a211d32` | Useful for live deployment reconnaissance, but not canonical for the May 2026 snapshots. [Repository](https://github.com/itbench-hub/ITBench/tree/a4946db21052d40c6d67fce2179aae979a211d32) |
| ITBench latest release | `v1.4.1`, tag commit `e04779de62d840ae44ad1881c911732b7c886c16` | Prefer this release over moving `main` for any later live smoke test. [Release](https://github.com/itbench-hub/ITBench/releases/tag/v1.4.1) |
| Artificial Analysis Stirrup | `v0.2.0`, commit `247f24d56b2108235880ed2a2baea5d35b5a67ee` | Generic open-source harness named by AA. It contains no published ITBench-specific prompt, task packaging, matcher, or grader. [Repository](https://github.com/ArtificialAnalysis/Stirrup/tree/247f24d56b2108235880ed2a2baea5d35b5a67ee) |

The full AA dataset is approximately 31.1 GB; the six selected scenario directories are approximately 5.27 GB. Selective, revision-pinned download is therefore practical and preferable to cloning the full corpus.

## What is and is not reproducible

### ITBench-AA public methodology

AA says each task gives the model a sandboxed shell and an offline Kubernetes incident snapshot containing alerts, events, traces, metrics, logs, and application topology. The model returns structured JSON listing the minimal set of independent root-cause Kubernetes entities. Runs have a 100-turn cap and three repeats per task. [AA launch methodology](https://artificialanalysis.ai/articles/itbench-aa-launch)

The public dataset provides per-scenario alert JSON, metric TSVs, `k8s_events_raw.tsv`, `k8s_objects_raw.tsv`, `otel_logs_raw.tsv`, `otel_traces_raw.tsv`, and `ground_truth.yaml`; global `sre/data.jsonl` repeats every ground truth. It does not include a task prompt or an application-topology file in each scenario directory. The topology used by IBM's runner is a separate `architecture.json` in the public agent repository. [AA Scenario 102 tree](https://huggingface.co/datasets/ArtificialAnalysis/ITBench-AA/tree/76df38a82288f75ba9e41dc8c515033332497473/sre/Scenario-102), [IBM topology file](https://github.com/itbench-hub/ITBench-CISO-SRE-FinOps-Agent/blob/30673b23a7166fc53162b2e6c23a364e7c5f0197/metadata/otel_demo_astronomy_shop/architecture.json)

AA has not published the exact system/user prompt, output JSON schema, topology version, entity parsing and alias-normalization code, retry policy, or model sampling configuration used for its leaderboard. Stirrup is generic and does not fill those gaps. The data and public scoring formula can be pinned; exact leaderboard execution cannot.

### Reproducible IBM offline runner

IBM's public task prompt is exact and requires an `agent_output.json` with `entities`, `propagations`, and `alerts_explained`; contributing factors must be minimal and irreducible, with evidence and a causal chain. [Exact prompt](https://github.com/itbench-hub/ITBench-CISO-SRE-FinOps-Agent/blob/30673b23a7166fc53162b2e6c23a364e7c5f0197/zero/zero-config/prompts/sre_react_shell_investigation.md) An instantiated prompt and full session are visible in the [Scenario 24 trajectory](https://huggingface.co/datasets/ibm-research/ITBench-Trajectories/blob/c3093ee33b4f16a8eed97ade1266d0d7e88b2dec/ReAct-Agent-Trajectories/OpenAI-GPT-OSS-120B/sre/Scenario-24/1/session.jsonl).

That is useful for benchmark reproduction but a poor control prompt for this study: it mandates hypothesis generation, validation, propagation analysis, and restraint against premature conclusions. Those are close to the intended Wayfinder treatment, so giving them to A, B, and C would attenuate or confound the treatment contrast.

## Leakage and scenario validity

The alerting-state files for Scenarios 102, 34, 83, 17, 24, and 80 describe symptoms rather than naming their root causes. The selected snapshots are therefore usable as evidence tasks. Three stronger leakage controls are mandatory:

1. **Physically exclude ground truth.** `ground_truth.yaml` is adjacent to observation data and `sre/data.jsonl` contains all answers. Do not rely on the prompt's instruction not to read them. Build a read-only agent view containing only observations and the pinned topology.
2. **Exclude trajectories and reconnaissance.** Published sessions, outputs, judge files, this report, the evaluation protocol, and the user's scenario-selection rationale contain answer-salient material. None may be mounted into a run workspace.
3. **Treat descriptive evidence as evidence, not prompt text.** Some raw Kubernetes objects and events make the injected fault readily searchable—for example, the NetworkChaos resource names in 80 and 83 and the incorrect environment value in 24. That is legitimate diagnostic evidence shared equally across conditions, not task-prompt leakage.

### Scenario 102

IBM's public prompt includes a worked example where a memory quota on `otel-demo/Namespace/otel-demo` prevents the ad deployment from creating pods. This is Scenario 102's expected root and causal structure. [Prompt example](https://github.com/itbench-hub/ITBench-CISO-SRE-FinOps-Agent/blob/30673b23a7166fc53162b2e6c23a364e7c5f0197/zero/zero-config/prompts/sre_react_shell_investigation.md#L186)

Conclusion:

- With a newly frozen neutral prompt that lacks this example, Scenario 102 remains valid.
- With IBM's public prompt, Scenario 102 is invalid and should be replaced by [Scenario 33](https://huggingface.co/datasets/ArtificialAnalysis/ITBench-AA/tree/76df38a82288f75ba9e41dc8c515033332497473/sre/Scenario-33), an invalid-node-selector scheduling incident that retains the desired platform/workload boundary.

### Ground-truth drift

Use the ground truth from the pinned snapshot, never current ITBench source. Current Scenario 83 injects a fraud-detection-to-Kafka partition while the pinned AA snapshot expects email-to-checkout; current Scenario 80 also contains a mismatched resource name. [Current Scenario 83 definition](https://github.com/itbench-hub/ITBench/blob/a4946db21052d40c6d67fce2179aae979a211d32/scenarios/sre/project/roles/scenarios/files/scenario_83/scenario.yaml#L17), [current Scenario 83 ground truth](https://github.com/itbench-hub/ITBench/blob/a4946db21052d40c6d67fce2179aae979a211d32/scenarios/sre/project/roles/scenarios/files/scenario_83/groundtruth_v1.yaml#L22), [current Scenario 80 definition](https://github.com/itbench-hub/ITBench/blob/a4946db21052d40c6d67fce2179aae979a211d32/scenarios/sre/project/roles/scenarios/files/scenario_80/scenario.yaml#L17)

Scenario 17's entity target is usable for native grading, but its packaged explanation is weak: the fault condition is unspecified and one fault field says `Service` while the scoring group identifies a `NetworkChaos` root. Treat it cautiously in the reasoning rubric and do not use it as the sole evidence for a qualitative conclusion.

## Native scoring

For each repeat, derive the predicted set only from entities explicitly marked as contributing factors. After applying a **pre-frozen** canonicalization/alias map:

```text
TP = predicted contributing-factor entities matching ground-truth roots
FP = predicted contributing-factor entities not matching a root
FN = ground-truth roots not matched
native_score = TP / (TP + FP), if FN == 0; otherwise 0
```

AA calls this average precision at full recall and averages it across all task repeats. [Official formula](https://artificialanalysis.ai/articles/itbench-aa-launch) Every selected scenario has one ground-truth root, so one correct entity alone scores `1.0`, the correct entity plus one false positive scores `0.5`, and missing the root scores `0`.

Record `TP`, `FP`, `FN`, `full_recall`, and `native_score`. AA does not publish a separate binary “success” definition, so do not silently invent one; if the protocol needs `success`, define it transparently as `full_recall && FP == 0` before any outputs are seen.

The unresolved part is exact matching. AA has not published its normalizer. Freeze a deterministic mapping from the pinned ground-truth `groups`, `filter`, `kind`, namespace, and aliases before running, preserve unmatched raw predictions, and label the result a derivative. Do not substitute IBM's LLM judge and call it the AA native metric.

IBM's current evaluator is a separate, LLM-as-judge system for semantic entity matching, reasoning, propagation, localization, and proximity; it reports entity precision/recall/F1 and derived top-k metrics. [Evaluator README](https://github.com/itbench-hub/ITBench-Evaluations/blob/14f026fc9cc348c4ecec5ab32714de954c95c1b1/README.md), [entity rubric](https://github.com/itbench-hub/ITBench-Evaluations/blob/14f026fc9cc348c4ecec5ab32714de954c95c1b1/itbench_evaluations/prompts/entity_correctness.py) If used at all, pin its commit, prompt, judge model, and settings and report it as a secondary official diagnostic score—not as AA's headline score.

## Snapshot versus live runtime

The offline snapshots are the right primary runtime for this causal comparison. They hold evidence constant, avoid cluster state and timing variance, make randomized A/B/C ordering meaningful, and reduce setup from a Kubernetes observability stack to a read-only filesystem sandbox.

The tradeoff is explicit: IBM says ITBench-Lite lacks real-time streaming, runtime state changes and nondeterminism, interactive/human-in-the-loop debugging, and active remediation such as rollouts or scaling. [Official limitations](https://huggingface.co/datasets/ibm-research/ITBench-Lite/blob/d0916b08ba421ce5e672e9ad68aa947d938dfef0/README.md#limitations) The resulting experiment can support claims about diagnosis and causal attribution over fixed evidence, not live incident response or remediation.

A live run is much heavier and less reproducible: ITBench requires Python 3.12–3.14, `uv`, Ansible, `kubectl`, Helm, a Kubernetes cluster, OpenTelemetry/Prometheus/Jaeger/ClickHouse/OpenCost services, container-image pulls, and scenario deployment/cleanup. [Current prerequisites](https://github.com/itbench-hub/ITBench/blob/a4946db21052d40c6d67fce2179aae979a211d32/pyproject.toml), [scenario workflow](https://github.com/itbench-hub/ITBench/blob/a4946db21052d40c6d67fce2179aae979a211d32/documentation/getting-started/scenarios.md) It should be reserved for a later, small confirmatory smoke test after source inconsistencies are resolved, not used for the 54-run primary study.

IBM's current offline Zero runner is also not lightweight in the strict sense: it requires Python 3.12/3.13, `uv`, Node/npm, Codex CLI exactly `0.94.0`, a model-provider endpoint, and its documented MCP/container stack. [Agent prerequisites](https://github.com/itbench-hub/ITBench-CISO-SRE-FinOps-Agent/tree/30673b23a7166fc53162b2e6c23a364e7c5f0197#quick-start) A small local adapter over the pinned flat files is simpler and adequate for this experiment, but again must be reported as a public-data derivative.

## Reference trajectories

The trajectory dataset has three GPT-OSS-120B runs for each selected scenario, with `session.jsonl`, usually `agent_output.json`, and usually `judge_output.json`. These are historical baseline executions, not canonical solutions; published runs can be wrong, and Scenario 80 run 2 lacks a final output and judge file despite the dataset card's completeness claim. Keep the entire dataset sealed until prompts, rubric, and normalization are frozen, and never expose it to evaluated agents. [Scenario 80 trajectories](https://huggingface.co/datasets/ibm-research/ITBench-Trajectories/tree/c3093ee33b4f16a8eed97ade1266d0d7e88b2dec/ReAct-Agent-Trajectories/OpenAI-GPT-OSS-120B/sre/Scenario-80)

## Phase 0 gate

Proceed to runs only after the run manifest records all of the following:

- AA dataset commit `76df38a...`, selected scenario IDs, per-file hashes, and topology hash;
- an agent-visible allowlist that excludes every ground-truth, trajectory, protocol, rubric, and reconnaissance artifact;
- the exact neutral prompt and structured output schema, identical in A/B/C;
- the deterministic entity-normalization map and native score implementation;
- the separately frozen reasoning rubric/evaluator;
- the frozen Codex model, reasoning effort, CLI/app build, turn/time/token limits, tool permissions, network policy, and condition-specific Agentic Workflow version/configuration;
- the Scenario 102 decision: neutral prompt and retain it, or IBM prompt and replace it with 33.

Until those are frozen, this phase is a **no-go for evaluated runs**, not a failure of the benchmark. The snapshots themselves are suitable; the missing AA adapter and IBM prompt contamination are the blockers.
