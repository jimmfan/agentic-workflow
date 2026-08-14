# Workflow routing

The authoritative consuming-project routing contract is
[`payload/ai-workflow/routing.md`](../skills/agentic-workflow/payload/ai-workflow/routing.md).
Lifecycle adoption installs it at `.ai-workflow/routing.md`, and the compact root
policy loads it only for a named skill, resume, uncertain route, or route that is
not confidently direct.

This source-level document records why that placement matters. Agentic Workflow
routes normal intent without requiring users to memorize skill syntax. The root
policy retains only universal authorization, truthfulness, preservation, and
evidence invariants plus these defaults:

- direct is a first-class route for clear, bounded, low-risk work;
- select one dominant workflow or activity;
- add zero or more capabilities only when they materially help;
- availability alone never justifies invocation; and
- load detailed provider, workflow, state, runtime, and host policy only after
  the selected route makes it relevant.

The installed routing contract owns the detailed classification ladder,
provider invocation and setup gates, host compatibility fallback, composition,
canonical-artifact boundaries, authorization examples, evidence semantics, and
route-marker labels. Selected skills own their methodology. The state and
profile contracts own their respective persistence rules. The runtime controller
owns only observable lifecycle consistency; it does not select routes.

GitHub Copilot in VS Code remains the reference host, but its Preview hooks are
not an adoption prerequisite. The compact root invariants plus the progressively
loaded routing contract form the advisory fallback when hooks are unavailable.
See [Lifecycle enforcement and hard-rule audit](enforcement.md) for the division
between programmatic invariants, model judgment, and soft guidance.
