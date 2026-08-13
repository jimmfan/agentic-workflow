# Workflow routing

Choose the minimum process justified by intent, uncertainty, impact, and
reversibility. File count is not a proxy for risk.

| Signal | Route | Boundary |
|---|---|---|
| Explicit learning request or blocking knowledge gap | Teach | Return control without deciding or implementing |
| Material unresolved architecture, security, cost, dependency, or visible-behavior choice | Discovery | Record the accepted or explicitly provisional decision |
| Existing unexplained failure or regression | Debugging | Diagnosis alone does not authorize a fix |
| Approved coherent scope | Implementation | Build, then hand to Verification |
| Approved work spanning dependency-ordered or independently deliverable sessions | Decomposition | Produce canonical tickets and one actionable frontier |
| Completed meaningful work or causal fix | Verification, then proportional Review | Executable evidence and independent inspection remain separate |
| Clear, bounded, low-risk request | Direct | Skip workflow ceremony |

The host-native parent owns synthesis, decisions, edits, finding disposition,
and final verification. Native subagents are optional for bounded independent
work when isolation or parallelism materially helps. Optional upstream skills
are used only when explicitly requested; their native artifacts remain
canonical and are never mirrored into framework state.

Examples:

- “Rename this Terraform variable” is direct when impact is understood.
- “Choose the identity boundary for these services” uses Discovery.
- “The API started returning 500 and the cause is unknown” uses Debugging.
- “Implement the approved pagination design” uses Implementation, Verification,
  and proportional Review.
- “Deliver this approved migration across ordered sessions” uses Decomposition
  before implementing one ready frontier ticket.
