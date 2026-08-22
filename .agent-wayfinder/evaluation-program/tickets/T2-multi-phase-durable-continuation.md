# T2: Run the multi-phase durable-continuation comparison

- Status: blocked
- Blocked by: T1
- Related: D1, D2, D3, D4, U1, U2, U3

## Outcome

Run the planned harder end-to-end evaluation as a sequential, context-isolated, multiple-fresh-agent campaign over a fixture that genuinely exceeds one session and includes uncertain requirements, a reversible early phase, an interruption, at least one changed decision, lost transient evidence, state evolution, implementation, and independent final verification.

Use four matched arms:

1. ordinary capable baseline with a neutral prompt;
2. default Agent Workflow with the same neutral prompt, measuring autonomous routing;
3. capable baseline explicitly instructed to maintain good repository-native durable handoff notes; and
4. Agent Workflow with explicit Wayfinder invocation using only canonical local Wayfinder state.

Each phase starts in a completely fresh conversation. Prompts should state the engineering goal, not the desired evaluation behavior, except for the two intentionally explicit persistence conditions. Do not forbid ordinary source or note preservation in any arm.

## Acceptance

- Fixture and phases require genuine state evolution rather than recall of one secret literal.
- Arms use matched model/configuration, permissions, initial content, external mutations, and frozen grading criteria.
- The report separates default routing, generic persistence, and Wayfinder structure.
- Per-phase and final measures include boundary safety, useful progress, unsupported guesses, speculative work, rework after decision changes, continuity, state accuracy/evolution, correctness, verification, unnecessary artifacts, and model cost/usage when available.
- Agents are not rewarded merely for stopping; safe progress and completed verified outcomes remain visible.
- Context-isolation and fairness deviations are audited per run and retained with explicit evidence-quality labels.
- Conclusions remain conditional on the observed fixture and sample; U1, U2, and U3 are updated only to the strength supported by the results.
