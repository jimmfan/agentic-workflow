# Local Wayfinder state contract

Use this contract only when Wayfinder is selected, including a justified
mid-task escalation, or a request continues a relevant local Wayfinder effort.
The existence of an effort under `.agent-wayfinder/` is not a
routing signal. Clear, bounded, or unrelated work stays on its minimum useful
route and does not read or create Wayfinder state.

Wayfinder is Agent Workflow's sole framework-owned durable coordination
layer. Its effective runtime is derived from Matt Pocock's Wayfinder
methodology, while this contract owns the Git-native state and continuation
mechanics. This is durable project knowledge and coordination state, not an
issue tracker, specialist notebook, or mirror of `.scratch/` or an external
tracker.
The selected effort's `map.md` is its only re-entry point. Add no global state
registry or second framework-owned frontier.

## Responsibility boundary

Wayfinder may preserve four kinds of durable knowledge:

- `unknown`: a precise unresolved question preserved independently while
  unanswered because it could materially improve a later developer’s ability
  to make or evaluate a decision;
- `evidence`: an observation, measurement, report, or source result, including
  its provenance, scope, and limitations;
- `fact`: a sufficiently established descriptive conclusion, scoped to the
  evidence available now; and
- `decision`: a committed choice made under the project's authority.

These are distinctions, not a mandatory pipeline. Evidence may leave an
unknown unresolved, a fact may require no decision, and a decision may be made
under uncertainty without manufacturing a fact.

Never persist secrets, tokens, private keys, raw credentials, sensitive command
output, unnecessary personal data, raw transcripts, or private agent memory in
Wayfinder state.

Git/session observations such as the current branch, HEAD commit, dirty
working-tree status, or ahead/behind status are execution context, not normal
durable state. Inspect this information when useful for safe execution, but
normally do not persist it because it is likely to become stale as work
proceeds. Persist it when it represents a durable constraint or dependency,
such as work is authorized only on a named branch, a branch must remain
untouched, a particular commit is the required baseline, or another branch
contains implementation required for continuation.

## Semantic territory and effort identity

U/E/F/D is a knowledge taxonomy, not the effort's problem structure. Every
durable effort keeps enough low-resolution semantic structure in `map.md` to
give a fresh agent useful bearings. When relevant, that includes:

- the destination and substantive scope boundary;
- the major coherent areas or domains within the effort; and
- important relationships, dependencies, or seams between those areas.

Establish the destination and enough relevant territory to orient the effort
before substantial decomposition.

Use the smallest clear representation: prose, bullets, a compact table, or a
small diagram are all valid. `## Territory` is a useful default heading, not a
required schema. Do not create area identifiers, nested domain directories, or
parallel maps merely to express this structure; the flat effort layout with
optional F/D ledgers and independently useful U/E files remains canonical.

Territory is provisional, adaptive, and judgment-based. It helps Wayfinder
explore relevant areas and seams, challenge incomplete framing, and revise its
understanding as evidence develops. Exploration may broaden understanding, but
must not silently broaden the user's goal, delegated authority, or
implementation scope.

For a new durable effort, reuse authoritative project structure from accepted
ADRs, specifications, domain documentation, source, or another canonical
artifact when it already establishes sufficient bearings. Otherwise establish
it directly when current context supports it confidently. If structural
ambiguity remains, the Wayfinder runtime may select an appropriate specialist;
this state contract does not own that method. Establish enough structure before
substantial U/E/F/D state accumulates, then derive the effort's identity,
readable name, destination, boundary, and stable path from that understanding.
Do not choose `.agent-wayfinder/<effort-name>/` first and rationalize its structure
afterward.

When evidence changes the semantic structure, update the current map's areas,
relationships, boundary, fog, and frontier coherently. Do not retain stale or
parallel territory structures merely because an earlier map used them.

## Specialist result boundary

The Wayfinder runtime decides whether to continue directly or load one
materially useful specialist. Specialists own their methods and native
artifacts; they create no framework persistence record. Reconcile only the
consequential coordination needed to continue: the unresolved frontier, useful
evidence or conclusions, relevant artifact pointers, resolution mode when it
helps re-entry, dependencies, blockers, and next work. Do not copy a specialist
method, transcript, or temporary bookkeeping into Wayfinder.

If specialist work is interrupted, the selected effort map and only justified
U/E/F/D detail become the re-entry point. Create no separate specialist
continuity record.

The resolution method determines what evidence or authority is sufficient to
answer the question. It is not merely a label on a U# and does not require a
ceremonial specialist invocation when equivalent authoritative evidence already
exists. Human clarification requires an answer from the responsible authority
and cannot be supplied by agent inference or substituted research. Research
requires appropriate source evidence. Prototype and debugging require relevant
observed or experimental evidence. Discovery, Domain Modeling, Grilling, and
direct resolution retain their stated methods and authority boundaries. Running
a named method is not itself resolution.

When a choice requires human or project authority, do not decide it on the
human's behalf. Surface the concrete question, explain why that authority is required,
and state what the answer will unblock. Keep the uncertainty or blocker explicit
until an authoritative answer exists. Do not turn an assumed answer into an
accepted D#, specification, or implementation ticket.

Durable Wayfinder state can record authority; it cannot create authority. An
agent-authored map, U#, E#, F#, D#, or note is not an authority source merely
because it persists. Link the actual human or project source, or the valid
delegated scope, before treating an authority-owned boundary as answered or
accepted.

`map.md` owns the current state, blockers, dependencies, and next work. It is
the effort's coordination and re-entry point. Keep enough information there for
a fresh session to choose the next relevant detail without loading every
supporting record.

When ready work becomes substantial enough to need dependency ordering or
independently deliverable sessions, hand it to `to-tickets`. That workflow owns
its native ticket artifacts and frontier. Wayfinder links the resulting native
artifact from `map.md`; it does not duplicate those work items in Wayfinder.
Each independently ready scope may pass directly from the map, a settled D#, or
another accepted specification to Implementation and Verification. Each
Implementation handoff still consumes one coherent scope at a time. No
implementation continuity record is created.

## Ownership and locations

All paths below are project-owned durable data:

```text
.agent-wayfinder/
└── <effort>/
    ├── map.md
    ├── facts.md        # optional current F# ledger
    ├── decisions.md    # optional current D# ledger
    ├── unknowns/       # optional independent U# files
    └── evidence/       # optional substantial E# files
```

`map.md` alone is a complete and valid Wayfinder effort. Create `facts.md` or
`decisions.md` lazily with the first justified current record. Create an
`unknowns/` or `evidence/` directory lazily with the first record that earns an
independently named artifact. Create a separate artifact because it is an
independently useful coordination or retrieval unit, not merely because it
belongs to a semantic category. A distinct, precise, unresolved, assigned, or
easy-to-template record does not by itself justify a separate file.

Short-lived observations, obvious repository facts, one-line conclusions, and
development questions safely answerable during authorized implementation
normally stay as concise map notes or links. Planned development validation is
not a current blocker merely because it remains to be performed. Do not turn
every source read or test run into an E#, extract every stable sentence into an
F#, or create a separate U# for every item on a human-question list.

The map remains an index and orientation surface rather than a duplicate fact
or decision store. If a fresh human or agent must read most supporting
artifacts merely to understand the current route, the effort is over-decomposed
and should be reconciled.

Create an effort only when repository writes are authorized and structured
durable notes materially reduce the risk of losing or conflating important
state. A read-only analysis, audit, diagnosis, review, `do not change files`
instruction, or equivalent restriction never authorizes a Wayfinder state
write.

Assessment, including assessment after automatic Wayfinder routing, may find
that no consequential uncertainty or continuity need is worth preserving. In
that case, report that no durable Wayfinder state is needed and create neither a
map nor a supporting record merely because Wayfinder was considered or selected.

Install, update, status, remove, and reinstall never seed, inventory, checksum,
validate, migrate, rewrite, or remove Wayfinder state.

## Recognized current state boundary

Wayfinder recognizes only an effort's `map.md`, optional `facts.md` and
`decisions.md` ledgers, and canonical U#/E# files below `unknowns/` and
`evidence/`. Content outside that shape is project-owned data: do not interpret
it as current Wayfinder state, use it for automatic re-entry or allocation, or
mutate or silently normalize it.

Unknown project-owned content does not by itself block independent current
work. Continue when the authorized read and write set does not depend on that
content. Stop safely when it creates a real target or ancestor collision,
reference conflict, semantic ambiguity in a recognized current container,
unsafe filesystem boundary, or inability to perform the authorized current
write truthfully. Preserve every unknown byte when stopping. Lifecycle,
provider repair, and projection regeneration treat all `.agent-wayfinder/`
content as opaque project-owned data.

## Effort naming, selection, and stable paths

The H1 heading in `map.md` is the durable human-readable effort name. Derive it
after context establishes the destination, boundary, major areas, and relevant
relationships. The directory slug is only its stable storage key, not a second
identity.

Route before inspecting state. An unrelated Wayfinder directory never selects
Wayfinder or justifies a scan.

For an exact repository-relative effort path, verify that it stays below
`.agent-wayfinder/`, traverses no symlink, and names a regular `map.md`; then use
it without inventing a replacement.

For a likely resume without an exact path: List effort directory names, identify
the smallest plausible candidate set, read only those maps, and compare their
names, destinations, boundaries, and current state. Resume only a clear match.

If multiple efforts remain plausible, neither choose nor merge them, create a
third synonymous effort, or write affected state. Ask the user, or report the
ambiguity and remain read-only in noninteractive execution.

Create only when Wayfinder and durable writes are authorized, structured notes
materially reduce loss or conflation risk, and no effort has the same destination
and boundary. A branch, ticket, file, command, temporary task description, or
chat title does not define a new durable effort.

Choose a durable noun phrase, then derive a lowercase, filesystem-safe,
hyphen-separated, concise slug without a timestamp or random suffix by default.

Immediately before creating the directory, reread its parent and inspect any new
plausible map. Resume a colliding slug only for the same effort; otherwise use
the shortest stable meaningful disambiguator without overwriting or merging.

Once created, the effort directory path is stable across wording, branch,
phase, ticket, and evidence changes. Preserve an established safe path; do not
rename it merely to improve wording.

Continue while the destination and boundary remain intact. A different endpoint,
bringing previously out-of-scope work inside the boundary, a misleading old
map, or a new destination after completion requires a fresh effort. Never reuse
a historical directory for an unrelated destination.

Maps may carry `- Status: current | completed | abandoned | superseded` below the
H1. Current remains resumable; historical statuses record reached, stopped, or
replaced destinations, and superseded maps link their successor. This single
line is the effort lifecycle representation; add no lifecycle registry or move.

During likely resume, an explicit `current` match outranks a similarly named
historical match. Read a historical map when it is directly named, explicitly
requested, or materially relevant; do not load its supporting records by
default. An older map without a status remains valid. Infer lifecycle only when
unambiguous, and never let it displace an explicit current match.

## Progressive loading

1. Route from the request first. Do not scan Wayfinder state for confidently
   direct or unrelated work.
2. Apply the effort naming, selection, and stable-path rules above; do not load
   every map to resolve a likely resume.
3. Read the relevant `map.md`, including its lifecycle when present, as the
   low-resolution orientation.
4. Follow only links needed for the current question or work. Retrieve the
   linked F# or D# section from its ledger, or the linked U#/E# file; do not
   load unrelated ledger sections or every U/E artifact.
5. Derive the current frontier from the map and any linked native ticket source;
   do not persist a second frontier or global state registry.

An implementation request may consume a coherent next-work scope from the map,
a settled decision or specification, or a native ticket without rerunning
Wayfinder. A new unknown returns work to Wayfinder only when it
materially obscures the destination; ordinary implementation detail stays in
implementation.

## Identifiers and links

Use per-type positive identifiers within an effort: `U#`, `E#`, `F#`, and
`D#`. U# and E# keep the numeric prefix plus a readable filename slug, such as
`U17-node-group-isolation.md`; do not reduce their filenames to bare numbers.
F# and D# use H2 ledger headings with the identifier, an em dash, and a readable
title, such as `## D4 — Use a dedicated node group`. The identifier is a stable
handle within the current Wayfinder representation, not a repository-lifetime
primary key. Never renumber an existing current record, and never allow two
current records of one type to share a number. Numeric uniqueness is scoped to
current same-type records within that effort.

A bare U#/E#/F#/D# identifier is effort-local current-state shorthand. Inside
the selected effort's map and records, concise statements such as
`U17 blocks D4` and `D4 follows from F8` are valid when the effort context
is unambiguous. A U#/E# readable filename is its canonical filesystem path. A
current F#/D# durable link uses a readable label and the exact ledger heading,
for example `[D4 — Use a dedicated node group](decisions.md#d4--use-a-dedicated-node-group)`.
The anchor convention is the ordinary Markdown heading form: lowercase the
heading text, remove punctuation including the em dash, and replace each space
with `-`; the spaces on both sides of the removed em dash therefore produce
`--`. Do not add hidden IDs, registries, or metadata. Renaming a current ledger
heading requires reconciling affected current links.

Assign one greater than the highest currently present identifier of that type,
or `1` when none exists. Do not search for or deliberately recycle interior
gaps. A retired number is not reserved: removing the current highest record may
cause its number to appear again in a later repository state, and Git
distinguishes historical meanings that actually entered Git.

When a canonical artifact outside the selected effort needs a reference that
survives beyond the current Wayfinder representation, use a repository-relative
Markdown link with a readable label to the exact ledger section, U#/E# file, or
a longer-lived canonical artifact. Do not rely on bare prose such as `See D4`
as permanent repository-wide identity. An external canonical artifact need not
retain a reference to a temporary current record that has no independent value;
reconcile or remove any known current reference before retiring that record.
Do not scan the repository or Git history merely to find historical bare
identifiers. Retirement remains bounded to the selected effort and known current
canonical references that would otherwise become broken or misleading.

Within the effort, use repository-relative Markdown links and readable titles
when a path is useful. Every current fact contains at least one truthful
provenance mode: `Source`, `Authority`, or `Derived from`. Multiple modes may
appear when genuinely applicable; omit inapplicable fields instead of leaving
empty ceremony. A repeated agent-authored summary is not an independent source
unless it is itself an accepted canonical authority artifact. Scope and
limitations prevent unjustified generalization. Evidence may optionally name
facts it supports or contradicts, but reciprocal backlinks are not required.
Decisions should link the facts, evidence, unknowns, ADRs, or policies that
materially constrained the choice.

Git is the history mechanism. Do not add an event log, revision files, a graph
index, or another versioning scheme.

Serialize every map, ledger, U#, or E# mutation for an effort by atomically
creating the empty `<effort>/.wayfinder-mutation-lock/` directory. Hold it
through the affected reads, writes, and removals, then remove it. The lock
contains no data, is not durable Wayfinder state, and must not be committed. If
it already exists, wait through host coordination or stop conservatively;
never steal or guess that a lock is stale. If atomic directory creation is
unavailable, do not mutate the effort.

Under that lock, allocation rereads the F#/D# ledger or U#/E# directory,
parses every canonical same-type identifier, rejects malformed or duplicate
identifiers, and recomputes one greater than the highest current same-type
identifier. Append one ledger section or exclusively create one U#/E# file.
Immediately before writing, reread the ledger or directory, map, target, and
affected state. The lock makes retirement's final reference scan and removal
indivisible. Preserve concurrent conflicts and reconcile explicitly.

## The low-resolution map

Use these headings as a compact authoring default, not a strict schema. Preserve
clear existing human content instead of normalizing it for ceremony.

```markdown
# <Effort name>

- Status: current

## Destination

<What it means for the route to be clear.>

## Territory

<When useful: major coherent areas and the relationships or seams that matter.>

## Current state

<Concise established state and links to independently useful U/E/F/D detail.>

## Blockers and dependencies

<What prevents progress, what depends on what, and any recovery condition.>

## Next work

<The coherent ready frontier: one or more independently ready scopes, or a
linked native ticket frontier.>

## Notes

<Standing constraints and useful canonical links.>

## Decisions so far

- [D1 — Title](decisions.md#d1--title) — one-line gist

## Not yet specified

<In-scope fog or unresolved detail that does not currently justify independent
U# tracking.>

## Out of scope

<Explicit boundaries beyond this destination.>
```

`Territory` is optional when the same bearings are already clear elsewhere in
the map. Keep small facts inline; promote reusable, disputed, independently
revised, provenance-sensitive, or oversized detail. Keep the coherent ready
frontier concise, list one or more independently ready scopes only when useful,
exclude dependency-blocked work, and link rather than copy a native ticket
frontier.

The ready frontier is the set of coherent scopes whose material decision
dependencies are answered or explicitly dispositioned and can therefore
proceed now. Explicit disposition is responsible-authority acceptance of
remaining uncertainty for a named boundary, never an agent assumption.

When evidence establishes execution order, surface the critical path,
independent parallel work, and any off-path dependency with material external
lead time. Never manufacture a critical path from an unordered backlog or
incomplete dependency evidence.

Map uncertainty broadly, then promote selectively. A precise question becomes
U# when preserving it while unanswered could materially improve a later
developer’s ability to make or evaluate a decision. Human or project
authority, an external owner or approval, expensive reconstruction, premature
dependent work, or multiple downstream areas or a meaningful seam are strong
signals, not a checklist.

Ask substantive project questions, not whether to create U#. Keep incidental,
routine, easily reconstructed, or merely unspecified detail in the map.
Precision alone is insufficient. Never create a U# from a template, precision,
or item count alone, or as create-and-retire ceremony. Keep low-value fog under
`Not yet specified`; out-of-scope work stays out until the destination changes.

## Knowledge records and artifacts

These are permissive authoring shapes, not lifecycle schemas. Omit inapplicable
fields instead of creating empty ceremony.

Use U# when a question is consequential enough to track independently:

```markdown
# U1: <Question>

- Status: open
- Resolution mode: direct | discovery | debugging | research | prototype | domain modeling | human clarification | grilling
- Blocked by: none
- Related: none

## Why it matters

<How the answer changes the destination, a decision, or next work.>

## Evidence

<Observations or links relevant to answering the question.>
```

A separate U# earns its file when preserving the detailed question or eventual
answer materially improves coordination or later continuation, especially
through substantial reasoning or tradeoffs, distinct authority or external
ownership, material external lead time, multiple downstream dependencies,
expensive reconstruction, or consequential risk from acting prematurely.
Human-question lists, planned development validation, and ordinary unspecified
detail need not each become U# files.

Use E# when an observation needs durable provenance, scope, limitations, or
independent reuse:

```markdown
# E1: <Evidence title>

- Observed: YYYY-MM-DD
- Source: <repository-relative link, command/result, or cited primary source>
- Scope: <where this evidence applies>
- Supports: <relevant F#/D#/U#>
- Limitations: <sampling, uncertainty, or conflict>

<Observation, method, result, and only the detail needed to reuse or evaluate
it.>
```

A simple source link normally belongs directly on its fact. Evidence earns an
artifact when its observations, methods, calculations, provenance,
limitations, conflict, or reuse value require independent preservation.

Use an H2 section in `facts.md` when a descriptive conclusion is established
enough to rely on across sessions and retaining it adds value:

```markdown
## F1 — <Established descriptive conclusion>

- Status: established | disputed | stale
- Scope: <where and when the conclusion applies>
- Source: <canonical URL or repo/path:lines>
- Authority: <named authority or canonical authority artifact, date, forum>
- Derived from: <supporting F#/E#/source and concise derivation>
- Limitations: <material limitation, when applicable>

<Concise scoped conclusion.>
```

A fact must contain at least one truthful `Source`, `Authority`, or
`Derived from`. Working assumptions are not facts; keep them in the map or an
appropriate U# with `Assumed:` and `Settled by:`. An agent-created inference
does not become established merely because it is placed in the ledger.

Fact correction: Treat each F# as the current canonical statement of one scoped
factual conclusion. When stronger evidence corrects, narrows, or refines the
same conclusion — same subject, corrected value or scope — update that F# in
place and reconcile its provenance, scope, limitations, and affected references.
Do not create a new F# merely to preserve history; retain the previous value only
when it remains materially useful, otherwise Git owns the history. Create a new
F# only for an independently useful fact with distinct meaning or scope. If
conflicting evidence remains unresolved, mark the existing fact `disputed` or
`stale` rather than creating another established fact.

Use an H2 section in `decisions.md` for a committed choice, not for a
descriptive conclusion:

```markdown
## D1 — <Committed choice>

- Status: accepted | provisional | superseded
- Authority: <named person, responsible project role, or accepted authority artifact; include date and forum where applicable>
- Based on: <facts, evidence, unknowns, policies, ADRs, or other decisive sources>
- Revisit when: <required for provisional; optional otherwise>
- Consequences: <concise material consequences>

<The choice, decisive rationale, tradeoffs, and explicit remaining uncertainty.>
```

`accepted` is a current committed choice. `provisional` is an explicitly
adopted temporary choice with a real revisit condition, not a proposal or agent
recommendation. Keep a `superseded` decision only while it adds current
navigational value. Accepted and provisional decisions require actual project
authority. Evidence can support a choice but cannot create authority. A
proposal, inferred preference, or working assumption does not become D#.

Answering a U# need not create F# or D# before retirement. An E# need not create
F#. A routine source read, transient command output, or fact obvious from current
source does not deserve an E#. A conclusion used only to orient the current
session does not deserve an F#. A preference, proposal, or agent assumption is
not an accepted D# unless the user or project policy grants the necessary
authority.

The `Resolution mode` field constrains sufficiency rather than adding a
lifecycle. A current U# remains open until sufficient evidence or authority
answers it and it is retired. Record the mode when it helps re-entry. A source,
result, or authority answer may satisfy the named mode without forcing a
specialist run, but an invalid kind of evidence cannot answer the U#.

## Knowledge settlement and effort completion

Wayfinder retains the smallest durable representation needed to navigate the
effort's current state. The map is current orientation, not a session log, and
Git preserves historical evolution.

A semantic area is settled when no consequential uncertainty remains
undispositioned for that area and every durable outcome has either reached its
proper canonical owner or been handed to the workflow that owns the resulting
work. Owners include ADRs, specifications, project documentation or source,
`to-tickets`, Implementation, another native artifact, or no separate artifact.
Settlement does not require every area or D# to become an ADR or ticket.

As an area settles, reconcile its map, fog, blockers, dependencies, frontier,
and links. Retain U/E/F/D only while currently useful; add no area IDs,
per-area lifecycle files, or state hierarchy.

An answered U# is no longer current unknown state. Preserve any independently
useful outcome in its proper current owner, reconcile affected current
references and dependencies, then retire the U#. Do not retain a resolved U#
solely for history; Git owns history. If the question remains unanswered but
responsible authority explicitly accepts the uncertainty for a boundary, keep
the U# open and unblock only that boundary.

Record accepted residual uncertainty, its authority source, and its named
boundary in a canonical owner. Other dependencies remain blocked.

The map may be the entire current result. Answering a U# does not require
U# -> E# -> F# -> D#, and creates no ceremonial record.

U/E files and F/D ledger sections are current durable knowledge, not history.
Retain E#/F#/D# only for current provenance, descriptive, or authority value;
Git owns retired history.

Before retiring a record, inspect the selected effort's map, ledgers, U#/E#
files, and known current canonical references outside the effort for references
to its identifier, path, or heading anchor. Reconcile every current dependency
first: replace the reference with a current canonical source or successor,
preserve the record when its provenance or meaning is still required, and never
leave a dangling current link. A fact that still depends on an E# is evidence
that the E# remains independently useful unless the fact can truthfully link
the authoritative source directly. Do not scan or reconcile unrelated efforts,
the whole repository, or Git history.

Removal is allowed once all independently useful current information is
preserved and every current reference is reconciled truthfully. There is no
requirement that the record's exact contents already exist in Git. Git preserves
states that actually entered Git; transient navigation artifacts may disappear
without first becoming historical records.

Before removal under the effort mutation lock, reread the target and affected
state; stop for references or useful information, and retry after change.
Retiring a fact or decision removes only its selected H2 section after
reconciliation and preserves other sections byte-for-byte where practical.
Remove an otherwise empty `facts.md` or `decisions.md`. Retiring U#/E# removes
only its file; an empty directory may remain or disappear. An empty `unknowns/`
directory has no semantic meaning: it is not a current unknown, blocker,
dependency, or frontier item and requires neither creation nor removal.
The retired number follows the ordinary highest-current-plus-one rule.

Do not implement automatic ledger sharding or use an arbitrary F#/D# file-count
rule. A future explicit refactor may split an unwieldy ledger by coherent
domain; this contract does not pre-build that machinery.

Answer or explicitly disposition consequential U#, reconcile and shrink the
map, then expose the coherent ready frontier and hand off one or more ready
scopes without advancing dependency-blocked work. Independent ready work need
not wait for unrelated blocked work, but each Implementation invocation
consumes one coherent scope at a time.

To complete an effort, confirm its destination is reached, no consequential
uncertainty remains undispositioned in any in-scope area, durable outcomes are
canonically owned or handed off, and redundant supporting knowledge is retired.
Completed efforts should normally shrink to a concise map with the outcome and
canonical pointers. Then set the map status to `completed`, record the outcome,
reconcile current canonical links, and replace `Next work` with none for that
effort.

To abandon or supersede an effort, set the corresponding status, record the
concise reason or outcome, reconcile current canonical links, and replace `Next
work` with none for that effort. A superseded effort also links the successor or
governing direction. Do not load supporting detail from a completed, abandoned,
or superseded effort during ordinary effort selection, rename the stable
directory, repurpose it for a new destination, or move it into a
framework-owned archive. Git owns history.

Current E/F/D statuses retain their meanings; preserve ambiguous state. Install,
update, status, remove, reinstall, provider repair, and projection regeneration
treat all Wayfinder state as opaque and
never inventory, validate, migrate, repair, or settle it.

## Contradictions and revision

Live source and current observed behavior outrank stale Wayfinder summaries.
When newer or stronger evidence conflicts with a fact:

1. preserve the conflicting evidence and its provenance;
2. if the conflict is unresolved, mark the F# `disputed`, open or reopen the
   relevant U#, and surface the blocker in the map;
3. if resolved, apply the fact-correction rule to update the same F# and affected
   references; and
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
next action, reconcile the affected map and only the directly affected records
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

Direct reasoning or one lazily selected specialist may supply reasoning,
evidence, or clarification while Wayfinder alone retains framework-owned
durable coordination. Specialist-native artifacts stay canonical and are linked
rather than copied.

Use `to-tickets` only when clear work benefits from dependency ordering or
separately deliverable sessions. Pass the map and only relevant U/E/F/D context.
The configured tracker or local-ticket convention owns the resulting artifacts;
Wayfinder records only the current pointer and coordination consequence.

No Jira synchronization, automatic archival, schema migration, database, graph
engine, allocation registry, event log, or validation service belongs in this
contract.
