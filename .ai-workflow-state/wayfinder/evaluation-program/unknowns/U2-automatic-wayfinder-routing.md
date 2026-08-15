# U2: When should Agentic Workflow select durable Wayfinder state automatically?

- Status: open
- Resolution mode: prototype
- Blocked by: U1, T2
- Related: D2, U3

## Question

If structured Wayfinder state proves useful, can Agentic Workflow recognize the task characteristics that warrant it without explicit invocation, and would automatic selection create more net value than ceremony or false positives?

## Evidence

- In the clean Resume rerun, default Agentic Workflow selected no Wayfinder or other durable state in 3/3 workflow runs.
- The fixture was small relative to the documented “large, foggy, multi-session” threshold, so non-selection is evidence about this fixture, not proof that the router misses tasks that clearly meet the threshold.
- Direct campaigns exist specifically to expose interference and unnecessary ceremony on bounded tasks; the refined three-paired Direct evidence found no agent-authored workflow state for the bounded retry task.
- The explicit `arc-wayfinder-e2e-v1` smoke found a narrow continuity advantage but no final completion advantage, and it exposed a possible Wayfinder over-blocking failure. It did not test neutral automatic selection and is not sufficient evidence for a routing change.

## Resolution

Wait for evidence that explicit Wayfinder provides value and for neutral-prompt results from a larger fixture aligned with the documented threshold. Only then define candidate recognition signals or consider a product change.
