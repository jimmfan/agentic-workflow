# Local Wayfinder state contract

Use this contract only when Wayfinder is selected, including a justified
mid-task escalation, or a request continues a relevant local Wayfinder effort.
The existence of any effort under
`.ai-workflow-state/wayfinder/` is not itself a routing signal. Clear, bounded,
or unrelated work stays on its minimum useful route and does not read or create
Wayfinder state.

Upstream Wayfinder supplies the planning method: orient around a destination,
keep the map low resolution, represent fog honestly, resolve consequential
uncertainty incrementally, and zoom into detail only when needed. Agentic
Workflow supplies an authoritative local-mode adapter plus the configured
Git-native representation below. This representation is canonical local
Wayfinder data, not a framework mirror of an issue tracker.
Do not create a second copy under `.scratch/`, another planning directory, or an
external tracker. Do not create or update `.ai-workflow-state/active.md` for a
Wayfinder effort.

## Ownership and locations

All paths below are project-owned durable data:

```text
.ai-workflow-state/
└── wayfinder/
    └── <effort>/
        ├── map.md
        ├── unknowns/
        │   └── U1-<slug>.md
        ├── decisions/
        │   └── D1-<slug>.md
        └── tickets/
            └── T1-<slug>.md
```

Create an effort only when repository writes are authorized and structured
durable notes materially reduce the risk of losing or conflating important
state. Ordinary authorized project work may create or update this selected
workflow's project-owned state without a second request for permission. A
read-only analysis, audit, diagnosis, review, `do not change files` instruction,
or equivalent restriction never authorizes a Wayfinder state write.

A task need not already be multi-session. Create child directories lazily with
their first item; Git does not preserve empty directories. Install, update,
status, remove, and reinstall never seed, inventory, checksum, validate,
migrate, rewrite, or remove this state.

The effort directory name is a short stable slug. Do not silently merge two
efforts, rename an effort that another session may reference, or reuse an old
effort directory for a different destination.

## Progressive loading

1. Route from the request first. Do not scan Wayfinder state for confidently
   direct or unrelated work.
2. When the request names an effort, use that exact safe repository-relative
   path. For a likely resume without an exact path, list effort directory names
   and read only the smallest set of `map.md` files needed to identify the
   relevant effort. If relevance remains ambiguous, ask rather than combining
   efforts.
3. Read the relevant `map.md` as the low-resolution session orientation.
4. Follow its links and the user's target to load only the U/D/T files needed
   for the current question or executable work. Do not read every child file.
5. When choosing frontier work, inspect filenames plus concise status and
   dependency lines across plausible candidates; load a full child body only
   after it is relevant. Derive the frontier from current item state and
   dependencies rather than persisting a separate frontier file.

An implementation request may consume a relevant map, decision, and ticket
without rerunning Wayfinder. A new unknown discovered during implementation may
return the effort to Wayfinder only when it materially obscures the destination;
ordinary implementation detail stays in the implementation route.

## Identifiers and relationships

- `U#` is an unresolved question that materially affects the destination.
- `D#` is a durable project decision.
- `T#` is concrete executable work.
- An upstream decision, investigation, research, prototype, grilling, or human
  clarification ticket normally becomes a U# with an appropriate resolution
  mode. An upstream `task` ticket becomes a T# only when it is genuinely
  executable work, often linked to the U# it unblocks.
- Resolving a U# updates its evidence, resolution, and status. Create or update
  a D# only when the result is a durable project decision. Create a T# only when
  a concrete executable outcome exists and decomposition adds value. Never
  force every U# to produce a D# or every D# to produce a T#.
- Assign the next unused positive number for that type within the effort. Never
  reuse an ID, and never change it when a title or slug changes.
- Use repository-relative Markdown links and concise `Related` or `Blocked by`
  lines for many-to-many relationships. Refer to an item with both its stable ID
  and readable title, for example `D2 — Keep compact JSON` linked to
  `decisions/D2-compact-json.md`.
- Git is the history mechanism. Do not add an event log, revision files, or a
  second versioning scheme.

Before writing, reread the target file and the relevant map. Never overwrite a
newly appeared ID. If concurrent edits disagree, preserve both sets of evidence
and reconcile the Markdown explicitly rather than choosing silently.

## The low-resolution map

`map.md` is an index and orientation aid, not the store for detailed reasoning.
Keep these Wayfinder headings, adding only concise links and gists:

```markdown
# <Effort name>

## Destination

<One or two lines describing what it means for the route to be clear.>

## Notes

<Standing constraints, relevant U#/D#/T links, and useful skills or evidence.>

## Decisions so far

- D1 — <title> (`decisions/D1-<slug>.md`) — <one-line gist; make the title a link>

## Not yet specified

<Fog of war that is in scope but not yet sharp enough to state as a U#.>

## Out of scope

<Explicit boundaries beyond this destination.>
```

Keep a new map lightweight. Its initial Notes may contain only concise known
facts, unknowns, blockers, assumptions, and work that can proceed, while empty
or still-foggy sections remain short. Add U#/D#/T# children only when a sharp
question, durable decision, or executable outcome actually exists; the map
grows with the problem rather than anticipating ceremony.

Link details instead of restating them. A precise material question belongs in
an unknown file, not in `Not yet specified`; fog stays on the map until the
question can be stated sharply. Out-of-scope work does not graduate into the
frontier unless the destination is deliberately redrawn.

## Child files

These are authoring shapes, not lifecycle schemas. Omit inapplicable fields,
rename headings when clarity improves, and use readable existing human content
rather than rejecting a file for format differences.

An unknown records the question, useful evidence, and how it may be resolved:

```markdown
# U1: <Question title>

- Status: open | resolved
- Resolution mode: research | prototype | grilling | human clarification | direct
- Blocked by: none
- Related: none

## Question

<The precise uncertainty and why it materially affects the destination.>

## Evidence

<Concise findings or links; do not paste research transcripts.>

## Resolution

<Leave open until resolved; link any resulting D# or explain why none is needed.>
```

A decision records the durable choice and its consequences:

```markdown
# D1: <Decision title>

- Related: U1, T1

## Decision

<The current decision.>

## Why

<Concise rationale and decisive evidence.>

## Consequences

<Important effects and constraints.>

## Change note

<Only when changed: what changed and why. Git retains the full history.>
```

When a decision changes, update the same D# and add one brief change note. Do
not create a competing D# merely to version the old answer. A resolved U# may
link no D# when the answer is a fact, eliminates a path, or otherwise creates no
durable choice worth preserving.

A ticket records one concrete executable outcome after the route is sufficiently
clear:

```markdown
# T1: <Executable outcome>

- Status: ready | blocked | in-progress | done
- Blocked by: none
- Related: D1

## Outcome

<The end-to-end behavior or result to deliver.>

## Acceptance

- <Observable completion criterion>
```

## Workflow boundaries

The usual direction is `uncertainty -> U# -> evidence -> D# -> to-tickets ->
T# -> implementation`, but it is not a rigid pipeline. One unknown may inform
many decisions, a decision may need no ticket, and an unknown may resolve
without creating a decision. Research, prototype, debugging, grilling, or human
clarification may supply evidence without taking ownership of the map.

Wayfinder owns durable coordination, not an execution monopoly. A task may
escalate from Debugging, Discovery, or another useful workflow into Wayfinder
state while that specialized capability continues to resolve the relevant U#.
Research and Prototype may create their own native evidence artifacts, but they
link back rather than becoming a competing map. Implementation may consume a
settled D# or T# without reopening the whole effort.

Use Grilling and Domain Modeling while charting only when the destination,
human preferences, domain language, or ownership boundaries genuinely require
them. Grilling is human-in-the-loop and never answers for the user. Do not run
either capability ceremonially for a clear mid-task escalation, a straightforward
resume, or to make an evaluation observe a skill invocation.

Use `to-tickets` when clear work benefits from dependency-ordered or separately
deliverable sessions. For this configured local representation, its canonical
output is T# files under the effort; do not also publish `.scratch/` tickets.
Pass only the map and relevant U#/D# context into ticketing. Implementation
loads the selected T# and only the decisions or unknowns that constrain it.

No Jira, external synchronization, automatic archival, schema migration,
database, graph engine, or validation service belongs in this contract. A T#
may contain a normal link to an external issue in the future, but the link does
not change ownership or authorize external access or mutation.
