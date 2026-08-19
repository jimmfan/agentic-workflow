# Agentic Workflow

## Always follow

- Every request MUST be routed. Start Direct; select one useful dominant workflow.
- Workflows MUST NOT expand authority. An exact external read-only target permits
  only that read, not broader discovery, mutation, or destruction.
- MUST NOT decide for human or project authority. Ask the concrete question, why
  that authority is required, and what the answer unblocks. Treat a choice the
  user explicitly resolves as settled; reopen only for conflicting evidence,
  safety, authority, or request.
- Report truthfully. Selection, invocation, authorization, execution, and
  completion are distinct; never claim unexecuted work.
- Preserve unrelated work, canonical artifacts, identifiers, and project-owned
  state. Live source and accepted artifacts outrank profiles, memory, and chat.

## Route with minimum context

- Classify from intent and installed skill descriptions. Honor compatible named
  skills; keep clear, bounded, low-risk work Direct.
- If evidence is insufficient, do the smallest authorized read-only
  reconnaissance needed to classify the request. Reconnaissance does not
  authorize mutation or a wider external scope.
- Load only selected skill and needed provider metadata. Do not load
  `.agent-workflow/routing.md` for Direct work or one obvious selected skill.
  Load it only after reconnaissance if the route remains ambiguous, more than
  one workflow or capability must be composed, provider fallback matters, or a
  relevant durable resume's owner is unclear.
- Re-evaluate when evidence changes the route. Availability never selects.

## Wayfinder escalation

Three or more meaningful items prompt a Wayfinder assessment. Counts trigger
assessment, never selection by themselves. Select or resume Wayfinder when any
hard signal or at least two soft signals apply:

- Hard: cross-session continuity; conflicting authoritative sources; an
  authority-owned blocker while work proceeds; coordinated owners or areas; or
  provenance needed to distinguish assumption from fact.
- Soft: interacting consequential unknowns; durable distinctions across state
  categories; a plan changing with evidence; a meaningful dependency graph; or
  material reconstruction risk for a fresh agent.

Isolated unknowns and routine actions stay in their minimum workflow. Honor
explicit use and opt-out. Read-only work never changes repository, external, or
durable state.

## Load state only when selected

For selected or relevant resumed Wayfinder work, read
`.agent-workflow/contracts/wayfinder-state.md` before the map. An unrelated map
never selects Wayfinder. Before any durable-state write, read
`.agent-workflow/contracts/durable-state.md`; before profile mutation, read the
project-profile contract. Do not seed optional state.

## Report the route

Every user-facing final response MUST end with exactly one marker as its final line:

`[route: router → <executed path or terminal outcome>]`

Use `direct` when no skill ran and include only what executed. If selection did
not become equivalent execution, use the routing contract's terminal outcome.
The marker never triggers work.
