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
- In `arc-wayfinder-e2e-v2`, the neutral Agentic Workflow condition read the
  Wayfinder skill and created Wayfinder state in phase 1, then used or modified
  that state in all later fresh phases despite no `$wayfinder` invocation. This
  is direct evidence that the durable multi-session mapping prompt crossed the
  current automatic-selection boundary. Its engineering outcome matched both
  vanilla durable notes and explicit Wayfinder, while its recorded overhead was
  highest of the three one-run trajectories.

- `arc-wayfinder-state-complexity-v1` explicitly invoked Wayfinder and
  intentionally omitted a neutral Agentic Workflow arm. It adds no automatic
  selection evidence and must not be used to change routing.

- `itbench-wayfinder-v1` supplies 18 repeatable neutral-routing observations on
  bounded offline SRE diagnosis. B selected Workflow Debugging in 18/18 and
  Wayfinder in 0/18. Explicit Wayfinder C did not improve strict correctness or
  reasoning over B and added token/process overhead without durable state. This
  supports non-selection for this bounded task class; it does not identify the
  threshold for genuinely long-lived work.

## Resolution

Keep open and make no routing change. V2 supplies a neutral-prompt selection
observation but not evidence of incremental net value. The controlled ITBench
campaign supports the current non-selection behavior for bounded incident
diagnosis. A future long-lived design must still separate automatic selection
from an explicitly supported non-Wayfinder Agentic Workflow treatment before
candidate recognition signals are changed.
