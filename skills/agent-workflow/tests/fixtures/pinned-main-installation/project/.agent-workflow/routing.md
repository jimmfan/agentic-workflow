# Detailed routing policy

The root policy performs first-pass routing. Read this policy only for
ambiguous responsibility, material provider fallback, an exact user invocation
instruction, agent handoff, or unclear durable resumption. Direct work, one
obvious workflow, and one obvious specialist inside Wayfinder do not load it.
Root rules for action authorization, project decision authority, preservation,
and reporting remain binding.

## Decide and compose

Choose the minimum useful process justified by intent, uncertainty, impact,
reversibility, and expected duration. File count and skill availability do not
select a workflow.

1. Choose Direct or one primary workflow; add only supporting capabilities that
   materially help.
2. Confirm host support and the invocation policy for each selected provider
   operation.
3. Execute only actions authorized by the current user request or accepted
   project policy, and only within that scope.

Do not treat a consequential project choice as committed until required
evidence is sufficient and either accepted project policy determines the choice
for that boundary or the person, role, or valid delegate with project decision
authority commits it. Authorization to perform an action does not commit that
choice, and a committed choice does not authorize an unrelated action. Host
permission supplies neither.

Installed skill descriptions are the first selection interface. Before making
or acting on a consequential choice, resolve any material unresolved
prerequisite using the minimum sufficient method. This table resolves overlaps:

| Signal | Selection | Boundary |
|---|---|---|
| Explicit compatible skill request | Named skill | Honor unless action authorization, safety, or compatibility blocks it |
| Sustained learning intent | `teach` | Ordinary questions stay Direct |
| Durable coordination threshold crossed | `wayfinder` | Structured project state must materially improve continuity |
| Consequential bounded choice | Direct or Discovery | Load Discovery only when alternative and tradeoff analysis helps |
| Interdependent choices requiring human input or project decision authority materially shape downstream work | Direct or `grilling` | Use Grilling to resolve their unresolved prerequisites; factual questions and one straightforward clarification use the minimum sufficient method |
| Domain concepts, vocabulary, boundaries, responsibilities, or relationships need active clarification | Direct or Domain Modeling | Load Domain Modeling only when changing or reorganizing the model materially helps; ordinary vocabulary lookup stays Direct |
| Throwaway implementation would answer a design or behavior question | Direct or `prototype` | Ordinary production implementation stays Direct or with its primary workflow |
| Module interface, seam, depth, locality, or testability needs explicit design | Direct or `codebase-design` | Load Codebase Design only when its vocabulary materially improves the design; ordinary edits and refactors stay Direct or with their primary workflow |
| Unexplained failure or regression | Direct or Debugging | Load Debugging only when causal investigation helps; diagnosis grants no action authorization for a fix |
| External uncertainty needing primary sources | Direct or `research` | Simple lookups stay Direct |
| A sufficiently defined scope needs a specification | `to-spec` | Its artifact maintains the accepted scope |
| Approved work needs ordered independent sessions | `to-tickets` | Its ticket artifact maintains ticket contents, ordering, and readiness |
| One implementation scope is ready | Implementation, then `implement` | Trivial low-risk edits stay Direct; meaningful work ends with Verification |
| Explicit bounded test-first work | `tdd` | The provider defines its loop |
| Completion audit or meaningful finished change | Verification | Add only uncovered acceptance or integration evidence |
| Standalone fixed-point review | `code-review` | Do not repeat a review completed by `implement` |
| Clear bounded low-risk request | Direct | Skip workflow ceremony |

Normal intent may select an implicitly invocable provider. Exact skill syntax is
needed only for explicit invocation or a user-only operation. A supporting
capability does not become the primary workflow or create Agent Workflow durable
coordination state.

## Re-evaluate and resume

Re-evaluate when evidence changes uncertainty, scope, coordination, failure
mode, or action authorization. Apply the root Wayfinder threshold; counts trigger
assessment, never selection. Explicit Wayfinder use and opt-out control the route.

Resume only relevant work. Continue from an exact Wayfinder map or provider-native
artifact. For an unnamed likely Wayfinder resume, inspect the smallest plausible
effort set and resume only one clear objective-and-scope
match. A safe regular map identifies current resumable coordination; a mapless
directory is not a candidate. An unrelated map never captures the route.

After selecting Wayfinder, read `contracts/wayfinder-state.md`, then the map and
only relevant F#/D# ledger sections or U#/E# artifacts. Implementation may
consume ready work from a map, a current decision record, a specification, or a
provider-native ticket without rerunning Wayfinder.

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

## Resolve providers

Resolve only selected provider operations through
`.agent-workflow/providers.json`:

- `implicit`: a compatible host may invoke it normally;
- `user-only`: require the declared explicit prefix;
- `unavailable`: do not claim it ran.

Keep the stages distinct. Route selection chooses Direct or a workflow;
supporting-capability selection chooses additional help; provider resolution
identifies the configured provider operation; skill invocation calls or
activates the selected skill; material execution means the selected method
actually ran; and completion and verification require evidence beyond the route
marker.

Do not conflate host support, invocation policy, configuration readiness,
installed provider-projection status, and host-native fallback. A selected
operation may be supported by the host but require explicit invocation, may be
invocable but not configuration-ready, or may need its installed projection
repaired before invocation.

If a preferred provider cannot run, use host-native capability when the current
request or accepted project policy authorizes the required actions and it can
satisfy the request. Do not imitate the provider or create its provider-native
artifacts. Stop or give the exact user invocation instruction only when the user
required that provider or no safe authorized fallback exists.

For a user-only operation, form the invocation from the active host's declared
prefix. If the host is unknown, label supported forms instead of guessing.
Check configuration only after selecting an operation that declares it. Never
run setup automatically or inspect setup for an unrelated route.

## Preserve responsibilities and transitions

Providers supply their methods, terminology, evidence, and provider-native
artifacts. Wayfinder is Agent Workflow's sole durable coordinator and stores
only consequential state and references. Specifications, tickets, research,
maps, learning workspaces, and reviews remain in the provider-native or project
artifacts that maintain their results; provider identifiers remain unchanged.

The Implementation integration supplies accepted scope, references to the
artifacts that maintain it, and acceptance criteria. Invoked `implement` is
responsible for its build loop, TDD, and closing Code Review. Framework Verification runs
afterward and adds only uncovered evidence. The specialist creates no Agent
Workflow durable coordination state.

## Report the executed route

Every user-facing final response ends with exactly one truthful marker listing
only workflows and composed capabilities that executed, in effective-use order:

```text
[route: router → implement → verification]
```

Use compact labels: `workflow-discovery`, `workflow-debugging`,
`workflow-implementation`, and `workflow-verification` become `discovery`,
`debugging`, `implement`, and `verification`. Use `direct` when no named local
workflow or installed skill ran.

Use a terminal suffix only when selection did not become equivalent execution:

- `<skill>-handoff`: explicit user invocation remains required;
- `<skill>-unavailable`: the required provider cannot run;
- `<skill>-blocked`: action authorization, state, prerequisite, or integrity stopped it.

`<skill>-handoff` means the required provider still needs explicit user
invocation; the suffix itself is unchanged. After a successful fallback, report
the host-native activity and omit the unavailable provider. Availability or
status checks, invocation instructions, and unexecuted selections do not count
as execution. Provider-defined TDD and Code Review remain represented by
`implement` unless separately selected. The ASCII `->` separator is valid when
Unicode is unavailable.

The marker is instruction-level observability, not proof of execution. Never
reroute, load skills, execute work, explain rejected routes, or write state only
to produce it.
