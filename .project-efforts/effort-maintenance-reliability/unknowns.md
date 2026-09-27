## U1 — How should required work after delivery get resumed?

Why it matters: an effort kept open after its PR merges records the remaining work, but nothing prompts an agent to return, because existing effort state never selects Wayfinder by design ([ADR-0027](../../architecture-decisions/0027-use-direct-first-progressive-routing.md)).
Maps that outlived their merged PRs before 2026-09-19 sat unread until a manual cleanup.

Options identified on 2026-09-27, smallest first:

1. State remaining work and the exact next prompt in the delivering PR description and final response; the person merging sees it.
2. Hand the trigger to something that already notifies people: a tracker issue or a host scheduler, linked from the map, when authorized.
3. Let agents discover efforts on their own, for example by listing effort names at session start; reverses ADR-0027's rule and adds per-request cost.
4. Deterministic tooling such as a CI check for maps that mention merged PRs; conflicts with the thin-layer boundary and [ADR-0010](../../architecture-decisions/0010-separate-framework-output-from-project-owned-state.md), and can only notify.

Recommendation recorded 2026-09-27: options 1 and 2 together as one contract change.
Resolution: user decision.

## U2 — Should other earlier authorization carry forward across turns?

Why it matters: [ADR-0025](../../architecture-decisions/0025-preserve-authority-at-consequential-boundaries.md) now carries earlier authorization forward only for effort maintenance, and [terminology](../../.agent-workflow/terminology.md#requests-and-authorization) states that it does not decide other cases, so "current user request" stays ambiguous for other writes.
Resolution: user decision; broadening affects authorization boundaries, which the project treats as a pre-1.0 priority.

## U3 — Should long-running efforts without an achievable objective remain efforts?

Why it matters: the [language-coherence](../language-coherence/map.md), [workflow-responsibility-boundaries](../workflow-responsibility-boundaries/map.md), and [context-efficiency](../context-efficiency/map.md) objectives describe ongoing upkeep, so the ending rule never applies and their maps go stale unless someone asks.
Options: keep them with explicit resume conditions, or move their open questions and findings into their owning documents and end them.
Resolution: user decision.
