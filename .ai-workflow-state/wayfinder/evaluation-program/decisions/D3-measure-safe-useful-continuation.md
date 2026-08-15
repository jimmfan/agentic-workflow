# D3: Measure safe and useful continuation

- Related: U3, T1, T2

## Decision

Evaluate safety and useful progress together. Safe stopping is valuable only when the agent correctly identifies a consequential boundary; stopping alone must not outrank an agent that safely preserves evidence, advances reversible work, resumes correctly, and verifies the final result.

For long-lived evaluations, capture separate observations for:

- boundary safety and unsupported guessing;
- useful progress in each phase and final task completion;
- continuity of approved facts, unresolved questions, decisions, and pending work;
- speculative work and later rework, including removal of still-valid evidence;
- state evolution as decisions change rather than a static handoff snapshot;
- final correctness and verification quality;
- changed files and unnecessary artifacts; and
- model, reasoning configuration, tokens, elapsed time, action/tool counts, and other cost/usage signals when the interface exposes them reliably.

Do not collapse these into a synthetic score until evidence justifies weights.

## Why

Existing Resume results show why a single metric misleads. Safe stopping and continuity separated: some agents stopped safely but failed to preserve the AMI, while others crossed the Phase 1 architecture boundary yet recovered the fact and completed Phase 2. In the clean rerun, workflow had a small 2/3 versus 1/3 safe-stop edge but baseline recovered and completed 3/3 versus workflow 0/3. Two workflow agents removed a still-valid live-source fact because a newer decision was silent about it.

## Consequences

- Reports present a metric vector and run-level anomalies rather than declaring a winner from stop rate alone.
- Unknown execution metadata stays `null`/`n/a`; it is never inferred.
- Evidence-preservation and speculative-rework checks are first-class acceptance boundaries in the next experiments.
