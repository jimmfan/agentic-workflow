# Local Wayfinder state contract

Use this contract only after routing selects Wayfinder or a request explicitly continues a relevant effort.
Existing Wayfinder state alone is never a routing signal.

This contract owns recognition, representation, map authoring, identifiers, reconciliation, preservation, pruning, and effort ending.
The Wayfinder skill owns navigation and specialist handoffs; specialists own their methods, and detailed routing owns selection and composition.
The already-loaded root policy's authority, authorization, preservation, and truthfulness rules remain binding.
Use [Agent Workflow terminology](../terminology.md) for cross-cutting meanings when they materially affect interpretation or behavior.

## State model and boundaries

Wayfinder is Agent Workflow's sole durable coordination model.
Load this state contract before effort state.
When resuming, read the selected effort's `map.md` first, then only the ledger sections or E# files relevant to the work.
Specialists retain their methods and create no Agent Workflow durable coordination state.
Wayfinder retains consequential coordination and references across sessions and workflow transitions, not procedures, bookkeeping, or a permanent journal.
Lasting results remain in their designated maintaining artifacts; Git retains committed history.

All content below `.project-efforts/` is project-owned durable data.
Wayfinder interprets or changes only the recognized current paths described below.
All other entries are unrecognized project-owned content: their bytes remain unchanged, and they are not interpreted as Wayfinder state.

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
A map-only effort is valid; supporting ledgers and `evidence/E<ID>-<slug>.md` are created lazily under [Current knowledge](#current-knowledge).
Without `map.md`, a directory is not a recognized resumable effort.

## Effort shape and selection

Objective and scope identify an effort.
Establish that identity before creation; an unresolved route, choice, dependency, or involved area does not itself prevent creation.
Do not materially invent objective or scope from ambiguous user intent.
When materially different interpretations would identify different efforts, obtain the minimum sufficient clarification or resolution before creation.
Scope may be clarified, narrowed, or elaborated as understanding and evidence develop.
Preserve the effort and its path while its objective and substantive scope remain the same, including through wording, phase, branch, ticket, or evidence changes.
A materially different objective or substantive scope requires a new effort; never repurpose earlier state for unrelated work.

The map H1 is the durable human-readable effort name.
Its directory slug is a concise, lowercase, filesystem-safe, hyphen-separated storage key derived from the objective and scope at creation, not a branch, ticket, phase, timestamp, random suffix, or chat title.

An exact effort path must be repository-relative, remain strictly below `.project-efforts/`, cross no symlink in the root, ancestors, effort, or `map.md`, and identify a regular `map.md`.
Reject an unsafe or invalid exact path; do not invent a replacement.

Without an exact path, inspect only the smallest plausible candidate set.
Compare safe maps semantically by objective, scope, and name, and resume only one clear match.
If selection remains ambiguous, do not guess, merge efforts, create a synonymous duplicate, or change affected state.

Create a new effort only when its identity is established, the current user request or accepted project policy authorizes the durable writes, consequential coordination needs preservation across continuations, and no recognized effort represents the same objective and substantive scope.
Selection alone requires no effort, map, or supporting record.
Immediately before creation, reread the parent and any newly plausible map.
A storage-key collision resumes only the same effort; otherwise use the shortest meaningful disambiguator.

## Map authoring

Use this default H2 order beneath the human-readable effort-name H1:

1. **Objective** — the result the effort is intended to achieve.
2. **Scope** — what the effort includes and excludes, including relevant project or authority limits.
3. **Ready work** — concrete authorized scopes that may proceed now.
   Placement never bypasses authority or dependencies.
   When no work is ready, explain why truthfully rather than inventing work.
4. **Current state** — the smallest truthful durable coordination summary needed for safe resumption.
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

Keep the map brief, preserve enough information to resume safely, and link detailed roadmaps, specifications, ADRs, tickets, project artifacts, and sources that establish relevant claims instead of copying their bodies or detailed backlogs.
If a fresh session must read most supporting records to recover the current route, reconcile the map instead of adding more supporting detail.

Represent areas, relationships, and ownership or operating boundaries in the single `map.md`.
Do not add area identifiers, nested state by domain or phase, parallel maps, or another state hierarchy.

### Responsibilities in the map

State consequential participant responsibilities within Areas and relationships, optionally under `### Ownership`; no separate section or matrix is required.
Use precise verbs such as provides, maintains, implements, or decides.
Do not infer an assignment or decision authority from a title, implementation responsibility, access, or agent-authored text.
Naming the decision-maker does not establish approval or authorize execution.
When no designated artifact maintains established effort-specific responsibilities, the map may maintain them directly.
Otherwise link that content, adding a brief source-linked summary only when useful for navigation; do not create a competing matrix or mirror ticket assignments.
Responsibilities, required inputs, and their blocking effects are different relationships and may each deserve mention.
Avoid independently maintained copies of status, dates, and assignments across sections.
Keep consequential unknown responsibility or authority explicit and clarify it when required.
Unknown ownership blocks only work that actually requires it; do not invent assignments or prerequisites, or create U/E/F/D records merely to categorize ownership.

### Dependencies and readiness

Dependencies are required inputs; blockers are conditions currently preventing particular work, not a separate record type.
Do not create separate blocker records, identifiers, statuses, or storage.
Represent ready, paused, or waiting work through map content, without a map status or historical label.
Planned tests, verification, commit or push steps, and other unfinished work are not automatically blockers or dependencies merely because they remain.
Identify the condition preventing particular work: for example, an unsatisfied dependency, unresolved consequential uncertainty, an uncommitted required project choice, or missing action authorization.
An unresolved U# records a question; only its unresolved condition may block affected work.
Delay, inconvenience, risk, or unfinished work alone does not make a condition a blocker.
Assess readiness per scope; independent ready work may proceed while unrelated work remains blocked.

Satisfy dependencies by obtaining their required inputs.
Questions and uncertainties are resolved through appropriate evidence or their resolution method.
Apply root policy to required project choices and action authorization, and the [scoped acceptance rule](#scoped-uncertainty-acceptance) when uncertainty is explicitly accepted.
These changes affect only the corresponding work; none automatically unblocks unrelated work.

When no durable ticket or ticket set exists, the map may state ready work directly.
Once a durable ticket or ticket set exists, that artifact maintains its contents, dependencies, ordering, and readiness.
The map links it with a readable Markdown link and may include a current ready-work reference without copying or mirroring ticket-level state.
A chat-only draft is not a durable ticket or ticket set.

## Current knowledge

Keep a separate record only when it has independently useful coordination, evaluation, retrieval, reference, or update value beyond the map.
This gate applies to all four record types; using one does not require creating the others, and the map may remain the entire result.
Do not create records from ceremony, templates, counts, or category fit.

U/E/F/D are Wayfinder's only durable record types, described below.
A recognized record's presence carries only its type's meaning; U# and E# do not automatically become established project truth.
Apply [Reconcile affected state](#reconcile-affected-state) to every record change; the following rules describe each type's lifecycle.

### Unresolved questions — U#

Represent a U# as an H2 section in `unknowns.md` stating one current consequential question and why it matters.
Create, reopen, or retain it only while unanswered, when its answer could change direction or next work and retaining it helps later decisions within the effort's objective and scope.
Surface it in the map only when it affects the route.
Precision, external uncertainty, or an unexplained condition alone does not satisfy this gate, even for a temporary U#.
Keep incidental or intentionally deferred detail under `Not yet specified` in the map.
Include dependencies, sources, human input or authority, and a sufficiently known resolution method only when useful for continuation.
Preserve consequential uncertainty when its resolution method or authority is unknown; clarify vague concerns without inventing answers or precision.
Short records are valid; `Why it matters:` is a recommended authoring aid, not a required field or recognition criterion.
Map-only questions need no Open questions heading or promotion into U#.
Do not create empty ledgers, split records by size, or maintain dual U# formats.

When a U# is answered, preserve its independently useful result through reconciliation, then prune it; do not retain answered questions as history.
For [scoped uncertainty acceptance](#scoped-uncertainty-acceptance), keep the U# unresolved.

### Evidence — E#

An E# file states evidence using `Source:`, `Scope:`, the existing `Observation` heading or field language, and `Limitations:`.
Record when it was observed only when timing changes meaning, applicability, or validity.
Prefer a direct source link on a fact record when a separate evidence record adds no independent value.
Treat consequential evidence supplied by a user or observed from an external system as independently useful when it materially supports a diagnosis or implementation choice and a future agent cannot reliably reconstruct the needed source, scope, observation, and limitations from durable project sources.
Preserve it before dependent work relies on it or before final response or handoff; use a separate E# when its source, method, limitations, or reuse value justify independent preservation.
Otherwise do not create or retain an E# merely as a transition step.

### Facts — F#

Fact records are H2 sections in `facts.md`.
Presence means the conclusion is sufficiently supported and current, not immutable; no separate status field is required.
State the relation directly: `Source:` identifies a source that establishes the conclusion for its stated scope, `Derived from:` identifies evidence or another record from which it was derived, and `Authority:` may name a source that establishes a policy claim.
Each fact record contains one scoped descriptive conclusion and its material limitations.
Repeated agent summaries are not independent evidence.

A conclusion about another system remains scoped to that system; it does not establish a conclusion about the current project.
Record a project-specific F# only when project evidence or current source sufficiently supports the claim for that scope.
Otherwise preserve independently useful external evidence as E#, a consequential unresolved project question as U#, or a working proposal in the map or specialist artifact, only when that representation independently earns preservation.

When evidence strengthens or narrows a fact, update the same F# with its current conclusion, sources, scope, and material limitations.
When support is invalidated, narrow or remove the unsupported conclusion and reconcile references that treated it as supported.
Prune the F# when no supported conclusion with independent current value remains; do not create a second fact record to preserve history.
Changed factual evidence also requires reviewing dependent decisions and ready work under the authority rules below.

### Decisions — D#

Decision records are H2 sections in `decisions.md`; each holds one current consequential choice committed for its boundary under the root policy's evidence and project-choice gate.
`Authority:` identifies the person, role, or valid delegate whose choice binds that boundary, or references accepted project policy that determines the choice directly; policy is not an entity holding authority.
Record the choice, decisive basis or constraints, material consequences, and a revisit condition only when one genuinely applies.
Reference the project artifact recording the choice when one exists.
Wayfinder can record authority; it cannot create it.
Alternatives, research findings, hypotheses, recommendations, inferred preferences, and routine implementation judgment within delegated scope do not independently justify a D# or replace a binding choice.
Neither persistence nor agent inference turns a proposal into a committed choice or an assumption into a supported conclusion.

When accepted project policy determines a different choice, or the person, role, or valid delegate with project decision authority commits one, update the same D# and its authority, basis, consequences, revisit condition, and affected references.
Allocate another D# only for a distinct current decision.
Prune a D# that no longer records the current binding choice through the common reconciliation sequence; Git retains the prior choice.

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
Append a U/F/D section only if its ledger still matches the content used to plan the append; for all record creation apply the no-overwrite and current-state checks in [Reconcile affected state](#reconcile-affected-state).
Before creating an E# file, recheck the same-type identifiers.

An identity-like ledger section or E# entry that cannot be interpreted safely blocks only operations whose correctness depends on identifying records in that affected ledger or evidence container.
It does not automatically block unrelated work elsewhere; ambiguous content remains unchanged.

A bare identifier is local shorthand only.
Durable references outside the selected effort use a readable repository-relative Markdown link to the exact E# file, U/F/D heading, or longer-lived artifact that maintains the referenced result.
Inside the effort, prefer navigable links when a path or heading matters.

U/F/D anchors must retain the established lowercase `u<ID>--<slug>`, `f<ID>--<slug>`, and `d<ID>--<slug>` forms derived from those headings' em-dash representation.

## Reconciliation and pruning

Reconcile affected current state with current truth, binding project choices, and designated maintaining artifacts.
The common sequence below applies to every record-specific change, pruning operation, and effort ending.

### Reconcile affected state

Reconcile before renaming or pruning recognized state, and before claiming completion when authorized work changes what the selected effort represents.
Read-only work may report stale or conflicting state but does not change it.

Work only within current action authorization, including edits to linked artifacts.
A link neither makes its target a Wayfinder record nor authorizes editing it.
Do not copy maintaining-artifact bodies, normalize unchanged files, resolve unrelated questions, or reconcile unrelated efforts.
Apply root policy's cross-artifact rule: a useful summary or detail held elsewhere is not itself an inconsistency.

If affected state changed or conflicts, evidence is insufficient, or a required edit, preservation check, or reference repair is unauthorized or blocked, stop that operation and report the limitation.
Retain affected records and useful information without creating a competing authoritative copy; independent authorized work may continue.

Use this sequence for every affected reconciliation:

1. **Check current state immediately before mutation.**
   Confirm the affected state and known references still support each planned write, rename, or removal; create targets without overwriting existing paths.
   Use regular files/directories; reject symlinks in selected state paths or their ancestors and paths escaping the selected effort.
   For ledger edits, reread the ledger and affected references, validate the target ID and H2 boundaries, and change only the intended section.
   Preserve neighboring sections, preambles, and unrecognized content; ambiguous boundaries prevent the edit.
2. **Preserve useful information.**
   Retain newly supplied, corrected, and still-valid details that matter to the accepted result, its use, authority, dependencies, or established next work.
   Keep operational detail in the artifact designated to maintain it or a usable durable reference, not only in chat or a high-level summary.
   Keep the map brief and link the detail rather than duplicating the result or retaining everything.
3. **Update affected relationships.**
   Reconcile map content, records, blocking conditions, dependencies, ready work, and known references under [Current knowledge](#current-knowledge).
   Preserve relationships among identities, statuses, sources, and scopes.
   Do not infer verification from a report, commitment from a proposal, action authorization from a committed choice, or fresh verification from recorded external evidence.
   Reassess established dependencies and readiness when choices or contingencies change, without inventing requirements or making every unknown a blocker.
4. **Prune obsolete records after preservation and reference checks.**
   Remove only recognized records without independent current value.
   First verify that still-useful information is retrievable from its designated artifact and affected references resolve.
   A working link is insufficient if its target loses useful evidence, source/scope qualifications, or consequential relationships.
5. **Read back the saved result before claiming a material authorized update complete.**
   Check affected results and references against relevant input and current state, including whether linked targets supply the needed detail.
   Consequential information and relationships must remain usable without the original conversation.
   This is an affected-work check, not a requirement for every message or the whole repository.

#### Before renaming or pruning

Discover incoming references with a narrowly targeted, read-only search of current repository text, including relevant hidden directories.
Match affected paths and heading anchors, accounting for relative links that omit the full path; inspect only relevant matches.
A bare ID outside the effort is not by itself a reference to its record.
This search applies only to the operation, not ordinary resumption or every message; it authorizes no broad document reads, unrelated-effort discovery or reconciliation, or Git-history search.
Report material limits: repository search cannot establish the absence of external or dynamically constructed references.

### Interpret review answers before recording

A review request alone grants no blanket write permission.
When recording is authorized, interpret answers under [Current knowledge](#current-knowledge) without adding statuses:

- Distinguish committed choices from preferences, factual reports, and corrections; apply the evidence and authority gates rather than inferring assignments or approval.
- Preserve conditions and the remaining consequential question in partial answers.
- Accepted uncertainty stays unresolved under the scoped acceptance rule; a scope change may make a question inapplicable without answering it.
- Respect deferrals and preserve qualifications, scope, sources, and authority in the artifact that maintains the result.

Clarify materially ambiguous scope, conditions, or authority; do not reconfirm a clear authorized answer.
Apply the common reconciliation sequence to answered subsets at meaningful round boundaries, not per sentence or through a journal.
Reuse the existing decision for the same boundary and respect specification, ticket, and decision ownership.
Recording a choice does not authorize implementation or publication; runtime-contract and skill Markdown edits are implementation too.
A completed review round does not itself justify tickets, ADRs, U/E/F/D records, archives, or ending the effort.

### Prune one record

Pruning removes a recognized record from current coordination after the common sequence's preservation and reference checks; it does not require committing a transient record first.

Pruning an E# removes only that E# file.
Pruning U/F/D removes only the selected H2 section, stopping at the next H2 or end of file.
Remove an empty ledger only when no useful or unrelated content remains.
Unrelated ledger content remains byte-for-byte unchanged where practical, and unrecognized project-owned content remains unchanged and uninterpreted by Wayfinder.
Never recursively delete an effort or `evidence/` directory.

### Keep or end the effort

Keep an effort's map while it may realistically resume, including when it is paused, blocked, or waiting.
Do not remove `map.md` while consequential unresolved coordination still needs continuity.
Retain the effort, transfer that coordination to a recognized current successor, or preserve the consequential result or constraint in the artifact designated to maintain it before ending the effort.

An effort ends only when it has no legitimate continuation because its objective was achieved, a committed project choice ended it, or continuing coordination belongs to a different objective or substantive scope.
Apply the common sequence across affected records to preserve lasting outcomes and continuing relationships or constraints in their designated maintaining artifacts, then remove `map.md` last.
Never recursively delete the effort directory; the absence of `map.md` ends Wayfinder recognition, and any unrecognized project-owned bytes and their containing directories remain unchanged and uninterpreted by Wayfinder.

Record a useful replacement relationship in its successor or the artifact that maintains the lasting result.
Do not retain the predecessor map or add tombstones, redirects, archives, or successor metadata.
Do not clean up other efforts; Git preserves history.
