# Local Wayfinder state contract

Use this contract only after routing selects Wayfinder or a request explicitly continues a relevant
effort. Existing state is never a routing signal. Clear, unrelated, and read-only work does not
inspect or create Wayfinder state merely because state exists.

This contract owns Wayfinder's durable representation, selection, mutation, reconciliation, and
retirement. The Wayfinder runtime owns navigation and specialist methodology.

## Core invariants

Wayfinder is the sole framework-owned durable coordination model. The selected effort's
`map.md` is its re-entry point; no other framework continuity record may compete with it.

Specialists retain their methods and native artifacts. Wayfinder records consequential results
and links, not procedures or bookkeeping. `to-tickets` owns executable decomposition and its
frontier; link it rather than mirroring tickets.

All content below `.agent-wayfinder/` is project-owned durable data. Framework delivery and
provider operations treat it as opaque: they do not inventory, validate, normalize, migrate,
repair, reconcile, or delete its contents. They may create an absent root.

Wayfinder recognizes this current-state layout. Only `map.md` is required:

```text
.agent-wayfinder/
└── <effort>/
    ├── map.md                    # required re-entry point
    ├── facts.md                  # optional current F# ledger
    ├── decisions.md              # optional current D# ledger
    ├── unknowns/                 # optional current U# files
    │   └── U<ID>-<slug>.md
    └── evidence/                 # optional reusable E# files
        └── E<ID>-<slug>.md
```

A safe regular `.agent-wayfinder/<effort>/map.md` makes an effort current and resumable. A map-only
effort is valid; optional `facts.md`, optional `decisions.md`, `unknowns/U<ID>-<slug>.md`, and
`evidence/E<ID>-<slug>.md` records are created lazily when independently useful. Without `map.md`,
a directory is not a recognized resumable effort.

Except for the transient mutation lock, content outside recognized paths is opaque project-owned data.
Preserve it exactly; it blocks only a mutation affected by a target or ancestor collision,
recognized-container ambiguity, reference conflict, unsafe boundary, or inability to mutate
truthfully.

Read-only work never authorizes Wayfinder mutation. A mutating workflow authorizes changes only
to its requested effort and affected current state.

Never persist credentials, secrets, sensitive data or sensitive command output, raw
transcripts, private agent memory, or unnecessary personal information.

Wayfinder represents current, resumable coordination, not a permanent journal. Canonical project
artifacts own lasting outcomes; Git owns historical evolution. Do not add unjustified coordination,
history, registry, synchronization, migration, compatibility, or lifecycle machinery.

## Effort shape and selection

The map H1 is the durable human-readable effort name. Its directory slug is a concise,
lowercase, filesystem-safe, hyphen-separated storage key derived from the destination and
material scope boundary, not a branch, ticket, phase, timestamp, random suffix, or chat title.
Use only the shortest meaningful disambiguator for a genuine collision.

An exact effort path must be repository-relative, remain strictly below `.agent-wayfinder/`, cross
no symlink in the root, ancestors, effort, or `map.md`, and identify a regular `map.md`. Reject an
unsafe or invalid exact path; do not invent a replacement.

Without an exact path, inspect only the smallest plausible candidate set. Compare safe maps
by destination, boundary, and name, and resume only one clear match. If selection remains
ambiguous, stay read-only: do not guess, merge efforts, create a synonymous duplicate, or
mutate affected state. A mapless directory is not a candidate.

Selection does not require persistence. If assessment leaves no consequential cross-session
coordination worth preserving, create no effort, map, or supporting record.

Create a new effort only when durable writes are authorized, persistence is justified, and
no recognized effort owns materially the same destination and boundary. Immediately before
creation, reread the parent and any newly plausible map. A storage-key collision resumes
only the same effort; otherwise use the shortest meaningful disambiguator.

Preserve the established effort path while its destination and boundary remain materially
the same, including through wording, phase, branch, ticket, or evidence changes. A materially
different destination or boundary requires a new effort. Never repurpose earlier state to
represent different work.

A recognized effort may be ready, paused, blocked on evidence, waiting for authority, or
waiting for an external dependency. Represent that condition through current state,
blockers, dependencies, and frontier. Do not add a map status or historical label.

Use this brief default map shape, combining, renaming, or omitting an item only when its
purpose is inapplicable or a clearer equivalent exists:

- **Destination** — desired endpoint and material scope or authority boundary.
- **Territory** — major areas, ownership constraints, relationships, or seams.
- **Current state** — smallest truthful summary needed for re-entry.
- **Blockers and dependencies** — only material constraints on progress.
- **Ready frontier** — coherent work that can proceed and the next handoff.
- **Key links** — the few canonical artifacts needed for continuation.

Do not create empty headings. Keep the map low-resolution and link canonical roadmaps,
specifications, ADRs, tickets, and project artifacts instead of copying their bodies or
detailed backlogs. Load only records linked for the current question; do not read every
ledger section or U/E file. If a fresh session must read most supporting records to recover
the current route, reconcile the map instead of adding more supporting detail.

Remaining work is not automatically blocked work. A blocker is an unmet dependency,
unresolved consequential boundary, or missing authority that prevents otherwise coherent
work from proceeding; planned but unperformed validation alone is not a blocker.

The ready frontier contains only coherent scopes whose material dependencies are answered or
explicitly dispositioned by responsible authority. Independent ready work may proceed while
unrelated work remains blocked. Native ticket artifacts, when used, remain the executable
frontier.

## Current knowledge

U/E/F/D classify current knowledge; they are neither a mandatory pipeline nor the effort's
territory or problem hierarchy:

- `U#`: an unresolved consequential question whose separate preservation materially improves
  a later decision or continuation.
- `E#`: independently reusable evidence with a source, scope, observation, and material
  limitations.
- `F#`: a sufficiently supported current scoped descriptive conclusion with truthful
  provenance.
- `D#`: a current committed choice made under actual project authority.

A map may remain the entire result. Do not create U/E/F/D from ceremony, templates, counts, or
category fit. No type must produce another.

Represent areas, seams, relationships, and ownership boundaries in the single `map.md`. Do not
add area identifiers, nested state by domain or phase, parallel maps, or another state hierarchy.

A U# file uses a readable question title and states why it matters. Presence in `unknowns/`
means the question is current and unresolved. Record its resolution mode, dependencies,
sources, and required authority only when useful for re-entry.

An E# file states the reusable observation and enough source, scope, and limitations to evaluate
it. Record when it was observed only when time materially affects meaning, applicability, or
validity. Prefer a direct source link on a fact when separate evidence adds no independent value.

Facts are H2 sections in `facts.md`. Presence means the conclusion is sufficiently supported
and current; a separate status field is not required. Each fact states its scoped descriptive
conclusion and truthful provenance through at least one `Source`, `Authority`, or
`Derived from` value, plus material limitations. Repeated agent summaries are not independent
provenance.

Decisions are H2 sections in `decisions.md`. Presence in `decisions.md` means the choice is
current and committed under actual project authority. Record the choice, authority, decisive
basis or constraints, material consequences, and a revisit condition only when one genuinely
applies.

Wayfinder can record authority; it cannot create it. Assumptions, hypotheses, proposals,
recommendations, inferred preferences, and agent-authored persistence do not become supported
facts or accepted decisions merely because they are recorded. Link the actual human, project
artifact, policy, or valid delegated scope for an authority-owned conclusion.

A fact about another system remains a fact about that system; it does not establish a fact about
the current project. Record a project-specific F# only when project evidence, current source, or
valid project authority supports it. Otherwise preserve an independently useful external
observation as E#, a consequential project uncertainty as U#, or a non-durable proposal in the
map or native specialist artifact, only when that representation independently earns preservation.

Volatile branch, HEAD, working-tree, ahead/behind, and session observations normally remain
execution context. Persist one only when it is an actual continuing authorization constraint,
baseline, or dependency that materially affects future work.

Identifiers are effort-local, positive, and unique within their type. U/E files retain
readable slugs. F/D records retain these exact H2 representations:

- `## F<ID> — <title>`
- `## D<ID> — <title>`

Never renumber or duplicate a current same-type number. Under the lock, allocate one greater
than the highest current same-type identifier, or 1 when none exists. Do not deliberately recycle
interior gaps; a retired highest number is not reserved.

A bare identifier is local shorthand only. Durable references outside the selected effort
use a readable repository-relative link to the exact U/E file, F/D heading, or longer-lived
canonical owner. Inside the effort, prefer links when a path or heading matters.

F/D anchors must retain the established lowercase `f<ID>--<slug>` and `d<ID>--<slug>` forms
derived from those headings' em-dash representation. Reconcile affected references before
renaming a U/E file or F/D heading.

## Safe mutation

Every authorized mutation is serialized through the empty, atomically created
`<effort>/.wayfinder-mutation-lock/` directory. Hold it across affected reads, allocation,
reference checks, writes, renames, and removals, then remove it. Never commit, steal, or assume
an existing lock is abandoned. Without atomic directory creation, do not mutate.

Reread affected state under the lock immediately before writing, renaming, or removing it.
For allocation, parse all current canonical same-type identifiers and reject malformed or
duplicate state before computing the next identifier. Append one F/D section or exclusively
create one U/E file.

Compare the final reread with the state used to plan the mutation. If any affected content
changed concurrently, preserve the conflict and stop or retry from the new truth. Never
silently overwrite another writer or infer that similar-looking content is equivalent.

Interpret only recognized current state required by the operation. Content outside recognized
containers stays opaque and does not block unrelated work. Noncanonical content inside
`unknowns/` or `evidence/` blocks only an affected allocation, rename, or retirement when safe
interpretation, identifier allocation, or target selection is ambiguous. Preserve unknown bytes;
never normalize, migrate, rename, delete, or globally scan them.

Before renaming or retiring state, inspect the selected map, ledgers, U/E files, and known
current canonical references outside the effort for affected identifiers, paths, or heading
anchors. Preserve still-useful information in its current canonical owner and reconcile every
affected current reference before removal. Do not scan unrelated efforts, the entire
repository, or Git history.

Retiring U/E removes only the selected file. Retiring F/D removes only the selected H2 section
and preserves unrelated ledger content byte-for-byte where practical. An otherwise empty ledger
may be removed. After recognized state retires, a confirmed-empty directory may be removed only
nonrecursively; leaving it is valid. Never recursively delete an effort, `unknowns/`, or
`evidence/` directory, or remove a record with a required reference or independent current value.

Whole-effort retirement may remove only recognized files and sections that are safe to retire.
Remove `map.md` last. Never recursively delete the effort directory. If unknown project-owned
content remains, leave its bytes and containing directory untouched; the absence of `map.md` is
sufficient to end recognition.

A failed safety check leaves targets and unrelated project content intact. Do not turn
collision handling, locking, parsing, reconciliation, or retirement into a registry, schema
engine, database, service, migration, or repository-wide cleanup subsystem.

## Reconciliation and settlement

Keep only current coordination needed to navigate the effort. Correction, settlement, and
retirement converge existing state; they do not preserve a second history alongside Git.

When stronger evidence makes the current conclusion known, update the same F# in place with its
current claim, scope, provenance, and material limitations. Narrow it when only a narrower
conclusion remains supported. Retire it after reference reconciliation when it no longer has
independent current value. Do not create a second fact merely to preserve history.

When a material factual question remains unresolved, remove or narrow the unsupported F# and
reconcile references that treated it as supported. Preserve a conflicting observation as E#
only when its source, method, limitations, or reuse value independently justify it; create or
reopen U# only when the precise question has consequential current coordination value. Surface
it in the map only when it affects the route. Do not create an E#/U# pair by template.

Changed factual evidence requires review of dependent decisions and frontier work. It does
not create decision authority or silently rewrite a current choice. A read-only review may
report that a fact appears outdated,
contradicted, or unsupported, but that observation authorizes neither mutation nor a durable
status label.

An answered U# is no longer current unknown state. First preserve any independently useful
evidence, fact, decision, or canonical outcome and reconcile known current references; then
retire the U#. Do not retain it merely as history.

If responsible authority explicitly accepts residual uncertainty for a named boundary, the
question remains factually unresolved: keep its U# current and unresolved, record the authority source and
boundary in a canonical owner, and unblock only that accepted boundary. The disposition
neither answers the U# nor unblocks other dependencies.

When authority changes the choice for the same decision boundary, update the same D# and its
authority, basis, consequences, revisit condition, and affected references. Allocate another D#
only for a distinct current decision. When a D# is no longer current, preserve any lasting result,
reconcile references, and retire it; Git retains the prior choice. Evidence alone cannot do this.

Authorized work that materially changes reality represented by the selected effort performs
bounded reconciliation before claiming completion. Update only affected map consequences,
records, and canonical links. Do not globally scan or reconcile unrelated efforts, copy
canonical artifact bodies, normalize unchanged files, or resolve unrelated questions.

Do not manufacture inconsistency merely because one artifact summarizes, abstracts, or omits
detail held elsewhere. Reconcile only a concrete incompatible statement or a requirement the
current owner no longer satisfies. When evidence or concurrent edits are insufficient for a
truthful update, preserve state and report the blocker.

Keep an effort's map while it may realistically resume, including when it is paused, blocked,
or waiting. Keep its blockers, dependencies, and truthful frontier sufficient for re-entry.

Do not retire `map.md` while consequential unresolved coordination still needs continuity.
Retain the effort, transfer that coordination to a recognized current successor, or preserve
the consequential result or constraint in its canonical owner before retirement.

Settle an effort when it has no legitimate continuation frontier because its destination was
reached, it was intentionally ended, or another direction replaced it. Under one authorized
effort mutation:

1. Preserve lasting outcomes in their canonical owners or native workflow handoffs.
2. Preserve only consequential relationships or constraints that remain currently useful.
3. Reconcile known current references.
4. Retire redundant U/E/F/D state.
5. Retire `map.md` and any remaining recognized state once safe.

Record a useful replacement relationship in its successor or canonical owner. Do not retain the
predecessor map or add tombstones, redirects, archives, registries, history ledgers, or successor
metadata. Do not clean up other efforts; Git preserves history.
