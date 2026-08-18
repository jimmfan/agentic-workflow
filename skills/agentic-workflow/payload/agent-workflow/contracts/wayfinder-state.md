# Local Wayfinder state contract

Use this contract only when Wayfinder is selected, including a justified
mid-task escalation, or a request continues a relevant local Wayfinder effort.
The existence of an effort under `.agent-workflow-state/wayfinder/` is not a
routing signal. Clear, bounded, or unrelated work stays on its minimum useful
route and does not read or create Wayfinder state.

Agentic Workflow's effective Wayfinder workflow is a framework-owned runtime
projection derived from Matt Pocock's Wayfinder methodology. It keeps the
method's destination, low-resolution map, honest fog, frontier, incremental
resolution, readable-name, and progressive-loading concepts while Agentic
Workflow owns the Git-native state and continuation contract below. This is
durable project knowledge and coordination state, not an issue tracker and not
a mirror of `.scratch/` or an external tracker.
Do not create or update `.agent-workflow-state/active.md`; the effort map is the
only re-entry point.

## Responsibility boundary

Wayfinder may preserve four kinds of durable knowledge:

- `unknown`: an unresolved question that materially affects the destination;
- `evidence`: an observation, measurement, report, or source result, including
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
artifact from `map.md`; it does not duplicate those work items in Wayfinder.
Work that fits one coherent implementation session can pass directly from the
map, a settled D#, or another accepted specification to implementation.

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
validate, migrate, rewrite, or remove Wayfinder state.

## Effort naming, selection, and stable paths

The H1 heading in `map.md` is the durable human-readable effort name. Its
Destination states the intended endpoint, while Not yet specified and Out of
scope distinguish in-scope fog from the scope boundary. The effort is
recognized from that readable name, destination, scope boundary, and map
context. The directory slug is only its stable storage key; it is not a
separate semantic identity object and does not replace the readable name.

Route before inspecting state. An unrelated Wayfinder directory never selects
Wayfinder or justifies a scan.

When the user or authoritative context supplies an exact repository-relative
effort path, verify that it is safe, stays below
`.agent-workflow-state/wayfinder/`, traverses no symlink, and names a regular
`map.md`. Use that path and do not invent a replacement directory.

For a likely resume without an exact path:

1. List effort directory names.
2. Use the request and directory names to identify the smallest plausible
   candidate set.
3. Read only those candidate maps.
4. Compare their readable effort names, destinations, scope boundaries,
   current state, and relevant context.
5. Resume one effort only when one match is sufficiently clear.

If multiple efforts remain plausible, do not merge them or choose arbitrarily.
Do not create a third synonymous effort or write affected state. Ask the user when
interaction is available. In noninteractive execution, report the ambiguity
and remain read-only for the affected state.

Create a new effort only when Wayfinder is selected, durable writes are
authorized, structured notes materially reduce the risk of losing or
conflating important state, no existing effort has the same substantive
destination and scope boundary, and the destination is materially distinct
enough to warrant its own map. A branch, ticket, file, command, temporary task
description, or chat title does not define a new durable effort.

Choose a concise human-readable noun phrase that remains sensible across
sessions and implementation phases. Avoid temporary or generic names such as
`Current work`, `Project update`, `Fix branch`, and `Miscellaneous`. Derive the
directory slug once from that name using a simple default: lowercase,
filesystem-safe, hyphen-separated, concise, and recognizable, with no timestamp
or random suffix by default. This is an authoring rule, not a generic slugging
framework.

Immediately before creating the directory, reread the relevant Wayfinder
directory listing, account for another session having created an effort, and
inspect any newly appearing plausible map. If the desired slug already exists,
resume it only when it represents the same effort. When a materially distinct
effort has a real collision, use the shortest stable meaningful disambiguator;
do not overwrite or merge the existing state, and avoid hashes or timestamps
while a readable alternative exists.

Once created, the effort directory path is stable. Do not rename it because the
map title improves, implementation phases or branches change, tickets change,
or new evidence revises current understanding. Established awkward or legacy
slugs remain valid and resumable. Preserve clear existing maps without
normalizing them or automatically migrating project-owned state.

Continue the same effort when wording becomes more precise, evidence changes,
implementation advances, unknowns resolve, or decisions are superseded while
the substantive destination and scope boundary remain intact. A materially
different endpoint, bringing previously out-of-scope work inside the boundary,
a change that would make the old map misleading as low-resolution orientation,
or a new destination after the original one completes normally requires a
fresh effort. Do not reuse a completed, abandoned, or superseded directory for
an unrelated destination.

Maps may carry one lifecycle line immediately below the H1:
`- Status: current | completed | abandoned | superseded`. `current` means the
destination remains a legitimate continuation target. The other values are
historical: `completed` reached the destination, `abandoned` stopped without
reaching it, and `superseded` was replaced by a materially different effort or
authoritative direction. A superseded map links its successor or governing
artifact. This single line is the effort lifecycle representation; do not add a
metadata file, directory move, archive tree, registry, or state machine.

During likely resume, an explicit `current` match outranks a similarly named
historical match. Read a historical map when it is directly named, explicitly
requested, needed to follow a successor, or otherwise materially relevant; its
children do not become part of normal loading merely because the effort once
matched. An older map without a status remains valid. Infer its lifecycle only
when its current state, outcome, and next work make that unambiguous; otherwise
do not silently classify, normalize, or let it displace an explicit current
match.

## Progressive loading

1. Route from the request first. Do not scan Wayfinder state for confidently
   direct or unrelated work.
2. Apply the effort naming, selection, and stable-path rules above; do not load
   every map to resolve a likely resume.
3. Read the relevant `map.md`, including its lifecycle when present, as the
   low-resolution orientation.
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

Use per-type positive identifiers within an effort: `U#`, `E#`, `F#`, and
`D#`. Never renumber an existing current record. Assign one greater than the
highest current filename of that type, or `1` when none exists. A retired number
is not reserved: a later repository state may reuse it, and Git distinguishes
the historical meanings.

Use repository-relative Markdown links and readable titles. Facts must link the
evidence artifacts or direct authoritative sources that justify them. Evidence
may optionally name facts it supports or contradicts, but reciprocal backlinks
are not required; requiring both directions creates synchronization work without
improving provenance. Decisions should link the facts, evidence, unknowns, ADRs,
or policies that materially constrained the choice.

Git is the history mechanism. Do not add an event log, revision files, a graph
index, or another versioning scheme.

Serialize every map or child mutation for an effort by atomically creating the
empty `<effort>/.wayfinder-mutation-lock/` directory. Hold it through all reads,
writes, and removals in that mutation, then remove it. The directory contains no
data, is not durable Wayfinder state, and must not be committed. If it already
exists, wait through host coordination or stop conservatively; never steal or
guess that a lock is stale. Atomic directory creation is the required host
primitive. If it is unavailable, do not mutate the effort.

Before creating a child under that lock, reread the map and relevant child
directory, reject duplicate current numbers, recompute the candidate, and
create the child without overwriting any path. The lock covers the directory
read and completed create so two different slugs cannot claim the same number.
If another creator won before the lock was acquired, the reread naturally
chooses the new current maximum. Before editing an existing child, reread it and
the map. If concurrent edits disagree, preserve both claims and reconcile
explicitly rather than choosing silently.

## The low-resolution map

Use these headings as a compact authoring default, not a strict schema. Preserve
clear existing human content instead of normalizing it for ceremony.

```markdown
# <Effort name>

- Status: current

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

<Concise observations or links; when resolved, state the answer and resulting
links.>
```

Use E# when an observation needs durable provenance, scope, limitations, or
independent reuse:

```markdown
# E1: <Evidence title>

- Observed: YYYY-MM-DD
- Source: <repository-relative link, command/result, or cited primary source>
- Scope: <where this evidence applies>
- Related: U1, F1

## Observation

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

## Knowledge settlement and effort completion

Wayfinder retains the smallest durable representation needed to navigate the
effort's current state. The map is current orientation, not a session log, and
Git preserves historical evolution.

When a U# is answered:

1. state the answer unambiguously in the U# or, when the child no longer adds
   value, as a compact resolution in the map;
2. mark an existing U# `resolved` and remove it from unresolved fog, blockers,
   and frontier work;
3. reconcile current state, dependencies, next work, and any affected links in
   the map; and
4. retain or create E#, F#, or D# only when that record keeps independent
   provenance, descriptive, or project-authority value.

The map may be the entire current result. Resolution does not require
U# -> E# -> F# -> D#, and no child is created merely to record that settlement
happened. Repeating reconciliation against the same answer changes neither the
map nor its current children.

U/E/F/D files are current durable knowledge, not historical allocation markers.
A resolved U# may leave the representation once its answer is unambiguous in
current state and it has no remaining navigational value. Evidence remains only
while its provenance, scope, limitations, or observation is independently
useful. Facts remain only while their established descriptive conclusion and
support chain are useful. Decisions remain only while the committed choice is
current or still needed to navigate current authority. Git owns historical
investigation and removed child content.

Before removing a child, inspect the selected effort's map and current child
files for references to its identifier or path. Reconcile every current
dependency first: replace the reference with a current canonical source or
successor, preserve the child when its provenance or meaning is still required,
and never leave a dangling current link. A fact that still depends on an E# is
evidence that the E# remains independently useful unless the fact can truthfully
link the authoritative source directly. Do not scan or reconcile unrelated
efforts.

Removal is allowed only after recoverable Git history contains the retiring
file's current content. If that content has never entered recoverable history,
history is unavailable, or current references cannot be reconciled truthfully,
keep the file and report the exact blocker. Acquire the effort mutation lock,
reread the map and current children, confirm no current reference remains, and
remove the child before releasing the lock. If current state changed before the
lock was acquired, reconcile again rather than overwriting it. An empty child
directory may then disappear. The retired number becomes available to the
ordinary current-state allocation rule.

To finish an effort, set the map status to `completed`, `abandoned`, or
`superseded`, record the concise outcome or reason, reconcile current canonical
links, and replace `Next work` with none for that effort. A superseded effort
also links the successor or governing direction. Do not load historical child
detail during ordinary effort selection, rename the stable directory, repurpose
it for a new destination, or move it into `.agent-workflow-state/archive/`;
that archive belongs to other durable workflow records.

Legacy maps and children require no repository-wide migration. Existing
U/E/F/D statuses retain their meanings. When authorized work on the relevant
effort supplies enough evidence, add the lifecycle line or settle only the
directly affected records; otherwise preserve the state and treat ambiguous
lifecycle as unknown. Install, update, status, remove, reinstall, provider
repair, and projection regeneration treat all Wayfinder state as opaque and
never inventory, validate, migrate, repair, or settle it.

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

No Jira synchronization, automatic archival, schema migration, database, graph
engine, allocation registry, event log, or validation service belongs in this
contract.
