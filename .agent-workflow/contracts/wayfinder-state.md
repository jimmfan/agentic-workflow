# Local Wayfinder state contract

Use this contract only after routing selects Wayfinder or a request explicitly continues a relevant effort.
Existing Wayfinder state alone is never a routing signal.

This contract owns recognition, representation, map authoring, identifiers, reconciliation, preservation, pruning, and effort ending.
The Wayfinder skill owns navigation and specialist methodology; detailed routing owns workflow selection and composition.
The already-loaded root policy's authority, authorization, preservation, and truthfulness rules remain binding.
Use [Agent Workflow terminology](../terminology.md) for cross-cutting meanings when they materially affect interpretation or behavior.

## State model and boundaries

Wayfinder is Agent Workflow's sole durable coordination model.
Load this state contract before effort state.
When resuming, read the selected effort's `map.md` first, then only the ledger sections or E# files relevant to the work.
No other Agent Workflow durable coordination record may compete with this brief coordination summary.

Each specialist retains its method.
A specialist creates no Agent Workflow durable coordination state.
Wayfinder retains consequential coordination and references across sessions and workflow transitions, not procedures, bookkeeping, or a permanent journal.
Lasting results remain in their designated maintaining artifacts; Git retains committed history.

U/E/F/D are Wayfinder's durable record types.
Blocking is a scoped relationship between a condition and particular work, not a separate Wayfinder record type.
Do not create blocker identifiers, files, ledgers, directories, stores, or statuses.

All content below `.project-efforts/` is project-owned durable data.
Wayfinder interprets or changes only the recognized current paths described below.
All other entries are unrecognized project-owned content: their bytes remain unchanged, and they are not interpreted as Wayfinder state.

Wayfinder recognizes only the contract-defined paths and record forms in the layout below.
Only `map.md` is required:

```text
.project-efforts/
└── <effort>/
    ├── map.md                    # required coordination summary
    ├── facts.md                  # optional current F# ledger
    ├── decisions.md              # optional current D# ledger
    ├── unknowns.md               # optional current U# ledger
    └── evidence/                 # optional reusable E# files
        └── E<ID>-<slug>.md
```

A safe regular `.project-efforts/<effort>/map.md` is recognized as a whole and makes an effort current and resumable.
A map-only effort is valid; `facts.md`, `decisions.md`, `unknowns.md`, and `evidence/E<ID>-<slug>.md` are created lazily under [Current knowledge](#current-knowledge).
Without `map.md`, a directory is not a recognized resumable effort.

## Effort shape and selection

Objective and scope identify an effort.
Do not create a new effort until its objective and scope are sufficiently established to identify it.
Unresolved route, choices, dependencies, or involved areas may be the reason durable coordination is warranted; they do not prevent initial effort creation when that identity is otherwise sufficiently established.
Do not materially invent objective or scope from ambiguous user intent.
When materially different interpretations would identify different efforts, obtain the minimum sufficient clarification or resolution before creation.
Scope may be clarified, narrowed, or elaborated as understanding and evidence develop.
Preserve the effort and its path while its objective and substantive scope remain the same, including through wording, phase, branch, ticket, or evidence changes.
A materially different objective or substantive scope requires a new effort; never repurpose earlier state for unrelated work.

The map H1 is the durable human-readable effort name.
Its directory slug is a concise, lowercase, filesystem-safe, hyphen-separated storage key derived from the objective and scope at creation, not a branch, ticket, phase, timestamp, random suffix, or chat title.
Use only the shortest meaningful disambiguator for a genuine collision.

An exact effort path must be repository-relative, remain strictly below `.project-efforts/`, cross no symlink in the root, ancestors, effort, or `map.md`, and identify a regular `map.md`.
Reject an unsafe or invalid exact path; do not invent a replacement.

Without an exact path, inspect only the smallest plausible candidate set.
Compare safe maps semantically by objective, scope, and name, and resume only one clear match.
Scope wording need not be textually identical.
If selection remains ambiguous, do not guess, merge efforts, create a synonymous duplicate, or change affected state.

Selection does not require persistence.
If assessment leaves no consequential coordination worth preserving across session continuations, create no effort, map, or supporting record.

Create a new effort only when the creation gate above is satisfied, the current user request or accepted project policy authorizes the durable writes, persistence is justified, and no recognized effort represents the same objective and substantive scope.
Immediately before creation, reread the parent and any newly plausible map.
A storage-key collision resumes only the same effort; otherwise use the shortest meaningful disambiguator.

A recognized effort may contain ready or paused work, work waiting on evidence or authority, and work waiting on an external dependency.
Represent each condition through map content that identifies the affected work, relevant dependencies, and any ready work.
Do not add a map status or historical label.

## Map authoring

Use this default H2 order beneath the human-readable effort-name H1:

1. **Objective** — the result the effort is intended to achieve.
2. **Scope** — what the effort includes and excludes, including relevant project or authority limits.
3. **Ready work** — concrete authorized scopes that may proceed now.
   Placement never bypasses authority or dependencies.
   When no work is ready, explain why truthfully rather than inventing work.
4. **Current state** — the smallest truthful durable coordination summary needed for safe resumption.
   Persist only coordination state whose meaning remains relevant to future work.
   Transient Git or session observations, such as a clean working tree, current HEAD, or branch position, remain execution context unless they are genuinely a continuing action authorization constraint, baseline, or dependency.
5. **Areas and relationships** — major areas, their interactions, and consequential participant responsibilities and operating boundaries, not just component names.
6. **Dependencies** — required inputs for particular work.
7. **Blockers** — conditions currently preventing particular work, an assessed absence of blockers, or a material limitation in the blocker assessment.
   Never automatically write `None.` or represent unknown or unassessed conditions as absent.
8. **Key references** — a few readable, navigable sources needed for continuation.

For newly authored default maps, keep Objective, Scope, Ready work, and Blockers visible.
Omit other sections only when genuinely inapplicable, preserving their relative order when present; avoid filler.
A missing answer is not an inapplicable topic.
Preserve uncertainty and **Not yet specified** content without requiring a complete model before independent work proceeds.
These are authoring conventions, never effort-recognition or parser requirements.
Existing maps with alternate layouts remain valid and resumable; do not rewrite them merely to match this default.

### Responsibilities in the map

Make consequential participant responsibilities explicit within Areas and relationships, optionally using an `### Ownership` subsection rather than a mandatory top-level section or responsibility matrix.
Use precise verbs such as provides, maintains, implements, or decides.
For example, when these assignments are established:

```markdown
### Ownership
- Platform team: provides and maintains the test environment.
- Application team: implements the consumer.
- Project lead: decides whether production rollout may proceed.
```

Do not infer an assignment or decision authority from a title, implementation responsibility, access, or agent-authored text.
Naming the decision-maker does not establish approval or authorize execution.
When no designated artifact maintains established effort-specific responsibilities, the map may maintain them directly.
Otherwise link the relevant maintaining content; a brief source-linked orientation summary is useful when it helps navigation without creating a competing matrix or mirroring ticket assignments.
The goal is one authoritative assignment, not zero repeated words.
Responsibilities, required inputs, and their blocking effects are different relationships and may each deserve mention.
Avoid independently maintained copies of status, dates, and assignments across sections.
Use the existing reconciliation rules to update affected summaries and references after authorized changes.
Keep consequential unknown responsibility or authority explicit and clarify it when required.
Unknown ownership blocks only work that actually requires it; do not invent assignments or prerequisites, or create U/E/F/D records merely to categorize ownership.

The map summarizes the effort's current coordination state, conditions blocking particular work, dependencies, and ready work.
When no durable ticket or ticket set exists, the map may state ready work directly.
Once a durable ticket or ticket set exists, that artifact maintains its contents, dependencies, ordering, and readiness.
The map links it with a readable Markdown link and may include a current ready-work reference without copying or mirroring ticket-level state.
A chat-only draft is not a durable ticket or ticket set.

Keep the map brief, preserve enough information to resume safely, and link detailed roadmaps, specifications, ADRs, tickets, project artifacts, and sources that establish relevant claims instead of copying their bodies or detailed backlogs.
If a fresh session must read most supporting records to recover the current route, reconcile the map instead of adding more supporting detail.

### Dependencies and readiness

The Dependencies section records required inputs.
The Blockers section records their or other conditions' current effect on particular work.
Planned tests, verification, commit or push steps, and other unfinished work are not automatically blockers or dependencies merely because they remain.
Identify the condition preventing particular work: for example, an unsatisfied dependency, unresolved consequential uncertainty, an uncommitted required project choice, or missing action authorization.
An unresolved U# records a question; only its unresolved condition may block affected work.
Delay, inconvenience, risk, or unfinished work alone does not make a condition a blocker.
Assess readiness for each scope; the same condition may block one scope without blocking another.
Independent ready work may proceed while unrelated work remains blocked.

Dependencies are satisfied by obtaining the action, artifact, decision, participation from a person, system result, external result, or other input they require.
Questions and uncertainties are resolved through appropriate evidence or their resolution method.
Apply root policy to required project choices and action authorization, and the [scoped acceptance rule](#scoped-uncertainty-acceptance) when uncertainty is explicitly accepted.
These changes affect only the corresponding work; none automatically unblocks unrelated work.

## Current knowledge

U/E/F/D are Wayfinder's distinct durable record types.
They do not form stages or a mandatory U → E → F → D pipeline, and they do not represent the effort's areas, relationships, or problem hierarchy:

- `U#` (unresolved question record) contains one current consequential question that remains unanswered and is independently useful to preserve.
- `E#` (evidence record) contains independently useful evidence with its source, scope, observation, and material limitations.
- `F#` (fact record) contains one current scoped descriptive conclusion judged sufficiently supported.
  The conclusion remains revisable as evidence changes.
- `D#` (decision record) contains one current consequential choice determined directly by accepted project policy or committed by the person, role, or valid delegate with project decision authority.

Keep a separate record only when it has independently useful coordination, evaluation, retrieval, reference, or update value beyond the map.
A map may remain the entire result.
A recognized record's presence carries only its type's meaning; U# and E# do not automatically become established project truth.
Do not create U/E/F/D from ceremony, templates, counts, or category fit.
No type must produce another.

Represent areas, relationships, and ownership or operating boundaries in the single `map.md`.
Do not add area identifiers, nested state by domain or phase, parallel maps, or another state hierarchy.

A U# is an H2 section in `unknowns.md` stating the question and why it matters.
Presence in `unknowns.md` means the question is current and unresolved.
Preserve a precise question separately while unanswered when doing so helps a later developer make or evaluate a decision within the effort's objective and scope.
This is especially useful when the answer requires project decision authority, depends on an external participant or approval, or gates several downstream areas or a consequential boundary.
Precision, ordinary external uncertainty, an unexplained cause, a long list, or a template alone does not justify a U#.
A temporary U# must improve current coordination or later continuation, not serve create-and-prune ceremony.
Keep incidental or intentionally deferred detail under `Not yet specified` in the map.
Record its resolution method, dependencies, sources, and required human input or authority only when they help later resumption or continuation.
Short records are valid.
Clarify vague concerns into useful questions without padding or invented precision; link substantial results in their maintaining artifacts.
Keep map-only questions valid, with no mandatory Open questions heading or promotion into U#.
Do not create an empty ledger, retain answered sections as a completed archive, split records by size, or maintain dual U# formats.

An E# file states independently useful evidence using `Source:`, `Scope:`, the existing `Observation` heading or field language, and `Limitations:`.
Record when it was observed only when timing changes meaning, applicability, or validity.
Prefer a direct source link on a fact record when a separate evidence record adds no independent value.

Fact records are H2 sections in `facts.md`.
Presence means the recorded conclusion is sufficiently supported and current; a separate status field is not required.
State the relation directly: `Source:` identifies a source that establishes the conclusion for its stated scope, `Derived from:` identifies evidence or another record from which it was derived, and `Authority:` may name a source that establishes a policy claim.
Each fact record contains its scoped descriptive conclusion and material limitations.
Repeated agent summaries are not independent evidence.

Decision records are H2 sections in `decisions.md`.
Presence in `decisions.md` means the recorded choice is current and committed for its decision boundary: accepted project policy determines the choice directly, or the person, role, or valid delegate with project decision authority committed it.
Keep the existing `Authority:` representation for the source of that binding choice.
Record the choice, decisive basis or constraints, material consequences, and a revisit condition only when one genuinely applies.

Create a D# only for a consequential current choice committed under that gate.
Alternatives still under consideration, research findings, evidence changes, hypotheses, recommendations, agent inference, and routine implementation judgment within already delegated scope do not independently justify a D#.
They may inform a choice or require review of an existing decision, but they cannot create project decision authority or replace a current choice.

Apply the root policy's evidence and project-choice gate before recording a committed choice.
Record the person, role, or valid delegate with project decision authority where that authority is required.
When accepted project policy determines a choice directly, reference that policy without describing it as an entity that holds authority.
Wayfinder can record authority; it cannot create it.
Assumptions, proposals, inferred preferences, and agent-authored persistence do not become supported conclusions or committed choices merely because they are recorded.
Reference the project artifact that records it when one exists.

A conclusion about another system remains scoped to that system; it does not establish a conclusion about the current project.
Record a project-specific F# only when project evidence or current source sufficiently supports the claim for that scope.
Otherwise preserve independently useful external evidence as E#, a consequential unresolved project question as U#, or a working proposal in the map or specialist artifact, only when that representation independently earns preservation.

### Scoped uncertainty acceptance

When the person, role, or valid delegate with project decision authority explicitly accepts unresolved uncertainty for a named boundary, record that authority and boundary in the project artifact recording the committed choice.
Keep the question and any U# current and unresolved; unblock only the named boundary.
Acceptance neither answers the question nor commits a broader project choice, authorizes an unrelated action, or satisfies another dependency.
It alone establishes neither a new dependency for other work nor its readiness.
Preserve independently established restrictions and require relevant evidence or authority for an additional dependency.

### Identifiers and references

Identifiers are effort-local, positive, and unique within their type.
E# files retain readable slugs.
U/F/D records retain these exact H2 representations:

- `## U<ID> — <question>`

- `## F<ID> — <title>`
- `## D<ID> — <title>`

Never renumber or duplicate a current same-type number.
Allocate one greater than the highest current same-type identifier, or 1 when none exists.
Do not deliberately recycle interior gaps; a pruned highest number is not reserved.

Immediately before assigning an identifier, reread all recognized same-type identifiers and reject malformed or duplicate identifiers in current coordination state.
Append a U/F/D section only if its ledger still matches the content used to plan the append.
Before creating an E# file, recheck the same-type identifiers and create the target without overwriting an existing path.

An identity-like ledger section or E# entry that cannot be interpreted safely blocks only operations whose correctness depends on identifying records in that affected ledger or evidence container.
It does not automatically block unrelated work elsewhere; ambiguous content remains unchanged.

A bare identifier is local shorthand only.
Durable references outside the selected effort use a readable repository-relative Markdown link to the exact E# file, U/F/D heading, or longer-lived artifact that maintains the referenced result.
Inside the effort, prefer navigable links when a path or heading matters.

U/F/D anchors must retain the established lowercase `u<ID>--<slug>`, `f<ID>--<slug>`, and `d<ID>--<slug>` forms derived from those headings' em-dash representation.
Reconcile affected references before renaming an E# file or U/F/D heading.

### Explicit conversion of old question files

Individual `unknowns/U<ID>-<slug>.md` files are not a second current representation.
Absence of `unknowns.md` does not establish absence of unresolved questions: inspect the selected map and relevant maintaining artifacts, and report encountered unconverted or unassessed old-format data.
Preserve that data unless the current request explicitly authorizes bounded conversion of those files.
Do not perform installer migration, downstream sweeps, or automatic conversion or deletion of ordinary document question lists.

For an authorized conversion, read the affected files and ledger, preserve IDs, contents, sources, relative-link meaning, and qualifications, and plan exact target sections and affected reference repairs.
Recheck inputs immediately before mutation; collisions, malformed or duplicate IDs, ambiguous section boundaries, unsafe paths, or intervening changes stop only affected operations.
Never overwrite a ledger: create it without overwriting an existing path or add only checked noncolliding sections to its current content.
Verify every converted target and repaired reference before removing the corresponding old file.
Remove only explicitly converted files, never directories recursively; preserve and report remaining old or unrecognized data.
An interrupted conversion requires checking actual targets, sources, and references before continuing; do not infer completion from a missing ledger or partial copy.

## Reconciliation and pruning

Use the common sequence below for affected current state, including every record-specific change, pruning operation, and effort ending.
Reconcile current coordination with current truth, binding project choices, and designated maintaining artifacts.
Pruning removes only recognized records whose useful results are preserved and references reconciled; ending an effort is separate.

### Reconcile affected state

Reconciliation is required before renaming or pruning recognized state and whenever work authorized within the current scope changes reality represented by the selected effort before claiming completion.
Read-only work may report stale or conflicting state but does not change it.

Plan a mutation from current affected state.
Immediately before writing, renaming, or removing, confirm that the directly affected state and known affected references still support the planned mutation.
Create a new target without overwriting an existing path.
If affected state changed or conflicts, stop the affected operation rather than overwrite it; independent work may proceed.
For ledger edits, reread the ledger and affected references, validate the target ID and H2 boundaries, and edit only the intended section.
Protect neighboring sections, preambles, and unrecognized content; ambiguous boundaries prevent that edit.
All selected Wayfinder state paths, including their ancestors, ledgers, and E# files, must use regular files/directories without crossing symlinks or escaping the selected effort.

Before renaming or pruning state, inspect the selected map, ledgers, E# files, and known current references outside the effort for affected identifiers, paths, or heading anchors.
Do not scan unrelated efforts, the entire repository, or Git history.

Use this common sequence for every affected reconciliation:

1. Preserve newly supplied, corrected, and still-valid information whose loss would materially affect the accepted result, its use, authority, dependencies, or established next work.
   Keep operational details in the artifact designated to maintain the result or a usable durable reference, not solely in chat or a high-level summary.
   Keep the map brief and link that detail; do not duplicate the detailed result or retain everything.
2. Update affected map content, records, conditions blocking affected work, dependencies, ready work, and known references.
   Preserve the relationships among identities, statuses, sources, and scopes under the authority and evidence rules in `## Current knowledge`.
   Do not infer verification from a report, commitment from a proposal, action authorization from a committed choice, or fresh verification from recorded external evidence.
   When a choice or contingency changes, reconcile its consequences for established dependencies and ready work without inventing requirements or making every unknown a blocker.
3. Prune only recognized records that no longer have independent current value.
   Before pruning, verify that any still-useful information in the record is retrievable from its designated maintaining artifact and that affected references resolve.
   If preservation cannot be established, retain the affected record without blocking independent work.
4. Before claiming a material authorized update complete, reread the affected saved results and references against the relevant input and current state.
   Check that consequential details and relationships remain retrievable and usable without the original conversation, including whether a retained reference actually supplies the needed detail.
   Bound this check to affected work; it is not required for every message or across the whole repository.

Update only affected records and references to artifacts that maintain relevant results.
Do not copy those artifact bodies, normalize unchanged files, resolve unrelated questions, or reconcile unrelated efforts.
Apply root policy's cross-artifact rule: a useful summary or omitted detail held elsewhere is not itself an inconsistency.
Linking a project artifact does not make it a Wayfinder record or grant authorization to write it.
When evidence is insufficient for a truthful update, preserve state and report what prevents the affected work from proceeding.

### Apply record-specific changes

When evidence strengthens or narrows an F#, update the same F# in place with its current scoped conclusion, the source or records from which it was derived, and material limitations.
When evidence invalidates its support, narrow or remove the unsupported conclusion and reconcile references that treated it as supported.
Prune the F# when no supported conclusion with independent current value remains.
Do not create a second fact record merely to preserve history.

When an observation independently earns E# preservation through its source, method, limitations, or reuse value, preserve it as E#.
Otherwise do not create or retain an E# merely as a transition step.
Create or reopen a U# only when the precise unresolved question has consequential current coordination value, and surface it in the map only when it affects the route.
Do not create an E#/U# pair by template.

When a U# is answered, preserve any independently useful result through the common sequence and prune the U#; an answered question is no longer a current unresolved question and is not retained as history.
For accepted uncertainty, apply [Scoped uncertainty acceptance](#scoped-uncertainty-acceptance); do not prune the unresolved U#.

When factual evidence changes, review dependent D# records and ready work under the authority rule in `## Current knowledge`.
When accepted project policy changes the choice for a decision boundary, or the person, role, or valid delegate with project decision authority commits a different choice, update the same D# and its authority, basis, consequences, revisit condition, and affected references.
Allocate another D# only for a distinct current decision.
When a D# no longer records the current binding choice, apply the common sequence and prune it; Git retains the prior choice.

### Prune one record

Before removal, apply the common sequence's preservation, reference reconciliation, and pre-pruning retrievability check.
Pruning does not require committing a transient record first.

Pruning E# removes only the selected file.
Pruning U/F/D removes only the selected H2 section, stopping at the next H2 or end of file.
Remove an empty ledger only when no useful or unrelated content remains.
Unrelated ledger content remains byte-for-byte unchanged where practical, and unrecognized project-owned content remains unchanged and uninterpreted by Wayfinder.
Never recursively delete an effort, `unknowns/`, or `evidence/` directory.

### Keep or end the effort

Keep an effort's map while it may realistically resume, including when it is paused, blocked, or waiting.
Keep its map content current enough for safe resumption, including conditions blocking particular work, dependencies, and any ready work.
Do not remove `map.md` while consequential unresolved coordination still needs continuity.
Retain the effort, transfer that coordination to a recognized current successor, or preserve the consequential result or constraint in the artifact designated to maintain it before ending the effort.

An effort ends only when it has no legitimate continuation because its objective was achieved, a committed project choice ended it, or continuing coordination belongs to a different objective or substantive scope.
Before removing recognized Wayfinder records, ensure lasting outcomes and continuing relationships or constraints have a designated maintaining artifact and reconcile affected references.
Apply the common sequence across affected records, then remove `map.md` last.
Never recursively delete the effort directory; the absence of `map.md` ends Wayfinder recognition, and any unrecognized project-owned bytes and their containing directories remain unchanged and uninterpreted by Wayfinder.

Record a useful replacement relationship in its successor or the artifact that maintains the lasting result.
Do not retain the predecessor map or add tombstones, redirects, archives, or successor metadata.
Do not clean up other efforts; Git preserves history.
