# D2: Evaluate three distinct behavior layers

- Related: U1, U2, U3, T2

## Decision

Keep these experimental targets distinct:

1. **Default Agentic Workflow behavior:** the installed router and policy operate under a neutral task prompt, with no instruction to create durable state.
2. **Generic durable handoff behavior:** a capable baseline agent is explicitly told to preserve useful repository-native continuation notes, without Agentic Workflow or Wayfinder structure.
3. **Explicit Wayfinder behavior:** Agentic Workflow is explicitly invoked to maintain its canonical map and structured U#/D#/T# state across sessions.

## Why

The completed Resume campaigns compared baseline with default Agentic Workflow behavior. In the clean rerun, workflow agents used no Wayfinder or other Agentic Workflow durable state in all three runs. The campaign therefore tested whether default routing autonomously selected durable continuity for that fixture; it did not test whether explicit Wayfinder state is effective once selected.

The baseline repeatedly retained the transient fact in ordinary live source. That establishes that persistence can arise without framework-owned structure, but it does not answer whether deliberately written repository-native handoff notes would match or outperform Wayfinder. A matched durable-note arm is required to isolate structure from the generic benefit of writing facts down.

## Consequences

- Do not attribute a default-router outcome to explicit Wayfinder.
- A future causal comparison needs at least baseline, default Agentic Workflow, baseline-with-durable-notes, and explicit Wayfinder arms if it aims to isolate structured-state value.
- Automatic Wayfinder selection remains a separate product question from Wayfinder efficacy.
