# Local Wayfinder state contract

Use this contract only when Wayfinder is selected, including a justified
mid-task escalation, or a request continues a relevant local Wayfinder effort.
The existence of an effort under `.agent-workflow-state/wayfinder/` is not a
routing signal. Clear, bounded, or unrelated work stays on its minimum useful
route and does not read or create Wayfinder state.

Upstream Wayfinder supplies the planning method: orient around a destination,
keep the map low resolution, represent fog honestly, resolve consequential
uncertainty incrementally, and zoom into detail only when needed. Agentic
Workflow supplies the canonical Git-native representation below. It is durable
project knowledge and coordination state, not an issue tracker and not a mirror
of `.scratch/` or an external tracker.
Do not create or update `.agent-workflow-state/active.md`; the effort map is the
only re-entry point.

## Responsibility boundary

Wayfinder may preserve four kinds of durable knowledge:

- `unknown`: an unresolved question that materially affects the destination;
- `evidence`: an observation, measurement, report, or source finding, including
  its provenance, scope, and limitations;
- `fact`: a sufficiently established descriptive conclusion, scoped to the
  evidence available now; and
- `decision`: a committed choice made under the project's authority.

These are distinctions, not a mandatory pipeline. Evidence may leave an
unknown unresolved, a fact may require no decision, and a decision may be made
under uncertainty without manufacturing a fact.

`map.md` owns the current state, blockers, dependencies, and next work. It is
the effort's coordination and re-entry point. Keep enough information there for
a fresh session to choose the next relevant detail without loading every child.

When ready work becomes substantial enough to need dependency ordering or
independently deliverable sessions, hand it to `to-tickets`. That workflow owns
its native ticket artifacts and frontier. Wayfinder links the resulting native
artifact from `map.md`; it does not create a shadow T# copy. Work that fits one
coherent implementation session can pass directly from the map, a settled D#,
or another accepted specification to implementation.

## Ownership and locations

All paths below are project-owned durable data:

```text
.agent-workflow-state/
└── wayfinder/
    └── <effort>/
        ├── map.md
        ├── unknowns/       # optional U# files
        ├── evidence/       # optional E# files
        ├── facts/          # optional F# files
        └── decisions/      # optional D# files
```

`map.md` alone is a complete and valid Wayfinder effort. Create each child
directory lazily with its first item, and create an item only when preserving it
independently has real value. Short-lived observations, obvious repository
facts, and one-line conclusions normally stay as concise map notes or links.
Do not turn every source read or test run into an E# and do not extract every
stable sentence into an F#.

Create an effort only when repository writes are authorized and structured
durable notes materially reduce the risk of losing or conflating important
state. A read-only analysis, audit, diagnosis, review, `do not change files`
instruction, or equivalent restriction never authorizes a Wayfinder state
write.

Install, update, status, remove, and reinstall never seed, inventory, checksum,
validate, migrate, rewrite, or remove Wayfinder state. The effort directory is a
short stable slug. Do not silently merge two efforts, rename one another session
may reference, or reuse an old effort for a different destination.

## Progressive loading

1. Route from the request first. Do not scan Wayfinder state for confidently
   direct or unrelated work.
2. When the request names an effort, use that exact safe repository-relative
   path. For a likely resume without an exact path, list effort directory names
   and read only the smallest set of maps needed to identify the effort.
3. Read the relevant `map.md` as the low-resolution orientation.
4. Follow only links needed for the current question or work. Do not read every
   U/E/F/D child.
5. Derive the current frontier from the map and any linked native ticket source;
   do not persist a second frontier or global active index.

An implementation request may consume a coherent next-work scope from the map,
a settled decision or specification, or a native ticket without rerunning
Wayfinder. A new unknown returns work to Wayfinder only when it
materially obscures the destination; ordinary implementation detail stays in
implementation.

## Identifiers and links

Use stable, per-type positive identifiers within an effort: `U#`, `E#`, `F#`,
and `D#`. Assign one greater than the highest existing ID of that type. Never
reuse or renumber an ID when its title, slug, status, or interpretation changes.

Use repository-relative Markdown links and readable titles. Facts must link the
evidence artifacts or direct authoritative sources that justify them. Evidence
may optionally name facts it supports or contradicts, but reciprocal backlinks
are not required; requiring both directions creates synchronization work without
improving provenance. Decisions should link the facts, evidence, unknowns, ADRs,
or policies that materially constrained the choice.

Git is the history mechanism. Do not add an event log, revision files, a graph
index, or another versioning scheme.

Before writing, reread the target and map. Never overwrite a newly appeared ID.
If concurrent edits disagree, preserve both claims and reconcile explicitly
rather than choosing silently.

## The low-resolution map

Use these headings as a compact authoring default, not a strict schema. Preserve
clear existing human content instead of normalizing it for ceremony.

```markdown
# <Effort name>

## Destination

<What it means for the route to be clear.>

## Current state

<Concise established state and links to independently useful U/E/F/D detail.>

## Blockers and dependencies

<What prevents progress, what depends on what, and any recovery condition.>

## Next work

<The smallest coherent next action or linked native ticket frontier.>

## Notes

<Standing constraints and useful canonical links.>

## Decisions so far

- D1 — Title (`decisions/D1-title.md`) — one-line gist

## Not yet specified

<In-scope fog not yet sharp enough to state as a U#.>

## Out of scope

<Explicit boundaries beyond this destination.>
```

The map may summarize small facts and evidence inline. Promote detail to a child
only when it is likely to be reused, disputed, independently revised, too large
for low-resolution orientation, or important enough to require provenance.
Prioritize one coherent next action; list parallel work only when the dependency
structure makes it genuinely useful. If work has been decomposed by
`to-tickets`, link its canonical frontier rather than restating every ticket.

A precise material question belongs in U#; vague fog stays under `Not yet
specified` until it can be asked sharply. Out-of-scope work does not become next
work unless the destination is deliberately redrawn.

## Optional child files

These are permissive authoring shapes, not lifecycle schemas. Omit inapplicable
fields and rename headings when clarity improves.

Use U# when a question is consequential enough to track independently:

```markdown
# U1: <Question>

- Status: open | resolved
- Resolution mode: research | prototype | debugging | human clarification | direct
- Blocked by: none
- Related: none

## Why it matters

<How the answer changes the destination, a decision, or next work.>

## Evidence and resolution

<Concise findings or links; when resolved, state the answer and resulting links.>
```

Use E# when an observation needs durable provenance, scope, limitations, or
independent reuse:

```markdown
# E1: <Observation or finding>

- Observed: YYYY-MM-DD
- Source: <repository-relative link, command/result, or cited primary source>
- Scope: <where this evidence applies>
- Related: U1, F1

## Finding

<What was observed, without promoting it beyond what the source establishes.>

## Limitations

<Important uncertainty, sampling limits, or conflicting evidence.>
```

Use F# when a descriptive conclusion is established enough to rely on across
sessions and retaining its evidence chain matters:

```markdown
# F1: <Established conclusion>

- Status: current | disputed | stale
- Scope: <where and when the conclusion applies>
- Supported by: E1, <or direct authoritative source>
- Contradicted by: none

## Fact

<The scoped conclusion.>

## Change note

<Only when revised: what changed and why.>
```

Use D# for a committed choice, not for a descriptive conclusion:

```markdown
# D1: <Choice>

- Status: accepted | superseded
- Authority: <user, accepted policy, or canonical ADR>
- Related: U1, F1

## Decision

<The choice now in force.>

## Why and consequences

<Decisive context, tradeoffs, and important constraints.>

## Change note

<Only when changed: what changed and why.>
```

A resolved U# need not create F# or D#. An E# need not create F#. A routine
source read, transient command output, or fact obvious from current source does
not deserve an E#. A conclusion used only to orient the current session does not
deserve an F#. A preference, proposal, or agent assumption is not an accepted
D# unless the user or project policy grants the necessary authority.

## Contradictions and revision

Live source and current observed behavior outrank stale Wayfinder summaries.
When newer or stronger evidence conflicts with a fact:

1. preserve the conflicting evidence and its provenance;
2. if the conflict is unresolved, mark the F# `disputed`, open or reopen the
   relevant U#, and surface the blocker in the map;
3. if resolved, update the same F# with its current scope, supporting and
   contradicting links, plus one concise change note; and
4. review dependent decisions and next work, but do not silently change a
   decision merely because its factual basis changed.

Use `stale` when a fact's scope or evidence no longer supports present use but
the replacement conclusion is not yet established. A newer decision that is
silent about a fact does not supersede that fact. A changed decision updates the
same D# or points to the canonical superseding ADR; Git retains history.

## Scoped reconciliation at completion

During authorized mutating work, an existing effort is relevant when the
request or progressively loaded context connects the work to it. If work
materially changes a represented fact, decision, dependency, status, result, or
next action, reconcile the affected map and only the directly affected children
before claiming completion. This needs no separate request.

Do not globally scan for related efforts. Compare the selected state with
authoritative source, ADRs, documentation, tests, and results. Update concise
coordination consequences and links; do not copy canonical artifact bodies,
normalize unchanged files, or resolve unrelated questions. Read-only work
reports the exact stale claim and authoritative evidence without writing.

If conflicting edits or insufficient evidence prevent truthful reconciliation,
preserve state, report the blocker, and do not claim the affected work fully
complete. No hook, daemon, synchronization service, or lifecycle machinery is
implied; the acting agent performs this bounded reconciliation.

## Workflow and ticket boundaries

Research, Prototype, Debugging, Grilling, Domain Modeling, or human clarification
may supply evidence while Wayfinder retains durable coordination. Their native
artifacts stay canonical and are linked rather than copied.

Use `to-tickets` only when clear work benefits from dependency ordering or
separately deliverable sessions. Pass the map and only relevant U/E/F/D context.
The configured tracker or local-ticket convention owns the resulting artifacts;
Wayfinder records only the current pointer and coordination consequence.

Older `tickets/T#` artifacts are outside this contract. Lifecycle operations
preserve them as opaque project data but do not load, validate, or migrate them.
Before resuming such an effort, manually move its current state, blockers,
dependencies, and smallest coherent next action into `map.md`; use `to-tickets`
only if the remaining work still needs decomposition. Old T# files may then be
kept as history or removed by the project owner.

No Jira synchronization, automatic archival, schema migration, database, graph
engine, or validation service belongs in this contract.
