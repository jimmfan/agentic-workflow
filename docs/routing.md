# Workflow routing

The installed router solves one problem: choose the minimum useful way to handle
the request without expanding the user's authority. Clear, bounded, low-risk
work is `direct`; availability of a workflow or provider is never a reason to
invoke it.

The compact always-loaded rules live in
`payload/root/AGENTS.md.template`. Detailed selection, composition, invocation,
fallback, evidence, and route-marker rules live in
`payload/ai-workflow/routing.md` and load only for a named skill, resume,
uncertain route, or route not confidently direct.

Keep these decisions separate:

1. select one dominant workflow or activity;
2. add only capabilities that materially help it;
3. determine whether the active host may invoke each optional provider; and
4. execute only actions authorized by the user.

Unavailable or user-only providers normally fall back to truthful host-native
work. Use an exact `$skill-name` or `/skill-name` handoff only when the user
explicitly requires that provider or a real configuration boundary prevents
host-native progress. Never simulate provider execution.

The dominant workflow owns any durable continuity under `.ai-workflow-state/`.
Provider-native maps, tickets, specifications, research, reviews, and learning
artifacts remain canonical; the framework does not mirror them. Diagnosis,
review, explanation, and audit requests stay read-only unless the user separately
authorizes mutation.

After meaningful implementation or a causal fix, gather acceptance evidence not
already supplied by the selected provider. Do not repeat provider-owned TDD or
Code Review merely to add a framework stage.

When route visibility materially helps debugging, emit at most one truthful
instruction-level marker such as:

```text
[route: router -> implement -> verification]
```

The marker is optional metadata, not telemetry or proof that work ran.
