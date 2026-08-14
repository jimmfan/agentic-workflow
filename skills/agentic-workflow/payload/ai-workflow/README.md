# Installed AI workflow orchestration

ai-workflow is the routing and integration layer. Mature planning, learning,
research, specification, ticketing, implementation, TDD, and Code Review
methods come from curated upstream skills installed under `.agents/skills/`.
Their tested source, version, revision, subtree identities, complete file lists,
and capability mapping are declared in `providers.json`.

The root `AGENTS.md` is the small always-on router. Detailed skill bodies load
only when selected. Framework-owned local skills remain for bounded Discovery,
diagnosis with authorization controls, implementation integration, and
acceptance/integration Verification:

```text
request -> router
        -> direct
        -> upstream wayfinder | teach | research
        -> local discovery | debugging
        -> upstream to-spec -> to-tickets -> implement
        -> local verification
```

`implement` already composes `tdd` and `code-review`; the router does not invoke
them again mechanically. A direct `code-review` remains available when the user
requests its fixed-point Standards/Spec contract outside an implement run.

## Provider lifecycle

The public ai-workflow bootstrap is the only required adoption path. Internally
it delegates upstream installation to GitHub CLI `gh skill`, pins every skill to
the tested tag, then validates injected source/ref/tree-SHA metadata and complete
adjacent resources. `provider-state.json` records only ai-workflow lifecycle
ownership and file checksums; it is not a second package manager.

Pinned providers do not float during normal updates. A maintainer upgrades the
declaration to a reviewed stable tag and subtree identities, runs live provider
compatibility checks plus the hermetic suite, refreshes the distribution
manifest, and releases ai-workflow. Target projects receive that new baseline
only through an intentional ai-workflow update. Missing or incompatible
dependencies fail with a diagnostic; the router never falls back to a retired
local fork.

Python 3.11 or newer and GitHub CLI 2.97.0 or newer are required for install and
update. Runtime use and status verification read ordinary repository files and
do not contact upstream.
Project-scoped `.agents/skills` is shared by Codex and GitHub Copilot. Removal
deletes only checksum-clean skills that ai-workflow installed and preserves
pre-existing compatible or locally changed skill directories.

## Setup lifecycle

`setup-matt-pocock-skills` is installed but never run automatically during
adoption or every prompt. Before the first tracker-dependent workflow, the
router checks for `docs/agents/issue-tracker.md` and `docs/agents/domain.md`.
When absent, it invokes setup visibly because setup is prompt-driven and writes
user-owned tracker/domain configuration plus a root `## Agent skills` block.
Rerun it only to switch or reset that configuration; ordinary edits go directly
to `docs/agents/*.md`.

Teach also has a lifecycle boundary: invoke it only for explicit sustained
learning intent and use a dedicated learning workspace for its `MISSION.md`,
lessons, references, and learning records. A normal knowledge question stays a
direct explanation and does not write course artifacts into the engineering
project.

## Framework-owned continuity and safety

`project-profile.md` and `state/active.md` are project-owned. Complete the
profile before relying on project checks. Durable framework records link to
canonical provider artifacts rather than copying their content or renaming their
identifiers. Provider instructions do not grant extra authority: commits,
external tracker changes, setup writes, and other mutations remain governed by
the user's request, host sandbox, and project command contract.

Root `AGENTS.md` contains a managed router block followed by a project-owned
instruction section. Add repository commands and conventions only below the
`ai-workflow:project-instructions` marker. Updates validate the managed block and
preserve that project section.

Each final response ends with one effective route line, for example
`[route: router → implement → verification]`. It lists only stages or upstream
skills that materially affected the response; availability alone does not count
and reporting the route never causes another skill load or state write.

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
