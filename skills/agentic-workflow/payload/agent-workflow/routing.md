# Detailed routing contract

This is the progressively loaded routing policy for an installed Agentic
Workflow project. The root `AGENTS.md` already performs the cheap first-pass
classification. Read this file only when ownership remains ambiguous, provider
fallback or handoff materially matters, or relevant durable re-entry is
unclear. Direct work, one obvious selected skill, and one obvious specialist
inside a selected Wayfinder effort do not load it. Root invariants remain
binding.

## Decide and compose

Choose the minimum useful process justified by intent, uncertainty, impact,
reversibility, and expected duration. File count is not a proxy for risk, and
skill availability is not a reason to invoke one. Keep these decisions separate:

1. select one dominant workflow or activity;
2. add only capabilities that materially help inside it;
3. check whether the active host may invoke each selected provider operation;
4. execute only within the user's authorization.

The installed skill descriptions are the first selection interface; this table
resolves overlaps and compositions rather than replacing those descriptions.
Normal intent is enough to select and execute an implicitly invocable skill.
Exact skill syntax is required only for explicit invocation or a user-only
provider operation. A supporting capability does not automatically become the
dominant workflow or create durable state.

| Signal | Dominant selection | Boundary |
|---|---|---|
| User explicitly names an installed skill | Named skill | Honor it unless authorization, safety, or host compatibility blocks execution |
| Explicit sustained learning intent | `teach` | Dedicated learning workspace; ordinary questions stay Direct |
| Several consequential state distinctions need durable coordination | `wayfinder` | Select only when structured project notes materially reduce the risk of losing or conflating them |
| Bounded consequential architecture, security, cost, dependency, or visible-behavior choice | Direct or local Discovery | Load Discovery only when explicit alternative and tradeoff analysis materially helps |
| Existing unexplained failure or regression | Direct or local Debugging | Load Debugging only when its causal method materially helps; diagnosis does not authorize a fix |
| Explicit substantive research or external facts needing primary sources | Direct or `research` | Load Research only when its primary-source artifact materially helps; simple lookups stay Direct |
| Settled scope benefits from a durable specification | `to-spec` | The provider artifact stays canonical |
| Approved work needs dependency-ordered or independently deliverable sessions | `to-tickets` | Preserve native tickets/frontier; create no shadow tickets |
| One coherent ready implementation scope where orchestration and integration verification add material value | local adapter, then `implement` | Trivial local, low-risk edits stay Direct |
| Explicit bounded test-first implementation | `tdd` | The provider owns the loop; local Verification checks the integrated result |
| Completed meaningful change, causal fix, or explicit completion audit | local Verification | Add uncovered acceptance/integration evidence; reuse current evidence |
| User requests standalone fixed-point review | `code-review` | Do not repeat review already completed by `implement` |
| Clear, bounded, low-risk request | Direct | Skip workflow ceremony and unrelated readiness checks |

## Re-evaluate and continue

Routing is not frozen at the first prompt. Re-evaluate when evidence changes the
task's uncertainty, scope, coordination, failure mode, or authorization needs.
Transition to the newly dominant workflow; do not keep executing an obsolete
route merely because it was selected first.

After any reconnaissance, MUST assess Wayfinder before completing. Three or
more meaningful items also trigger assessment, not selection. MUST select
Wayfinder when any hard signal or at least two soft signals make durable
coordination materially safer than conversation alone. This is an activation
rubric, not a numeric complexity score.

Hard signals are likely cross-session or handoff continuity, conflicting
authoritative sources, an authority-owned blocker while other work can proceed,
coordination across owners or areas, or provenance needed to keep an assumption
distinct from fact. Soft signals are interacting consequential unknowns, several
durable distinctions across state categories, a plan changing with evidence, a
meaningful dependency graph, or material reconstruction risk for a fresh agent.

Counts alone never select Wayfinder. One isolated unknown, several independent
routine actions, an ordinary implementation detail, or a bounded choice that
fits Discovery does not justify it.

An explicit Wayfinder request selects it subject to authorization and host
compatibility. An explicit instruction not to use it prevents automatic
selection. Read-only analysis, audit, diagnosis, review, and `do not change
files` requests never create or update Wayfinder state.

Resume only relevant work. A named Wayfinder effort or provider-native artifact
selects that exact re-entry point; a likely but unnamed Wayfinder resume
justifies the minimum inspection needed to identify it. An unrelated map never
captures the route, and confidently unrelated work does not scan durable state.
Legacy DEC/IMP/DBG files are historical project data, not current re-entry
points. Implementation may consume a coherent map scope, settled D#,
specification, or native ticket without rerunning Wayfinder.

For likely Wayfinder resume, prefer an explicit current map over a similarly
named completed, abandoned, or superseded map. Historical maps remain available
when directly named, explicitly requested, needed to follow a successor, or
otherwise materially relevant; do not load their child history merely to select
current work. A legacy map without lifecycle status remains valid and does not
receive an inferred status unless its outcome and next work make that clear.

After Wayfinder selection or relevant resume, load
`contracts/wayfinder-state.md` before the map and only the child files needed for
the current work. Do not load `contracts/durable-state.md` merely to mutate
Wayfinder. Load that general contract only for another authorized project-state
write that it still owns. No route uses a global active index or allocates DEC,
IMP, or DBG.

## Use default transitions, not mandatory pipelines

Keep current-session actions in the host todo mechanism. Use Wayfinder for
durable uncertainty, decisions, conflicts, dependencies, blockers, and
provenance. Use specifications for settled scope and acceptance criteria, and
use tickets for approved independently deliverable work and blocking edges.
Never copy one representation into another merely to complete a route.

- Direct work stays Direct unless new evidence changes the route.
- A consequential choice stays Direct when it is safely resolvable without
  extra methodology. Load Discovery for material alternative analysis, Domain
  Modeling for material conceptual ambiguity, and Wayfinder only at its durable
  threshold.
- An observed failure stays Direct when simple evidence resolves it. Load
  Debugging when causal investigation materially helps, add Wayfinder only for
  durable coordination, and move to Implementation only when a fix is
  authorized.
- Settled scope may use `to-spec`; approved work uses `to-tickets` only when
  dependency ordering or independent sessions add value.
- Meaningful Implementation runs Verification once. New unexplained failure
  returns to Debugging; a material unresolved choice returns to Discovery or
  Wayfinder.

These are defaults with entry conditions, not stages to execute merely because
they appear in a path.

## Resolve providers

Resolve only selected provider operations through
`.agent-workflow/providers.json`. Use its active-host declaration, discovery
path, invocation policy, explicit prefix, prerequisites, and adapter metadata as
current facts:

- `implicit`: a compatible host may load and execute the skill normally;
- `user-only`: execute only after exact explicit host invocation;
- `unavailable`: do not claim the provider ran.

Selection is not execution. When a preferred provider is unavailable,
incompatible, absent, misconfigured, or user-only without explicit invocation,
continue with truthful host-native capability when authorized. Do not load or
imitate the provider, create its native artifacts, or claim it ran. Stop or
return an exact handoff only when the user required that provider or no safe,
authorized host-native path can satisfy the request. When material, disclose
that the preferred provider did not execute and why.

For a required user-only operation, name the selected workflow and form the
exact invocation from the active host's declared prefix, such as `$skill-name`
or `/skill-name`. If the host cannot be distinguished, label the supported forms
instead of guessing. A handoff does not execute work or authorize state changes.

Check configuration only after selecting an operation that declares it. If the
requested provider-owned outcome requires missing configuration and there is no
authorized host-native equivalent, offer the exact user-only
`setup-matt-pocock-skills` handoff even when the user did not literally ask to
enable setup. Never run setup automatically, and never inspect setup for an
unrelated route. When an authorized host-native path can satisfy the request,
use it instead of making setup ceremony a prerequisite.

## Preserve workflow ownership

The selected provider owns its internal method, terminology, and native
artifacts by default. Wayfinder is the declared exception: Agentic Workflow's
installed skill is the owned effective runtime derived from the pinned upstream
methodology. The router owns selection and composition, not a duplicate
methodology. Reuse provider evidence and add a second pass only for a distinct
request or a demonstrated gap.

For Implementation, the local adapter supplies accepted scope, canonical
artifacts, acceptance criteria, and configured commands. Invoked `implement`
owns its build loop, appropriate TDD, and closing Code Review. Framework
Verification runs once afterward, reusing that evidence and adding only
uncovered acceptance, artifact, integration, or compatibility checks. An
unexplained existing failure returns to Debugging; a material unresolved choice
returns to Discovery or Wayfinder according to the state threshold.

The workflow that creates a durable artifact owns its canonical form. Native
specifications, tickets, research, maps, learning workspaces, reviews, and
provider identifiers remain in their owning locations. Framework state stores
only orchestration facts and pointers unless a dedicated contract defines a
canonical local representation.

Wayfinder is the sole framework-owned durable coordination layer. When selected,
it owns continuity under `.agent-workflow-state/wayfinder/` without
monopolizing reasoning. Discovery, Debugging, Research, Prototype, Grilling,
human clarification, and Domain Modeling may resolve a frontier as stateless
supporting activities. Invoke only the smallest method that materially helps;
otherwise continue directly. Obvious selection does not require this detailed
router, and no specialist creates DEC, IMP, DBG, or a competing notebook.

Implementation is a transition to an execution owner, not a Wayfinder reasoning
mechanism. It consumes a coherent map, specification, decision, or native
ticket, executes once, and invokes Verification. If later continuity becomes
unsafe, Wayfinder preserves only the consequential frontier and artifact
pointers; there is no implementation record.

Use `workflow-verification` for evidence procedure and
`contracts/project-profile.md` only when profile facts or an authorized profile
update are relevant. Do not invent commands, repeat provider checks, or inspect
the repository merely to complete a route.

## Report the executed route

Every user-facing final response must end with exactly one compact, truthful
marker containing workflows and explicitly composed capabilities that actually
executed, in effective-use order:

```text
[route: router → implement → verification]
```

Use compact local labels: `workflow-discovery`, `workflow-debugging`,
`workflow-implementation`, and `workflow-verification` become `discovery`,
`debugging`, `implement`, and `verification`.

Use a terminal suffix only when selection did not become equivalent execution:

- `<skill>-handoff`: exact user-only invocation is still required;
- `<skill>-unavailable`: the required provider cannot run on the active host;
- `<skill>-blocked`: authorization, state, prerequisite, or integrity stopped it.

After a successful provider fallback, report the actual host-native activity
that executed and omit the unavailable provider. Use `direct` when no named
local workflow or installed skill actually ran. Do not add a terminal suffix
merely because the preferred provider was skipped.

Examples:

```text
[route: router → direct]
[route: router → debugging → wayfinder]
[route: router → implement → verification]
[route: router → research-handoff]
```

The ASCII `->` separator is equivalent when Unicode output is unavailable.
Availability checks, catalog lookup, configuration checks, handoffs, and
unexecuted selection do not count as execution. Provider-owned TDD and Code
Review remain represented by `implement` unless separately selected;
independently executed framework Verification remains visible.

The marker is instruction-level observability, not host telemetry or proof of
execution. Do not reroute, load skills, execute workflows, explain rejected
routes, or write state merely to produce it.
