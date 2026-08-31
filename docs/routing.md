# Workflow routing

The installed router solves one problem: choose the minimum useful way to handle
the request without granting action authorization or project decision authority
beyond the user's direction. It starts Direct, classifies
from intent and installed skill descriptions, and may perform the smallest
read-only reconnaissance within delegated scope when evidence is insufficient. One
obvious skill loads directly; availability alone never selects a capability.

Routing is dynamic. After reconnaissance, the agent must assess Wayfinder before
completing. Three or more meaningful items also prompt an assessment, but count
alone never selects it. Wayfinder must start or resume when any hard signal or
at least two soft signals show that durable coordination is materially safer
than conversation alone. Hard signals cover session-continuation or
agent-handoff continuity, conflicting sources that establish the same scoped
claim, an uncommitted required project choice alongside independent work that can
proceed, coordinated areas or responsible participants, and missing source
traceability. Soft signals cover interacting unresolved questions, multiple
durable state categories, evidence-driven plan change, dependency graphs, and
fresh-agent reconstruction risk. This is an activation rubric, not a weighted
complexity score. Explicit user selection and opt-out control the route.

The compact always-loaded rules live in `payload/root/AGENTS.md.template`.
Detailed overlap resolution, composition, transitions, selected-skill fallback,
unclear durable resumption responsibility, and route-marker edge cases live in
`payload/agent-workflow/routing.md`. They load only after the thin gate identifies
one of those needs, not for Direct work or one obvious selected skill.

Runtime responsibility is deliberately split:

| Surface | Runtime responsibility |
|---|---|
| Root `AGENTS.md` | Every-request routing, action authorization, project decision authority, preservation, truthfulness, progressive-loading gates, and the marker requirement |
| `routing.md` | Selection criteria, route transitions, relevant resumption, installed-skill resolution, workflow composition, and detailed marker semantics |
| Installed skills | The selected workflow's methodology, behavior-bearing frontmatter, invocation metadata, and execution boundary |
| State contracts | Storage, identifiers, progressive state loading, reconciliation, and map-first resumption mechanics |
| ADRs and project documentation | Architectural rationale, history, maintenance policy, and compatibility explanation |

This keeps concrete host details and specialist methodology out of the router
while retaining the routing consequence of installed availability and
invocation restrictions.

Keep these stages separate:

1. choose Direct or one primary workflow;
2. add only supporting capabilities that materially help;
3. resolve each selected skill from `.agents/skills/<name>/SKILL.md` and its
   packaged support files;
4. check host support and behavior-bearing invocation metadata;
5. invoke the selected skill only when policy allows it;
6. materially execute only actions authorized by the current user request or accepted
   project policy; and
7. require completion and verification evidence beyond the route marker.

A project choice is committed only after required evidence is sufficient and
accepted project policy determines the choice for that boundary or the person,
role, or valid delegate with project decision authority commits it. That gate is
independent from authorization to act: either may exist without the other, and
host permission supplies neither.

Default route sequences are transitions with entry conditions, not mandatory
pipelines. Host todos hold current-session actions; Wayfinder holds durable
coordination; specifications hold accepted scope and acceptance criteria; tickets
hold approved independently deliverable work and blocking edges. Domain Modeling
joins Discovery or Wayfinder only when conceptual or vocabulary ambiguity is
material.

A selected skill that is unavailable or still requires explicit user invocation
normally falls back to truthful host-native work. Give an exact invocation instruction only when the current
host exposes one and the user explicitly requires that skill or a real boundary
prevents host-native progress. Never simulate skill execution.

Three seams are intentionally explicit. Trivial local, low-risk edits remain
Direct even though they mutate files; Implementation is for ready work where its
orchestration and integration verification add material value. A selected skill
that cannot run returns an exact supported invocation instruction only when no
host-native equivalent authorized within the current scope can deliver the
requested outcome.
After a successful host-native fallback, the route marker reports what actually
ran and omits the unavailable skill; a terminal suffix is reserved for a
selection that did not become equivalent execution.

Wayfinder is Agent Workflow's sole durable coordination model;
`.agent-wayfinder/` is its project-owned durable representation.
Tickets, specifications, research results, and review reports remain in the
project or external locations; the artifact designated to maintain the result
is not mirrored by Agent Workflow. Local Wayfinder uses the genuinely designated canonical
tree under `.agent-wayfinder/`. When resuming a Wayfinder effort, read its map
first. Its maintained skill is derived from and attributed to Matt Pocock's
`v1.2.3`
Wayfinder methodology. The map summarizes current coordination state, conditions
blocking particular work, dependencies, and ready work; sparse F#/D# ledger
sections and U#/E# records stay lazy. F# contains a sufficiently supported,
scoped, revisable conclusion; D# contains a current consequential choice
determined directly by accepted project policy or committed by the person, role,
or valid delegate with project decision authority; U# contains an unresolved
question and is not itself a blocker; E# contains evidence with source, scope,
observation, and limitations. Before
detailed decomposition, the map
may state ready work directly. New decomposed work belongs to the `to-tickets`
ticket or ticket set, which maintains ticket contents, dependencies,
ordering, and readiness; the map links it without mirroring ticket-level state.
A safe regular map makes an effort current and resumable; a mapless directory is not a candidate. The
router loads the Wayfinder contract only after Wayfinder is selected or a
relevant effort is being resumed, then reads the map and only relevant F#/D#
ledger sections or U#/E# artifacts. An unrelated
existing map never changes a request's route.

When the current request or accepted project policy authorizes repository-local
Wayfinder writes, routing may create a lightweight map without asking again after
Wayfinder is selected.

Within a selected effort, continue directly with ready work. Load Discovery,
Debugging, Research, Prototype, Domain Modeling, Grilling, or human clarification
only when that method materially improves how a current question, uncertainty,
unexplained cause, consequential choice, or structural ambiguity is addressed.
The specialist creates no Agent Workflow durable coordination state, but may
create the artifact designated to maintain the result, produce evidence, or return consequential
results for Wayfinder reconciliation. Implementation is a workflow transition
for ready work, followed by Verification, not a Wayfinder reasoning method or
coordination record.

After meaningful implementation or a causal fix, gather acceptance evidence not
already supplied by the selected skill. Do not repeat skill-defined TDD or
Code Review merely to add a framework stage.

To Spec and To Tickets resolve a publication destination from the current
request, then project instructions, then existing project-owned tracker
configuration; otherwise there is no inferred destination. A known destination
does not authorize publication. Without both a destination and action
authorization, they return the complete draft in chat, create no temporary
repository file, and stop before publication. Conflicting applicable sources
require clarification. Labels and statuses require both project-defined
semantics and authorization for that mutation. Code Review uses tracker access
only as optional source lookup, completes its Standards axis without a tracker,
and returns its report in chat unless publication is separately authorized.

Every user-facing final response ends with exactly one truthful instruction-level
marker such as:

```text
[route: router -> implement -> verification]
```

The marker is required observability, not telemetry or proof that work ran, and
must not trigger additional workflow work. The unchanged `<skill>-handoff`
terminal suffix means the required skill still needs explicit user invocation.
Detailed syntax and terminal outcomes are defined by the installed routing policy.
