# Detailed routing policy

The root policy performs first-pass routing.
Read this policy only when artifact or record responsibility is unclear or selected-skill availability, an exact invocation instruction, agent handoff, or durable resumption materially matters.
Root rules for action authorization, project decision authority, preservation, and reporting remain binding.

## Decide and compose

Choose the minimum useful process justified by intent, uncertainty, impact, reversibility, and expected duration.
File count does not select a workflow.

Before making or acting on a consequential choice, resolve any material unresolved prerequisite using the minimum sufficient method.
This table resolves overlaps:

| Signal | Selection | Boundary |
|---|---|---|
| Explicit skill request | Named skill | Honor when available unless action authorization or safety blocks execution; otherwise apply the unavailable-skill rule |
| Durable coordination threshold crossed | `wayfinder` | Structured project state must materially improve continuity |
| Consequential bounded choice | Direct or Discovery | Load Discovery only when alternative and tradeoff analysis helps |
| Interdependent choices requiring human input or project decision authority materially shape downstream work | Direct or `grilling` | Use Grilling to resolve their unresolved prerequisites; factual questions and one straightforward clarification use the minimum sufficient method |
| Domain concepts, terminology or ubiquitous language, domain or context boundaries, or domain responsibilities and relationships need active clarification | Direct or Domain Modeling | Load Domain Modeling only when changing or reorganizing the domain model materially helps; ordinary vocabulary lookup stays Direct |
| An interactive logic demo or UI exploration would answer a design question | Direct or `prototype` | CLI and infrastructure experiments may use Direct or existing methods; production implementation retains its normal route |
| Module interface, seam, depth, locality, or testability needs explicit design | Direct or `codebase-design` | Load Codebase Design only when its vocabulary materially improves the design; ordinary edits and refactors stay Direct or with their primary workflow |
| Unexplained failure or regression | Direct or Debugging | Load Debugging only when causal investigation helps; diagnosis grants no action authorization for a fix |
| External uncertainty needing primary sources | Direct or `research` | Simple lookups stay Direct |
| A sufficiently defined scope needs a specification | `to-spec` | The specification maintains the accepted scope |
| Approved work needs ordered independent sessions | `to-tickets` | The durable ticket or ticket set maintains its contents, dependencies, ordering, and readiness |
| One implementation scope is ready | Implementation, then `implement` | Trivial low-risk edits stay Direct; meaningful work ends with Verification |
| Explicit bounded test-first work | `tdd` | The skill defines its loop |
| Completion audit or meaningful finished change | Verification | Add only uncovered acceptance or integration evidence |
| Standalone fixed-point review | `code-review` | Do not repeat a review completed by `implement` |
| Clear bounded low-risk request | Direct | Skip workflow ceremony |

A bounded architectural choice remains Direct or uses Discovery when alternative and tradeoff analysis materially helps.
It does not select Domain Modeling merely because the choice is architectural.
Discovery may compose Research when its additional method materially helps establish external evidence and Domain Modeling when domain-model ambiguity materially affects the decision.

Use the table to guide the current routing choice.
How a skill is used for one request does not determine how it must be used later.

## Re-evaluate and resume

Re-evaluate when evidence changes uncertainty, scope, coordination, failure mode, or action authorization.
Apply the root Wayfinder threshold.

Resume only relevant work.
Continue from the current authorized request, selected Wayfinder map, current decision record, accepted specification, or approved durable ticket or ticket set.
For an unnamed likely Wayfinder resume, inspect the smallest plausible effort set and resume only one clear semantic match on objective and scope.
Scope refinement need not preserve the original wording when the objective and substantive scope remain the same.
A safe regular map identifies current resumable coordination; a mapless directory is not a candidate.
An unrelated map never captures the route.

After selecting Wayfinder, read the [state contract](contracts/wayfinder-state.md) before effort state; it owns full recognition, creation, map-first resumption, and preservation mechanics.
Implementation may consume ready work from the current authorized request, selected Wayfinder map, current decision record, accepted specification, or approved durable ticket or ticket set without rerunning Wayfinder.

Avoid routing loops: a bounded decision remains in Discovery unless it crosses the Wayfinder threshold.
Inside selected Wayfinder, use each needed specialist once for the relevant question, uncertainty, unexplained cause, consequential choice, or domain-model ambiguity without creating another Agent Workflow durable coordination model.
Meaningful Implementation runs Verification once.
New causal uncertainty returns to Debugging; a material unresolved choice returns to Discovery or Wayfinder according to the coordination threshold.

## Use selected skills

Prefer native skill execution when the host exposes the selected skill.
When the host exposes the selected skill natively, use its native skill mechanism to load and execute the installed canonical instructions.

When the host does not expose the selected skill natively, the method may still run when its canonical `.agents/skills/<name>/SKILL.md` is readable and every capability required for the current method is available in the session.
Read that file and only the support files needed for the current request, then execute the portable parts of its method directly as repository instructions.
This is portable method execution, not native host skill invocation.
Do not claim a native invocation, native discovery, unavailable tool, independent reviewer, parallel worker, interactive surface, or other host-specific feature ran merely because its instructions were readable.

<!-- portable-skill-routing-matrix -->
| Native exposure | Canonical instructions | Required capabilities | Contract result |
|---|---|---|---|
| exposed | host-loaded | available | native skill execution |
| not exposed | readable | available | portable method execution |
| not exposed | missing or unreadable | any | unavailable |
| not exposed | readable | required capability unavailable | unavailable or blocked |
<!-- /portable-skill-routing-matrix -->

Execution means using the skill's method; selecting it, reading instructions, checking availability, or giving invocation instructions does not count.
Using a skill for focused work need not change the primary route, including Direct.
Completion and verification require evidence beyond execution or a route marker.

Research and factual lookup may run synchronously when their evidence requirements remain satisfied.
Preserve a selected method's required independence or parallelism; if that capability is unavailable, report the execution gap under the availability conventions below rather than claiming independent work ran.

If the canonical instructions are missing or unreadable, or a capability required by the method is unavailable, apply the existing unavailable or blocked outcome rather than claiming partial steps as the full method.
If a selected skill is unavailable or requires explicit user invocation, continue Direct only when the user did not require that skill and available capabilities can satisfy the request.
Otherwise stop, explain what is needed, give the exact supported invocation instruction when applicable, and use the terminal suffix below.
Also stop affected work when authorization, current state, a required input, or an integrity check prevents it from proceeding.
Never present Direct work as execution of a skill that could not run.

## Preserve responsibilities and transitions

Selected skills supply their methods, terminology, and evidence.
Wayfinder is Agent Workflow's sole durable coordinator and stores only consequential state and references.
Specifications, tickets, research, maps, and reviews remain in the artifacts or records designated to maintain their results; external identifiers remain unchanged.

The Implementation integration supplies the accepted scope, its maintaining references, and acceptance criteria from the resumption inputs above.
Invoked `implement` is responsible for its build loop, TDD, and closing Code Review.
Completion follows `workflow-implementation`'s Verify the result step.
Using a skill for specialist work does not create separate Agent Workflow durable coordination state.

## Report the executed route

Every user-facing final response ends with exactly one truthful marker listing only workflows and composed capabilities that executed, in effective-use order:

```text
[route: router → implement → verification]
```

Use compact labels: `workflow-discovery`, `workflow-debugging`, `workflow-implementation`, and `workflow-verification` become `discovery`, `debugging`, `implement`, and `verification`.
Use `direct` when no named workflow or skill ran.
The marker names the method that executed and does not encode which instruction-loading path ran.
For portable method execution, surrounding prose must not imply native skill invocation or unavailable host features.

Use a terminal suffix only when selection did not become equivalent execution:

- `<skill>-handoff`: explicit user invocation remains required;
- `<skill>-unavailable`: the required skill cannot run;
- `<skill>-blocked`: action authorization, state, prerequisite, or integrity stopped it.

After a successful Direct fallback, omit the skill that could not run from the marker.
TDD and Code Review run within `implement` remain represented by `implement` unless separately selected.
The ASCII `->` separator is valid when Unicode is unavailable.

The marker reports execution; it does not prove it.
Never reroute, load skills, execute work, explain rejected routes, or write state only to produce it.
