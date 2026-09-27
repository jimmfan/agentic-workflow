# Claude Code skill exposure

## Objective

Enable native Claude Code to discover and run Agent Workflow's curated skills both in this source checkout and in consuming projects after Agent Workflow install or update.
Keep the source devcontainer usable for Claude Code development.

## Scope

Includes:

- The source-checkout `.claude/skills/*` links to the canonical `.agents/skills/*` directories, merged in [PR #58](https://github.com/jimmfan/agentic-workflow/pull/58).
- The Claude Code devcontainer extension, persistent `/home/vscode/.claude` volume, and provisioning in `.devcontainer/`, including removal of the redundant environment checker, merged in the same PR.
- The consumer lifecycle change that creates those links during install and update, reports missing links in status, and removes only matching links during remove.
  Existing Claude Code content outside the curated names is preserved; a conflicting entry at a curated name blocks install or update before mutation.

Excludes changes to canonical skill content and changes to any specific consuming project.

## Ready work

No additional implementation work is identified.
The reviewed consumer lifecycle change on `codex/claude-consumer-skills` is prepared for delivery.

## Current state

[PR #58](https://github.com/jimmfan/agentic-workflow/pull/58) merged the source-checkout links, devcontainer support, and checker removal into `main` at commit `4e9b861`.
After the workspace rebuild on 2026-09-27, the user confirmed `/wayfinder-effort` ran in Claude Code, establishing that the source-checkout links were discovered there.
The rebuild also showed `/home/vscode/.claude` with the expected ownership and permissions; whether a prior OAuth sign-in survived without a prompt was not observed.

The consumer lifecycle change is an uncommitted local change on `codex/claude-consumer-skills`, with `VERSION` set to 0.36.0.
Its existing-installation update test, full package verification (219 tests), evaluation tests (88), and wheel smoke tests (2) passed; native Claude Code was not run in a consuming project.
The released 0.35.3 lifecycle still installs only `.agents/skills/`, so an existing project's normal update does not yet create `.claude/skills/`.

## Areas and relationships

- **Canonical skills and native discovery:** `.agents/skills/` remains the maintained skill source.
  Source-checkout links and the consumer lifecycle project each curated skill into `.claude/skills/` for native Claude Code without copying skill content.
- **Consumer preservation:** [ADR-0010](../../architecture-decisions/0010-separate-framework-output-from-project-owned-state.md) and the [lifecycle](../../agent_workflow/lifecycle.py) define the managed link boundary and preservation of unrelated project content.
- **Devcontainer provisioning:** `.devcontainer/devcontainer.json` configures the extension and volume; `.devcontainer/post-create.sh` prepares the directory and permissions.

## Dependencies

Consumer projects can receive the new links only after the lifecycle change is committed, merged, and released, and those projects run an update using that release.
Confirming OAuth persistence specifically would require observing a rebuild with existing credentials; it is optional for the stated objective.

## Blockers

The consumer rollout awaits delivery of the uncommitted 0.36.0 change.

## Key references

- [Consumer lifecycle](../../agent_workflow/lifecycle.py) and [lifecycle tests](../../tests/test_lifecycle.py) — link creation, status, removal, collision handling, and the existing-project update case.
- [README.md](../../README.md) and [.agent-workflow/README.md](../../.agent-workflow/README.md) — installed behavior and host support.
- [ADR-0010](../../architecture-decisions/0010-separate-framework-output-from-project-owned-state.md) — ownership and preservation boundary.
- [PR #58](https://github.com/jimmfan/agentic-workflow/pull/58) — merged source-checkout and devcontainer work.
