---
name: wayfinder-effort
description: Establish or update a project effort in Wayfinder from an objective, plan, or referenced material without implementing product changes.
---

# Orient a Wayfinder effort

Treat the user's description, pasted plan, and attached or referenced material as input to the effort.

Invoke the installed `wayfinder` skill to establish or update the effort's Wayfinder state.
`wayfinder` and `.agent-workflow/contracts/wayfinder-state.md` are authoritative for effort identity, creation or resumption, map authoring, state preservation, reconciliation, and all other Wayfinder behavior.
Do not duplicate those rules or create another durable-state representation.
If the required Wayfinder capability or state contract is unavailable, report that accurately rather than emulate a second Wayfinder implementation.

Do not implement product changes during this orientation pass.
Preserve normal Agent Workflow authorization and project-decision boundaries.

When finished, report what Wayfinder state was created or updated, what remains uncertain, and the recommended next prompt for continuing the effort.
