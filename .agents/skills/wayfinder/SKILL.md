---
description: Keep a lightweight structured map when important unknowns, decisions, dependencies, blockers, or conflicting facts are becoming unreliable to hold in ordinary context.
disable-model-invocation: false
metadata:
    github-path: skills/engineering/wayfinder
    github-pinned: v1.2.3
    github-ref: refs/tags/v1.2.3
    github-repo: https://github.com/mattpocock/skills
    github-tree-sha: 48c3a8b0a9705d6310d37f7f9b53bcb2c55955c7
name: wayfinder
---
# Wayfinder

Wayfinder keeps a lightweight durable map when important unknowns, decisions,
dependencies, blockers, or conflicting facts are becoming unreliable to hold
in ordinary context. Agentic Workflow's effective Wayfinder workflow is a
framework-owned runtime projection derived from Matt Pocock's Wayfinder
methodology. The pinned upstream snapshot remains unchanged as reviewed
provenance and reference; Agentic Workflow owns this runtime's routing,
Git-native state, effort selection, continuation, concurrency, U/E/F/D, and
`to-tickets` handoff contracts.

Use Wayfinder when structured project notes materially reduce the risk of
losing or conflating several consequential state distinctions. Explicit use is
allowed, and an explicit opt-out prevents automatic selection. Keep clear,
bounded, low-risk, unrelated, and read-only work on its minimum useful route;
one ordinary implementation detail or isolated unknown does not justify a map.

When Wayfinder is selected or a request continues a relevant effort, read
`.agent-workflow/contracts/wayfinder-state.md` before the map. Before an
authorized durable write, also read
`.agent-workflow/contracts/durable-state.md`. If the required Wayfinder
contract is missing, treat the installation as incomplete: do not create
tracker or `.scratch/` fallback state, do not run setup to obtain a tracker,
and either stop safely or continue through another truthful authorized route.

## Method

Name the destination before decomposing the route. Keep `map.md` at low
resolution, represent fog honestly, and identify the frontier from current
state and dependencies. Resolve consequential uncertainty incrementally and
load detail only when it becomes relevant. Advance the frontier until the route
is sufficiently clear, then continue the authorized work, hand it off to its
owning workflow, or stop with the map's next work explicit.

- **Destination** states what it means for the route to be clear or the effort
  to reach its intended endpoint.
- **Not yet specified** holds in-scope fog that is not sharp enough to express
  as a precise U#.
- **Out of scope** records work consciously beyond the destination.
- The **frontier** is the smallest coherent next work that can advance now.

Readable names matter. Refer to maps and child knowledge by readable title,
with stable paths and identifiers carried in their links rather than used as
substitutes for names.

## Effort naming, selection, and stable paths

Route before scanning state. The existence of
`.agent-workflow-state/wayfinder/` is not a routing signal.

The map H1 is the durable human-readable effort name. Recognize an effort from
that name, its Destination, its scope boundary, and map context. The directory
slug is only a stable storage key; do not create an Identity section, registry,
or I# record type.

When authoritative context supplies an exact safe repository-relative effort
path, use it, verify it stays inside the Wayfinder state root, and read its
`map.md`. Do not invent a replacement directory.

For a likely resume without an exact path:

1. list effort directory names;
2. use the request and those names to choose the smallest plausible candidate
   set;
3. read only those candidate maps; and
4. compare their H1 names, destinations, scope boundaries, current state, and
   relevant context.

Resume only when one match is sufficiently clear. If several efforts remain
plausible, do not select, merge, write, or create a third synonym. Ask the user
when interaction is available; otherwise report the ambiguity and remain
read-only for the affected state.

Create an effort only when Wayfinder is selected, durable writes are authorized,
structured notes materially help, and no existing effort has the same
substantive destination and scope boundary. A branch, ticket, file, command,
temporary task description, or chat title does not define a new effort.

Choose a concise durable noun phrase for the map H1, such as `Wayfinder runtime
projection`, rather than `Current work` or `Implement ticket 42`. Derive the
slug once from that name: lowercase, filesystem-safe, hyphen-separated,
concise, and recognizable, with no timestamp or random suffix by default.
Immediately before creation, reread the effort-directory listing and inspect
any newly appearing plausible map.

If the slug exists, resume it only when it is the same effort. For a materially
different destination, use the shortest stable meaningful disambiguator and
never overwrite or merge the existing effort. Once created, keep the directory
path stable even if the title improves, phases or branches change, or new
evidence revises the map. Established awkward slugs remain valid.

Clarified wording, changed evidence, implementation progress, resolved
unknowns, and superseded decisions remain in the same effort while the
substantive endpoint and scope boundary stay intact. A materially different
endpoint, bringing explicitly out-of-scope work inside the boundary, or a new
destination after the prior one finishes normally requires a fresh effort.

Maps may state `Status: current | completed | abandoned | superseded` below the
H1. Prefer an explicit current match over a similarly named historical effort
during likely resume. Historical efforts keep their stable paths and remain
readable when directly named or materially relevant, but do not load their
children during ordinary current-effort selection. Legacy maps without a status
remain valid; infer lifecycle only when their outcome and next work make it
unambiguous.

## Canonical state

The only canonical local representation is:

```text
.agent-workflow-state/wayfinder/<stable-effort-slug>/
├── map.md
├── unknowns/       # optional U# files
├── evidence/       # optional E# files
├── facts/          # optional F# files
└── decisions/      # optional D# files
```

`map.md` alone is valid. Keep the map self-contained as the effort's
coordination and re-entry point; it owns current state, blockers, dependencies,
and smallest coherent next work. Link specifications, research, ADRs, source,
tests, and provider-native artifacts from their owning locations rather than
copying them.

Create children lazily only when independent preservation adds value:

- U# is an unresolved consequential question.
- E# is independently useful evidence with provenance, scope, and limitations.
- F# is a sufficiently established scoped descriptive conclusion.
- D# is a committed choice made under project authority.

These are semantic distinctions; never force U# -> E# -> F# -> D# as ceremony.
Keep stable numeric handles plus readable slugs while records are current, such
as `U17-node-group-isolation.md`; never renumber a current record or allow a
same-type duplicate. Allocate one above the highest currently present number,
or `1` when none exists, without searching for interior gaps. A retired number
may reappear in a later repository state; it is not permanently reserved.
Facts link their evidence or direct authoritative sources. Preserve conflicting
evidence; mark an unresolved fact disputed and surface the blocker rather than
silently replacing history. Git owns historical evolution.

When a U# resolves, state the answer and reconcile the map's current state,
blockers, dependencies, fog, and next work. Create or retain E#, F#, or D# only
when each keeps independent current value; the map may be sufficient. U/E/F/D
files are current knowledge roles, not permanent historical identities. Git
preserves retired investigation.

Serialize every map or child mutation with atomic creation of the empty
transient `<effort>/.wayfinder-mutation-lock/` directory. Hold it through the
affected reads, writes, and removals; then remove it. Never commit, populate, or
steal it. If safe atomic locking is unavailable, stop conservatively. Under the
lock, allocation rereads the type directory, rejects duplicate current IDs,
chooses one above the current maximum, and creates without overwrite. One
effort-wide lock remains the smallest mechanism because readable slugs defeat
exact-path collision protection and retirement must exclude concurrent current
reference edits through its final scan and removal.

Before removing a child, preserve independently useful current information and
reconcile every current map and child reference in the selected effort. Under
the effort lock, reread the affected current state immediately before removal
and retain the child if truthful reconciliation is incomplete. Remove it before
releasing the lock. Exact current contents need not already exist in Git;
transient navigation artifacts may disappear. After removal its number is no
longer reserved.

Completing, abandoning, or superseding an effort records that status and a
concise outcome in its map, leaves no next work for that effort, and never
renames or repurposes its directory. Do not move Wayfinder state into the
general workflow-record archive or add allocation metadata, a registry, history
log, or migration sweep.

On resume, load the map first and only the child files needed for the current
question or work. Live source and accepted canonical artifacts outrank stale
state. During authorized mutating work, reconcile only the materially affected
map and children before claiming completion. Read-only analysis, audit,
diagnosis, or review may reason with Wayfinder but must not create or update
state.

Wayfinder does not create implementation work items or a ticket subtree. One
coherent scope may pass directly from the map, a settled D#, or another accepted
source to implementation. When work needs dependency ordering or separately
deliverable sessions, use `to-tickets`; its native artifacts and frontier stay
canonical, and the map records only the pointer and coordination consequence.

Do not create a Wayfinder `.scratch/` mirror, external issue-tracker mirror,
global active index, T# work items, automatic state migration, or a separate
settlement/archive subsystem.
