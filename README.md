# Agent Workflow

Agent Workflow is an experimental routing and coordination layer for coding agents.

It keeps straightforward work direct, loads engineering workflows and specialist skills when they are useful, and uses Wayfinder when an effort needs durable project state across sessions or handoffs.

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

Lifecycle commands use the current directory by default and also accept an explicit project path.

## What it does

Agent Workflow has three main responsibilities:

- route work to the smallest useful workflow or skill;
- preserve authorization and project ownership boundaries; and
- keep durable coordination state when an effort needs to survive beyond the current session.

A bounded request can remain Direct.

Other work can use workflows or specialist methods for areas such as:

- discovery and design decisions;
- debugging;
- research;
- domain modeling;
- prototyping;
- implementation;
- test-driven development;
- code review; and
- verification.

Agent Workflow selects one dominant workflow or activity and adds other capabilities only when they are useful.

It does not run every potentially relevant skill.

## Routing

Routing starts Direct.

The root project instructions perform the initial classification. More detailed routing guidance is loaded only when ownership, workflow composition, provider fallback, handoff, or durable re-entry is unclear.

Routing can change as work develops. For example, a bounded implementation task may expose an unresolved design decision or enough coordination state to justify a different workflow.

The router does not expand the user's authority.

If work depends on evidence, approval, or a project decision that has not been resolved, dependent work does not proceed through that boundary. Independent work may continue.

Current source, observed behavior, and accepted project artifacts take precedence over stale workflow state or previous chat history.

See [Workflow routing](docs/routing.md) for the current routing model.

## Wayfinder

Wayfinder is Agent Workflow's durable coordination mechanism.

It is used when project-owned state would materially help an effort continue across sessions, handoffs, dependencies, or unresolved decisions.

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

`map.md` is the effort's main re-entry point. It records enough current context for a later agent or developer to understand the effort, including:

- goal and scope;
- important areas and relationships;
- current blockers and dependencies;
- unresolved questions that matter to the work; and
- what can happen next.

A simple effort may need only `map.md`.

Additional state is created only when it is useful to preserve separately:

- `unknown` — an unresolved question worth retaining;
- `evidence` — an observation or source result with provenance and limitations;
- `fact` — an established descriptive conclusion;
- `decision` — a committed project choice.

Wayfinder coordinates this information. It does not replace source code, documentation, architecture decisions, specifications, tickets, or other canonical project artifacts.

As work settles, lasting results should live with the artifact that owns them rather than accumulating indefinitely in Wayfinder.

Exact Wayfinder storage and mutation behavior is defined in the installed Wayfinder state contract.


Example text to use Wayfinder:
```text
Use the installed Agent Workflow and explicitly start Wayfinder for this
repository's current development effort.

First inspect the project instructions, relevant accepted architecture
decisions and documentation, repository structure, current Git state, and the
source and tests relevant to the effort. Then create a lightweight
`.agent-wayfinder/<stable-effort-name>/map.md` that will help developers and
future agents resume the work without depending on this chat.

Record only durable, evidence-backed coordination context:

- the goal and scope boundary;
- the important areas and relationships in the effort;
- supported current conclusions with pointers to their authoritative sources;
- consequential unknowns, decisions, dependencies, and blockers; and
- a concise ready frontier describing what can happen next.

Create a separate unknown or evidence file only when it is an independently
useful coordination or retrieval unit. When a supported current conclusion or
committed decision warrants durable representation, record it as an F# or D# section in
the optional `facts.md` or `decisions.md` ledger. Treat live source and accepted
project artifacts as more authoritative than assumptions, chat history, or
outdated Wayfinder claims. Do not copy the transcript, invent requirements, or
implement product changes during this first pass.

If the current effort cannot be inferred confidently, ask me one concrete scope
question before creating the Wayfinder state. When finished, summarize what you
created, what remains uncertain, and the best next prompt for continuing the
work.
```

## Project ownership

Agent Workflow separates reconstructable framework files from durable project-owned state.

```text
target-project/
├── AGENTS.md
├── CLAUDE.md
├── .agents/
│   └── skills/
│
├── .agent-workflow/          # framework-owned
│   ├── install-manifest.json
│   ├── providers.json
│   ├── routing.md
│   └── contracts/
│
└── .agent-wayfinder/         # project-owned
    └── <effort>/
        └── ...
```

### `.agent-workflow/`

Framework-owned and reconstructable.

Install and update may replace these files with the current package version.

### `.agent-wayfinder/`

Project-owned durable state.

Install, update, status, remove, and reinstall preserve its contents.

### `AGENTS.md` and `CLAUDE.md`

Agent Workflow manages only its marked section and preserves project-owned content outside that section.

### Provider artifacts

Specifications, tickets, research, reviews, and other provider-native artifacts remain canonical where they are created.

Agent Workflow links to those artifacts rather than maintaining duplicate copies.

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

The current provider-skill projection supports:

- Codex through `.agents/skills/`;
- GitHub Copilot through `.agents/skills/`.

A Claude model running inside GitHub Copilot uses GitHub Copilot's `.agents/skills/` support.

Native Claude Code can use the installed root policy for routing and host-native work, but Agent Workflow does not currently project provider skills into `.claude/skills/`.

Provider availability is checked at runtime. Agent Workflow does not report that a provider ran when it did not.

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
- Can a fresh session recover the current state of an effort?
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
- Do not cross unresolved consequential decision boundaries without the required evidence or authority.
- Prefer current repository reality over stale state.
- Keep durable project state separate from reconstructable framework files.
- Store coordination state, not execution history.
- Load detailed instructions and state only when needed.
- Keep existing project and provider artifacts canonical.
- Keep Agent Workflow small.

## More detail

- [Architecture and ownership](docs/architecture.md)
- [Workflow routing](docs/routing.md)
- [Behavioral testing](docs/behavioral-testing.md)
- [Verification](docs/verification.md)
- [Provider research](docs/provider-research.md)

Exact behavior is defined by the current source, tests, installed policies and contracts, and accepted architecture decisions.

## Acknowledgments

Agent Workflow uses a pinned snapshot of [Matt Pocock's Skills for Real Engineers](https://github.com/mattpocock/skills) as an optional provider.

Its effective Wayfinder runtime is derived from Matt Pocock's Wayfinder methodology. Agent Workflow's routing, Git-native durable state, continuation behavior, and integrations are separate project work.

Agent Workflow is available under the [MIT License](LICENSE).
