# Workflow routing

The installed router solves one problem: choose the minimum useful way to handle the request without granting action authorization or project decision authority beyond the user's direction.
It starts Direct, classifies from intent and skill descriptions exposed in the current session, and may perform the smallest read-only reconnaissance within delegated scope when evidence is insufficient.
A clearly applicable skill may help with focused work; availability alone never selects it.

## Routing roles

Every discoverable package under `.agents/skills/` is a skill.
Direct is the default route.
A request may remain Direct while the agent uses a skill for focused work.
When more structure is needed, the agent may choose one primary workflow.
Additional skills may support the current route when they materially help, but they do not become additional primary workflows.
How the agent uses a skill for one request does not permanently classify that skill.
Use `specialist` only for focused specialist work.

Routing is dynamic.
Assess durable coordination after any needed reconnaissance; item count alone never selects Wayfinder.
User intent is the primary source for establishing an effort's objective and scope.
Goal-directed language or an apparent desired future state cues semantic assessment of whether stable objective and scope can be established and whether achieving them crosses the existing durable-coordination threshold; an objective alone never selects Wayfinder.
When materially different interpretations would identify different efforts, use the minimum sufficient clarification or resolution before creating state.
Wayfinder must start or resume when at least one hard signal or at least two soft signals apply.
Hard signals cover work that continues a relevant Wayfinder effort, is intended to continue across sessions or agents, or has an establishable consequential objective and scope whose route remains materially unclear and cannot responsibly be resolved within one useful agent session.
Cross-session continuation includes a current request that creates or updates an external dependency whose result later in-scope work is expected to await or consume.
They also cover conflicting sources that establish the same scoped claim, an uncommitted required project choice while independent work proceeds, coordinated responsible participants or areas, and source and scope needed to distinguish assumption from fact.
Soft signals cover interacting consequential unresolved questions, durable distinctions across record or state categories, evidence-driven plan change, a meaningful dependency graph, and material fresh-agent reconstruction risk.
For goal-directed work, Wayfinder is for a consequential objective needing reliable continuity because its route, dependencies, choices, or involved areas remain materially unclear.
A clear bounded plan does not select Wayfinder merely because later work will execute or depend on it.
When the route can already be responsibly established within one useful session, use Direct or the applicable planning workflow instead.
This is an activation rubric, not a weighted complexity score.
Existing Wayfinder state alone never selects Wayfinder.
A bounded read-only check may establish that the current work clearly continues a relevant effort.
Explicit user selection and opt-out control the route.

The compact always-loaded rules live in `payload/root/AGENTS.md.template`.
Detailed overlap resolution, composition, transitions, unavailable-skill handling, exact user-invocation instructions, unclear responsibility for resumption records, and route-marker edge cases live in `payload/agent-workflow/routing.md`.
They load only after the thin gate identifies one of those needs, not for Direct work or one obvious selected skill.

Runtime responsibility is deliberately split:

| Surface | Runtime responsibility |
|---|---|
| Root `AGENTS.md` | Every-request routing, action authorization, project decision authority, preservation, truthfulness, progressive-loading gates, and the marker requirement |
| `routing.md` | Selection criteria, route transitions, relevant resumption, workflow composition, and detailed marker semantics |
| Skills exposed in the current session | The selected method and its execution instructions |
| State contracts | Storage, identifiers, progressive state loading, reconciliation, and map-first resumption mechanics |
| ADRs and project documentation | Architectural rationale, history, maintenance policy, and compatibility explanation |

Host-specific discovery stays outside the router.
Once a skill is selected, that skill's instructions define its method.

For each request:

1. choose Direct or one primary workflow;
2. add only supporting capabilities that materially help;
3. when using a skill, use one exposed in the current session and follow its instructions;
4. never claim a skill ran unless its method ran;
5. materially execute only actions authorized by the current user request or accepted project policy; and
6. require completion and verification evidence beyond the route marker.

A project choice is committed only after required evidence is sufficient and accepted project policy determines the choice for that boundary or the person, role, or valid delegate with project decision authority commits it.
That gate is independent from authorization to act: either may exist without the other, and host permission supplies neither.

Default route sequences are transitions with entry conditions, not mandatory pipelines.
Current-session actions remain in the session; Wayfinder holds durable coordination; specifications hold accepted scope and acceptance criteria; tickets hold approved independently deliverable work and blocking edges.
Discovery resolves bounded consequential alternatives and tradeoffs, including architectural choices when that analysis materially helps.
Research establishes externally sourced facts without selecting the project's preferred alternative.
Domain Modeling joins Discovery or Wayfinder only when ambiguity in concepts, terminology, boundaries, responsibilities, areas, or relationships is material; a choice being architectural does not select it.

Two boundaries are intentionally explicit.
Trivial local, low-risk edits remain Direct even though they mutate files; Implementation is for ready work where its orchestration and integration verification add material value.
Use a skill only when it is exposed in the current session.
If a selected skill is unavailable or cannot run without explicit user invocation, continue Direct only when it was optional and available capabilities can satisfy the authorized request.
Otherwise report the limitation or give the exact invocation instruction.
Never imitate the skill, and report only what actually ran.

Wayfinder is Agent Workflow's sole durable coordination model; its project-owned state lives under `.agent-wayfinder/`.
Chat output is session-local.
Wayfinder links project or external records only when they are durable.
If a chat-only result later needs continuity, Wayfinder preserves only the minimum needed coordination or evidence.
When resuming a Wayfinder effort, read its map first.
The map summarizes current coordination state, conditions blocking particular work, dependencies, and ready work; sparse F#/D# ledger sections and U#/E# records stay lazy.
F# contains a sufficiently supported, scoped, revisable conclusion; D# contains a current consequential choice determined directly by accepted project policy or committed by the person, role, or valid delegate with project decision authority; U# contains an unresolved question and is not itself a blocker; E# contains evidence with source, scope, observation, and limitations.
Before detailed decomposition, the map may state ready work directly.
When `to-tickets` decomposes work, the resulting durable ticket or ticket set maintains ticket contents, dependencies, ordering, and readiness; the map links that durable ticket or ticket set without mirroring ticket-level state.
A safe regular map makes an effort current and resumable; a mapless directory is not a candidate.
The router loads the Wayfinder contract only after Wayfinder is selected or a relevant effort is being resumed, then reads the map and only relevant F#/D# ledger sections or U#/E# files.
An unrelated existing map never changes a request's route.

When the current request or accepted project policy authorizes repository-local Wayfinder writes, routing may create a lightweight map without asking again after Wayfinder is selected.

Within a selected effort, continue directly with ready work.
Load Discovery, Debugging, Research, Prototype, Domain Modeling, Grilling, or human clarification only when that method materially improves how a current question, uncertainty, unexplained cause, consequential choice, or structural ambiguity is addressed.
Using a skill for specialist work does not create separate Agent Workflow durable coordination state.
While using the skill, the agent may return findings or produce the result described by its instructions; Wayfinder records only consequential results or references needed for coordination.
Implementation is a workflow transition for ready work, followed by Verification, not a Wayfinder reasoning method or coordination record.

After meaningful implementation or a causal fix, gather acceptance evidence not already supplied by the implementation method.
Do not repeat TDD or Code Review already completed by that method merely to add a framework stage.

Every user-facing final response ends with exactly one truthful instruction-level marker such as:

```text
[route: router -> implement -> verification]
```

The marker is required observability, not telemetry or proof that work ran, and must not trigger additional workflow work.
The unchanged `<skill>-handoff` terminal suffix means the selected skill still requires explicit user invocation and no Direct fallback satisfied the request.
Detailed syntax and terminal outcomes are defined by the installed routing policy.
