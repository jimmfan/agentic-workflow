# Claude Code source-checkout exposure

## Objective

Let native Claude Code tooling discover and run this source repository's authored content directly from checkout: the curated skills authored under `.agents/skills/`, and a devcontainer provisioned for the Claude Code extension.
This is a source-checkout experiment, not a change to what Agent Workflow installs into consuming projects.

## Scope

Includes:

- `.claude/skills/*` symlinks into `.agents/skills/*`, added in [commit 386584e](https://github.com/jimmfan/agentic-workflow/commit/386584ec91397cd2bb7d890aaa1077c2ad0ea1e9) on branch `codex/claude-skill-symlinks`, and the accompanying note added to [README.md](../../README.md) under the ownership section stating these links are a source-checkout experiment excluded from consuming-project installation.
- `.devcontainer/` changes, committed in [8c40bff](https://github.com/jimmfan/agentic-workflow/commit/8c40bff802f676a586f620ed5d85ef132a1218cf), that add the `anthropic.claude-code` extension, a persistent `/home/vscode/.claude` volume, and provisioning steps in `post-create.sh`, mirroring the existing Codex devcontainer pattern.
- A follow-up removal of the redundant devcontainer environment checker, requested on 2026-09-27, while retaining the provisioning steps.

Excludes:

- Agent Workflow's install/update/remove lifecycle for consuming projects; per [.agent-workflow/README.md](../../.agent-workflow/README.md), Agent Workflow installs skills under `.agents/skills/`, not `.claude/skills/`, and this maintainer-only symlink experiment must stay outside distributed consumer instructions.
- Canonical skill content itself.

## Ready work

Review the checker-removal follow-up; committing it requires a separate request.
Merging `codex/claude-skill-symlinks` to `main` also needs the project choice and delivery checks under Dependencies.

## Current state

The 16 `.claude/skills/*` symlinks and the initial devcontainer support are committed in [386584e](https://github.com/jimmfan/agentic-workflow/commit/386584ec91397cd2bb7d890aaa1077c2ad0ea1e9) and [8c40bff](https://github.com/jimmfan/agentic-workflow/commit/8c40bff802f676a586f620ed5d85ef132a1218cf).
The checker removal is a pending working-tree change on `codex/claude-skill-symlinks`.
On 2026-09-27, post-rebuild verification found `/home/vscode/.claude` (mode `700`, owned `vscode:vscode`) and `.claude/.credentials.json` (mode `600`); the former environment checker exited 0 before removal; and the user confirmed `/wayfinder-effort` runs as a slash command in Claude Code, which also confirms the `.claude/skills/*` symlinks resolve and are discovered by the extension.
Not yet specified: whether Claude Code's OAuth sign-in specifically survived this rebuild without re-prompting — the checks above confirm the volume, permissions, and extension configuration, not that a prior login carried forward.

## Areas and relationships

- **Skill exposure**: `.claude/skills/*` symlinks to `.agents/skills/*`, documented in [README.md](../../README.md)'s ownership section. This is the only mechanism by which native Claude Code (which reads `.claude/skills/`) can see this repository's curated skills in a source checkout, since Agent Workflow's own lifecycle only ever writes `.agents/skills/`.
- **Devcontainer provisioning**: `.devcontainer/devcontainer.json` (extension + volume mount), `.devcontainer/post-create.sh` (directory creation and permission setup), and `.devcontainer/Dockerfile`/`.devcontainer/README.md`. These extend the existing Codex-specific provisioning pattern to also cover Claude Code.

## Dependencies

Merging `codex/claude-skill-symlinks` to `main` needs the checker-removal follow-up reviewed and committed, delivery checks run, and the person with project decision authority to commit that choice; per [AGENTS.md](../../AGENTS.md), responsibility for verifying the branch does not by itself establish that authority.
Confirming the OAuth-persistence claim specifically (README's "should not require another login") needs a further observation of whether sign-in was re-prompted after a rebuild where credentials already existed; optional, not required by this effort's stated objective.

## Blockers

The checker-removal follow-up remains uncommitted, and the merge decision and delivery checks remain pending.
The earlier live rebuild check passed for the initial devcontainer support (see Current state).

## Key references

- [Commit 386584e](https://github.com/jimmfan/agentic-workflow/commit/386584ec91397cd2bb7d890aaa1077c2ad0ea1e9) — adds the symlinks and README note.
- [Commit 8c40bff](https://github.com/jimmfan/agentic-workflow/commit/8c40bff802f676a586f620ed5d85ef132a1218cf) — adds the `.devcontainer/` Claude Code support and this map.
- [.agent-workflow/README.md](../../.agent-workflow/README.md) — states Agent Workflow installs skills under `.agents/skills/`, not `.claude/skills/`.
- [README.md](../../README.md) ownership section — documents the symlink experiment and its exclusion from consumer installation.
- `.devcontainer/devcontainer.json`, `.devcontainer/post-create.sh` — Claude Code devcontainer configuration and retained provisioning.
