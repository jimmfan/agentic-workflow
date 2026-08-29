# Detailed routing policy

The root policy performs first-pass routing. Read this policy only for
ambiguous ownership, material provider fallback or handoff, or unclear durable
re-entry. Direct work, one obvious workflow, and one obvious specialist inside
Wayfinder do not load it. Root authorization, preservation, and reporting rules
remain binding.

## Decide and compose

Choose the minimum useful process justified by intent, uncertainty, impact,
reversibility, and expected duration. File count and skill availability do not
select a workflow.

1. Select one dominant workflow or activity.
2. Add only capabilities that materially help it.
3. Confirm the host can invoke each selected provider operation.
4. Execute only authorized actions.

Installed skill descriptions are the first selection interface. Before making
or acting on a consequential choice, resolve any material unresolved
prerequisite using the minimum sufficient method. This table resolves overlaps:

| Signal | Selection | Boundary |
|---|---|---|
| Explicit compatible skill request | Named skill | Honor unless authorization, safety, or compatibility blocks it |
| Sustained learning intent | `teach` | Ordinary questions stay Direct |
| Durable coordination threshold crossed | `wayfinder` | Structured project state must materially improve continuity |
| Consequential bounded choice | Direct or Discovery | Load Discovery only when alternative and tradeoff analysis helps |
| Interdependent human/project-owned decisions materially shape downstream choices | Direct or `grilling` | Use Grilling to resolve their unresolved prerequisites; factual unknowns and one straightforward clarification use the minimum sufficient method |
| Domain concepts, vocabulary, boundaries, responsibilities, or relationships need active clarification | Direct or Domain Modeling | Load Domain Modeling only when changing or reorganizing the model materially helps; ordinary vocabulary lookup stays Direct |
| Throwaway implementation would answer a design or behavior question | Direct or `prototype` | Ordinary production implementation stays Direct or with its dominant workflow |
| Module interface, seam, depth, locality, or testability needs explicit design | Direct or `codebase-design` | Load Codebase Design only when its vocabulary materially improves the design; ordinary edits and refactors stay Direct or with their dominant workflow |
| Unexplained failure or regression | Direct or Debugging | Load Debugging only when causal investigation helps; diagnosis does not authorize a fix |
| External uncertainty needing primary sources | Direct or `research` | Simple lookups stay Direct |
| Settled scope needs a specification | `to-spec` | Its artifact remains canonical |
| Approved work needs ordered independent sessions | `to-tickets` | Its tickets and frontier remain canonical |
| One coherent ready implementation | Implementation, then `implement` | Trivial low-risk edits stay Direct; meaningful work ends with Verification |
| Explicit bounded test-first work | `tdd` | The provider owns its loop |
| Completion audit or meaningful finished change | Verification | Add only uncovered acceptance or integration evidence |
| Standalone fixed-point review | `code-review` | Do not repeat a review completed by `implement` |
| Clear bounded low-risk request | Direct | Skip workflow ceremony |

Normal intent may select an implicitly invocable provider. Exact skill syntax is
needed only for explicit invocation or a user-only operation. A supporting
capability does not become the dominant workflow or create durable state.

## Re-evaluate and resume

Re-evaluate when evidence changes uncertainty, scope, coordination, failure
mode, or authorization. Apply the root Wayfinder threshold; counts trigger
assessment, never selection. Explicit Wayfinder use and opt-out remain authoritative.

Resume only relevant work. An exact Wayfinder map or provider-native artifact
selects that re-entry point. For an unnamed likely Wayfinder resume, inspect the
smallest plausible effort set and resume only one clear destination-and-boundary
match. A safe regular map identifies current resumable coordination; a mapless
directory is not a candidate. An unrelated map never captures the route.

After selecting Wayfinder, read `contracts/wayfinder-state.md`, then the map and
only relevant F#/D# ledger sections or U#/E# artifacts. Implementation may
consume a coherent map scope, settled D#, specification, or native ticket
without rerunning Wayfinder.

Avoid routing loops: a bounded decision remains in Discovery unless it crosses
the Wayfinder threshold; a selected Wayfinder frontier may use Discovery once
without changing durable ownership. The same rule applies to Debugging and
other specialists. Meaningful Implementation runs Verification once. New causal
uncertainty returns to Debugging; a material unresolved choice returns to
Discovery or Wayfinder according to the coordination threshold.

Discovery owns bounded consequential choice and tradeoff analysis. Compose
Domain Modeling when structural ambiguity materially affects that analysis or
reorganizing the domain would materially improve it; otherwise Discovery runs
alone.

## Resolve providers

Resolve only selected provider operations through
`.agent-workflow/providers.json`:

- `implicit`: a compatible host may invoke it normally;
- `user-only`: require the declared explicit prefix;
- `unavailable`: do not claim it ran.

Selection is not execution. If a preferred provider cannot run, use authorized
host-native capability when it can satisfy the request. Do not imitate the
provider or create its native artifacts. Stop or give the exact handoff only
when the user required that provider or no safe authorized fallback exists.

For a user-only operation, form the invocation from the active host's declared
prefix. If the host is unknown, label supported forms instead of guessing.
Check configuration only after selecting an operation that declares it. Never
run setup automatically or inspect setup for an unrelated route.

## Preserve ownership and handoffs

Providers own their methods, terminology, evidence, and native artifacts.
Wayfinder is the sole framework-owned durable coordinator and stores only
consequential state and pointers. Native specifications, tickets, research,
maps, learning workspaces, reviews, and provider identifiers remain canonical
where created.

The Implementation adapter supplies accepted scope, canonical artifacts, and
acceptance criteria. Invoked `implement` owns its build loop, TDD, and closing
Code Review. Framework Verification runs afterward and adds only uncovered
evidence. No specialist creates a separate framework continuity record.

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
- `<skill>-blocked`: authorization, state, prerequisite, or integrity stopped it.

After a successful fallback, report the host-native activity and omit the
unavailable provider. Availability checks, handoffs, and unexecuted selections
do not count as execution. Provider-owned TDD and Code Review remain represented
by `implement` unless separately selected. The ASCII `->` separator is valid
when Unicode is unavailable.

The marker is instruction-level observability, not proof of execution. Never
reroute, load skills, execute work, explain rejected routes, or write state only
to produce it.
