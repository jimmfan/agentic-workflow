# Durable workflow state contract

Repository files, not agent or chat memory, preserve workflow continuity. The single
`active.md` index identifies current work; detailed records use templates from
`../templates/`. Actual code and live evidence remain authoritative for system
behavior. Repository records are authoritative for workflow status and recorded
decisions when chat disagrees.

When sources disagree, apply this precedence unless a narrower accepted project
rule says otherwise: accepted repository decision/state, active workflow
artifact, agent memory, then chat recollection. Agent memory can be a
convenience signal but cannot silently supersede an accepted decision, resume
target, project profile, or verification record. Persist only a concise accepted
result from delegated work, never a raw transcript or private memory.

## Locations and identifiers

- `active.md`: one small active/interrupted workflow and provider pointer.
- `records/<ID>-<slug>.md`: active durable records.
- `archive/<year>/<ID>-<slug>.md`: completed, rejected, or superseded history.

Use stable, never-reused identifiers: `DEC-NNNN` for bounded local decisions,
`IMP-NNNN` for implementation orchestration, `DBG-NNNN` for debugging, and
`IDP-NNNN` for optional internal-developer-platform opportunities. Allocate one
greater than the highest
matching ID in both records and archive. Renaming a slug does not change its ID.
These prefixes apply only to framework-owned state; they never wrap or replace
an identifier owned by Wayfinder or another native tracker.

Wayfinder-owned maps and decision tickets remain outside this allocator. Store a
needed origin or return pointer exactly as Wayfinder supplies it, including the
tracker issue ID or URL, and do not create a parallel `DEC`, `TKT`, `UNK`, `LRN`,
or other alias. A Jira key such as `ARC-384` and a GitHub issue such as `#384` stay
tracker identifiers; the framework does not rewrite them to resemble its local
records. See `../README.md` for the concise Wayfinder legend.

Decision statuses are `proposed`, `provisional`, `accepted`, `rejected`, and
`superseded`. Implementation and debugging records use `active`, `interrupted`,
`blocked`, `completed`, and `superseded`. Provider-owned maps, course workspaces,
specifications, tickets, and reviews keep their native status and identity;
framework state stores only pointers and exact return targets. `blocked` requires
a named blocker and recovery condition. Only decisions may use `provisional`;
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

## Provider artifacts and orchestration pointers

Upstream providers own their maps, course workspaces, research files,
specifications, tickets, TDD loop, and Code Review output. Keep those artifacts
canonical. A durable `IMP` record or `active.md` may store the provider skill,
native identifier or repository-relative link, current target, and exact return
point; it must not copy a provider body or allocate a parallel framework alias.

Use `to-tickets` only when dependency-ordered or independently deliverable
sessions add value. Its tracker or local-markdown ticket identity and frontier
semantics pass through unchanged. Work that fits one coherent implementation
session skips ticket decomposition. A ticket's status or text never grants
permission to run a command, access an external system, or mutate state.

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
`discovery`, `implementation`, `debugging`, `verification`, `provider`, and
`none`. `Provider skill` names the selected upstream skill when the value is
`provider`; `Provider artifact` stores its canonical pointer. A resume request
continues at `Resume target` after validating both the framework record and
provider artifact; it does not reconstruct the task from chat recollection.

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
