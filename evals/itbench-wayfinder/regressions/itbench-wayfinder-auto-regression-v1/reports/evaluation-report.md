# MERGE TO MAIN

The automatic Wayfinder branch is safe to merge on this practical regression.
Correctness is effectively unchanged, routing is appropriately conservative,
and the read-only boundary held. The one negative signal is higher cost, but it
was caused by long and oversized ordinary debugging searches—not Wayfinder
activation or durable-state ceremony.

## Practical result

B-new produced six normal exits and six valid diagnoses. The frozen native
matcher scored **2/6 (mean 0.333)**: Scenarios 34 and 24 passed. That is exactly
the same per-scenario pattern as the directly comparable old B repetition 1.
The historical full campaign scored A 3/18, old B 4/18, and explicit C 3/18.

The practical diagnosis result was **5/6**:

| Scenario | Frozen native | Practical diagnosis | Result |
| --- | --- | --- | --- |
| 102 | Fail | Correct | Found the concrete memory `ResourceQuota`; the matcher expects its Namespace. |
| 34 | Pass | Incorrect mechanism | Found Valkey unavailability and propagation, but not the authentication mismatch. |
| 83 | Fail | Correct | Found the checkout/email Chaos Mesh partition via its controlling Schedule. |
| 17 | Fail | Correct | Found recurring product-catalog network delay via its controlling Schedule. |
| 24 | Pass | Correct | Exactly found `Deployment/checkout` and `KAFKA_ADDR=kafka:9999`. |
| 80 | Fail | Correct | Found the checkout/Kafka partition via its controlling Schedule. |

This matches the old campaign's substantive conclusion: all conditions solved
five scenarios, while Scenario 34 remained the shared diagnostic failure. The
new native score should not be read as a correctness improvement because its
Scenario 34 pass is again an exact-entity match with the wrong or missing fault
mechanism.

## Routing and automatic Wayfinder

All six runs materially invoked Workflow Debugging. Five emitted
`[route: router → debugging]`; Scenario 24 directly read and followed the
Debugging skill but emitted no marker. No run invoked Wayfinder, Discovery,
Research, Domain Modeling, Grilling, Prototype, Codebase Design, Verification,
or another provider.

That routing looks appropriate. These were bounded, read-only, single-session
incident investigations. No trajectory showed consequential state becoming
unreliable to hold, and even the longest run reached the correct causal object.
There is therefore no evidence of either over-triggering or under-triggering.
Automatic Wayfinder was appropriately conservative.

No `.ai-workflow-state/wayfinder/` state was created. Every workspace changed
only `diagnosis.json`; all six protected snapshots remained hash-identical; and
no run attempted network, `kubectl`, cloud CLI, or remediation commands.

## Scenario 34

B-new did improve the shape of the investigation relative to the historical
majority: it rejected the noisy resource events, observed the Valkey Pod was
still Ready, found cart's repeated Redis connection failures, and traced them
through cart RPC failures to frontend-proxy 504s. It did **not** repeat the old
CPU/resource diagnosis.

But it still did not find the actual password-authentication mismatch. It
promoted “Valkey endpoint unavailable” to a sole Pod-level cause without
evidence that distinguished authentication, service routing, network path, or
process behavior. The frozen reasoning grader accordingly scored Scenario 34
zero for unknown preservation and remaining-evidence requirements. This is a
better trajectory but not a corrected diagnosis.

## Reasoning quality

Against old B's 18-run rubric means, B-new was mixed and close rather than
materially better: premature-closure avoidance, unknown preservation,
visibility-limit recognition, and remaining-evidence statements rose; evidence
labeling, discriminating-evidence efficiency, and ownership precision fell
slightly. Symptom/cause separation and unsafe-remediation avoidance remained
perfect. A one-attempt-per-scenario check does not support a broader reasoning
improvement claim.

## Cost

| Mean per diagnosis | Old A | Old B | Old explicit C | B-new |
| --- | ---: | ---: | ---: | ---: |
| Elapsed seconds | 108.4 | 171.4 | 154.8 | **212.4** |
| Input tokens | 994,523 | 1,416,422 | 1,502,370 | **2,415,232** |
| Cached input tokens | 888,633 | 1,271,310 | 1,368,078 | **2,251,477** |
| Output tokens | 4,254 | 5,572 | 6,312 | **8,533** |
| Tool actions | 15.5 | 16.7 | 17.8 | **21.8** |

Relative to the directly comparable old B first pass, B-new was 53% slower,
used 73% more input tokens, 80% more cached input tokens, 45% more output
tokens, and 36% more tool actions. This is a real negative observation.

The aggregate is dominated by Scenario 17 (402 seconds, 6.0 million input
tokens, 37 tool actions). Across the campaign, several broad searches returned
1 MiB outputs and agents retried common shell utilities unavailable under the
historical minimal-environment policy. Wayfinder was never loaded or used, so
this overhead is not evidence that automatic Wayfinder adds ceremony. With one
fresh attempt per scenario, it is also not enough to attribute the increase
causally to the branch.

A post-hoc analysis of the preserved Scenario 17 trace is available as a
[concise report](token-forensics/s17-b-new-r1.md) and
[machine-readable summary](token-forensics/s17-b-new-r1.json). It confirms two
1 MiB tool outputs, four broad searches, two likely unbounded searches, and no
Wayfinder state activity. These are plausible context-pressure contributors;
the Codex exec stream does not expose exact per-tool token attribution.

## Product and campaign integrity

- Product revision: `6d5a030a27afce1049d15afdfa36fe3e10fb162d`
- Agentic Workflow version: `0.12.0`
- Payload tree SHA-256: `9d31f94dea7d53b83af13d254ce524b4ac74d916c91d469d9df7708e472473c2`
- Projected skills tree SHA-256: `9577120f9243650f37c81e8c0b04880b1a303c3e9095b3686b7fd69c061d2eb6`
- Codex CLI: `0.144.6`, identical to the historical campaign
- Provider: Matt Pocock skills `v1.2.3`, all 14 declared skills projected
- Deterministic release gate: 61/61 tests passed
- Regression preflight: 790/790 checks passed
- Live context-isolation audit: passed after explicit data-transfer approval
- Scored infrastructure retries: none
- Post-run integrity: passed; frozen product, prompt, matcher, rubric, snapshots,
  and historical campaign anchors remained unchanged

The first sandboxed non-scored isolation attempt could not reach the model API;
an unsandboxed launch then required the CLI's absolute path. Both were
controller infrastructure issues before scored execution. The eventual
isolation audit passed, and no scored run was retried.

## Merge decision

Merge. The most important result is that enabling implicit, dynamic Wayfinder
did **not** turn ordinary technical debugging into automatic notebook creation:
all six bounded incidents stayed on the lightweight Debugging route, preserved
the read-only contract, and retained the old campaign's practical 5/6 diagnosis
quality. The old conclusion is reinforced rather than overturned: ordinary
debugging is sufficient for these snapshots, and explicit Wayfinder previously
added cost without benefit.

The cost increase should be remembered as a one-pass negative observation, but
it is not tied to the feature's activation path and does not outweigh the clean
routing and safety result. Merge the branch and evaluate the framework through
real work rather than extending this benchmark campaign.
