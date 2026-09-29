# Agent Workflow Language

## Routing

**Direct**:
The default route, in which the agent handles a request with its own reasoning and tools rather than a primary workflow.
It may still add supporting capabilities, such as a skill, that materially help.

## Wayfinder coordination

**Wayfinder**:
Agent Workflow's durable coordination method: selecting, resuming, maintaining, and ending efforts through its skill and state contract.
Reading an effort's files for context is not using Wayfinder.

**Wayfinder effort**:
One resumable body of coordination with one objective and scope.
Its effort state lives under `.project-efforts/<effort>/`; the filesystem name describes ownership without introducing another domain concept.

**Effort state**:
The project-owned files under `.project-efforts/<effort>/` that store a Wayfinder effort's current coordination state: its map and any U/E/F/D records.

**Map**:
The brief coordination summary for a Wayfinder effort and the first effort file read when resuming it.

**Objective**:
The result a Wayfinder effort is intended to achieve.

**Scope**:
What a Wayfinder effort includes and excludes, including relevant project or authority limits.
It may be clarified, narrowed, or elaborated without creating a new effort while the objective and substantive scope remain the same.

**Consequential**:
A matter is consequential when handling it differently could change the effort's objective, scope, required authority, lasting result, dependencies, or which work may proceed.

**Current coordination state**:
The information that remains relevant to coordinating a Wayfinder effort now.

**Ready work**:
Work to which no blocker currently applies.

**Dependency**:
Something particular work requires from an action, artifact, decision, person, system, external result, or other input.

**Blocker**:
A condition that currently prevents particular work from proceeding.
An unsatisfied dependency, unresolved consequential uncertainty, or missing required authority can be a blocker for affected work.
Blocking is scoped to that work and is not a separate effort record type.

## Effort records and project decisions

**U# (unresolved question record)**:
A durable record of one current consequential question that remains unanswered and is independently useful to preserve.
The record is not itself a blocker; the unresolved condition may block particular work.

**E# (evidence record)**:
A durable record of one consequential observation, with its source, scope, and limitations, that is independently useful to preserve.
Recording it does not make the observation established project truth.

**F# (fact record)**:
A durable record of one current scoped descriptive conclusion judged sufficiently supported.
It remains revisable as evidence changes.

**D# (decision record)**:
A durable record of one current consequential project choice committed for its boundary, with the authority or accepted project policy that makes it binding.
Recording the choice does not create that authority.

**Project decision authority**:
The person, role, or valid delegate whose choice the project treats as binding within a defined decision boundary.
Accepted project policy may determine the choice for that boundary directly or establish who holds that authority; this does not restrict technical judgment already delegated by the user or policy.

**Committed project choice**:
A consequential project choice becomes committed when required evidence is sufficient and either accepted project policy determines it for its boundary or the person, role, or valid delegate with project decision authority for that boundary commits it.
Assumptions, defaults, proposals, precedents, and model preferences do not commit a choice, and commitment does not by itself authorize acting on it.

## Current-state operations

**Reconciliation**:
Updating affected current coordination state so it agrees with current truth, project choices determined by accepted project policy or committed by project decision authority, and the designated artifacts that maintain lasting results.

**Effort maintenance**:
Creating, updating, pruning, or ending a selected Wayfinder effort's state under the state contract.
It writes project-owned files and requires action authorization like any other write; reconciliation is the procedure it follows.

**Pruning**:
Pruning removes a recognized effort record from current coordination after useful results are preserved and affected references are reconciled.
File or ledger-section removal carries out pruning; ending an effort is separate.

## Requests and authorization

**Action authorization**:
Permission to perform a specific action within a stated scope, supplied only by the current user request or accepted project policy.
It is separate from project decision authority: authorizing an action does not commit a project choice.

**Accepted project policy**:
Rules the project has accepted as binding for a stated boundary, such as project-authored agent instructions or accepted architecture decision records.
A rule that appears only in a skill, specification, ticket, or effort record is not accepted project policy.

**Read-only request**:
A request in which the user asks for no changes.
A limit that allows only reads on one target, such as an external system, does not make a request read-only for other targets.

## Ownership and persistence

**Framework-owned**:
Content or a delimited region under Agent Workflow's declared install, update, and remove lifecycle.
Framework ownership is separate from durability and reconstructability.

**Project-owned**:
Content whose meaning and preservation belong to the consuming project rather than Agent Workflow's lifecycle.
Agent Workflow may reference or interpret a recognized form without gaining lifecycle ownership.

**Durable**:
Intentionally retained across sessions or workflow transitions because it remains useful for continuation.
Durability is separate from lifecycle ownership and reconstructability.

**Reconstructable**:
Reproducible from current declared source or package content without losing unique project information.

**Maintaining artifact**:
The project artifact or record designated to keep a lasting result current, such as a specification, architecture decision record, ticket set, or product documentation.
