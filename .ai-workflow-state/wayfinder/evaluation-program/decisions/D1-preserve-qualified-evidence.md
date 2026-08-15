# D1: Preserve and qualify every evaluation campaign

- Related: U3, T1, T2

## Decision

Retain every existing campaign in its original evaluator context. Classify preliminary, potentially exposed, contaminated, limited, and clean-at-the-observable-boundary evidence explicitly; do not delete, retroactively regrade, or silently pool unlike campaigns.

## Why

The repository already records three campaigns with materially different evidence quality:

- [`2026-08-15-initial-spike`](../../../../evals/results/2026-08-15-initial-spike/campaign.md): one run per cell, earlier Direct evaluator, execution metadata unavailable, and no established clean context boundary. Its initial findings are preliminary and directional.
- [`2026-08-15-three-paired-trials`](../../../../evals/results/2026-08-15-three-paired-trials/campaign.md): three pairs per scenario after evaluator refinement. All runs had possible delegated-source exposure and one Resume workflow run has confirmed contamination. It is historical/directional evidence, though it remains the strongest completed evidence for the narrow Direct non-interference question.
- [`2026-08-15-context-isolated-resume`](../../../../evals/results/2026-08-15-context-isolated-resume/campaign.md): three baseline and three workflow Resume runs with distinct Phase 1 and Phase 2 conversations. Four runs are clean at the observable context boundary; two baseline runs have disclosed brief interrupted old-conversation starts with no recorded mutation. Concurrent execution limits timing inference.

Keeping these categories visible preserves learning without overstating causal confidence.

## Consequences

- Campaign-local reports and JSON remain canonical for their evaluator version.
- Cross-campaign summaries must carry evidence-quality labels and explain evaluator changes.
- Contamination is a limitation to disclose, not grounds to erase history.
