# Wayfinder

Wayfinder is Agent Workflow's sole durable coordination layer. Use it when
consequential state needs reliable continuity across session continuations,
agent handoffs, responsible participants, or interacting areas. Clear bounded work, one isolated
unresolved question, and read-only work stay on their minimum useful route.

This framework-owned runtime projection is derived from Matt Pocock's
Wayfinder methodology. It helps orient the effort, choose the minimum resolution
method, and identify ready work;
`.agent-workflow/contracts/wayfinder-state.md` defines state mechanics.

## Operating rules

- Route before inspecting state; an existing map never selects Wayfinder.
- Selection may conclude that no consequential continuity earns persistence;
  in that case create no effort, map, or supporting record.
- Establish the objective and scope, then enough relevant areas and relationships
  to orient the effort before substantial decomposition. Keep `map.md` brief,
  preserve enough information to resume safely, and load detail only when
  relevant. Apply the contract's default map shape when applicable; omit empty
  headings, allow a clearer equivalent, and never copy project artifacts that
  maintain plans.
- The map summarizes the effort's current coordination state, conditions blocking particular work,
  dependencies, and ready work.
  Optional F/D ledger sections and U/E artifacts are records that preserve only
  useful current conclusions, choices, unresolved questions, and evidence.
- Create a separate artifact because it is an independently useful coordination
  or retrieval unit, not merely because it belongs to a semantic category.
- Live source and accepted project artifacts outrank unsupported or outdated
  map claims.
- Inspect Git/session state when useful for safe execution, but do not normally
  persist volatile observations. Retain durable Git constraints and
  dependencies under the state contract.
- Durable Wayfinder state can record authority; it cannot create authority.
  Use the person, role, valid delegate, or accepted policy that holds project
  decision authority for a committed choice. Evidence-backed technical judgment
  within delegated scope remains valid. Keep the question and what it blocks
  explicit.

When selecting or resuming Wayfinder, read the state contract before effort state.
When resuming a Wayfinder effort, read `map.md` first among its effort files.
The state contract defines effort recognition and selection, paths and identifiers,
reconciliation, pruning, and effort ending. If the state contract is unavailable,
fail closed for the affected Wayfinder work: do not inspect or change a map; do not invent
substitute persistence or create tracker, specialist-record, or scratch state.
Report the incomplete installation.

## Establish areas and relationships

Reuse accepted project structure when it supplies a useful objective, scope,
areas, and important operating boundaries. Otherwise establish the smallest
useful structure directly. The effort's view of its areas, relationships, and
ownership or operating constraints is provisional, adaptive, and judgment-based.
It helps Wayfinder challenge incomplete framing and revise its understanding as
evidence develops. Exploration may broaden
understanding, but must not silently broaden the user's goal, delegated
authority, or implementation scope.

Domain Modeling is the preferred structural fallback when clarifying
or reorganizing concepts, vocabulary, boundaries, responsibilities, or
relationships would make the map clearer or more reliable;
progress need not already be blocked. When it would help, establish enough
areas and relationships before substantial U/E/F/D accumulates, then derive the
effort name and stable path from the objective and scope.

On resumption, do not reload Domain Modeling merely because Wayfinder resumed.
If later evidence from a source that establishes the relevant scoped claim shows
that the current areas and relationships no longer fit current truth, Domain
Modeling may be loaded again to revise the same map.
Reconcile the current structure rather than preserving unsupported or parallel
representations.

## Choose the minimum resolution method

Continue directly when no additional method is needed. Otherwise load only the
smallest specialist needed to resolve or accurately frame the current question,
uncertainty, unexplained cause, consequential choice, or structural ambiguity:

- **Discovery** for consequential alternatives and tradeoffs.
- **Debugging** for an observed behavior with an unknown cause.
- **Research** for external uncertainty needing primary-source evidence.
- **Prototype** when a disposable experiment is the cheapest honest test.
- **Domain Modeling** to establish, improve, or revise areas and relationships under the rule
  above.
- **Human clarification or Grilling** for authority, intent, preference, or
  prioritization.

Research resolves external uncertainty, Prototype answers a design question, and
Debugging investigates an unexplained cause within established areas and
relationships. They do not replace structural modeling when those areas or
relationships need improvement or revision.

The resolution method determines how a question, uncertainty, unexplained cause,
consequential choice, or structural ambiguity should be addressed and what
evidence or authority that method requires. It is not merely an artifact label:
human clarification requires the person with the relevant intent, preference,
or project decision authority; research requires appropriate source evidence;
and prototype or debugging requires relevant observed or experimental evidence.
Existing evidence from a source that establishes the scoped claim may satisfy
the method without a ceremonial specialist invocation, but one method cannot
substitute for another's required authority or evidence.

Do not load specialists speculatively. Specialists retain their methods and may
create provider-native artifacts or evidence. The specialist creates no Agent
Workflow durable coordination state. If work is interrupted,
reconcile only consequential questions, uncertainties, unexplained causes,
choices, structural ambiguity, conditions blocking particular work, evidence or
conclusions, artifact references, the resolution method when useful, and ready
work into Wayfinder. When resuming, read the map first rather than a specialist
notebook or coordination record.

## Reconcile and transition ready work

The map summarizes the objective, scope, current coordination state, conditions
blocking particular work, dependencies, and ready work. Keep it sufficient for
a fresh session to continue the effort. Reference the artifacts that maintain
lasting results instead of copying them. The state contract defines when U/E/F/D
records are worth retaining, how records are pruned, and when an effort ends.

Map uncertainty broadly, then preserve selectively. Record a precise question
as U# when separate preservation while unanswered is independently useful to a
later developer making or evaluating a decision. This applies within
the current objective and scope, especially when the answer
requires project decision authority, depends on an external participant or approval,
or gates multiple downstream areas or a consequential boundary. Ask the
substantive project question when project knowledge determines whether separate
preservation is useful; do not ask merely whether to create a U#. Keep
incidental or intentionally deferred detail under `Not yet specified` in the map.
Precision alone is insufficient. Ordinary external uncertainty, an unexplained cause, a long
list, or a template does not by itself justify a U#. A temporary U# is useful
only when separate preservation improves current coordination or later
continuation, not as create-and-prune ceremony.

When dependency evidence is sufficient, surface the navigation shape concisely:
the critical path, independent parallel work, and any off-path dependency whose
external lead time changes ordering or readiness. Do not infer a critical path
from an unordered backlog or incomplete evidence.

A blocker is a condition that currently prevents particular work from
proceeding. An unsatisfied dependency, unresolved consequential question, or
missing required project decision authority can be a blocker for affected work. Blocking is
scoped to affected work: the same condition may block one scope without blocking
another. An unresolved U# record contains a question and is not itself a blocker.
Delay, inconvenience, risk, or unfinished work alone does not make a condition a blocker.
Ready work is work to which no blocker currently applies. Independent ready work
may proceed while other work remains blocked.

Dependencies are satisfied by obtaining the action, artifact, decision,
participation from a person, system result, external result, or other input they
require. Questions and uncertainties are resolved through appropriate evidence
or their resolution method. Missing project decision authority is supplied by
the person, role, valid delegate, or accepted policy that holds it for the
decision boundary. Where the state contract permits it, project decision
authority may explicitly accept unresolved uncertainty for one named boundary.
For an unresolved consequential question, either resolve the question or record
that authority and acceptance in the project artifact recording the choice
committed by project decision authority. The acceptance leaves the U# current and unresolved, unblocks only that
named boundary, and does not grant broader authority, authorize another action,
or satisfy another dependency. The same uncertainty may remain a blocker for
other work. Satisfying a dependency or accepting unresolved uncertainty for one
boundary changes blocking only for affected work and does not automatically
unblock unrelated work. Reconcile and shrink the map, then transition one or
more ready implementation scopes to the Implementation workflow without
advancing work that remains dependency-blocked. Each workflow transition to
Implementation consumes one ready scope and its acceptance criteria;
Verification follows material execution. Use `to-tickets` only
when approved work needs substantial dependency ordering or independently
deliverable sessions. When no ticket artifact exists, the map may state ready
work directly. Once To Tickets creates a ticket artifact or ticket set, that
artifact maintains ticket contents, dependencies, ordering, and readiness. The
map links that artifact and does not mirror ticket-level state; it may include
the current ready-work reference.
