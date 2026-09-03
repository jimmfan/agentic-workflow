# Agent Workflow

Agent Workflow is an experimental routing and coordination layer for coding agents.

It keeps straightforward work direct, uses skills directly or as part of a
workflow when they help, and uses Wayfinder when an effort needs durable project
state across session continuations, workflow transitions, or agent handoffs.

The project is pre-1.0 and actively evolving.

## Quick Start

Install the CLI:

```bash
uv tool install git+https://github.com/jimmfan/agentic-workflow.git
```

Install Agent Workflow in the current project:

```bash
agent-workflow install
```

Then start a new supported coding-agent session from the project root and ask for work normally.

You do not need to choose a workflow first. Agent Workflow routes the request and loads additional instructions or skills when needed.

Manage the installed framework with:

```bash
agent-workflow update
agent-workflow status
agent-workflow remove
```

With no target path, lifecycle commands use the containing Git worktree root when
Git can discover one, otherwise the current directory. An explicit target path is
always used directly. Git repository state is not a lifecycle prerequisite.
Install and update select the newest stable Agent Workflow release, so ordinary
framework updates do not require a separate CLI upgrade. `--ref` remains an
explicit development and testing override for a branch, tag, or commit.

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

Agent Workflow chooses Direct or one primary workflow and adds only supporting
capabilities that materially help.

It does not run every potentially relevant skill.

## Routing

Routing starts Direct.

The root project instructions perform the initial classification. More detailed
routing guidance is loaded only when artifact or record responsibility or
workflow composition is unclear, or selected-skill availability, an exact
invocation instruction, agent handoff, or durable resumption materially matters.

Routing can change as work develops. For example, a bounded implementation task may expose an unresolved design decision or enough coordination state to justify a different workflow.

The router does not expand the user's authority.

Do not treat a consequential project choice as committed until required evidence
is sufficient and either accepted project policy determines the choice for that
boundary or the person, role, or valid delegate with project decision authority
commits it. Dependent work stops while a required project choice remains
uncommitted; independent work may continue. Perform only actions authorized by the
current user request or accepted project policy and only within that scope.
Authorization to act does not commit a project choice, a committed choice does not
authorize an unrelated action, and host permission supplies neither.

Current source, observed behavior, and accepted project artifacts take
precedence over stale workflow state or previous chat history.

See [Workflow routing](docs/routing.md) for the current routing model.

## Wayfinder

Wayfinder is Agent Workflow's durable coordination mechanism.

It is used when project-owned durable state would materially help an effort
continue across sessions, agent handoffs, dependencies, or unresolved
consequential choices.

Wayfinder is not required for every task, and the existence of an existing Wayfinder effort does not cause unrelated work to use it.

A Wayfinder effort is map-first:

```text
.agent-wayfinder/
└── <effort>/
    ├── map.md
    ├── facts.md        # optional
    ├── decisions.md    # optional
    ├── unknowns/       # optional
    └── evidence/       # optional
```

When resuming a Wayfinder effort, read `map.md` first. It records the objective,
scope, ready work, smallest truthful current-state summary, dependencies,
conditions blocking particular work, relevant ownership boundaries, and the few
references materially useful for continuation. Important areas, relationships,
and unresolved questions remain visible where they affect that coordination.

A simple effort may need only `map.md`.

Initialize a new map shell with the installed helper, then replace its required
content placeholders before treating it as populated durable state:

```bash
python3 .agent-workflow/tools/wayfinder.py init-effort --effort <stable-effort-slug> --name "<human-readable effort name>"
```

The framework-owned literal schema at
`.agent-workflow/schemas/wayfinder/map.md` is the single source for exact
new-map headings, ordering, placeholders, and empty representation. Existing
maps remain recognizable and resumable without migration or formatting-only
rewrites.

Additional records are created only when they are useful to preserve separately:

- `U#` unresolved question record — one current consequential question that
  remains unanswered; the record is not itself a blocker;
- `E#` evidence record — independently useful evidence with source, scope,
  observation, and limitations;
- `F#` fact record — one current scoped descriptive conclusion judged
  sufficiently supported and revisable as evidence changes; and
- `D#` decision record — one current consequential choice determined directly by
  accepted project policy or committed by the person, role, or valid delegate with
  project decision authority.

Wayfinder coordinates this information. It does not replace source code,
documentation, architecture decisions, specifications, tickets, or other
artifacts or records designated to maintain lasting results.

As lasting results are established, they should live with the artifact or record
designated to maintain them rather than accumulating indefinitely in Wayfinder.

Exact Wayfinder representation and reconciliation behavior is defined in the installed Wayfinder state contract.


Example text to use Wayfinder:
```text
Project/effort plan path (if available):

Use the installed Agent Workflow and explicitly start Wayfinder for this
repository's current development effort.

First inspect any project/effort plan identified above, the project instructions,
relevant accepted architecture decisions and documentation, repository structure,
and the source and tests relevant to the effort.

Use an available project/effort plan to understand the intended objective, scope,
dependencies, sequencing, and remaining work where applicable. Reference the plan
from Wayfinder when useful rather than copying it.

Use the installed Wayfinder initializer to create a lightweight map shell, then
replace its required placeholders with enough meaningful coordination content
for developers and future agents to resume without depending on this chat. Do
not implement product changes during this first pass.

If the current effort cannot be inferred confidently, ask only the minimum
concrete scope questions needed before creating the Wayfinder state. When
finished, summarize what you created, what remains uncertain, and the best next
prompt for continuing the work.
```

## Project ownership

Agent Workflow separates reconstructable framework files from durable project-owned state.

```text
target-project/
├── AGENTS.md
├── CLAUDE.md
├── .agents/
│   └── skills/
│       └── <15 curated skills>
│
├── .agent-workflow/          # framework-owned
│   ├── routing.md
│   ├── README.md             # includes third-party MIT notice
│   ├── contracts/
│   ├── schemas/wayfinder/map.md
│   └── tools/wayfinder.py
│
└── .agent-wayfinder/         # project-owned
    └── <effort>/
        └── ...
```

### `.agent-workflow/`

Framework-owned and reconstructable.

Install and update replace this directory with the current package version.
There is no installed manifest, provenance record, migration history, or
framework backup.

### `.agents/skills/`

Each of the fifteen current curated skill names is reserved for Agent Workflow.
Install and update replace those complete skill directories, including extra
files inside them, while preserving unrelated skill directories.

### `.agent-wayfinder/`

Project-owned durable state.

The lifecycle does not directly traverse, interpret, or change this directory.
Wayfinder alone owns its use.

### `AGENTS.md` and `CLAUDE.md`

Agent Workflow manages only its marked section and preserves project-owned
content outside that section byte-for-byte. `AGENTS.md` uses one logical
managed-begin/managed-end region; repeated install and update keep exactly one
such region. The existing `CLAUDE.md` integration remains unchanged.

### Lifecycle safety

Lifecycle commands operate on an existing non-root target directory. Install,
update, and remove preflight composite ownership and the managed roots and
parents they will traverse, rejecting malformed markers, symlink or unsupported
root/parent entries, and paths that could escape the target. Nested entries
inside a replaceable managed directory are removed through ordinary convergence.
`status` diagnoses managed-state drift and conflicts; unrelated repository
changes do not make Agent Workflow unhealthy.

Install and update converge to the same current package state. Remove deletes
`.agent-workflow/` and the current curated skill directories and strips the
managed regions from `AGENTS.md` and `CLAUDE.md`; it deletes a composite file
only when no project-authored bytes remain. A failure after mutation may leave a
partial result; resolve the reported filesystem error and rerun the command to
converge.

On a target with current curated-name directories but no recognizable Agent
Workflow installation, remove refuses before mutation because those directories
may be project-owned.

There is no migration subsystem. Existing installations converge in one install
or update: complete replacement of `.agent-workflow/` removes obsolete framework
files. Skill directories outside the current curated inventory are unrelated
content and remain untouched.

### Where results live

Specifications, tickets, research, reviews, and other artifacts or records
remain in the locations designated to maintain their results. Agent Workflow
references those artifacts and records rather than maintaining duplicate copies.
Chat output is session-local; a durable ticket, artifact, or record may be linked
when useful for continuity.

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

Wayfinder works the same way. A later session starts from `map.md` and reads supporting state only when it is relevant to the current work.

## Supported hosts

Agent Workflow installs its skills under `.agents/skills/`, which is supported
by:

- Codex through `.agents/skills/`;
- GitHub Copilot through `.agents/skills/`.

A Claude model running inside GitHub Copilot uses GitHub Copilot's `.agents/skills/` support.

Native Claude Code can use the installed root policy for routing and work
directly, but Agent Workflow does not currently copy the skills into
`.claude/skills/`.

At runtime, use only skills exposed in the current session. Agent Workflow does
not report that a named skill ran when it did not. If an optional selected skill
is unavailable or cannot run without explicit user invocation, authorized Direct
work may continue only when available capabilities can satisfy the request.

## Requirements

The current CLI requires:

- Python 3.11 or newer;
- `uv`;
- HTTPS access when installing the CLI from GitHub; and
- a POSIX-style shell.

Supported environments include:

- macOS with Bash or Zsh;
- Linux;
- WSL; and
- Linux-based devcontainers.

Native PowerShell and CMD are not currently supported. Git Bash on native Windows is best-effort.

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
- Keep required evidence and project-choice commitment separate from authorization
  to act; cross neither boundary until its own gate is satisfied.
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

Eleven curated skills are copied from or derived from [Matt Pocock's Skills for Real Engineers](https://github.com/mattpocock/skills), release `v1.2.3`. Agent Workflow maintains their effective versions and installs complete copyright and MIT license attribution with the framework.

Agent Workflow's routing, Git-native durable state, continuation behavior, and integrations are separate project work.

Agent Workflow is available under the [MIT License](LICENSE).
