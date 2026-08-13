# Durable workflow state contract

Repository files, not agent or chat memory, preserve workflow continuity. The single
`active.md` index identifies current work; detailed records use templates from
`../templates/`. Actual code and live evidence remain authoritative for system
behavior. Repository records are authoritative for workflow status and recorded
decisions when chat disagrees.

When sources disagree, apply this precedence unless a narrower accepted project
rule says otherwise: accepted repository decision/state, active workflow
artifact, agent memory, then chat recollection. Codex or Hermes memory can be a
convenience signal but cannot silently supersede an accepted decision, resume
target, project profile, or verification record. Persist only a concise accepted
result from delegated work, never a raw Hermes transcript or private memory.

## Locations and identifiers

- `active.md`: one small active/interrupted workflow pointer.
- `records/<ID>-<slug>.md`: active durable records.
- `archive/<year>/<ID>-<slug>.md`: completed, rejected, or superseded history.

Use stable, never-reused identifiers: `DEC-NNNN` for decisions, `IMP-NNNN` for
implementation coordination, `TKT-NNNN` for local implementation tickets,
`DBG-NNNN` for debugging, `LRN-NNNN` for learning, and `IDP-NNNN` for optional
internal-developer-platform opportunities. Allocate one greater than the highest
matching ID in both records and archive. Renaming a slug does not change its ID.

Decision statuses are `proposed`, `provisional`, `accepted`, `rejected`, and
`superseded`. Implementation, debugging, and learning records use `active`,
`interrupted`, `blocked`, `completed`, and `superseded`. Tickets use `draft`,
`ready`, `active`, `blocked`, `completed`, and `superseded`. `blocked` requires a
named blocker and recovery condition. Only decisions may use `provisional`;
every provisional decision must state a review trigger. An IDP opportunity is
supplemental, never an active workflow, and uses `proposed`, `accepted`,
`rejected`, `completed`, or `superseded`.

## Durable specifications

Specifications are project-owned engineering documents, not workflow-state
records. Put them in the consuming project's normal documentation location named
under the profile's `Important paths`; if no location is established, agree one
before creating a durable spec. Decision, implementation, and debugging records
link to the canonical specification and record only status or evidence that is
not already there. Do not copy a specification into state or invent a global
framework-owned specs directory.

## Durable decomposition and actionable frontier

Decompose only an approved canonical specification whose implementation needs
multiple dependency-ordered, parallel, or independently deliverable sessions.
Work that fits one coherent implementation session remains one `IMP` record or
no durable record. An `IMP` coordinator links the specification, canonical
ticket set, and current frontier; it never copies complete ticket bodies.

Use local `TKT` records from `../templates/ticket-record.md` when no accepted
native tracker owns the tickets. When an installed native ticket system is used,
its issue bodies are canonical: the coordinating `IMP` and active index contain
only native identifiers or links, current ticket, frontier, and concise
disposition. Do not create shadow `TKT` records or mirror native issue content.

Every ticket has stable blocker references. Reject self-dependencies, missing
blockers, and cycles. The actionable frontier is every incomplete,
non-superseded `ready` ticket whose blockers are all `completed` and which has no
separately named active blocker. Recompute it after Verification and any required
Review. An incomplete ticket set with no frontier is invalid or blocked and must
name the exact condition before work resumes unless one valid ticket is already
`active`. Ticket readiness never grants
permission to run a command, access an external system, or mutate state.
`ready` means its definition is approved and implementation-ready, not that it
is currently actionable; dependency edges gate the frontier. Reserve `blocked`
for an exceptional named condition beyond declared ticket dependencies.
Implementation moves a selected frontier ticket to `active`; an interrupted
task resumes that active ticket through `active.md` rather than putting it back
on the ready frontier.

## Optional IDP opportunities

Capture an `IDP-NNNN` record only when work exposes meaningful recurring manual
or cross-team friction with a plausible reusable internal-developer-platform
improvement. Do not interrupt routine work or create a record for an isolated
inconvenience. Persistence additionally requires an explicit user request or
accepted project policy authorizing retrospective state writes. During a
read-only audit, review, explanation, or status request, report a candidate but
do not write one. Use this compact shape directly; no separate workflow or
template is required:

```markdown
# IDP-NNNN: Opportunity title
- Type: idp-opportunity
- Status: proposed
- Created: YYYY-MM-DD

## Problem and discovery
Problem, how it was discovered, and evidence that it recurs.

## Current process and dependencies
Manual process, information required, and teams or systems involved.

## Potential platform behavior
Proposed behavior and solution type: documentation, automation, template,
validation, or guided workflow.

## Human control and notes
Whether human approval remains required, constraints, owner, and next review.
```

## Retrospective and controlled promotion

At completion, classify useful lessons as project-specific facts, reusable
workflow guidance, private agent learning, or transient observations. Persist
only evidence-backed material that will remain useful, at the narrowest
appropriate scope, after checking existing instructions for duplication and
staleness. A read-only audit or review may report a candidate but cannot create
or change an `IDP` record, shared instruction, profile, decision, or durable
state without authorization.

Private agent memories, learned skills, and curator output are never repository
truth. Promotion into `AGENTS.md`, `.agents/skills`, the project profile, a
decision, or durable state is a separate controlled-learning change with
reusable evidence and an explicit reviewable diff; raw transcripts are not
promoted.

## Active index rules

`active.md` follows `../templates/active-state.md`. Use `none` when idle. It must
name at most one active workflow, at most one interrupted workflow, existing
record paths, a precise pending question, and an actionable resume target. The
interrupted workflow cannot equal the active workflow. Update the index only at
workflow transitions, not after every message.

Allowed values for `Active workflow` and `Interrupted workflow` are
`discovery`, `teach`, `decomposition`, `implementation`, `debugging`,
`verification`, `review`, and `none`. The router maps each non-`none` value to
the matching `workflow-*` skill. A resume request with an active value continues
at `Resume target` after validation; it does not reconstruct the task from chat
recollection.

## Invalid, stale, or conflicting state

- `invalid`: required fields are absent, an enum or ID is unknown, or a pointer
  target does not exist. Do not continue from it; preserve it, report the exact
  defect, and repair only facts supported by repository evidence or the user.
- `stale`: a `Review after` date passed or assumptions conflict with current
  source/evidence. Revalidate before use and update `Last reviewed`.
- `conflicting`: multiple records claim to be active, a record contradicts the
  index, or accepted decisions disagree. Stop the transition, identify both
  claims, and resolve explicitly; do not silently select the convenient one.

Never delete questionable history as a repair. Supersede it with a linked record
when necessary.

If `active.md` is missing, there is no trustworthy durable resume pointer. Report
the missing state and do not infer one from chat. Recreate an idle index from the
template only when repository evidence or the user confirms that no workflow was
active; otherwise repair it from explicitly confirmed facts.

To reduce collisions across concurrent chats, inspect records and archives
immediately before writing, reserve the selected ID by creating its record before
delegating work, and retry with the next number if the path already exists. A
collision never overwrites a record. Prefer one parent workflow owner; concurrent
sessions coordinate through the active index.

## Archival and compaction

When work completes, is rejected, or is superseded, add its outcome and links,
move it to `archive/<year>/`, and remove its pointer from `active.md`. Preserve
rationale and consequences but compact verbose logs into a short evidence summary
with repository-relative links. Review archives when they exceed 50 records or
once per year; consolidate repeated background into project documentation without
discarding stable IDs or decision history.

Never store secrets, tokens, private keys, raw credentials, sensitive command
output, or unnecessary personal data. Put unavoidable local transient material
under `.ai-workflow-local/` and add that path to the consuming repository's
`.gitignore`; the framework creates no such directory by default.
