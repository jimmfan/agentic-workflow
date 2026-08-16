# ITBench Scenario 17 token-spike replication

## Result

**TOKEN SPIKE NOT REPRODUCED**

The single authorized replication completed normally and produced a
substantively correct diagnosis. It used 877,135 input tokens, of which 758,016
were cached, in 85.752 seconds and 14 tool actions. The historical B-new outlier
used 6,012,435 input tokens, of which 5,766,144 were cached, in 402.068 seconds
and 37 actions.

The tested source revision was `7a6bfaaae859ec0b16f4cee4807cd0021d7da76f`.
The preceding B-new manifest recorded `6d5a030a27afce1049d15afdfa36fe3e10fb162d`,
but the installed product payload and projected-skill tree fingerprints are
unchanged; the intervening revision adds passive forensics and evaluation
storage only. Both runs used Codex CLI `0.144.6`, `gpt-5.6-terra`, medium
reasoning, the same frozen prompt/snapshot, and the same sandbox and approval
contract. Preflight and post-run integrity passed, and exactly one model-started
attempt was recorded.

The replication is therefore 85.4% lower in total input, 86.9% lower in cached
input, 78.7% faster, and 62.2% shorter by tool actions. Its 877K input, 758K
cached input, and 14 actions are within or immediately adjacent to the old-B
Scenario 17 range (883K-1.530M input, 750K-1.374M cached, 14-18 actions).

## Direct comparison

| Metric | Historical B-new | Replication |
|---|---:|---:|
| Native result | fail (0.0) | fail (0.0) |
| Practical diagnosis | correct | correct |
| Seconds | 402.068 | 85.752 |
| Input tokens | 6,012,435 | 877,135 |
| Cached input | 5,766,144 | 758,016 |
| Uncached input | 246,291 | 119,119 |
| Output | 14,435 | 3,827 |
| Cached ratio | 95.9% | 86.4% |
| Tool actions | 37 | 14 |
| Total tool-output bytes | 3,256,648 (3.11 MiB) | 3,463,651 (3.30 MiB) |
| Largest single output | 1,048,576 bytes | 1,048,576 bytes |
| Broad / likely unbounded searches | 4 / 2 | 3 / 3 |
| Failed commands | 5 | 5 |
| Exact repeated commands | 0 | 0 |
| Near-identical command groups | 1 | 0 |
| Inferred repeated-read paths | 10 | 6 |
| Material skill | Debugging | Debugging |
| Wayfinder | not loaded or used | not loaded or used |
| Compaction | unobservable | unobservable |

The analyzer's totals reconcile exactly with the trace's sole
`turn.completed` aggregate usage event. The one observed top-level Codex turn
must not be interpreted as one internal model inference.

## What happened

Large outputs repeated but the long trajectory did not. The replication emitted
three 1 MiB results and 3.30 MiB total—6.4% more recorded output than the
historical outlier. Those outputs occurred with seven, six, and two later tool
actions remaining. By contrast, the historical run emitted a 1 MiB result with
24 actions still to come and continued to 37 actions total.

The replication did revisit related evidence: `k8s_objects_raw.tsv` appeared in
five commands, while events and logs appeared twice each. It also repeated the
campaign-wide missing-utility friction, with five failed commands. Neither
behavior became a long trajectory: failures emitted only 994 bytes, the agent
found the Chaos mechanism early, and it closed after 14 actions.

This is strong evidence against raw tool-output volume as a sufficient cause.
The historical spike is best explained by the interaction previously proposed:
a large/growing context followed by an unusually long exploratory trajectory,
causing the large cacheable context to be carried through many later internal
cycles. Because this one matched replication did not reproduce that trajectory,
the evidence supports treating the original 6M-token result primarily as
stochastic search-path variance. One replication supports that interpretation;
it does not prove it statistically.

## Framework and diagnosis

Both runs naturally selected Debugging. The replication observed 18,317 bytes
associated with reading routing and the Debugging skill, about 0.53% of recorded
tool-output bytes and nearly identical to the historical 17,451 bytes. No
Wayfinder instruction or state was read or written. Static Agentic Workflow and
Wayfinder overhead were not material contributors.

The frozen native matcher again returned zero because it expects
`NetworkChaos/chaos-mesh`, whereas the replication named the generated
`PodNetworkChaos/otel-demo/product-catalog-...`. The mechanism was nevertheless
correct: recurring Chaos Mesh network disruption against product-catalog caused
15-second upstream timeouts and downstream symptoms. The campaign's prior
blinded manual adjudication explicitly accepted this generated-child layer as
substantively correct. The prior B-new run named the controlling Schedule, so
the entity layer differed but practical diagnosis correctness was preserved.

## Evidence boundary and recommendation

Token counters, elapsed time, action chronology, output bytes, exit codes,
workspace changes, and the route marker are measured. Uncached input, cached
ratio, and deltas are derived. Repeated reads, unbounded-search labels,
framework-associated bytes, and context-pressure points are heuristics. The
causal attribution to trajectory variance is an inference from the matched
non-replication and the contrasting output/trajectory evidence.

Internal model-call count and context compaction remain unobservable because
the trace format still does not expose them.

No Agentic Workflow efficiency change is justified by this replication. Preserve
the historical warning and this result, then move on. A targeted behavior change
should wait until another natural run reproduces the long-trajectory plus
cached-context pattern; there is no smallest product change to recommend now.
