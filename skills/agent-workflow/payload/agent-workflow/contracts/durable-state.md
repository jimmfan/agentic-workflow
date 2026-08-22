# Durable project state contract

Repository files, not agent or chat memory, preserve project continuity. All
durable Agent Workflow state lives under `.agent-wayfinder/`, outside the
reinstallable `.agent-workflow/` directory. Lifecycle operations treat every
entry below that root as opaque project-owned data.

Wayfinder is the sole framework-owned durable coordination layer. Discovery,
Debugging, Implementation, Research, Prototype, Domain Modeling, Teach, TDD,
Verification, and Review create no framework continuity record merely because
they run. Provider-native artifacts remain canonical in their owning locations.

Current framework-authored durable state is limited to:

- `.agent-wayfinder/<effort>/`: map-first coordination under the
  dedicated Wayfinder contract;
- `.agent-wayfinder/project-profile.md`: an optional advisory cache under
  the project-profile contract; and
- `.agent-wayfinder/records/IDP-NNNN-<slug>.md`: an optional accepted
  internal-developer-platform opportunity under the narrow rule below.

There is no global active index and no current DEC, IMP, or DBG allocation,
resume, conflict, or archive protocol.

## Canonical sources and artifacts

Live source and observed behavior outrank stale summaries. Accepted ADRs and
domain documentation are canonical for project decisions; provider-native
research, specifications, tickets, learning workspaces, reviews, and other
artifacts are canonical for their output. Wayfinder stores only consequential
coordination and readable pointers, never a copied provider body or transcript.

The project profile is a concise cache and command contract, not project truth.
Agent memory and chat recollection cannot silently supersede repository evidence
or accepted artifacts.

Use `architecture-decision/` as the default Architecture Decision Record (ADR)
namespace. Preserve an existing project convention instead of creating a
parallel namespace or migrating it. Treat ADRs as maintained current decisions,
not an append-only workflow log. Keep a concise index when several ADRs exist,
preserve superseded tombstones, and retain the only recoverable rationale for a
consequential choice.

Do not promote every workflow choice. Create or update an ADR only when a
lasting architecture or contract decision warrants it. A current Wayfinder D#
may link that ADR while remaining effort-scoped coordination rather than a
competing source of project policy.

## Optional IDP opportunities

Capture an `IDP-NNNN` record only when work exposes meaningful recurring manual
or cross-team friction with a plausible reusable platform improvement and an
explicit request or accepted project policy authorizes the write. Do not create
one for an isolated inconvenience or during read-only work.

Allocate one greater than the highest matching ID in both `records/` and
`archive/`. Immediately before an authorized write, reread those filenames and
create the selected path without overwriting. A collision retries with the next
number. Status is `proposed`, `accepted`, `rejected`, `completed`, or
`superseded`; completed or superseded records may move to
`.agent-wayfinder/archive/<year>/`.

Use this compact shape directly; no separate template or workflow is required:

```markdown
# IDP-NNNN: Opportunity title
- Type: idp-opportunity
- Status: proposed
- Created: YYYY-MM-DD

## Problem and discovery
Problem, recurrence evidence, and how it was discovered.

## Current process and dependencies
Manual process, required information, and involved teams or systems.

## Potential platform behavior
Proposed documentation, automation, template, validation, or guided workflow.

## Human control and notes
Approval boundary, constraints, owner, and next review.
```

## Controlled promotion

At completion, classify useful lessons as project-specific facts, reusable
workflow guidance, private learning, or transient observations. Persist only
evidence-backed material that remains useful at the narrowest appropriate
scope. Promotion into `AGENTS.md`, a skill, project profile, ADR, or durable
state is a separate authorized change with a reviewable diff; raw transcripts
and private memory are never repository truth.

## Legacy workflow records

Existing DEC, IMP, DBG, record, archive, active-index, or other pre-current
files remain project-owned historical data. Install, update, status, remove,
reinstall, routing, and provider repair never delete, migrate, rewrite, validate,
allocate from, resume, or normalize them. A directly named legacy file may be
read as historical project evidence, but it is not a current framework re-entry
point. When its live work still matters, an authorized project owner manually
reconciles only the consequential current frontier into Wayfinder or another
canonical project artifact.

Never store secrets, tokens, private keys, raw credentials, sensitive command
output, or unnecessary personal data in durable state. Never delete
questionable history as a repair.
