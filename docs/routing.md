# Workflow routing

The installed router solves one problem: choose the minimum useful way to handle
the request without expanding the user's authority. It starts Direct, classifies
from intent and installed skill descriptions, and may perform the smallest
authorized read-only reconnaissance needed when evidence is insufficient. One
obvious skill loads directly; availability alone never selects a capability.

Routing is dynamic. Three or more meaningful items prompt a Wayfinder assessment,
but count alone never selects it. Wayfinder starts or resumes when any hard
signal or at least two soft signals show that durable coordination is materially
safer than conversation alone. Hard signals cover continuity, authoritative
conflict, authority-owned blockers alongside work that can proceed, coordinated
owners or areas, and provenance risk. Soft signals cover interacting unknowns,
multiple durable state categories, evidence-driven plan change, dependency
graphs, and fresh-agent reconstruction risk. This is an activation rubric, not
a weighted complexity score. Explicit use and opt-out remain authoritative.

The compact always-loaded rules live in `payload/root/AGENTS.md.template`.
Detailed overlap resolution, composition, transitions, provider fallback,
unclear durable-resume ownership, and route-marker edge cases live in
`payload/agent-workflow/routing.md`. They load only after the thin gate identifies
one of those needs, not for Direct work or one obvious selected skill.

Runtime ownership is deliberately split:

| Owner | Runtime responsibility |
|---|---|
| Root `AGENTS.md` | Every-request routing, authorization, preservation, truthfulness, progressive-loading gates, and the marker requirement |
| `routing.md` | Selection criteria, route transitions, relevant resume, provider resolution, workflow composition, and detailed marker semantics |
| `providers.json` | Current host discovery, invocation, availability, configuration, and adapter facts |
| Provider and local skills | The selected workflow's methodology and its provider-specific execution boundary |
| State contracts | Storage, identifiers, progressive state loading, conflict handling, reconciliation, and re-entry mechanics |
| ADRs and project documentation | Architectural rationale, history, maintenance policy, and compatibility explanation |

This keeps concrete host snapshots and provider methodology out of the router
while retaining the routing consequence of those facts. For example, the router
must consult the active host's declared invocation prefix, but it does not need
an embedded list of which hosts currently use `$` or `/`.

Keep these decisions separate:

1. select one dominant workflow or activity;
2. add only capabilities that materially help it;
3. determine whether the active host may invoke each optional provider; and
4. execute only actions authorized by the user.

Default route sequences are transitions with entry conditions, not mandatory
pipelines. Host todos hold current-session actions; Wayfinder holds durable
coordination; specifications hold settled scope and acceptance criteria; tickets
hold approved independently deliverable work and blocking edges. Domain Modeling
joins Discovery or Wayfinder only when conceptual or vocabulary ambiguity is
material.

Unavailable or user-only providers normally fall back to truthful host-native
work. Use an exact `$skill-name` or `/skill-name` handoff only when the user
explicitly requires that provider or a real configuration boundary prevents
host-native progress. Never simulate provider execution.

Three seams are intentionally explicit. Trivial local, low-risk edits remain
Direct even though they mutate files; Implementation is for ready work where its
orchestration and integration verification add material value. A selected
provider operation with missing configuration returns the exact setup handoff
when no authorized host-native equivalent can deliver the requested outcome.
After a successful host-native fallback, the route marker reports what actually
ran and omits the unavailable provider; a terminal suffix is reserved for a
selection that did not become equivalent execution.

The dominant workflow owns any durable continuity under `.agent-workflow-state/`.
Provider-native tickets, specifications, research, reviews, and learning
artifacts remain canonical; the framework does not mirror them. Local Wayfinder
uses the configured canonical tree under `.agent-workflow-state/wayfinder/` and its
effort map as the re-entry point. Its effective skill is an Agentic Workflow-
owned runtime projection derived from and attributed to Matt Pocock's pinned
Wayfinder methodology. The map owns current state, blockers, dependencies, and
next work; sparse U#/E#/F#/D# knowledge stays lazy, and new decomposed work belongs
to native `to-tickets` output. A current effort outranks a similarly named
completed, abandoned, or superseded effort during likely resume; historical
maps remain accessible when directly named or materially relevant.
Other durable workflows resume from their
canonical DEC, IMP, or DBG record; there is no global active index. The router
loads that dedicated contract only
after Wayfinder is selected or a relevant effort is being resumed, then reads
the map and only relevant U#/E#/F#/D# children. An unrelated existing map never
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

Every user-facing final response ends with exactly one truthful instruction-level
marker such as:

```text
[route: router -> implement -> verification]
```

The marker is required observability, not telemetry or proof that work ran, and
must not trigger additional workflow work. Detailed syntax and terminal outcomes
remain owned by the installed routing contract.
