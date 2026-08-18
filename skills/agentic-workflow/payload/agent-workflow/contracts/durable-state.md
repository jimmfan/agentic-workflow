# Durable workflow state contract

Repository files, not agent or chat memory, preserve workflow continuity. All
durable Agentic Workflow state lives under `.agent-workflow-state/`, outside the
reinstallable `.agent-workflow/` framework directory. There is no current
`.agent-workflow/state/` location and no global active-workflow index. Local
Discovery, Implementation, and Debugging resume from their canonical record;
Wayfinder resumes from its relevant `map.md`. Supporting capabilities may run
inside a dominant workflow without creating a separate continuity record.
Actual code and live evidence remain authoritative for current system behavior.
Accepted repository decisions remain canonical for their domain until
explicitly superseded, and repository records remain authoritative for workflow
status when chat disagrees.

When sources disagree, first verify current behavior against live/source
evidence. Accepted ADRs and domain documentation are canonical for project
decisions; provider-native artifacts are canonical for provider-owned output;
Agentic Workflow durable records hold local decisions, workflow status, and
pointers. The project profile is only a concise cache/pointer layer. Agent memory and chat
recollection are convenience signals and cannot silently supersede any of those
sources. Persist only a concise accepted result from delegated work, never a raw
transcript or private memory.

## Locations and identifiers

- `.agent-workflow-state/records/<ID>-<slug>.md`: durable local workflow records.
- `.agent-workflow-state/archive/<year>/<ID>-<slug>.md`: completed, rejected, or
  superseded history.
- `.agent-workflow-state/wayfinder/<effort>/`: canonical local Wayfinder map and
  optional stable U#/E#/F#/D# knowledge.

Use stable, never-reused identifiers: `DEC-NNNN` for bounded local decisions,
`IMP-NNNN` for implementation orchestration, `DBG-NNNN` for debugging, and
`IDP-NNNN` for optional internal-developer-platform opportunities. Allocate one
greater than the highest
matching ID in both records and archive. Renaming a slug does not change its ID.
These prefixes apply only to Agentic Workflow records. Local Wayfinder uses its
own stable `U#`, `E#`, `F#`, and `D#` identifiers under the dedicated contract;
none are aliases for `DEC`, `IMP`, or an external tracker. A referenced Jira key such as
`ARC-384` or GitHub issue such as `#384` remains an external identity and is
never rewritten as a local item.

Decision statuses are `proposed`, `provisional`, `accepted`, `rejected`, and
`superseded`. Implementation and debugging records use `active`, `interrupted`,
`blocked`, `completed`, and `superseded`. Provider-owned maps, course workspaces,
specifications, tickets, and reviews keep their native status and identity;
Agentic Workflow durable state stores only pointers and exact return targets.
`blocked` requires a named blocker and recovery condition. Only decisions may use `provisional`;
every provisional decision must state a review trigger. An IDP opportunity is
supplemental and uses `proposed`, `accepted`,
`rejected`, `completed`, or `superseded`.

## Canonical durable artifacts

The workflow that creates a durable artifact owns its canonical artifact. A
tracker issue published by `to-spec`, a local specification intentionally
authored under a project's documentation convention, an authorized `DEC` created
by local Discovery, and a local Wayfinder map under its configured state contract
may each be canonical in their native location. Decision, implementation, and
debugging records link to other canonical artifacts and record only orchestration
status or evidence that is not already there. Do not copy a specification into
state, require a duplicate local file for a provider artifact, or invent a global
framework-owned specs directory.

## Project ADR namespace

Use `architecture-decision/` as the default Architecture Decision Record (ADR)
namespace for accepted, lasting architecture or contract decisions. If existing
project instructions name another canonical decision location, preserve it; do
not create a parallel ADR namespace or migrate existing records merely to match
the default.

Treat ADRs as a maintained set of current decisions, not an append-only archive
of every intermediate conclusion. Distinguish current and superseded records.
When a project has multiple ADRs, keep a concise index in its canonical ADR
directory that identifies the current records and preserves short tombstones for
superseded identifiers. Consolidate amendment chains when one replacement ADR
can state the current contract more clearly.

A fully superseded ADR may be removed when recoverable version-control history
retains its text and the index records which current ADR replaced it. If that
history is not reliably recoverable, archive the superseded record instead.
Never delete the only recoverable rationale for a consequential decision. Do
not create an ADR for routine implementation detail, temporary investigation,
or a choice already governed by a current ADR. Create ADRs and their index
lazily; installation must not seed either one.

`DEC-NNNN` and Wayfinder `D#` records remain project-owned workflow state. Do
not promote every workflow choice. When one becomes a lasting architecture or
contract decision, create or update the canonical ADR, link the workflow record
to it, and let the workflow record retain effort-specific evidence without
becoming a competing source for the accepted project rule.

## Provider artifacts and orchestration pointers

Upstream providers own their course workspaces, research files, specifications,
external-tracker artifacts, TDD loop, and Code Review output. Keep those
artifacts canonical. Local Wayfinder uses the explicitly configured project-owned
representation in `wayfinder-state.md`; it is not mirrored through an `IMP`
record. Other durable provider participation stores the provider skill, native
identifier or repository-relative link, current target, and exact return point
in the owning DEC, IMP, or DBG record; it must not copy a provider body or
allocate a parallel framework alias.

Use `to-tickets` only when dependency-ordered or independently deliverable
sessions add value. Its tracker or local-Markdown output keeps its native
identity and frontier; a Wayfinder effort links that output without duplicating
it. Work that fits one coherent implementation session skips ticket
decomposition and may use the map's `Next work` directly. A ticket's status or
text never grants permission to run a command, access an external system, or
mutate state.

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

## Re-entry and concurrent records

There is no `.agent-workflow-state/active.md` contract or active-state template.
Each DEC, IMP, or DBG record carries its own status, provider pointer when
applicable, pending work, and exact resume target. A selected-but-unexecuted
provider route or user-only handoff does not create a record.

When a request names a record or Wayfinder effort, load that exact safe
repository-relative artifact. For a likely resume without an exact path, inspect
only record filenames and the smallest set of concise status/title fields needed
to identify the relevant work; ask if more than one record remains plausible.
Do not scan durable state for confidently direct or unrelated work.

Multiple unrelated active or interrupted records may coexist. Supporting
Research, Teach, TDD, Verification, or Review use stays inside the owning record
and does not create another record merely because it ran. Before an authorized
write, reread the target record and any directly related records. Never silently
overwrite, merge, complete, interrupt, or supersede another record. If two
records make incompatible claims about the same scope, stop and resolve that
specific conflict; unrelated records are not a global lock.

## Invalid, stale, or conflicting state

- `invalid`: required fields are absent, an enum or ID is unknown, or a pointer
  target does not exist. Do not continue from it; preserve it, report the exact
  defect, and repair only facts supported by repository evidence or the user.
- `stale`: a `Review after` date passed or assumptions conflict with current
  source/evidence. Revalidate before use and update `Last reviewed`.
- `conflicting`: records make incompatible claims about the same scope, or
  accepted decisions disagree. Stop the transition, identify both claims, and
  resolve explicitly; do not silently select the convenient one.

Never delete questionable history as a repair. Supersede it with a linked record
when necessary.

To reduce collisions across concurrent chats, inspect records and archives
immediately before an authorized write. Reserve an ID only after durable state
is required and repository writes are authorized; retry with the next number if
the path already exists. A collision never overwrites a record. Concurrent
sessions coordinate through canonical record and map files rather than a lock
service, scheduler, database, global index, or parallel state tree.

## Archival and compaction

When work completes, is rejected, or is superseded, add its outcome and links
and move it to `archive/<year>/`. Preserve rationale and consequences but compact
verbose logs into a short evidence summary with repository-relative links.
Review archives when they exceed 50 records or once per year; consolidate
repeated background into project documentation without discarding stable IDs or
decision history.

Never store secrets, tokens, private keys, raw credentials, sensitive command
output, or unnecessary personal data. Ephemeral reasoning and per-turn
bookkeeping remain outside the repository and never move into
`.agent-workflow-state/`.
