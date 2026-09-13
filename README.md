# Agent Workflow

Agent Workflow is an experimental routing and coordination layer for coding agents.

It keeps straightforward work direct, uses skills directly or as part of a workflow when they help, and uses Wayfinder when an effort needs durable project state across session continuations, workflow transitions, or agent handoffs.

The project is pre-1.0 and actively evolving.

## Quick Start

Install and manage the CLI and framework with:

| Purpose | `uv` | `pip` |
|---|---|---|
| Install CLI | `uv tool install git+https://github.com/jimmfan/agentic-workflow.git` | `python3 -m pip install "git+https://github.com/jimmfan/agentic-workflow.git"` |
| Upgrade CLI | `uv tool upgrade agent-workflow` | `python3 -m pip install --upgrade "git+https://github.com/jimmfan/agentic-workflow.git"` |
| Force reinstall CLI | `uv tool install --force git+https://github.com/jimmfan/agentic-workflow.git` | `python3 -m pip install --force-reinstall "git+https://github.com/jimmfan/agentic-workflow.git"` |
| Install framework | `agent-workflow install` | `agent-workflow install` |
| Update framework | `agent-workflow update` | `agent-workflow update` |
| Check framework | `agent-workflow status` | `agent-workflow status` |
| Remove framework | `agent-workflow remove` | `agent-workflow remove` |

`uv tool` installs the CLI in an isolated tool environment.
Plain `pip` installs it into the active Python environment.

The CLI and installed framework are updated separately.
`agent-workflow update` updates the framework in the target project, while the CLI itself is upgraded with the applicable `uv` or `pip` command above.

For first-time setup, install the CLI using either `uv` or `pip`, then install Agent Workflow in the current project:

```bash
agent-workflow install
```

Then start a new supported coding-agent session from the project root and ask for work normally.

You do not need to choose a workflow first.
Agent Workflow routes the request and loads additional instructions or skills when needed.

With no target path, lifecycle commands use the containing Git worktree root when Git can discover one, otherwise the current directory.
An explicit target path is always used directly.
Git repository state is not a lifecycle prerequisite.
Install and update select the newest stable Agent Workflow release, so ordinary framework updates do not require a separate CLI upgrade.
`--ref` remains an explicit development and testing override for a branch, tag, or commit.

### One-time reinstall for the repository-layout release

The structural release is a pre-1.0 clean break.
Older CLIs hard-code the former `skills/agent-workflow/` snapshot location and cannot update themselves across this layout change.

If upgrading from one of those older CLI installations, use the **Force reinstall CLI** command in the table above, then run:

```bash
agent-workflow update
```

After that reinstall, `agent-workflow update` remains the single ordinary framework-update command.
The local Wayfinder path is now `.project-efforts/<effort>/`.
Projects with state at the former `.agent-wayfinder/` path must explicitly move that state and update their references; lifecycle commands never migrate or manage project-owned durable Wayfinder state.

## Source layout

This repository authors `.agent-workflow/` and the current `.agents/skills/<name>/` directories directly at their consuming-project paths.
There is one canonical copy of each runtime resource.
`.agent-workflow/terminology.md` defines Agent Workflow's terminology for both this repository and consuming projects; agents read it when those meanings materially affect their work.
Maintainers follow the [source-checkout ownership rule](AGENTS.md#source-checkout-ownership) for source edits and disposable lifecycle exercises.
The root `VERSION` is the sole authored framework/release version, and `agent_workflow/` contains the Python implementation; `agent_workflow/install/` contains only the two composite templates and the repository-relative source-to-target manifest.
`tests/` holds lifecycle, bootstrap, routing, Wayfinder, verifier, and wheel checks; `evals/` contains evaluation tooling, including trace analysis in `evals/token_forensics/`.

The installed CLI is bootstrap transport.
It selects the highest stable `vX.Y.Z` release tag, resolves it to an immutable commit, downloads one repository snapshot, and executes `agent_workflow/lifecycle.py` from that snapshot using its canonical content and install metadata.
The wheel contains Python and install resources; runtime framework content and skills come from the selected snapshot.
The manifest is not installed into consuming projects.

## What it does

Agent Workflow has three main responsibilities:

- route work to the smallest useful workflow or skill;
- preserve boundaries for action authorization, project decision authority, and project ownership; and
- keep durable coordination state when an effort needs to survive beyond the current session.

A bounded request can remain Direct.

Other work can use a skill directly or as part of a workflow for areas such as:

- discovery and design decisions;
- debugging;
- research;
- domain modeling;
- prototyping;
- implementation;
- test-driven development;
- code review; and
- verification.

Agent Workflow chooses Direct or one primary workflow and adds only supporting capabilities that materially help.

It does not run every potentially relevant skill.

## Routing

Routing starts Direct.

The root project instructions perform the initial classification.
More detailed routing guidance is loaded only when artifact or record responsibility or workflow composition is unclear, or selected-skill availability, an exact invocation instruction, agent handoff, or durable resumption materially matters.

Routing can change as work develops.
For example, a bounded implementation task may expose an unresolved design decision or enough coordination state to justify a different workflow.

The router does not expand the user's authority.

Do not treat a consequential project choice as committed until required evidence is sufficient and either accepted project policy determines the choice for that boundary or the person, role, or valid delegate with project decision authority commits it.
Dependent work stops while a required project choice remains uncommitted; independent work may continue.
Perform only actions authorized by the current user request or accepted project policy and only within that scope.
Authorization to act does not commit a project choice, a committed choice does not authorize an unrelated action, and host permission supplies neither.

Current source, observed behavior, and accepted project artifacts take precedence over stale workflow state or previous chat history.

See [Workflow routing](docs/routing.md) for the current routing model.

## Wayfinder

Wayfinder is Agent Workflow's durable coordination mechanism.

It is used when project-owned durable state would materially help an effort continue across sessions, agent handoffs, dependencies, or unresolved consequential choices.

Wayfinder is not required for every task, and the existence of an existing Wayfinder effort does not cause unrelated work to use it.

A Wayfinder effort is map-first:

```text
.project-efforts/
└── <effort>/
    ├── map.md
    ├── facts.md        # optional
    ├── decisions.md    # optional
    ├── unknowns.md     # optional
    └── evidence/       # optional
```

When resuming a Wayfinder effort, read `map.md` first.
It records enough current coordination context for a later agent or developer to understand the effort, including:

- objective;
- scope;
- important areas and relationships;
- conditions currently blocking particular work and the relevant dependencies;
- unresolved questions that matter to the work; and
- ready work.

A simple effort may need only `map.md`.

To review an effort together:

> Use Wayfinder to review this effort's unresolved questions with me and record our conclusions. Do not implement resulting changes.

Name the effort when context does not identify it clearly.
Wayfinder prepares from the map and relevant linked artifacts, asks simple clarifications directly, and uses Grilling for interdependent human choices.
Recording is limited to authorized maintaining artifacts; review alone permits no blanket edits, implementation, or publication.
The optional `unknowns.md` ledger uses `## U<ID> — <question>` sections; map-only questions remain valid.
An absent ledger does not mean there are no unresolved questions.

The [state contract](.agent-workflow/contracts/wayfinder-state.md) maintains default-map authoring conventions, including separate dependencies and scoped blocker assessments.
Existing maps remain valid with alternate layouts.
This is authoring guidance, not a recognition requirement or migration trigger.

Additional records are created only when they are useful to preserve separately:

- `U#` unresolved question record — one current consequential question that remains unanswered; the record is not itself a blocker;
- `E#` evidence record — independently useful evidence with source, scope, observation, and limitations;
- `F#` fact record — one current scoped descriptive conclusion judged sufficiently supported and revisable as evidence changes; and
- `D#` decision record — one current consequential choice determined directly by accepted project policy or committed by the person, role, or valid delegate with project decision authority.

Wayfinder coordinates this information.
It does not replace source code, documentation, architecture decisions, specifications, tickets, or other artifacts or records designated to maintain lasting results.

As lasting results are established, they should live with the artifact or record designated to maintain them rather than accumulating indefinitely in Wayfinder.

Exact Wayfinder representation and reconciliation behavior is defined in the installed Wayfinder state contract.

Invoke the convenience skill with instructions or a file path:

```text
/wayfinder-effort <instructions-or-path-to-file>
```

If the plan is attached, `/wayfinder-effort` is sufficient.

## Project ownership

Agent Workflow separates reconstructable framework files from durable project-owned state.

```text
target-project/
├── AGENTS.md
├── CLAUDE.md
├── .agents/
│   └── skills/
│       └── <curated skills>
│
├── .agent-workflow/          # framework-owned
│   ├── routing.md
│   ├── README.md             # includes third-party MIT notice
│   └── contracts/
│
└── .project-efforts/        # project-owned
    └── <effort>/
        └── ...
```

### `.agent-workflow/`

Framework-owned and reconstructable.

Install and update replace this directory with the current package version.
There is no installed manifest, provenance record, migration history, or framework backup.

### `.agents/skills/`

Each current curated skill name is reserved for Agent Workflow.
Install and update replace those complete skill directories, including extra files inside them, while preserving unrelated skill directories.

### `.project-efforts/`

Project-owned durable state.

The lifecycle does not directly traverse, interpret, or change this directory.
Wayfinder alone owns its use.

### `AGENTS.md` and `CLAUDE.md`

Agent Workflow manages only its marked section and preserves project-owned content outside that section byte-for-byte.
`AGENTS.md` uses one logical managed-begin/managed-end region; repeated install and update keep exactly one such region.
The existing `CLAUDE.md` integration remains unchanged.

### Lifecycle safety

Lifecycle commands operate on an existing non-root target directory.
Install, update, and remove preflight composite ownership and the managed roots and parents they will traverse, rejecting malformed markers, symlink or unsupported root/parent entries, and paths that could escape the target.
Nested entries inside a replaceable managed directory are removed through ordinary convergence.
`status` compares managed surfaces with the selected framework snapshot and diagnoses drift or conflicts; unrelated repository changes do not make Agent Workflow unhealthy.
CLI diagnostics label the installed CLI version separately from the selected framework release/ref, resolved commit, and target directory.
`agent-workflow --version` prints only the CLI version.
Status does not recover an installed-release history.

Install and update converge to the same current package state.
Remove deletes `.agent-workflow/` and the current curated skill directories and strips the managed regions from `AGENTS.md` and `CLAUDE.md`; it deletes a composite file only when no project-authored bytes remain.
A failure after mutation may leave a partial result; resolve the reported filesystem error and rerun the command to converge.

On a target with current curated-name directories but no recognizable Agent Workflow installation, remove refuses before mutation because those directories may be project-owned.

There is no migration subsystem.
Existing installations converge in one install or update: complete replacement of `.agent-workflow/` removes obsolete framework files.
Skill directories outside the current curated inventory are unrelated content and remain untouched.

### Where results live

Specifications, tickets, research, reviews, and other artifacts or records remain in the locations designated to maintain their results.
Agent Workflow references those artifacts and records rather than maintaining duplicate copies.
Chat output is session-local; a durable ticket, artifact, or record may be linked when useful for continuity.

## Progressive loading

Agent Workflow keeps the always-loaded project instructions small.

More detailed information is loaded only when needed:

```text
root instructions
      ↓
route
      ↓
selected workflow or skill
      ↓
relevant state or contract
```

Wayfinder works the same way.
A later session starts from `map.md` and reads supporting state only when it is relevant to the current work.

## Supported hosts

Agent Workflow installs its skills under `.agents/skills/`, which is supported by:

- Codex through `.agents/skills/`;
- GitHub Copilot through `.agents/skills/`.

A Claude model running inside GitHub Copilot uses GitHub Copilot's `.agents/skills/` support.

Native Claude Code can use the installed root policy for routing and work directly, but Agent Workflow does not currently copy the skills into `.claude/skills/`.

At runtime, use only skills exposed in the current session.
Agent Workflow does not report that a named skill ran when it did not.
If an optional selected skill is unavailable or cannot run without explicit user invocation, authorized Direct work may continue only when available capabilities can satisfy the request.

## Requirements

The current CLI requires:

- Python 3.11 or newer;
- either `uv` or `pip` to install and manage the CLI;
- HTTPS access when installing the CLI from GitHub; and
- a POSIX-style shell.

Supported environments include:

- macOS with Bash or Zsh;
- Linux;
- WSL; and
- Linux-based devcontainers.

Native PowerShell and CMD are not currently supported.
Git Bash on native Windows is best-effort.

For an explicit target project:

```bash
agent-workflow install /path/to/project
```

Preview install or update changes with:

```bash
agent-workflow install --dry-run
agent-workflow update --dry-run
```

See all current CLI options with:

```bash
agent-workflow --help
```

## Experimental status

Agent Workflow is still an experiment.

The current hypothesis is:

> Can lightweight workflow routing plus durable, project-owned state help coding agents continue long-running engineering work correctly across independent sessions without making straightforward work worse?

Current evaluation focuses on questions such as:

- Do bounded tasks stay Direct?
- Does routing select useful methods without unnecessary overhead?
- Can a fresh session recover the current coordination state of an effort?
- Does it avoid repeating completed investigation?
- Does new evidence correctly change later work?
- Does current repository state override stale recorded state?
- Does Wayfinder improve continuity enough to justify its additional context and maintenance?
- What time and token cost does the framework add?

These are evaluation targets, not claims that Agent Workflow has already been proven to improve agent performance.

The architecture may change as the project produces better evidence.

## Design principles

- Keep bounded work Direct.
- Use workflows and skills only when they materially help.
- Keep required evidence and project-choice commitment separate from authorization to act; cross neither boundary until its own gate is satisfied.
- Prefer current repository reality over stale state.
- Keep durable project state separate from reconstructable framework files.
- Store coordination state, not execution history.
- Load detailed instructions and state only when needed.
- Keep lasting results in the artifacts or records designated to maintain them.
- Keep Agent Workflow small.

## More detail

- [Architecture and ownership](docs/architecture.md)
- [Workflow routing](docs/routing.md)
- [Behavioral testing](docs/behavioral-testing.md)
- [Verification](docs/verification.md)
- [Curated skills](docs/skills.md)

Exact behavior is defined by the current source, tests, installed policies and contracts, and accepted architecture decisions.

## Acknowledgments

Eleven curated skills are copied from or derived from [Matt Pocock's Skills for Real Engineers](https://github.com/mattpocock/skills), release `v1.2.3`.
Agent Workflow maintains their effective versions and installs complete copyright and MIT license attribution with the framework.

Agent Workflow's routing, Git-native durable state, continuation behavior, and integrations are separate project work.

Agent Workflow is available under the [MIT License](LICENSE).
