# Agent Workflow Language

## Wayfinder coordination

**Wayfinder effort**:
One resumable body of coordination with one stable objective and scope.

**Map**:
The brief coordination summary for a Wayfinder effort and the first effort file
read when resuming it.

**Objective**:
The result a Wayfinder effort is intended to achieve.

**Scope**:
What a Wayfinder effort includes and excludes, including relevant project or
authority limits.

**Consequential**:
A matter is consequential when handling it differently could change the effort's
objective, scope, required authority, lasting result, dependencies, or which
work may proceed.

**Current coordination state**:
The information that remains relevant to coordinating a Wayfinder effort now.

**Ready work**:
Work to which no blocker currently applies.

**Dependency**:
Something particular work requires from an action, artifact, decision, person,
system, external result, or other input.

**Blocker**:
A condition that currently prevents particular work from proceeding. An
unsatisfied dependency, unresolved consequential uncertainty, or missing
required authority can be a blocker for affected work. Blocking is scoped to
that work and is not a separate Wayfinder record type.

## Wayfinder records and project decisions

**U# (unresolved question record)**:
A durable record of one current consequential question that remains unanswered
and is independently useful to preserve. The record is not itself a blocker;
the unresolved condition may block particular work.

**F# (fact record)**:
A durable record of one current scoped descriptive conclusion judged
sufficiently supported. It remains revisable as evidence changes.

**Project decision authority**:
The person, role, or valid delegate whose choice the project treats as binding
within a defined decision boundary. Accepted project policy may determine the
choice for that boundary directly or establish who holds that authority; this
does not restrict technical judgment already delegated by the user or policy.

## Current-state operations

**Reconciliation**:
Updating affected current coordination state to reflect current truth and project
choices determined by accepted project policy or committed by project decision
authority, including changes in relevant source or the accepted project record
designated to maintain the result.

**Pruning**:
Pruning removes a recognized Wayfinder record from current coordination after
useful results are preserved and affected references are reconciled. File or
ledger-section removal carries out pruning; ending an effort is separate.

## Ownership and persistence

**Framework-owned**:
Content or a delimited region under Agent Workflow's declared install, update,
and remove lifecycle. Framework ownership is separate from durability and
reconstructability.

**Project-owned**:
Content whose meaning and preservation belong to the consuming project rather
than Agent Workflow's lifecycle. Agent Workflow may reference or interpret a
recognized form without gaining lifecycle ownership.

**Durable**:
Intentionally retained across sessions or workflow transitions because it
remains useful for continuation. Durability is separate from lifecycle ownership
and reconstructability.

**Reconstructable**:
Reproducible from current declared source or package content without losing
unique project information.
