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
An objective cues semantic assessment rather than automatic selection: objective and scope must sufficiently identify the effort, and the existing durable-coordination threshold must still be met.
The [root policy](../agent_workflow/install/AGENTS.md.template#when-to-use-wayfinder) maintains the complete hard/soft thresholds, ambiguity gate, and explicit selection or opt-out rules.
For example, known work awaiting an external result may need durable coordination even without an unresolved design question.
A clear bounded plan does not qualify merely because later work will execute it, and existing state alone does not select Wayfinder.
The [detailed routing policy](../.agent-workflow/routing.md#re-evaluate-and-resume) permits a bounded read-only check to establish whether a request continues a relevant effort before selecting Wayfinder.

The compact always-loaded rules live in `agent_workflow/install/AGENTS.md.template`.
Detailed overlap resolution, composition, transitions, unavailable-skill handling, exact user-invocation instructions, unclear responsibility for resumption records, and route-marker edge cases live in `.agent-workflow/routing.md`.
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

A project choice is committed only after required evidence is sufficient and accepted project policy determines the choice for that boundary or the person, role, or valid delegate with project decision authority commits it.
That gate is independent from authorization to act: either may exist without the other, and host permission supplies neither.

Default route sequences are transitions with entry conditions, not mandatory pipelines.
Current-session actions remain in the session; Wayfinder holds durable coordination; specifications hold accepted scope and acceptance criteria; tickets hold approved independently deliverable work and blocking edges.
Discovery resolves bounded consequential alternatives and tradeoffs, including architectural choices when that analysis materially helps.
Research establishes externally sourced facts without selecting the project's preferred alternative.
Research returns evidence to its caller; consequential evidence alone does not require Discovery, and already-sufficient evidence does not require a Research invocation.
Compose either method only when it materially helps the current work.
Domain Modeling joins Discovery or Wayfinder only when ambiguity in domain concepts, terminology or ubiquitous language, domain or context boundaries, or domain responsibilities and relationships is material; a choice being architectural does not select it.

Two boundaries are intentionally explicit.
Trivial local, low-risk edits remain Direct even though they mutate files; Implementation is for ready work where its orchestration and integration verification add material value.
Use a skill only when it is exposed in the current session.
If a selected skill is unavailable or cannot run without explicit user invocation, continue Direct only when it was optional and available capabilities can satisfy the authorized request.
Otherwise report the limitation or give the exact invocation instruction.
Never imitate the skill, and report only what actually ran.

Wayfinder is Agent Workflow's sole durable coordination model; its project-owned state lives under `.project-efforts/`.
After selection, the agent loads the [state contract](../.agent-workflow/contracts/wayfinder-state.md) before effort state, starts from the map, and reads only relevant supporting records.
That contract owns effort identity, selective record preservation, map authoring, and reconciliation.
It also assigns map-versus-ticket responsibility: a map orients the effort and links a durable ticket set instead of mirroring its details.
Chat-only drafts remain session-local; authorized persistence preserves only what continuation needs.

Within a selected effort, continue directly with ready work.
Load Discovery, Debugging, Research, Prototype, Domain Modeling, Grilling, or human clarification only when that method materially improves how a current question, uncertainty, unexplained cause, consequential choice, or domain-model ambiguity is addressed.
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
