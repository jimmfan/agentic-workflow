# Agent Workflow

Agent Workflow is an experimental, pre-1.0 routing and coordination layer for coding agents.
It keeps straightforward work direct, brings in useful skills, and uses Wayfinder when durable project state helps work continue across sessions or handoffs.
Whether that improves agent performance enough to justify its cost remains an [evaluation question](evals/README.md).

## Quick Start

You need Python 3.11+, `uv` (recommended) or `pip`, Git for the Git-based CLI install, and HTTPS access to GitHub for installation and framework downloads.
Use a POSIX-style shell on macOS, Linux, WSL, or a Linux-based devcontainer.
Native PowerShell and CMD are unsupported; Git Bash on native Windows is best-effort.
See [Supported hosts](#supported-hosts) for coding-agent support.

Install the CLI in an isolated tool environment:

```bash
uv tool install git+https://github.com/jimmfan/agentic-workflow.git
```

The supported alternative installs into your active Python environment:

```bash
python3 -m pip install "git+https://github.com/jimmfan/agentic-workflow.git"
```

From the project you want to use with Agent Workflow, install the framework:

```bash
agent-workflow install
```

Start a new supported coding-agent session from that project root and ask for work normally, for example: “Fix the failing validation and verify the result.”
You do not need to choose a workflow first.

## Manage an installation

| Purpose | Command |
|---|---|
| Install or repair the framework | `agent-workflow install` |
| Update the framework | `agent-workflow update` |
| Check managed files against the selected framework | `agent-workflow status` |
| Remove the framework | `agent-workflow remove` |

Without a target, commands use the containing Git worktree root when discoverable, otherwise the current directory.
An explicit target is used directly and must be an existing non-root directory; a Git repository is not required.
Preview changes or inspect options with:

```bash
agent-workflow install /path/to/project --dry-run
agent-workflow update --dry-run
agent-workflow --help
```

Install and update select the newest stable framework release.
`--ref main` (or another branch, tag, or commit) is an explicit development/testing override.
Updating the framework is separate from upgrading the CLI:

```bash
uv tool upgrade agent-workflow
```

For a `pip` installation, use `python3 -m pip install --upgrade "git+https://github.com/jimmfan/agentic-workflow.git"`.
Ordinary framework updates do not require a CLI upgrade.

### Replacement and recovery

Install and update replace all of `.agent-workflow/` and each [current curated skill directory](.agents/skills/), including local edits and extra files inside those directories.
Keep project customizations outside those reserved surfaces.
Unrelated skills, project-owned `.project-efforts/` state, and all content outside the managed regions in `AGENTS.md` and `CLAUDE.md` are preserved.
Remove deletes the managed directories and regions; it refuses ambiguous ownership or curated-name collisions on an otherwise unrecognized installation.

Unsafe managed paths or malformed policy markers stop mutation before writes.
A later filesystem failure can leave partial changes: resolve the reported error and rerun the command to converge.
There is no automatic backup or rollback.
`status` reports managed drift or conflicts, not unrelated repository changes or an installed-release history.

### One-time reinstall for the repository-layout release

Older CLIs that use the former `skills/agent-workflow/` layout need one forced reinstall before they can update the framework:

```bash
uv tool install --force git+https://github.com/jimmfan/agentic-workflow.git
agent-workflow update
```

For `pip`, replace the first command with `python3 -m pip install --force-reinstall "git+https://github.com/jimmfan/agentic-workflow.git"`.
Projects with Wayfinder state at the former `.agent-wayfinder/` path must explicitly move it to `.project-efforts/` and repair their references; lifecycle commands never migrate project-owned state.

## Supported hosts

- [Codex](https://developers.openai.com/codex/skills) and [GitHub Copilot](https://code.visualstudio.com/docs/agent-customization/agent-skills) discover the installed skills under `.agents/skills/`.
- A Claude model inside GitHub Copilot uses Copilot's skill support.
- Native Claude Code can use the installed root policy for routing and Direct work, but Agent Workflow does not copy skills into its [`.claude/skills/` location](https://code.claude.com/docs/en/skills).

Only skills exposed in the current session can run.
An unavailable required skill remains an explicit limitation; an optional skill may have an authorized Direct fallback.

## Skills for ordinary work

The agent selects the smallest useful method as work develops.
These links describe the available capabilities; they are not a sequence you must follow.

| Work | Skills |
|---|---|
| Resolve questions and understand a design | [Discovery](.agents/skills/workflow-discovery/SKILL.md), [Research](.agents/skills/research/SKILL.md), [Grilling](.agents/skills/grilling/SKILL.md), [Domain Modeling](.agents/skills/domain-modeling/SKILL.md), [Codebase Design](.agents/skills/codebase-design/SKILL.md) |
| Explore behavior or diagnose a failure | [Prototype](.agents/skills/prototype/SKILL.md), [Debugging](.agents/skills/workflow-debugging/SKILL.md) |
| Define and deliver work | [To Spec](.agents/skills/to-spec/SKILL.md), [To Tickets](.agents/skills/to-tickets/SKILL.md), [Implementation](.agents/skills/workflow-implementation/SKILL.md) and its [build method](.agents/skills/implement/SKILL.md), [TDD](.agents/skills/tdd/SKILL.md), [Code Review](.agents/skills/code-review/SKILL.md), [Verification](.agents/skills/workflow-verification/SKILL.md) |
| Continue an effort | [Wayfinder](.agents/skills/wayfinder/SKILL.md), [Wayfinder Effort](.agents/skills/wayfinder-effort/SKILL.md) |

## Wayfinder

Wayfinder keeps the current objective, scope, dependencies, blockers, and ready work in `.project-efforts/<effort>/map.md`.
A map alone is valid; supporting records are optional.
Resumption starts with the map and follows relevant links to project artifacts that maintain lasting results.
Unrelated existing efforts do not capture ordinary work.

To orient a new or existing effort without implementing product changes, describe the effort or paste, attach, or reference a plan, then ask:

```text
Use the installed Agent Workflow and explicitly use Wayfinder to orient this repository's development effort for continued work across sessions.
Establish or update the effort's Wayfinder state.
Do not implement product changes during this pass.
Summarize what changed, what remains uncertain, and the recommended next prompt.
```

Alternatively, use `wayfinder-effort`, which performs the same orientation without product implementation:

| Host | Example |
|---|---|
| Codex | `$wayfinder-effort Migrate our GitHub Actions runners to ARC on EKS.` |
| GitHub Copilot | `/wayfinder-effort docs/implementation-plan.md` |

The effort or plan can also be pasted or attached.
To continue afterward, ask: “Resume the runner-migration effort from `.project-efforts/runner-migration/map.md` and carry out its ready work.”
Use your actual effort name and authorize the scope you want performed.

To review unresolved questions together:

> Use Wayfinder to review the runner-migration effort's unresolved questions with me and record our conclusions. Do not implement resulting changes.

Questions may live in the map even when no `unknowns.md` exists.
Wayfinder reads relevant context, asks simple clarifications directly, and uses Grilling for interdependent human choices.
Recording remains limited to authorized artifacts; reviewing questions does not authorize implementation or publication.
The [Wayfinder state contract](.agent-workflow/contracts/wayfinder-state.md) owns exact state and reconciliation rules.

## More detail

- [Architecture and ownership](docs/architecture.md) explains the system and its instruction-loading boundaries.
- [Verification](docs/verification.md) gives the maintainer and CI gate.
- [Behavioral testing](docs/behavioral-testing.md) explains scenario authoring and opt-in live runs.
- [Tests](tests/README.md) and [evaluations](evals/README.md) distinguish coverage from remaining evidence gaps.

## Acknowledgments

Eleven curated skills are copied from or derived from [Matt Pocock's Skills for Real Engineers](https://github.com/mattpocock/skills), release `v1.2.3`.
Agent Workflow maintains their effective versions and distributes the [complete copyright and MIT notice](.agent-workflow/README.md#third-party-license).
Its routing, Git-native durable state, continuation behavior, and integrations are separate project work.
Agent Workflow is available under the [MIT License](LICENSE).
