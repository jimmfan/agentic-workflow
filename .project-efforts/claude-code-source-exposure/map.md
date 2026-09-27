# Claude Code source-checkout exposure

## Objective

Let native Claude Code tooling discover and run this source repository's authored content directly from checkout: the curated skills authored under `.agents/skills/`, and a devcontainer provisioned for the Claude Code extension.
This is a source-checkout experiment, not a change to what Agent Workflow installs into consuming projects.

## Scope

Includes:

- `.claude/skills/*` symlinks into `.agents/skills/*`, added in [commit 386584e](https://github.com/jimmfan/agentic-workflow/commit/386584ec91397cd2bb7d890aaa1077c2ad0ea1e9) on branch `codex/claude-skill-symlinks`, and the accompanying note added to [README.md](../../README.md) under the ownership section stating these links are a source-checkout experiment excluded from consuming-project installation.
- `.devcontainer/` changes, committed in [8c40bff](https://github.com/jimmfan/agentic-workflow/commit/8c40bff802f676a586f620ed5d85ef132a1218cf), that add the `anthropic.claude-code` extension, a persistent `/home/vscode/.claude` volume, directory/credential permission checks in `check_environment.py`, and provisioning steps in `post-create.sh`, mirroring the existing Codex devcontainer pattern.

Excludes:

- Agent Workflow's install/update/remove lifecycle for consuming projects; per [.agent-workflow/README.md](../../.agent-workflow/README.md), Agent Workflow installs skills under `.agents/skills/`, not `.claude/skills/`, and this maintainer-only symlink experiment must stay outside distributed consumer instructions.
- Canonical skill content itself.

## Ready work

Both items previously listed here are done; see Current state.
No further work is ready within this effort's objective and scope.
Merging `codex/claude-skill-symlinks` to `main` is not itself ready work: it needs a committed choice from the person with project decision authority (see Dependencies).

## Current state

Branch `codex/claude-skill-symlinks` carries two relevant commits, already pushed to `origin/codex/claude-skill-symlinks`: [386584e](https://github.com/jimmfan/agentic-workflow/commit/386584ec91397cd2bb7d890aaa1077c2ad0ea1e9) (the 16 `.claude/skills/*` symlinks and the README note) and [8c40bff](https://github.com/jimmfan/agentic-workflow/commit/8c40bff802f676a586f620ed5d85ef132a1218cf) (the `.devcontainer/` changes and this map).
The working tree is clean; no uncommitted changes remain in this effort's scope.
On 2026-09-27, this session verified live, post-rebuild: `/home/vscode/.claude` exists (mode `700`, owned `vscode:vscode`) and `.claude/.credentials.json` exists (mode `600`); `python3 .devcontainer/check_environment.py` exits 0 and reports the Claude Code extension configured; and the user confirmed `/wayfinder-effort` runs as a slash command in Claude Code, which also confirms the `.claude/skills/*` symlinks resolve and are discovered by the extension.
Not yet specified: whether Claude Code's OAuth sign-in specifically survived this rebuild without re-prompting — the checks above confirm the volume, permissions, and extension configuration, not that a prior login carried forward.

## Areas and relationships

- **Skill exposure**: `.claude/skills/*` symlinks to `.agents/skills/*`, documented in [README.md](../../README.md)'s ownership section. This is the only mechanism by which native Claude Code (which reads `.claude/skills/`) can see this repository's curated skills in a source checkout, since Agent Workflow's own lifecycle only ever writes `.agents/skills/`.
- **Devcontainer provisioning**: `.devcontainer/devcontainer.json` (extension + volume mount), `.devcontainer/post-create.sh` (directory creation and permission setup), `.devcontainer/check_environment.py` (verification of extension, home directory mode, and credential file mode), and `.devcontainer/Dockerfile`/`.devcontainer/README.md`. These extend the existing Codex-specific provisioning pattern to also cover Claude Code.

## Dependencies

Merging `codex/claude-skill-symlinks` to `main` needs the person with project decision authority to commit that choice; per [AGENTS.md](../../AGENTS.md), responsibility for verifying the branch does not by itself establish that authority.
Confirming the OAuth-persistence claim specifically (README's "should not require another login") needs a further observation of whether sign-in was re-prompted after a rebuild where credentials already existed; optional, not required by this effort's stated objective.

## Blockers

No technical defect was found in the symlinks or the devcontainer diff.
The devcontainer changes are no longer unverified: this session's live rebuild check passed (see Current state).
No blocker currently prevents merging other than the pending project decision noted under Dependencies.

## Key references

- [Commit 386584e](https://github.com/jimmfan/agentic-workflow/commit/386584ec91397cd2bb7d890aaa1077c2ad0ea1e9) — adds the symlinks and README note.
- [Commit 8c40bff](https://github.com/jimmfan/agentic-workflow/commit/8c40bff802f676a586f620ed5d85ef132a1218cf) — adds the `.devcontainer/` Claude Code support and this map.
- [.agent-workflow/README.md](../../.agent-workflow/README.md) — states Agent Workflow installs skills under `.agents/skills/`, not `.claude/skills/`.
- [README.md](../../README.md) ownership section — documents the symlink experiment and its exclusion from consumer installation.
- `.devcontainer/devcontainer.json`, `.devcontainer/post-create.sh`, `.devcontainer/check_environment.py` — committed Claude Code devcontainer support, verified live in this session.
