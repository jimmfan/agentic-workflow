---
name: workflow-discovery
description: Resolve one bounded consequential project choice when explicit alternative and tradeoff analysis materially helps; operate standalone or inside Wayfinder without creating Agent Workflow durable coordination state.
---

# Bounded decision discovery

Discovery analyzes one bounded project choice.
Use it only when its method materially improves a choice.

## Establish the boundary

1. Read only relevant project evidence, sources, and artifacts that maintain accepted results.
2. Keep read-only work in the current session; a provisional choice does not authorize a write.
3. Standalone Discovery returns its result without creating Agent Workflow durable coordination state.
   Select Wayfinder only when the decision crosses its durable coordination threshold.
4. Inside Wayfinder, use only relevant map detail.
   Resume and continue the effort through its map; the state contract defines Wayfinder reconciliation.

## Resolve the decision

1. State the precise decision question and why it matters.
   An architectural decision is one possible kind of consequential project choice; architecture does not change the analysis or storage boundary.
2. Separate evidence and constraints from assumptions, preferences, unresolved questions, and out-of-scope matters.
   Inspect repository evidence before asking the user for information the workspace can provide.
3. Use primary sources for consequential or time-sensitive external facts.
   Compose Research only when its additional method materially helps establish the needed evidence.
   Already-sufficient evidence does not require another Research invocation.
   Compose Domain Modeling when ambiguity in domain concepts, terminology, or context boundaries materially affects the decision.
4. Compare viable alternatives by benefits, costs, risks, reversibility, consequences, and evidence that would change the choice.
5. Treat the choice as committed only under the root policy's evidence and project decision authority rules; preserve already-delegated technical judgment.
   An autonomous provisional choice must be reversible and state its review trigger; it does not authorize an action.

## Return the result

Report status, rationale, consequences, rejected alternatives, remaining uncertainty, project decision authority, and next workflow transition or ready work.
For Wayfinder, return only results worth reconciling into the map or independently useful U/E/F/D records.
Discovery does not maintain architecture decision records.
A lasting architecture decision belongs in the project record designated to maintain architecture decisions.
