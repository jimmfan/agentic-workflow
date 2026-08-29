# Local Wayfinder state contract

Use this contract only after routing selects Wayfinder or a request explicitly continues a relevant
effort. Existing state is never a routing signal.

This contract owns Wayfinder's durable representation, selection, reconciliation, pruning, and
effort ending.
The Wayfinder runtime owns navigation and specialist methodology.
Durable state is intentionally preserved across sessions or handoffs.

## State model and boundaries

An effort is one resumable body of coordination with one stable objective and scope.
Wayfinder is the sole framework-owned durable coordination model. The selected effort's
`map.md` is its brief coordination summary. Load this state contract before effort state.
When resuming a Wayfinder effort, read `map.md` first; it is the first effort file, and no
other framework continuity record may compete with it.

Specialists retain their methods and native artifacts. Wayfinder records consequential results
and links, not procedures or bookkeeping. To Tickets owns the ticket artifact or ticket set,
including ticket contents, dependencies, ordering, and readiness. Wayfinder links that artifact
instead of copying or mirroring ticket-level state.

All content below `.agent-wayfinder/` is project-owned durable data. Wayfinder interprets or
changes only the recognized current paths described below. All other entries are opaque
project-owned content: their bytes remain unchanged, and they are not interpreted as recognized
Wayfinder state.

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

Never persist credentials, secrets, sensitive data or sensitive command output, raw
transcripts, private agent memory, or unnecessary personal information.

Coordination is consequential when resolving it differently would change the objective, scope,
authority requirement, blocker or dependency, lasting result, or ready work. Wayfinder represents
current, resumable coordination, not a permanent journal. A
canonical artifact is the designated durable location for a lasting outcome; Git owns historical
evolution.

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

Selection does not require persistence. If assessment leaves no consequential cross-session
coordination worth preserving, create no effort, map, or supporting record.

Create a new effort only when durable writes are authorized, persistence is justified, and
no recognized effort owns the same objective and scope in substance. Immediately before
creation, reread the parent and any newly plausible map. A storage-key collision resumes
only the same effort; otherwise use the shortest meaningful disambiguator.

Preserve the established effort path while its objective and scope remain the same in
substance, including through wording, phase, branch, ticket, or evidence changes. A different
objective or substantive scope requires a new effort. Never repurpose earlier state to
represent different work.

A recognized effort may be ready, paused, blocked on evidence, waiting for authority, or
waiting for an external dependency. Represent that condition through current coordination state,
blockers, dependencies, and ready work. Do not add a map status or historical label.

Use this brief default map shape, combining, renaming, or omitting an item only when its
purpose is inapplicable or a clearer equivalent exists:

- **Objective** — the result the effort is intended to achieve.
- **Scope** — what the effort includes and excludes, including relevant project or authority limits.
- **Areas and relationships** — major areas, how they relate, and important ownership or operating constraints.
- **Current state** — smallest truthful summary needed to resume safely.
- **Blockers and dependencies** — only consequential constraints on progress.
- **Ready work** — work that may proceed now.
- **Key links** — the few canonical artifacts needed for continuation.

These headings guide content; they are not a recognition schema. Do not create empty headings.
The map summarizes the effort's current coordination state, blockers, dependencies, and ready
work. When no ticket artifact exists, the map may state ready work directly. Once To Tickets owns
detailed decomposition, the map links its ticket artifact or ticket set and may identify or
summarize the current ready handoff without mirroring ticket-level state.

Keep the map brief, preserve enough information to resume safely, and link detailed or authoritative
roadmaps, specifications, ADRs, tickets, and project artifacts instead of copying their bodies or
detailed backlogs. Load only records linked for the work at hand; do not read every ledger section
or U/E file. If a fresh session must read most supporting records to recover the current route,
reconcile the map instead of adding more supporting detail.

Remaining work is not automatically blocked work. A blocker is an unsatisfied dependency,
unresolved consequential uncertainty, or missing required authority that currently prevents
particular work from proceeding. A blocker applies to particular work, not automatically to the
entire effort. Planned but unperformed validation alone is not a blocker.

Ready work is work to which no blocker currently applies. Independent ready work may proceed while
unrelated work remains blocked.

## Current knowledge

U/E/F/D classify current knowledge; they are neither a mandatory pipeline nor a representation of
the effort's areas and relationships or problem hierarchy:

- `U#`: an unresolved consequential question whose separate preservation is independently useful
  for a later decision or continuation.
- `E#`: independently reusable evidence with a source, scope, observation, and material
  limitations.
- `F#`: a sufficiently supported current scoped descriptive conclusion with traceable
  provenance.
- `D#`: a current committed choice made under actual project authority.

A map may remain the entire result. Do not create U/E/F/D from ceremony, templates, counts, or
category fit. No type must produce another.

Represent areas, relationships, and ownership or operating boundaries in the single `map.md`. Do
not add area identifiers, nested state by domain or phase, parallel maps, or another state
hierarchy.

A U# file uses a readable question title and states why it matters. Presence in `unknowns/`
means the question is current and unresolved. Record its resolution mode, dependencies,
sources, and required authority only when they help later resumption or continuation.

An E# file states the reusable observation and enough source, scope, and limitations to evaluate
it. Record when it was observed only when timing changes meaning, applicability, or validity.
Prefer a direct source link on a fact when separate evidence adds no independent value.

Facts are H2 sections in `facts.md`. Presence means the conclusion is sufficiently supported
and current; a separate status field is not required. Provenance is traceable `Source`,
`Authority`, or `Derived from` support for a scoped fact. Each fact states its scoped descriptive
conclusion, provenance, and material limitations. Repeated agent summaries are not independent
provenance.

Decisions are H2 sections in `decisions.md`. Presence in `decisions.md` means the choice is
current and committed under actual project authority. Record the choice, authority, decisive
basis or constraints, material consequences, and a revisit condition only when one genuinely
applies.

Create a D# only for a consequential current choice committed under actual project authority.
Alternatives still under consideration, research findings, evidence changes, hypotheses,
recommendations, agent inference, and routine implementation judgment within already delegated
scope do not independently justify a D#. They may inform a choice or require review of an existing
decision, but they cannot create authority or replace a current choice.

Factual support establishes what is true; evidence may inform a choice. Only responsible project
authority may commit that choice or accept residual uncertainty for a named boundary. Record the
authority source separately where the choice or acceptance belongs. Wayfinder can record
authority; it cannot create it. Assumptions, proposals, inferred preferences, and agent-authored
persistence do not become supported facts or accepted decisions merely because they are recorded.
Link the actual human, project artifact, policy, or valid delegated scope for an authority-owned
conclusion.

A fact about another system remains a fact about that system; it does not establish a fact about
the current project. Record a project-specific F# only when project evidence, current source, or
valid project authority supports it. Otherwise preserve an independently useful external
observation as E#, a consequential project uncertainty as U#, or a working proposal in the
map or native specialist artifact, only when that representation independently earns preservation.

Volatile branch, HEAD, working-tree, ahead/behind, and session observations normally remain
execution context. Persist one only when it is an actual continuing authorization constraint,
baseline, or dependency that would change future work.

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
use a readable repository-relative link to the exact U/E file, F/D heading, or longer-lived
canonical artifact. Inside the effort, prefer links when a path or heading matters.

F/D anchors must retain the established lowercase `f<ID>--<slug>` and `d<ID>--<slug>` forms
derived from those headings' em-dash representation. Reconcile affected references before
renaming a U/E file or F/D heading.

## Reconciliation and pruning

Keep only current coordination needed to navigate the effort. Reconciliation updates affected map
content, recognized records, blockers, dependencies, ready work, and references to agree with
current truth, valid project authority, and the artifact that owns each lasting result. Pruning
removes a recognized Wayfinder record from current coordination after still-useful results are
preserved and affected references are reconciled. Removing the selected file or ledger section
carries out pruning; ending the effort is separate. Both preserve unrelated state. Git retains
committed history.

### Reconcile affected state

Reconciliation is required before renaming or pruning recognized state and whenever authorized
work changes reality represented by the selected effort before claiming completion. Read-only work
may report stale or conflicting state but does not change it.

Plan a mutation from current affected state. Immediately before writing, renaming, or removing,
confirm that the directly affected state and known affected references still support the planned
mutation. Create a new target without overwriting an existing path. If affected state changed or
conflicts, stop rather than overwrite it.

Before renaming or pruning state, inspect the selected map, ledgers, U/E files, and known current
references outside the effort for affected identifiers, paths, or heading anchors. Do not scan
unrelated efforts, the entire repository, or Git history.

Use this common sequence for every affected reconciliation:

1. Preserve any still-useful result in its proper canonical owner.
2. Update affected map content, records, blockers, dependencies, ready work, and known references.
3. Remove only the recognized record that no longer has independent current value.

Update only affected records and links to canonical artifacts. Do not copy canonical artifact
bodies, normalize unchanged files, resolve unrelated questions, or reconcile unrelated efforts.
Do not manufacture inconsistency merely because one artifact summarizes, abstracts, or omits
detail held elsewhere. Reconcile only a concrete incompatible statement or a requirement the
current owner no longer satisfies. When evidence is insufficient for a truthful update, preserve
state and report the blocker.

### Apply record-specific changes

When evidence strengthens or narrows an F#, update the same F# in place with its current claim,
scope, provenance, and material limitations. When evidence invalidates its support, narrow or
remove the unsupported conclusion and reconcile references that treated it as supported. Prune the
F# when no supported conclusion with independent current value remains. Do not
create a second fact merely to preserve history.

When an observation independently earns E# preservation through its source, method,
limitations, or reuse value, preserve it as E#. Otherwise do not create or retain an E# merely as
a transition step. Create or reopen a U# only when the precise unresolved question has
consequential current coordination value, and surface it in the map only when it affects the route.
Do not create an E#/U# pair by template.

When a U# is answered, preserve any independently useful result through the common sequence and
prune the U#; an answered question is no longer current unknown state and is not
retained as history. If responsible authority explicitly accepts residual uncertainty for a named
boundary, the question remains factually unresolved: keep its U# current and unresolved, record the
authority source and accepted boundary in its proper canonical artifact, and unblock only that
accepted boundary. The same uncertainty may remain a blocker for other work. The acceptance does
not answer the U#, grant unrelated authority, or unblock another dependency.

When factual evidence changes, review dependent D# records and ready work under the authority
rule in `## Current knowledge`. When responsible authority changes the choice for the same decision
boundary, update the same D# and its authority, basis, consequences, revisit condition, and affected
references. Allocate another D# only for a distinct current decision. When a D# is no longer
current under project authority, apply the common sequence and prune it; Git
retains the prior choice.

### Prune one record

Prune a record only after affected references are reconciled and the record no longer has
independent current value. Pruning does not require committing a transient record first.

Pruning U/E removes only the selected file. Pruning F/D removes only the selected H2 section. An
otherwise empty ledger may be removed. Unrelated ledger content remains byte-for-byte unchanged
where practical, and opaque project-owned content remains unchanged. Never recursively delete an
effort, `unknowns/`, or `evidence/` directory.

### Keep or end the effort

Keep an effort's map while it may realistically resume, including when it is paused, blocked, or
waiting. Keep its map content current enough for safe resumption, including blockers, dependencies,
and any ready work. Do not remove `map.md` while consequential unresolved coordination still needs
continuity. Retain the effort, transfer that coordination to a recognized current successor, or
preserve the consequential result or constraint in its canonical artifact before ending the effort.

An effort ends only when it has no legitimate continuation because its objective was achieved,
responsible authority stopped the effort, or continuing coordination moved to a different objective
and scope. Before removing recognized Wayfinder records, ensure lasting outcomes and continuing
relationships or constraints have an appropriate owner and reconcile affected references. Apply
the common sequence across affected records, then remove `map.md` last. Never recursively delete
the effort directory; the absence of `map.md` ends Wayfinder recognition, and any opaque
project-owned bytes and their containing directories remain unchanged.

Record a useful replacement relationship in its successor or canonical artifact. Do not retain the
predecessor map or add tombstones, redirects, archives, or successor metadata. Do not clean up
other efforts; Git preserves history.
