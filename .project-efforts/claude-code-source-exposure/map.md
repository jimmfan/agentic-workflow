# Claude Code source-checkout exposure

## Objective

Let native Claude Code tooling discover and run this source repository's authored content directly from checkout: the curated skills authored under `.agents/skills/`, and a devcontainer provisioned for the Claude Code extension.
This is a source-checkout experiment, not a change to what Agent Workflow installs into consuming projects.

## Scope

Includes:

- `.claude/skills/*` symlinks into `.agents/skills/*`, added in [commit 386584e](https://github.com/jimmfan/agentic-workflow/commit/386584ec91397cd2bb7d890aaa1077c2ad0ea1e9) on branch `codex/claude-skill-symlinks`, and the accompanying note added to [README.md](../../README.md) under the ownership section stating these links are a source-checkout experiment excluded from consuming-project installation.
- `.devcontainer/` changes (currently uncommitted in the working tree) that add the `anthropic.claude-code` extension, a persistent `/home/vscode/.claude` volume, directory/credential permission checks in `check_environment.py`, and provisioning steps in `post-create.sh`, mirroring the existing Codex devcontainer pattern.

Excludes:

- Agent Workflow's install/update/remove lifecycle for consuming projects; per [.agent-workflow/README.md](../../.agent-workflow/README.md), Agent Workflow installs skills under `.agents/skills/`, not `.claude/skills/`, and this maintainer-only symlink experiment must stay outside distributed consumer instructions.
- Canonical skill content itself.

## Ready work

Reviewing and, if the person with commit authority on this branch wants it, committing the five currently-unstaged `.devcontainer/` files (`Dockerfile`, `README.md`, `check_environment.py`, `devcontainer.json`, `post-create.sh`) is ready; no technical blocker was found in them.
Exercising the devcontainer change (an actual container rebuild) to confirm the Claude Code extension, volume, and permission checks behave as intended is ready but not yet done in any session.

## Current state

Branch `codex/claude-skill-symlinks` carries one relevant commit, 386584e, which added the 16 `.claude/skills/*` symlinks and the README note (both committed).
On 2026-09-27, verification in this session confirmed every one of the 16 symlinks resolves to an existing directory under `.agents/skills/` (`readlink` plus an existence check on each, all passing).
The working tree separately carries unstaged, uncommitted changes to five `.devcontainer/` files implementing Claude Code devcontainer support; these have not been committed or exercised in any session.

## Areas and relationships

- **Skill exposure**: `.claude/skills/*` symlinks to `.agents/skills/*`, documented in [README.md](../../README.md)'s ownership section. This is the only mechanism by which native Claude Code (which reads `.claude/skills/`) can see this repository's curated skills in a source checkout, since Agent Workflow's own lifecycle only ever writes `.agents/skills/`.
- **Devcontainer provisioning**: `.devcontainer/devcontainer.json` (extension + volume mount), `.devcontainer/post-create.sh` (directory creation and permission setup), `.devcontainer/check_environment.py` (verification of extension, home directory mode, and credential file mode), and `.devcontainer/Dockerfile`/`.devcontainer/README.md`. These extend the existing Codex-specific provisioning pattern to also cover Claude Code.

## Dependencies

Committing or amending the uncommitted `.devcontainer/` changes needs the person with project decision authority on this branch to ask for that commit; per [AGENTS.md](../../AGENTS.md) and the repository's git-safety instructions, commits are made only when explicitly requested.
Confirming the devcontainer changes work as intended needs an actual container rebuild, which no session has performed yet.

## Blockers

No technical defect was found in either the symlinks or the uncommitted devcontainer diff during this session's review.
The devcontainer changes remain unverified by an actual rebuild, and their effectiveness is a genuinely open question, not an assumed-passing one.

## Key references

- [Commit 386584e](https://github.com/jimmfan/agentic-workflow/commit/386584ec91397cd2bb7d890aaa1077c2ad0ea1e9) — adds the symlinks and README note.
- [.agent-workflow/README.md](../../.agent-workflow/README.md) — states Agent Workflow installs skills under `.agents/skills/`, not `.claude/skills/`.
- [README.md](../../README.md) ownership section — documents the symlink experiment and its exclusion from consumer installation.
- `.devcontainer/devcontainer.json`, `.devcontainer/post-create.sh`, `.devcontainer/check_environment.py` — uncommitted Claude Code devcontainer support.
