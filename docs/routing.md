# Workflow routing

The installed router solves one problem: choose the minimum useful way to handle
the request without expanding the user's authority. Clear, bounded, low-risk
work is `direct`; availability of a workflow or provider is never a reason to
invoke it.

Routing is dynamic. When an initially normal task reveals several consequential
unknowns, decisions, dependencies, ownership boundaries, blockers, assumptions,
or conflicting facts that are becoming unreliable to hold in conversational
context, the router may start or resume Wayfinder automatically. This is a
qualitative notebook threshold, not a numeric complexity score or a requirement
that the work already be huge or multi-session. Explicit use and opt-out
instructions remain authoritative.

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
Provider-native tickets, specifications, research, reviews, and learning
artifacts remain canonical; the framework does not mirror them. Local Wayfinder
uses the configured canonical tree under `.ai-workflow-state/wayfinder/` and its
effort map as the re-entry point. A narrow provider adapter makes that local
tree and its U#/D#/T# ontology authoritative over incompatible tracker mechanics
in the pinned method body while leaving the upstream reasoning method intact.
Other durable workflows resume from their
canonical DEC, IMP, or DBG record; there is no global active index. The router
loads that dedicated contract only
after Wayfinder is selected or a relevant effort is being resumed, then reads
the map and only relevant U#/D#/T# children. An unrelated existing map never
changes a request's route. Diagnosis, review, explanation, and audit requests
stay read-only unless the user separately authorizes mutation.

Normal authorized project work may create a lightweight Wayfinder map without a
second permission request after the router selects it. A read-only request may
use ephemeral structure but does not create or update Wayfinder state.

When a useful specialized activity is already underway, Wayfinder may own only
durable coordination: Debugging, Research, Prototype, Grilling, Domain Modeling,
human clarification, or Implementation can resolve or consume an item without
creating a competing map. Grilling and Domain Modeling are conditional on real
human/domain ambiguity, not mandatory ceremony for every escalation.

After meaningful implementation or a causal fix, gather acceptance evidence not
already supplied by the selected provider. Do not repeat provider-owned TDD or
Code Review merely to add a framework stage.

When route visibility materially helps debugging, emit at most one truthful
instruction-level marker such as:

```text
[route: router -> implement -> verification]
```

The marker is optional metadata, not telemetry or proof that work ran.
