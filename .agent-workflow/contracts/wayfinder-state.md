# Local Wayfinder state contract

Use this contract only after routing selects Wayfinder or a request explicitly continues a relevant
effort. Existing Wayfinder state alone is never a routing signal.

This contract defines Wayfinder's durable representation, selection,
reconciliation, pruning, and effort ending. The Wayfinder runtime defines
navigation and specialist methodology. Durable state is intentionally preserved
across session continuations and workflow transitions.

## State model and boundaries

An effort is one resumable body of coordination with one stable objective and scope.
Wayfinder is Agent Workflow's sole durable coordination model. The selected effort's
`map.md` is its brief coordination summary. Load this state contract before effort state.
When resuming a Wayfinder effort, read `map.md` first; it is the first effort file, and no
other Agent Workflow durable coordination record may compete with it.

Each specialist retains its method. A specialist creates no Agent Workflow
durable coordination state. Wayfinder records consequential results and
references, not procedures or bookkeeping. A durable ticket or ticket set
created by `to-tickets` maintains its contents, dependencies, ordering, and
readiness. Wayfinder uses a readable Markdown link to reference that durable
ticket or ticket set instead of copying or mirroring ticket-level state.

U/E/F/D are Wayfinder's durable record types. Blocking is a scoped relationship between a
condition and particular work, not a separate Wayfinder record type. Do not create blocker
identifiers, files, ledgers, directories, stores, or statuses.

All content below `.agent-wayfinder/` is project-owned durable data. Wayfinder
interprets or changes only the recognized current paths described below. All
other entries are unrecognized project-owned content: their bytes remain
unchanged, and they are not interpreted as Wayfinder state.

Wayfinder recognizes only the contract-defined paths and record forms in the layout below. Only
`map.md` is required:

```text
.agent-wayfinder/
└── <effort>/
    ├── map.md                    # required coordination summary
    ├── facts.md                  # optional current F# ledger
    ├── decisions.md              # optional current D# ledger
    ├── unknowns/                 # optional current U# files
    │   └── U<ID>-<slug>.md
    └── evidence/                 # optional reusable E# files
        └── E<ID>-<slug>.md
```

A safe regular `.agent-wayfinder/<effort>/map.md` is recognized as a whole and makes an effort
current and resumable. A map-only effort is valid; optional `facts.md`, optional `decisions.md`,
`unknowns/U<ID>-<slug>.md`, and
`evidence/E<ID>-<slug>.md` records are created lazily when independently useful. Separate
preservation is independently useful only when it has coordination, evaluation, retrieval,
reference, or update value beyond the map. Without `map.md`, a directory is not a recognized
resumable effort. Each recognized U#/E#/F#/D# record contributes to coordination according to its
type; its presence does not claim that every current U# or E# is established project truth.

A matter is consequential when handling it differently could change the effort's objective,
scope, required authority, lasting result, dependencies, or which work may proceed. Wayfinder
represents current, resumable coordination, not a permanent journal. Preserve a
lasting outcome in the artifact or record designated to maintain it; Git
maintains historical evolution.

## Effort shape and selection

The map H1 is the durable human-readable effort name. Its directory slug is a concise,
lowercase, filesystem-safe, hyphen-separated storage key derived from the objective and scope,
not a branch, ticket, phase, timestamp, random suffix, or chat title.
Use only the shortest meaningful disambiguator for a genuine collision.

An exact effort path must be repository-relative, remain strictly below `.agent-wayfinder/`, cross
no symlink in the root, ancestors, effort, or `map.md`, and identify a regular `map.md`. Reject an
unsafe or invalid exact path; do not invent a replacement.

Without an exact path, inspect only the smallest plausible candidate set. Compare safe maps
by objective, scope, and name, and resume only one clear match. If selection remains
ambiguous, do not guess, merge efforts, create a synonymous duplicate, or change affected state.
A mapless directory is not a candidate.

Selection does not require persistence. If assessment leaves no consequential
coordination worth preserving across session continuations, create no effort,
map, or supporting record.

Create a new effort only when the current user request or accepted project policy authorizes
the durable writes, persistence is justified, and no recognized effort represents the same
objective and scope in substance. Immediately before
creation, reread the parent and any newly plausible map. A storage-key collision resumes
only the same effort; otherwise use the shortest meaningful disambiguator.

Preserve the established effort path while its objective and scope remain the same in
substance, including through wording, phase, branch, ticket, or evidence changes. A different
objective or substantive scope requires a new effort. Never repurpose earlier state to
represent different work.

A recognized effort may contain ready or paused work, work waiting on evidence or authority, and
work waiting on an external dependency. Represent each condition through map content that
identifies the affected work, relevant dependencies, and any ready work. Do not add a map status
or historical label.

A new map is populated durable state only when its objective, scope, and current
state contain meaningful content. Existing safe regular maps remain recognizable
and resumable without exact-heading validation or formatting-only rewrites.

The objective states the result the effort must achieve. Scope states what the
effort includes and excludes, including relevant project or authority limits.
Current state is the smallest truthful coordination summary needed for safe
resumption. Persist only coordination state whose meaning remains relevant to
future work. Transient Git or session observations, such as a clean working
tree, current HEAD, or branch position, remain execution context unless they are
genuinely a continuing action authorization constraint, baseline, or dependency.
Represent major areas, their relationships, and important operating boundaries
within the most relevant map content. Ownership identifies who or what owns
consequential responsibilities, artifacts, decisions, or operating boundaries.
Key references are only the few sources or artifacts materially useful for
continuation, not a bibliography.

The map summarizes the effort's current coordination state, conditions blocking particular work,
dependencies, ready work, ownership, and key references. When no durable ticket or ticket set
exists, the map may state ready work directly. Once a durable ticket or ticket set exists, the map
links it and may include a current ready-work reference without mirroring ticket-level state. A
chat-only draft is not a durable ticket or ticket set.

Keep the map brief, preserve enough information to resume safely, and link
detailed roadmaps, specifications, ADRs, tickets, project artifacts, and sources
that establish relevant claims instead of copying their bodies or detailed
backlogs. Load only records linked for the work at hand; do not read every
ledger section or U/E file. If a fresh session must read most supporting records
to recover the current route, reconcile the map instead of adding more
supporting detail.

Dependencies record required inputs or dependencies. Blockers record actual blockers,
not ordinary remaining workflow steps. Planned tests, verification, commit or push steps,
and other unfinished work do not belong there merely because they remain. A blocker is a
condition that currently prevents particular work from proceeding. An unsatisfied dependency,
unresolved consequential uncertainty, or missing required authority can be a blocker for
affected work. The missing condition may be that a required project choice has not yet been
committed, a required action has not yet been authorized, or a required dependency remains
unsatisfied. Blocking is scoped to affected work: the same condition may block
one scope without blocking another. An unresolved U# records a question and is not
automatically a blocker. Delay, inconvenience, risk, or unfinished work alone does not make a
condition a blocker.

Ready work is work to which no blocker currently applies. Independent ready work may proceed while
unrelated work remains blocked.

Dependencies are satisfied by obtaining the action, artifact, decision,
participation from a person, system result, external result, or other input they
require. Questions and uncertainties are resolved through appropriate evidence
or their resolution method. Obtain a required project choice from the person,
role, or valid delegate with project decision authority, or apply accepted
project policy when it already determines the choice. When decision authority
itself is unclear, clarify who may decide. Responsibility alone does not establish
project decision authority. The person, role, or valid delegate with that authority
may explicitly accept unresolved uncertainty for one named boundary where this
contract permits it. Satisfying a
dependency, resolving a question or uncertainty, obtaining a required project
choice, authorizing a required action, or accepting unresolved uncertainty for
one boundary changes blocking only for affected work and does not automatically
unblock unrelated work.

## Current knowledge

U/E/F/D are Wayfinder's distinct durable record types. They do not form stages
or a mandatory U → E → F → D pipeline, and they do not represent the
effort's areas, relationships, or problem hierarchy:

- `U#` (unresolved question record) contains one current consequential question
  that remains unanswered and is independently useful to preserve.
- `E#` (evidence record) contains independently useful evidence with its source,
  scope, observation, and material limitations.
- `F#` (fact record) contains one current scoped descriptive conclusion judged
  sufficiently supported. The conclusion remains revisable as evidence changes.
- `D#` (decision record) contains one current consequential choice determined
  directly by accepted project policy or committed by the person, role, or valid
  delegate with project decision authority.

A map may remain the entire result. Do not create U/E/F/D from ceremony, templates, counts, or
category fit. No type must produce another.

Represent areas, relationships, and ownership or operating boundaries in the single `map.md`. Do
not add area identifiers, nested state by domain or phase, parallel maps, or another state
hierarchy.

A U# file uses a readable question title and states why it matters. Presence in
`unknowns/` means the question is current and unresolved. The U# record is not
itself a blocker; the unresolved condition may block particular work. Record
its resolution method, dependencies, sources, and required authority only when
they help later resumption or continuation.

An E# file states independently useful evidence using `Source:`, `Scope:`, the
existing `Observation` heading or field language, and `Limitations:`. Record when
it was observed only when timing changes meaning, applicability, or validity.
Prefer a direct source link on a fact record when a separate evidence record adds
no independent value.

Fact records are H2 sections in `facts.md`. Presence means the recorded
conclusion is sufficiently supported and current; a separate status field is
not required. State the relation directly: `Source:` identifies a source that
establishes the conclusion for its stated scope, `Derived from:` identifies
evidence or another record from which it was derived, and `Authority:` may name
a source that establishes a policy claim. Each fact record contains its scoped
descriptive conclusion and material limitations. Repeated agent summaries are
not independent evidence.

Decision records are H2 sections in `decisions.md`. Presence in `decisions.md`
means the recorded choice is current and committed for its decision boundary:
accepted project policy determines the choice directly, or the person, role, or
valid delegate with project decision authority committed it. Keep the existing
`Authority:` representation for the source of that binding choice. Record the
choice, decisive basis or constraints, material consequences, and a revisit
condition only when one genuinely applies.

Create a D# only for a consequential current choice committed under that gate.
Alternatives still under consideration, research findings, evidence changes,
hypotheses, recommendations, agent inference, and routine implementation judgment
within already delegated scope do not independently justify a D#. They may inform
a choice or require review of an existing decision, but they cannot create project
decision authority or replace a current choice.

Evidence may sufficiently support a descriptive conclusion or inform a
recommendation. Do not treat a consequential project choice as committed until
required evidence is sufficient. Accepted project policy may determine the choice
for a boundary directly, or the person, role, or valid delegate with project
decision authority may commit it. Authorization to perform an action does not
commit a project choice. A committed project choice does not authorize an unrelated
action. Host permission supplies neither action authorization nor a committed
project choice. A workflow or skill, its instructions, a test, specification,
ticket, or Wayfinder record grants neither. These gates and delegated scope may
each exist without the others. When both a required project choice is committed
and an action is authorized, affected work may proceed only within the authorized
scope. Agents may still exercise evidence-backed technical judgment already
delegated by the user or accepted project policy.

The person, role, or valid delegate with project decision authority may also
accept unresolved uncertainty for one named boundary under the scoped rule below.

Record the person, role, or valid delegate with project decision authority where
that authority is required. When accepted project policy determines a choice
directly, reference that policy without describing it as an entity that holds
authority. If decision authority itself is unclear, clarify who may decide.
Responsibility alone does not establish project decision authority. Wayfinder can
record authority; it cannot create it. Assumptions, proposals, inferred preferences,
and agent-authored persistence do not become supported conclusions or committed
choices merely because they are recorded. Reference the project artifact that
records it when one exists.

A conclusion about another system remains scoped to that system; it does not
establish a conclusion about the current project. Record a project-specific F#
only when project evidence or current source sufficiently supports the claim for
that scope. Otherwise preserve independently useful external evidence as E#, a
consequential unresolved project question as U#, or a working proposal in the
map or specialist artifact, only when that representation independently earns
preservation.

### Identifiers and references

Identifiers are effort-local, positive, and unique within their type. U/E files retain
readable slugs. F/D records retain these exact H2 representations:

- `## F<ID> — <title>`
- `## D<ID> — <title>`

Never renumber or duplicate a current same-type number. Allocate one greater than the highest
current same-type identifier, or 1 when none exists. Do not deliberately recycle interior gaps;
a pruned highest number is not reserved.

Immediately before assigning an identifier, reread all recognized same-type identifiers and reject
malformed or duplicate identifiers in current coordination state. Append an F/D section only if its
ledger still matches the content used to plan the append. Before creating a U/E file, recheck the
same-type identifiers and create the target without overwriting an existing path.

An identity-like U/E entry that cannot be interpreted safely blocks only operations whose
correctness depends on identifying records in that affected U/E container. It does not
automatically block unrelated work elsewhere; ambiguous content remains unchanged.

A bare identifier is local shorthand only. Durable references outside the selected effort
use a readable repository-relative Markdown link to the exact U/E file, F/D
heading, or longer-lived artifact that maintains the referenced result. Inside
the effort, prefer navigable links when a path or heading matters.

F/D anchors must retain the established lowercase `f<ID>--<slug>` and `d<ID>--<slug>` forms
derived from those headings' em-dash representation. Reconcile affected references before
renaming a U/E file or F/D heading.

## Reconciliation and pruning

Keep only current coordination needed to navigate the effort. Reconciliation
updates affected map content, recognized records, conditions blocking affected
work, dependencies, ready work, and references so they agree with current truth,
binding project choices, and designated artifacts that maintain lasting results.
Pruning removes a recognized Wayfinder record from
current coordination after still-useful results are preserved and affected
references are reconciled. Removing the selected file or ledger section carries
out pruning; ending the effort is separate. Both preserve unrelated state. Git
retains committed history.

### Reconcile affected state

Reconciliation is required before renaming or pruning recognized state and whenever work
authorized within the current scope changes reality represented by the selected effort before
claiming completion. Read-only work
may report stale or conflicting state but does not change it.

Plan a mutation from current affected state. Immediately before writing, renaming, or removing,
confirm that the directly affected state and known affected references still support the planned
mutation. Create a new target without overwriting an existing path. If affected state changed or
conflicts, stop rather than overwrite it.

Before renaming or pruning state, inspect the selected map, ledgers, U/E files, and known current
references outside the effort for affected identifiers, paths, or heading anchors. Do not scan
unrelated efforts, the entire repository, or Git history.

Use this common sequence for every affected reconciliation:

1. Preserve any still-useful result in the artifact designated to maintain it.
2. Update affected map content, records, conditions blocking affected work, dependencies, ready
   work, and known references.
3. Prune only recognized records that no longer have independent current value.

Update only affected records and references to artifacts that maintain relevant
results. Do not copy those artifact bodies, normalize unchanged files, resolve
unrelated questions, or reconcile unrelated efforts. Do not manufacture
inconsistency merely because one artifact summarizes, abstracts, or omits detail
held elsewhere. Reconcile only a concrete incompatible statement or a
requirement the designated artifact no longer satisfies. When evidence is
insufficient for a truthful update, preserve state and report what prevents the
affected work from proceeding.

### Apply record-specific changes

When evidence strengthens or narrows an F#, update the same F# in place with its
current scoped conclusion, the source or records from which it was derived, and
material limitations. When evidence invalidates its support, narrow or remove
the unsupported conclusion and reconcile references that treated it as
supported. Prune the F# when no supported conclusion with independent current
value remains. Do not create a second fact record merely to preserve history.

When an observation independently earns E# preservation through its source, method,
limitations, or reuse value, preserve it as E#. Otherwise do not create or retain an E# merely as
a transition step. Create or reopen a U# only when the precise unresolved question has
consequential current coordination value, and surface it in the map only when it affects the route.
Do not create an E#/U# pair by template.

When a U# is answered, preserve any independently useful result through the
common sequence and prune the U#; an answered question is no longer a current
unresolved question and is not retained as history. If the person, role, or valid
delegate with project decision authority explicitly accepts unresolved uncertainty
for a named boundary, the question remains factually unresolved: keep its U# current
and unresolved, record that authority and the accepted boundary in the project
artifact that records the committed choice, and unblock only that accepted boundary.
The same uncertainty may remain a blocker for other work. The acceptance does not
answer the U#: no broader project choice is committed, no unrelated action is
authorized, and no other dependency is satisfied.

When factual evidence changes, review dependent D# records and ready work under
the authority rule in `## Current knowledge`. When accepted project policy changes
the choice for a decision boundary, or the person, role, or valid delegate with
project decision authority commits a different choice, update the same D# and its
authority, basis, consequences, revisit condition, and affected references.
Allocate another D# only for a distinct current decision. When a D# no longer
records the current binding choice, apply the common sequence and prune it; Git
retains the prior choice.

### Prune one record

Prune a record only after affected references are reconciled and the record no longer has
independent current value. Pruning does not require committing a transient record first.

Pruning U/E removes only the selected file. Pruning F/D removes only the selected H2 section. An
otherwise empty ledger may be removed. Unrelated ledger content remains byte-for-byte unchanged
where practical, and unrecognized project-owned content remains unchanged and
uninterpreted by Wayfinder. Never recursively delete an effort, `unknowns/`, or
`evidence/` directory.

### Keep or end the effort

Keep an effort's map while it may realistically resume, including when it is paused, blocked, or
waiting. Keep its map content current enough for safe resumption, including conditions blocking
particular work, dependencies, and any ready work. Do not remove `map.md` while consequential
unresolved coordination still needs continuity. Retain the effort, transfer
that coordination to a recognized current successor, or preserve the
consequential result or constraint in the artifact designated to maintain it
before ending the effort.

An effort ends only when it has no legitimate continuation because its objective was achieved,
a committed project choice ended it, or continuing coordination belongs to a different objective
or substantive scope. Before removing recognized Wayfinder records, ensure lasting outcomes and
continuing relationships or constraints have a designated maintaining artifact and reconcile affected
references. Apply the common sequence
across affected records, then remove `map.md` last. Never
recursively delete the effort directory; the absence of `map.md` ends Wayfinder recognition, and
any unrecognized project-owned bytes and their containing directories remain
unchanged and uninterpreted by Wayfinder.

Record a useful replacement relationship in its successor or the artifact that
maintains the lasting result.
Do not retain the predecessor map or add
tombstones, redirects, archives, or successor metadata. Do not clean up other
efforts; Git preserves history.
