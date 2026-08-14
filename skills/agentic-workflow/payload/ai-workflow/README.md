# Installed AI workflow orchestration

ai-workflow is the routing and integration layer. Mature planning, learning,
research, specification, ticketing, implementation, TDD, and Code Review
methods come from curated upstream skills installed under `.agents/skills/`.
Their tested source, version, revision, subtree identities, complete file lists,
and capability mapping are declared in `providers.json`.

The root `AGENTS.md` is the small always-on router. Detailed skill bodies load
only when the host actually invokes them, not merely when the router selects a
user-only handoff. Framework-owned local skills remain for bounded Discovery,
diagnosis with authorization controls, implementation integration, and
acceptance/integration Verification:

```text
request -> router
        -> direct
        -> dominant workflow/activity + optional capabilities
        -> invocation policy -> execute | exact handoff | unavailable
        -> upstream wayfinder | teach | research
        -> local discovery | debugging
        -> upstream to-spec -> to-tickets -> implement
        -> local verification
```

Routing selection is not execution. Codex and GitHub Copilot may invoke skills
declared `implicit`; for a `user-only` selection the router returns the exact
`$skill-name` Codex or `/skill-name` Copilot handoff and does not claim that the
provider ran, create its artifacts, or write workflow state. Claude Code can
read the root `CLAUDE.md`, but neither local nor provider skill bodies are
projected from `.agents/skills` into Claude's native `.claude/skills` location.
This installation therefore supports policy classification and direct work on
Claude while reporting every skill-backed route unavailable.

A capability can support another dominant workflow or be dominant when it
directly matches intent. This permits Wayfinder plus Research or Implementation
plus Research/Debugging/Verification without treating every capability as a
durable state transition. It remains an instruction contract, not a scheduler.

`implement` already composes `tdd` and `code-review`; the router does not invoke
them again mechanically. A direct `code-review` remains available when the user
requests its fixed-point Standards/Spec contract outside an implement run.

## Provider lifecycle

The public ai-workflow bootstrap is the only required adoption path. Internally
it delegates upstream installation to GitHub CLI `gh skill`, pins every skill to
the tested tag, then validates injected source/ref/tree-SHA metadata and complete
adjacent resources. The package declaration owns the canonical SHA-256 for every
upstream file; verification removes only the exact validated GitHub provenance
block from `SKILL.md` before comparing its source hash. `provider-state.json`
records only ai-workflow lifecycle origin and installed-file checksums. Those
checksums are cleanliness evidence, not content authority, and the state file is
not a second package manager.

Pinned providers do not float during normal updates. A maintainer upgrades the
declaration to a reviewed stable tag and subtree identities, runs live provider
compatibility checks plus the hermetic suite, refreshes the distribution
manifest, and releases ai-workflow. Target projects receive that new baseline
only through an intentional ai-workflow update. Missing or incompatible
dependencies fail with a diagnostic; the router never falls back to a retired
local fork.

Across a declaration change, the new immutable package must first authenticate
the installed framework as an audited predecessor. Its exact historical
`providers.json` then authenticates the old provider identity and state shape.
Update replaces a provider directory only when predecessor state records it as
framework-created, every recorded installed-file SHA-256 is still clean, and
the complete directory matches the predecessor's inventory and source metadata.
Modified and pre-existing-compatible directories continue to fail closed.
Directories already compatible with the new declaration are retained without
losing their recorded origin; a predecessor-recorded directory that is genuinely
absent is installed from the new declared pin. The complete transition set and
new staged pin are verified before mutation. A supported clean upgrade therefore
does not require deleting `.agents`, `provider-state.json`, or individual skills.

Python 3.11 or newer is required for lifecycle commands. GitHub CLI 2.97.0 or
newer is required for initial provider adoption or an update that changes the
provider baseline. Initial adoption stages the exact pin and byte-compares any
pre-existing directory before claiming compatibility. Runtime use and the inner
status checks read ordinary repository files and do not contact the provider
upstream once that baseline and the exact framework package are recorded. The
documented public bootstrap still needs HTTPS to fetch the framework package;
an unchanged update needs no additional provider fetch.
Project-scoped `.agents/skills` is shared by Codex and GitHub Copilot. Removal
considers only exact declared names and deletes only package-authentic,
checksum-clean skills recorded as created by ai-workflow. It preserves
pre-existing-compatible, incompatible, locally changed, extra-file, and
undeclared directories. Repository-local origin history is useful evidence but
is not tamper-evident: coordinated forgery can reclassify an exact unmodified
canonical provider directory, but cannot authorize deletion of modified,
extra-file, or undeclared content.

## Setup lifecycle

`setup-matt-pocock-skills` is installed but never run automatically during
adoption or every prompt. Before the first tracker-dependent workflow, the
router checks only that selected skill's declaration for the required
`docs/agents/issue-tracker.md`, `docs/agents/domain.md`, and, where applicable,
`docs/agents/triage-labels.md`. When absent, it selects setup and returns the
exact user-only handoff on Codex or GitHub Copilot because setup is prompt-driven
and writes user-owned configuration plus a root `## Agent skills` block. On a
host where the provider is unavailable, it reports that limitation instead. It
does not run or write merely because it was selected. `triage` is installed so
setup can emit the label vocabulary required by to-spec and to-tickets; triage
is not a normal root route. Rerun setup only to switch or reset that
configuration; ordinary edits go directly to `docs/agents/*.md`.

Teach also has a lifecycle boundary: invoke it only for explicit sustained
learning intent and use a dedicated learning workspace for its `MISSION.md`,
lessons, references, and learning records. A normal knowledge question stays a
direct explanation and does not write course artifacts into the engineering
project.

## Framework-owned continuity and safety

`project-profile.md` and `state/active.md` are project-owned. A new profile is a
deterministic `uninitialized` document whose unknown values are `None`. For a
mature repository, initialize it once from verified repository evidence when
writes are authorized; afterward add only concise, durable facts and pointers
discovered naturally during work. Do not scan the whole repository per task,
store secrets or task notes, or let the cache override current source, accepted
ADRs/domain documentation, or canonical provider artifacts.

For a cross-version update, the immutable new package—not the target-local
`install-manifest.json`—defines trusted predecessors. Version, exact source
revision, installation-manifest schema, complete managed-path set, and every
source SHA-256 must match one audited record before the updater plans a write or
retirement. Provider migration additionally requires that authenticated record
to cover the installed predecessor `providers.json`, and requires exact matching
provider state and checksum-clean current directories. Unknown, partial, and
forged predecessor identities fail closed. During coordinated update, the
payload commits while provider backups are still reversible. Payload and
provider post-check failures restore both layers to the predecessor state.
Rollback removes only directories created by that operation; successful removal
may leave pre-existing unowned empty parent directories.

Durable framework records link to canonical provider artifacts rather than
copying their content or renaming their identifiers. The workflow that creates
an artifact owns its canonical form: a to-spec tracker issue, project-authored
local specification, or Wayfinder map can each be canonical where it was
created. Provider instructions do not grant extra authority: commits, external
tracker changes, setup writes, and other mutations remain governed by the
user's request, host sandbox, and project command contract.

Root `AGENTS.md` contains a managed router block followed by a project-owned
instruction section. Add repository commands and conventions only below the
`ai-workflow:project-instructions` marker. A freshly created `CLAUDE.md` now uses
the same managed/project composite ownership model, so setup may edit the
project-owned region without breaking status or update. Updates migrate the
previous clean fully-owned `CLAUDE.md` form and preserve existing project
content. Removal deletes only the managed region and leaves project content.

Payload origin/restoration fields and provider origin are repository-local
history, not tamper-evident proof. Coordinated local forgery can reclassify exact
canonical managed/provider bytes or substitute an exact current/audited
historical policy identity. It cannot authorize invented source identities or
deletion of modified, extra, undeclared, or unique project content. A stronger
historical-origin guarantee would require conservative no-delete behavior or a
trust anchor outside the target repository.

Normal lifecycle status reports framework integrity and provider integrity
separately from project readiness and setup host capability. An uninitialized profile
or missing optional setup document is a readiness warning and keeps a healthy
status successful; a missing or modified managed file remains an integrity
failure.

Each final response ends with one effective route line, for example
`[route: router → implement → verification]`. It lists router-selected stages
and explicitly composed capabilities that actually ran, without re-expanding
provider-owned internal composition such as implement's TDD and Code Review.
Availability alone does not count, and reporting the route never causes another
skill load or state write.

## Optional observability

`observability/analyze.py` is an inert, read-only utility for explicitly chosen
OTLP or Copilot JSON exports. It enables no host telemetry, reads no project
source, stores no data, creates no database, and is never called by the router
or a workflow. Its deterministic metadata-only report can compare observed
skill sequences, model calls, tokens, tools, duration, and errors when native
single-session debugging is insufficient. See
[`observability/README.md`](observability/README.md) for input compatibility,
privacy, exact opt-in and reversal steps, controlled experiments, and limits.

## Wayfinder identity boundary

Wayfinder owns its map and decision-ticket semantics. Preserve its tracker issue
ID or URL, linked issue title, `wayfinder:map`, `wayfinder:research`,
`wayfinder:prototype`, `wayfinder:grilling`, `wayfinder:task`, `Destination`,
`Decisions so far`, `Not yet specified`, and `Out of scope` terms unchanged.
Never translate those to `DEC`, `TKT`, `UNK`, or another framework prefix. A
Wayfinder ticket such as `T14`, a Jira issue such as `ARC-384`, and a GitHub issue
such as `#384` retain distinct native identities.
