---
description: Break a plan, spec, or the current conversation into a set of tracer-bullet tickets, each declaring its blocking edges.
name: to-tickets
---
# To Tickets

Break a plan, spec, or conversation into a set of **tickets** — tracer-bullet vertical slices, each declaring the tickets that **block** it.

Use a publication destination named by the user or documented by the project.
Publish only when the current request or accepted project policy authorizes it; otherwise return the complete ticket drafts in chat.
Do not invent a local destination, label, or status.

## Process

### 1. Gather context

Work from whatever is already in the conversation context.
If the user passes a reference (a spec path, an issue number or URL) as an argument, fetch it and read its full body and comments.

### 2. Explore the codebase (optional)

If you have not already explored the codebase, do so to understand the current state of the code.
Ticket titles and descriptions should use the project's domain glossary vocabulary, and respect ADRs in the area you're touching.

Consider prefactoring only when current code and the proposed change establish a concrete need.
Do not invent preparatory work merely to fill out the ticket sequence.

### 3. Draft vertical slices

Break the work into **tracer bullet** tickets.

<vertical-slice-rules>

- Each slice cuts a narrow but complete path through the layers applicable to its behavior, such as schema, API, UI, or tests
- A completed slice is demoable or verifiable on its own
- Each slice is sized to fit in a single fresh context window
- Order justified prefactoring before only the work that requires it

</vertical-slice-rules>

Give each ticket its **blocking edges** — the other tickets that must complete before it can start.
Include an edge only when that ticket supplies a real prerequisite.
State known external prerequisites separately, such as a required decision, access, or an external result; mark any material unassessed prerequisite honestly.
No ticket blockers means only that no other ticket gates the work.
Execution still requires applicable external prerequisites and action authorization; drafting or approving tickets supplies neither by itself.

**Wide refactors are the exception to vertical slicing.**
A **wide refactor** is one mechanical change — rename a column, retype a shared symbol — whose **blast radius** fans across the whole codebase, so a single edit breaks thousands of call sites at once and no vertical slice can land green.
Use a bounded atomic change when all affected callers can change and be verified together safely.
Use **expand–contract** when compatibility obligations or independent transitions require old and new forms to coexist.
In that case, first expand by adding the new form beside the old, then migrate callers in independently verifiable batches, then contract once no required caller needs the old form.
Declare only the blocking edges that this transition actually requires.
Do not invent migration machinery, compatibility obligations, or an integration branch from the fact that a refactor is wide.

### 4. Quiz the user

Present the proposed breakdown as a numbered list.
For each ticket, show:

- **Title**: short descriptive name
- **Blocked by**: which other tickets (if any) must complete first
- **Other prerequisites**: known external requirements and any material uncertainty about them
- **What it delivers**: the end-to-end behaviour this ticket makes work

Ask the user:

- Does the granularity feel right?
  (too coarse / too fine)
- Are the blocking edges correct — does each ticket only depend on tickets that genuinely gate it?
- Should any tickets be merged or split further?

Iterate until the user approves the breakdown.

### 5. Publish the tickets

When the publication boundary above permits it, publish the approved tickets to the named or documented destination.
Preserve blocking edges in the form that destination supports:

- **A project-documented local tracker** → follow its paths and format and declare blocking edges using its identifiers.
- **A real issue tracker (GitHub, Linear, …)** → publish one issue per ticket in dependency order (blockers first) so each ticket's blocking edges can reference real identifiers.
  Use the platform's native blocking or sub-issue relationship where it has one; otherwise set each ticket's "Blocked by" to the blocking issues.

Publish in dependency order; for a purely linear chain that means top to bottom.
Publishing the tickets does not start their implementation or authorize other tracker changes.

Do NOT close or modify any parent issue.

<local-ticket-template>

# <NN> — <Ticket title>

**What to build:** the end-to-end behaviour this ticket makes work, from the user's perspective — not a layer-by-layer implementation list.

**Blocked by:** the numbers/titles of the tickets that gate this one, or "None — no ticket dependencies".

**Other prerequisites:** known external requirements and material unassessed conditions, or "None identified" when assessed.

- [ ] Acceptance criterion 1
- [ ] Acceptance criterion 2

</local-ticket-template>

<issue-template>

## Parent

A reference to the parent issue on the tracker (if the source was an existing issue, otherwise omit this section).

## What to build

The end-to-end behaviour this ticket makes work, from the user's perspective — not layer-by-layer implementation.

## Acceptance criteria

- [ ] Criterion 1
- [ ] Criterion 2

## Blocked by

- A reference to each blocking ticket, or "None — no ticket dependencies".

## Other prerequisites

Known external requirements and material unassessed conditions, or "None identified" when assessed.

</issue-template>

In either form, avoid specific file paths or code snippets — they go stale fast.
Exception: if a prototype produced a snippet that encodes a decision more precisely than prose can (state machine, reducer, schema, type shape), inline it and note briefly that it came from a prototype.
Trim to the decision-rich parts — not a working demo, just the important bits.
