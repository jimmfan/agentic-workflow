# Installed AI workflow orchestration

`.ai-workflow/` is Agentic Workflow's internal, repository-local routing,
installation, and lifecycle state. It is not a general destination for project
documentation, specifications, tickets, or provider-native artifacts; those
remain in their existing canonical locations. Mature planning, learning,
research, specification, ticketing, implementation, TDD, and Code Review
methods may come from curated upstream skills installed under `.agents/skills/`.
Their reviewed repository, pinned version, paths, invocation requirements, and
capability mapping are declared in `providers.json`.

The root `AGENTS.md` is a small always-on orchestration kernel and hooks-off
semantic fallback. Detailed selection, invocation, composition, and route-output
rules live in `routing.md`, which loads only for a named skill, resume, uncertain
route, or route not confidently direct. Skill bodies load only after selection
and, for user-only providers, actual invocation. Framework-owned local skills
remain for bounded Discovery, diagnosis with authorization controls,
implementation integration, and acceptance/integration Verification:

```text
request -> router
        -> direct
        -> dominant workflow/activity + optional capabilities
        -> invocation policy -> execute | host-native fallback | explicit handoff
        -> upstream wayfinder | teach | research
        -> local discovery | debugging
        -> upstream to-spec -> to-tickets -> implement
        -> local verification
```

GitHub Copilot in VS Code is the primary/reference runtime. The installed
`.github/hooks/agentic-workflow.json` Preview adapter calls
`runtime/controller.py` to check route checkpoints, authorization boundaries,
provider outcomes, durable-state transitions, and verification evidence. Hooks
may be disabled, unsupported, or untrusted, so the root instruction contract
remains complete and direct work remains available. `runtime/capabilities.json`
records the truthful host matrix; `runtime/README.md` defines the compact
model-to-controller protocol and limitations.

Codex and Claude Code examples under `runtime/adapters/` are opt-in rather than
active: their fixed project hook files may already be user-owned. Copilot CLI
and cloud agent have distinct schemas/runtime behavior and are not treated as
aliases for the VS Code hook file.

Routing selection is not execution. Codex and GitHub Copilot may invoke skills
declared `implicit`. When a preferred provider is user-only and was not
explicitly invoked, or is unavailable on the active host, ordinary intent uses
truthful host-native capability instead. An exact handoff is reserved for an
explicitly required provider or a genuine configuration boundary. No fallback
may claim the provider ran, create provider-native artifacts, or copy its method.

A capability can support another dominant workflow or be dominant when it
directly matches intent. This permits Wayfinder plus Research or Implementation
plus Research/Debugging/Verification without treating every capability as a
durable state transition. It remains an instruction contract, not a scheduler.

`implement` already composes `tdd` and `code-review`; the router does not invoke
them again mechanically. A direct `code-review` remains available when the user
requests its fixed-point Standards/Spec contract outside an implement run.

## Provider lifecycle

The public ai-workflow bootstrap is the supported adoption path. Internally it
installs the framework first and then asks GitHub CLI `gh skill` to install the
optional provider set at the reviewed tag. It validates required source/path/ref
and invocation metadata without duplicating upstream tree SHAs or complete file
inventories. `provider-state.json` is created only when providers are installed;
it records repository/version, ownership origin, and hashes of the bytes
actually installed. Later updates use those local hashes to detect edits.

Pinned providers do not float during normal updates. A maintainer upgrades the
declaration to a reviewed stable tag, runs live provider compatibility checks
plus the hermetic suite, refreshes the distribution manifest, and releases
ai-workflow. Target projects receive that new baseline only through an
intentional update. Missing or incompatible providers produce a truthful
diagnostic and host-native fallback; the router never substitutes a retired
local fork or claims provider execution.

Across a declaration change, update uses local provider state as the ownership
and cleanliness baseline. It replaces a directory only when state records it as
framework-created or reconstructed and every recorded installed-file SHA-256 is
still clean. Modified and pre-existing-compatible directories are preserved.
Compatible directories retain their origin; a recorded directory that is
genuinely absent can be recreated from the new pin. New bytes are staged and
verified before replacement.

Fresh framework installs create only `.ai-workflow/`; optional provider install
also creates provider skill directories and `provider-state.json`. Update
recognizes the former `ai-workflow/` directory only when it has a valid managed
installation manifest, then relocates it before continuing. If both
directories exist, or if `ai-workflow/` is unrelated or unrecognizable, the
lifecycle stops without merging, overwriting, or claiming either directory.

Python 3.11 or newer is required for lifecycle commands. GitHub CLI 2.97.0 or
newer is required for initial provider adoption or an update that changes the
provider baseline, or to recreate a missing managed directory. Initial adoption
refuses any same-named directory because no framework ownership state exists for
it; it never adopts or overwrites unknown content. Runtime use and the inner
status checks read ordinary repository files and do not contact the provider
upstream. The documented public bootstrap still needs HTTPS to fetch the
framework package; an unchanged update needs no additional provider fetch.
Project-scoped `.agents/skills` is shared by Codex and GitHub Copilot. Removal
deletes only state-recorded, checksum-clean skills recorded as created by
ai-workflow. It preserves pre-existing-compatible, reconstructed, incompatible,
locally changed, and extra-file directories. Repository-local origin history is
useful ownership evidence but is not tamper-evident.

## Setup lifecycle

`setup-matt-pocock-skills` is installed but never run automatically during
adoption or every prompt. Before the first tracker-dependent workflow, the
router checks only that selected skill's declared requirements for
`docs/agents/issue-tracker.md`, `docs/agents/domain.md`, and, where applicable,
`docs/agents/triage-labels.md`. When absent, it selects setup and returns the
exact user-only handoff on Codex or GitHub Copilot because setup is prompt-driven
and writes user-owned configuration plus a root `## Agent skills` block. If a
normal workflow can proceed without that external configuration, it may instead
use host-native capability. Setup never runs or writes merely because it was
selected. `triage` is installed so
setup can emit the label vocabulary required by to-spec and to-tickets; triage
is not a normal root route. Rerun setup only to switch or reset that
configuration; ordinary edits go directly to `docs/agents/*.md`.

Teach also has a lifecycle boundary: invoke it only for explicit sustained
learning intent and use a dedicated learning workspace for its `MISSION.md`,
lessons, references, and learning records. A normal knowledge question stays a
direct explanation and does not write course artifacts into the engineering
project.

## Framework-owned continuity and safety

The filesystem boundary has three categories:

- `.ai-workflow/` is the framework installation. Its runtime, routing,
  contracts, templates, registry, and lifecycle metadata are reconstructable.
- `.ai-workflow-state/` is durable, project-owned, Git-trackable repository
  state. Install and update create the directory when absent but never seed a
  state file. Lifecycle operations preserve existing contents byte-for-byte,
  and the framework does not add the directory to `.gitignore` or require Git.
- transient controller bookkeeping is machine-local under the operating system
  temporary directory and never belongs in the repository.

Framework-owned **agent integration files** live at host-required paths such as
`.github/hooks/`, `.agents/skills/`, `AGENTS.md`, and `CLAUDE.md`. They remain
lifecycle-managed even though they are physically outside `.ai-workflow/`.

`.ai-workflow-state/project-profile.md` is optional advisory context, while
`.ai-workflow-state/active.md` is a stricter durable continuity pointer created
only when a workflow needs persistence. The parent directory is established by
install/update; both files are created lazily only by authorized workflows. The
framework profile template is a starting point whose unknown values are `None`,
but a workflow creates the project-owned profile only when it has useful
verified context to persist. Existing readable non-empty
profiles are simply `present`: headings and markers are not a versioned schema,
and lifecycle operations never migrate their content. Add only concise, durable
facts and pointers discovered naturally during work. Do not scan the whole
repository per task, store secrets or task notes, or let the cache override
current source, accepted ADRs/domain documentation, or canonical provider
artifacts.

Deleting `.ai-workflow/` and reinstalling reconstructs framework metadata while
preserving every `.ai-workflow-state/` entry. Exact surviving integration/provider
files can be authenticated locally; because deleted ownership history cannot
prove their original creation, reconstructed external files remain updateable
but are conservatively preserved on removal. Install and update migrate only the
known development-era profile, active, records, and archive paths when the
canonical state directory is absent or empty. A populated destination or unsafe
path is reported as a conflict; lifecycle never guesses, merges, or overwrites
project state.

For a cross-version update, the new package authenticates its own payload while
the target-local install and provider records establish ownership and the last
recorded clean bytes. Current-byte mismatches block replacement or deletion.
Framework and optional-provider transactions each stage and verify their own
changes and restore their own prior bytes on failure. Rollback removes only
directories created by that operation; successful removal may leave
pre-existing unowned empty parent directories.

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

Payload origin/restoration fields and provider origin/installed hashes are
repository-local history, not tamper-evident proof. Coordinated local forgery
can reclassify managed or provider bytes or alter restoration data. Without that forgery, modified, extra, undeclared,
and unique project content remains protected. A stronger historical-origin
guarantee would require conservative no-delete behavior or a trust anchor
outside the target repository.

Normal lifecycle status reports overall and framework integrity, project-state
readiness, and normal-work availability first. Optional provider/configuration
and installed/static host capability follow in a separate section; live host
loading is never inferred. Healthy state ends with `No action required.` A
missing, empty, unreadable, unsafe, or merely present profile does not become a
false framework-integrity claim. A missing active index
means no durable workflow is recorded; an existing malformed or unsafe index is
a correctness warning because it affects resumability. A disabled Preview hook
or missing optional setup document also remains separate from integrity, while a
missing or modified managed hook/file is still an integrity failure.

When useful for debugging or observability, a response may include an effective
route line such as `[route: router → implement → verification]`. If emitted, it
lists only stages and capabilities that actually ran. Its absence is normal and
never invalidates completed work or causes another skill load or state write.

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
