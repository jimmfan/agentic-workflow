# Detailed routing policy

The root policy performs first-pass routing.
Read this policy only when artifact or record responsibility is unclear or selected-skill availability, an exact invocation instruction, agent handoff, or durable resumption materially matters.
Root rules for action authorization, project decision authority, preservation, and reporting remain binding.

## Decide and compose

Choose the minimum useful process justified by intent, uncertainty, impact, reversibility, and expected duration.
File count does not select a workflow.

1. Choose Direct or one primary workflow; add only supporting capabilities that materially help.
2. Read the instructions for each selected skill and only the support files those instructions require.

Before making or acting on a consequential choice, resolve any material unresolved prerequisite using the minimum sufficient method.
This table resolves overlaps:

| Signal | Selection | Boundary |
|---|---|---|
| Explicit skill request | Named skill | Honor when available unless action authorization or safety blocks execution; otherwise apply the unavailable-skill rule |
| Durable coordination threshold crossed | `wayfinder` | Structured project state must materially improve continuity |
| Consequential bounded choice | Direct or Discovery | Load Discovery only when alternative and tradeoff analysis helps |
| Interdependent choices requiring human input or project decision authority materially shape downstream work | Direct or `grilling` | Use Grilling to resolve their unresolved prerequisites; factual questions and one straightforward clarification use the minimum sufficient method |
| Domain concepts, terminology or ubiquitous language, domain or context boundaries, or domain responsibilities and relationships need active clarification | Direct or Domain Modeling | Load Domain Modeling only when changing or reorganizing the domain model materially helps; ordinary vocabulary lookup stays Direct |
| Throwaway implementation would answer a design or behavior question | Direct or `prototype` | Ordinary production implementation stays Direct or with its primary workflow |
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
Discovery may compose Research when external evidence materially affects the decision and Domain Modeling when domain-model ambiguity materially affects it.

Use the table to guide the current routing choice.
How a skill is used for one request does not determine how it must be used later.

## Re-evaluate and resume

Re-evaluate when evidence changes uncertainty, scope, coordination, failure mode, or action authorization.
Apply the root Wayfinder threshold.

Resume only relevant work.
Continue from the current authorized request, selected Wayfinder map, current decision record, accepted specification, or approved durable ticket or ticket set.
For an unnamed likely Wayfinder resume, inspect the smallest plausible effort set and resume only one clear semantic match on objective and current scope.
Scope refinement need not preserve the original wording when the objective and coordination boundary remain the same in substance.
A safe regular map identifies current resumable coordination; a mapless directory is not a candidate.
An unrelated map never captures the route.

After selecting Wayfinder, read `contracts/wayfinder-state.md`, then the map and only relevant F#/D# ledger sections or U#/E# artifacts.
Implementation may consume ready work from the current authorized request, selected Wayfinder map, current decision record, accepted specification, or approved durable ticket or ticket set without rerunning Wayfinder.

Avoid routing loops: a bounded decision remains in Discovery unless it crosses the Wayfinder threshold.
Inside selected Wayfinder, use each needed specialist once for the relevant question, uncertainty, unexplained cause, consequential choice, or domain-model ambiguity without creating another Agent Workflow durable coordination model.
Meaningful Implementation runs Verification once.
New causal uncertainty returns to Debugging; a material unresolved choice returns to Discovery or Wayfinder according to the coordination threshold.

Discovery is the method for bounded consequential choice and tradeoff analysis.
Compose Domain Modeling when ambiguity in domain concepts, terminology, ubiquitous language, domain or context boundaries, or domain responsibilities and relationships materially affects that analysis; otherwise Discovery runs alone.

## Use selected skills

Use a skill only when it is exposed in the current session.
Read the selected skill's instructions and only the support files needed for the current request.
Selecting a skill is not execution: include it in the route marker only when its method actually ran.

Choosing a route, selecting a skill, loading its instructions, using its method, completing the request, and verifying the result are distinct.
The agent chooses Direct or one primary workflow.
A request may remain Direct while the agent uses a skill for focused work.
A skill may also support the current route without becoming its primary workflow.
Loading a selected skill makes its instructions available; execution means actually using the skill's method; and completion and verification require evidence beyond the route marker.

If a selected skill is unavailable or cannot run without explicit user invocation, continue Direct only when the user did not require that skill and available capabilities can satisfy the request.
Otherwise, give the exact supported invocation instruction and stop with `<skill>-handoff` when explicit user invocation remains required, or stop with `<skill>-unavailable` when the skill is unavailable.

If authorization, current state, a required input, or an integrity check prevents the selected work from proceeding, stop with `<skill>-blocked`.
Never claim an unavailable skill ran or present Direct work as that skill's result.

## Preserve responsibilities and transitions

Selected skills supply their methods, terminology, and evidence.
Wayfinder is Agent Workflow's sole durable coordinator and stores only consequential state and references.
Specifications, tickets, research, maps, and reviews remain in the artifacts or records designated to maintain their results; external identifiers remain unchanged.

The Implementation integration supplies accepted scope, references to the artifacts or records that maintain it, and acceptance criteria from the current authorized request, selected Wayfinder map, current decision record, accepted specification, or approved durable ticket or ticket set.
Invoked `implement` is responsible for its build loop, TDD, and closing Code Review.
Framework Verification runs afterward and adds only uncovered evidence.
Using a skill for specialist work does not create separate Agent Workflow durable coordination state.

## Report the executed route

Every user-facing final response ends with exactly one truthful marker listing only workflows and composed capabilities that executed, in effective-use order:

```text
[route: router → implement → verification]
```

Use compact labels: `workflow-discovery`, `workflow-debugging`, `workflow-implementation`, and `workflow-verification` become `discovery`, `debugging`, `implement`, and `verification`.
Use `direct` when no named workflow or skill ran.

Use a terminal suffix only when selection did not become equivalent execution:

- `<skill>-handoff`: explicit user invocation remains required;
- `<skill>-unavailable`: the required skill cannot run;
- `<skill>-blocked`: action authorization, state, prerequisite, or integrity stopped it.

After a successful Direct fallback, omit the skill that could not run from the marker; use `direct` only when no named workflow or skill ran.
Availability or status checks, invocation instructions, and unexecuted selections do not count as execution.
TDD and Code Review run within `implement` remain represented by `implement` unless separately selected.
The ASCII `->` separator is valid when Unicode is unavailable.

The marker is instruction-level observability, not proof of execution.
Never reroute, load skills, execute work, explain rejected routes, or write state only to produce it.
