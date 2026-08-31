# Detailed routing policy

The root policy performs first-pass routing. Read this policy only when
responsibility for the accepted project record designated to maintain a result
is unclear; a selected skill is unavailable or requires explicit user
invocation; an agent handoff occurs; or durable resumption is unclear.
Direct work, one obvious workflow, and one obvious specialist inside Wayfinder
do not load it.
Root rules for action authorization, project decision authority, preservation,
and reporting remain binding.

## Decide and compose

Choose the minimum useful process justified by intent, uncertainty, impact,
reversibility, and expected duration. File count and skill availability do not
select a workflow.

1. Choose Direct or one primary workflow; add only supporting capabilities that
   materially help.
2. Read the instructions for each selected skill and only the support files
   those instructions require.
3. Execute only actions authorized by the current user request or accepted
   project policy, and only within that scope.

Do not treat a consequential project choice as committed until required
evidence is sufficient and either accepted project policy determines the choice
for that boundary or the person, role, or valid delegate with project decision
authority commits it. Authorization to perform an action does not commit that
choice, and a committed choice does not authorize an unrelated action. Host
permission supplies neither.

Choose skills from the descriptions exposed in the current session. Before
making or acting on a consequential choice, resolve any material unresolved
prerequisite using the minimum sufficient method. This table resolves overlaps:

| Signal | Selection | Boundary |
|---|---|---|
| Explicit skill request | Named skill | Honor when available unless action authorization or safety blocks execution; otherwise apply the unavailable-skill rule |
| Durable coordination threshold crossed | `wayfinder` | Structured project state must materially improve continuity |
| Consequential bounded choice | Direct or Discovery | Load Discovery only when alternative and tradeoff analysis helps |
| Interdependent choices requiring human input or project decision authority materially shape downstream work | Direct or `grilling` | Use Grilling to resolve their unresolved prerequisites; factual questions and one straightforward clarification use the minimum sufficient method |
| Domain concepts, vocabulary, boundaries, responsibilities, or relationships need active clarification | Direct or Domain Modeling | Load Domain Modeling only when changing or reorganizing the model materially helps; ordinary vocabulary lookup stays Direct |
| Throwaway implementation would answer a design or behavior question | Direct or `prototype` | Ordinary production implementation stays Direct or with its primary workflow |
| Module interface, seam, depth, locality, or testability needs explicit design | Direct or `codebase-design` | Load Codebase Design only when its vocabulary materially improves the design; ordinary edits and refactors stay Direct or with their primary workflow |
| Unexplained failure or regression | Direct or Debugging | Load Debugging only when causal investigation helps; diagnosis grants no action authorization for a fix |
| External uncertainty needing primary sources | Direct or `research` | Simple lookups stay Direct |
| A sufficiently defined scope needs a specification | `to-spec` | The specification maintains the accepted scope |
| Approved work needs ordered independent sessions | `to-tickets` | The ticket or ticket set maintains its contents, dependencies, ordering, and readiness |
| One implementation scope is ready | Implementation, then `implement` | Trivial low-risk edits stay Direct; meaningful work ends with Verification |
| Explicit bounded test-first work | `tdd` | The skill defines its loop |
| Completion audit or meaningful finished change | Verification | Add only uncovered acceptance or integration evidence |
| Standalone fixed-point review | `code-review` | Do not repeat a review completed by `implement` |
| Clear bounded low-risk request | Direct | Skip workflow ceremony |

Clear intent or an explicit request may select a skill exposed in the current
session. A supporting skill does not become the primary workflow or create
Agent Workflow durable coordination state.

## Re-evaluate and resume

Re-evaluate when evidence changes uncertainty, scope, coordination, failure
mode, or action authorization. Apply the root Wayfinder threshold; counts trigger
assessment, never selection. Explicit Wayfinder use and opt-out control the route.

Resume only relevant work. Continue from the current authorized request,
relevant source, accepted project record designated to maintain the result, or
applicable Wayfinder map. For an unnamed likely Wayfinder resume,
inspect the smallest plausible effort set and resume only one clear
objective-and-scope match. A safe regular map identifies current resumable
coordination; a mapless directory is not a candidate. An unrelated map never
captures the route.

After selecting Wayfinder, read `contracts/wayfinder-state.md`, then the map and
only relevant F#/D# ledger sections or U#/E# artifacts. Implementation may
consume ready work from the current authorized request, relevant source, or
accepted project record without rerunning Wayfinder.

Avoid routing loops: a bounded decision remains in Discovery unless it crosses
the Wayfinder threshold. Inside selected Wayfinder, use each needed specialist
once for the relevant question, uncertainty, unexplained cause, consequential
choice, or structural ambiguity without creating another Agent Workflow durable
coordination model.
Meaningful Implementation runs Verification once. New causal uncertainty returns
to Debugging; a material unresolved choice returns to Discovery or Wayfinder
according to the coordination threshold.

Discovery is the method for bounded consequential choice and tradeoff analysis. Compose
Domain Modeling when structural ambiguity materially affects that analysis or
reorganizing the domain would materially improve it; otherwise Discovery runs
alone.

## Use selected skills

Use a skill only when it is exposed in the current session. Read the selected
skill's instructions and only the support files needed for the current request.
Selecting a skill is not execution: include it in the route marker only when its
method actually ran.

Keep the stages distinct. Route selection chooses Direct or a workflow;
supporting-capability selection chooses additional help; loading a selected
skill makes its instructions available; material execution means its method
actually ran; and completion and verification require evidence beyond the route
marker.

If a selected skill is unavailable or cannot run without explicit user
invocation, continue Direct only when the user did not require that skill and
available capabilities can satisfy the request. Direct work remains subject to
the current request's or accepted project policy's action authorization.
Otherwise, give the exact supported invocation instruction and stop with
`<skill>-handoff` when explicit user invocation remains required, or stop with
`<skill>-unavailable` when the skill is unavailable.

If authorization, current state, a required input, or an integrity check
prevents the selected work from proceeding, stop with `<skill>-blocked`. Never
claim an unavailable skill ran or present Direct work as that skill's result.

## Preserve responsibilities and transitions

Each selected skill defines its method, terminology, and evidence requirements.
The accepted project record designated to maintain its result remains
authoritative. Wayfinder stores only consequential coordination and links that
record when it is durable; a chat-only result remains session-local.

The Implementation integration supplies one accepted scope and its acceptance
criteria from the current authorized request, relevant source, or accepted
project record. `implement` owns its build loop, TDD, and closing Code Review.
Framework Verification runs afterward and adds only uncovered evidence. The
specialist creates no Agent Workflow durable coordination state.

## Report the executed route

Every user-facing final response ends with exactly one truthful marker listing
only workflows and composed capabilities that executed, in effective-use order:

```text
[route: router → implement → verification]
```

Use compact labels: `workflow-discovery`, `workflow-debugging`,
`workflow-implementation`, and `workflow-verification` become `discovery`,
`debugging`, `implement`, and `verification`. Use `direct` when no named
workflow or skill ran.

Use a terminal suffix only when selection did not become equivalent execution:

- `<skill>-handoff`: explicit user invocation remains required;
- `<skill>-unavailable`: the required skill cannot run;
- `<skill>-blocked`: action authorization, state, prerequisite, or integrity stopped it.

After a successful Direct fallback, omit the skill that could not run from the
marker; use `direct` only when no named workflow or skill ran. Availability or
status checks, invocation instructions, and unexecuted selections do not count
as execution. TDD and Code Review run within `implement` remain represented by
`implement` unless separately selected. The ASCII `->` separator is valid when
Unicode is unavailable.

The marker is instruction-level observability, not proof of execution. Never
reroute, load skills, execute work, explain rejected routes, or write state only
to produce it.
