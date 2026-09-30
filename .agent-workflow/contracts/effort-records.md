# Effort records contract

Read this contract only after the [state contract](effort-state.md) and only when creating, changing, renaming, pruning, or relying on a U/E/F/D record.
The state contract's boundaries, [rule for keeping separate records](effort-state.md#current-knowledge), and [reconciliation sequence](effort-state.md#reconcile-affected-state) remain binding, as do the root policy's authority, authorization, preservation, and truthfulness rules.

## Unresolved questions — U#

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
For [scoped uncertainty acceptance](effort-state.md#scoped-uncertainty-acceptance), keep the U# unresolved.

## Evidence — E#

An E# file states evidence using `Source:`, `Scope:`, the existing `Observation` heading or field language, and `Limitations:`.
Record when it was observed only when timing changes meaning, applicability, or validity.
Prefer a direct source link on a fact record when a separate evidence record adds no independent value.
Preserve evidence under the state contract's [evidence preservation rule](effort-state.md#current-knowledge).

## Facts — F#

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

## Decisions — D#

Decision records are H2 sections in `decisions.md`; each holds one current consequential choice committed for its boundary under the root policy's evidence and project-choice gate.
Use `Authority:` to identify the person, role, or valid delegate whose choice binds that boundary, or to cite accepted project policy that directly determines the choice.
Record the choice, decisive basis or constraints, material consequences, and a revisit condition only when one genuinely applies.
Reference the project artifact recording the choice when one exists.
Wayfinder can record authority; it cannot create it.
Alternatives, research findings, hypotheses, recommendations, inferred preferences, and routine implementation judgment within delegated scope do not independently justify a D# or replace a binding choice.
Neither persistence nor agent inference turns a proposal into a committed choice or an assumption into a supported conclusion.

When accepted project policy determines a different choice, or the person, role, or valid delegate with project decision authority commits one, update the same D# and its authority, basis, consequences, revisit condition, and affected references.
Allocate another D# only for a distinct current decision.
Prune a D# that no longer records the current binding choice through the common reconciliation sequence; Git retains the prior choice.

## Identifiers and references

Identifiers are effort-local, positive, and unique within their type.
E# files retain readable slugs.
U/F/D records retain these exact H2 representations:

- `## U<ID> — <question>`
- `## F<ID> — <title>`
- `## D<ID> — <title>`

Allocate one greater than the highest current same-type identifier, or 1 when none exists.
Do not deliberately recycle interior gaps when allocating; a pruned highest number is not reserved.

Renumber only on an explicit current user request specifying the effort and record type.
Assign 1 through N in ascending order of current numbers, changing only identifiers and affected references.
Follow the [reconciliation sequence for renames](effort-state.md#reconcile-affected-state), including incoming-reference discovery.
Update all affected links and same-effort mentions, then read back that each still identifies the same record.

Immediately before assigning an identifier, reread all recognized same-type identifiers and reject malformed or duplicate identifiers in current coordination state.
Append a U/F/D section only if its ledger still matches the content used to plan the append; for all record creation apply the no-overwrite and current-state checks in [Reconcile affected state](effort-state.md#reconcile-affected-state).
Before creating an E# file, recheck the same-type identifiers.

An identity-like ledger section or E# entry that cannot be interpreted safely blocks only operations whose correctness depends on identifying records in that affected ledger or evidence container.
It does not automatically block unrelated work elsewhere; ambiguous content remains unchanged.

A bare identifier is local shorthand only.
Durable references outside the selected effort use a readable repository-relative Markdown link to the exact E# file, U/F/D heading, or longer-lived artifact that maintains the referenced result.
Inside the effort, prefer navigable links when a path or heading matters.

U/F/D anchors must retain the established lowercase `u<ID>--<slug>`, `f<ID>--<slug>`, and `d<ID>--<slug>` forms derived from those headings' em-dash representation.

## Prune one record

Pruning removes a recognized record from current coordination after the common sequence's preservation and reference checks; it does not require committing a transient record first.

Pruning an E# removes only that E# file.
Pruning U/F/D removes only the selected H2 section, stopping at the next H2 or end of file.
Remove an empty ledger only when no useful or unrelated content remains.
Unrelated ledger content remains byte-for-byte unchanged where practical, and unrecognized project-owned content remains unchanged and uninterpreted by Wayfinder.
Never recursively delete an effort or `evidence/` directory.
