# Project profile

## Purpose and success

This repository distributes a lightweight Codex-first AI engineering workflow
with optional Hermes research and a GitHub Copilot-compatible subset. Success means a consuming
repository can adopt, update, use, verify, and remove the workflow without a
service, package registry, or third-party runtime skill.

## Technology and architecture

The implementation is repository-native Markdown plus Python 3 standard-library
verification, adoption, and optional-adapter scripts. Compact shared policy routes
requests to progressively loaded Agent Skills. Project-owned Markdown provides domain
context and durable workflow state.

## Important paths

- `AGENTS.md`: compact shared always-loaded policy.
- `.agents/skills/`: canonical conditional workflow modules.
- `adapters/hermes/`: optional bounded-research contracts and profile template.
- `ai-workflow/`: contracts, project profile, templates, and durable state.
- `scripts/`: adoption and verification utilities.
- `tests/`: acceptance specifications and standard-library tests.
- `docs/`: research, architecture, routing, and decision records.
- `ai-engineering-workflow-implementation-prompt.md`: canonical framework
  implementation specification retained for requirements audits.
- `ai-workflow/state/records/TKT-*.md`: local canonical implementation tickets;
  no native external tracker is configured for this repository.

## Terminology

- `core`: generic policy, skills, contracts, and templates copied to projects.
- `project-owned`: consuming-project content never overwritten by the updater.
- `framework-owned`: installed content updated only when its prior checksum still
  matches the installation manifest.

## Constraints and policy

Keep runtime behavior general-purpose, repository-scoped, reviewable, and usable
without optional third-party skills. Do not publish, deploy, install host-wide
software, or execute external mutations during framework verification. Meaningful
implementation in this repository does not require a separate plan-approval pause.

## Delivery workflow

Change the smallest relevant files, run the configured verifier, inspect its
reported evidence, then independently review meaningful changes for specification
fit, correctness, security, validation gaps, and unintended scope. The parent
task dispositions findings; only the maintainer may accept a material review
limitation. Skip formal independent review for trivial low-risk edits. Manually
inspect Copilot customization discovery when VS Code behavior itself changes.
Publishing and version tagging are out of scope.

## Commands

### `verify-framework`

- Purpose: Validate structure, skill metadata, contracts, scenario coverage,
  domain separation, context duplication, and adoption safety behavior.
- Action: `python3 scripts/verify_framework.py`
- Kind: `command`
- Working directory: `.`
- Prerequisites: Python 3.9 or newer.
- Environment: None.
- Scope: `host-local`
- Safety: `read-only`
- Approval required: `no`
- Timeout: 30 seconds.
- Success: Exit status 0 and a final `OK` summary with every check passing.
- Unavailable: Report blocked; do not substitute or claim full verification.
- Side effects and reversal: Temporary directories are created under the system
  temporary directory and removed automatically; no persistent change.

### `manual-copilot-discovery`

- Purpose: Confirm the running VS Code/Copilot instance discovers the installed
  shared policy and skills; static repository checks cannot prove this UI behavior.
- Action: In VS Code, open Chat, right-click the Chat view, choose `Diagnostics`,
  and confirm the report lists `AGENTS.md` plus all eight skills under
  `.agents/skills` without load errors. Then confirm the eight skills appear in
  the Chat `/` menu and send a request while checking Chat `References` for the
  `AGENTS.md`.
- Kind: `manual`
- Working directory: `.` opened as the VS Code workspace root.
- Prerequisites: Current stable VS Code and GitHub Copilot Chat with Agent Skills
  and repository instructions enabled (both default settings).
- Environment: A signed-in GitHub Copilot session; no credential value is stored.
- Scope: `external`
- Safety: `read-only`
- Approval required: `yes`
- Timeout: About 5 minutes.
- Success: Diagnostics shows `AGENTS.md` and eight skills with no load errors; the
  slash menu exposes each skill; References includes `AGENTS.md` on a chat turn.
- Unavailable: Use `Developer: Open Agent Debug Panel` or Chat's `Show Agent Debug
  Logs`; if neither is available, report interactive discovery unverified.
- Side effects and reversal: Sends one prompt to GitHub Copilot and may add it to
  the signed-in account's chat history. Delete that chat in VS Code if retention
  is unwanted; local Diagnostics inspection alone has no durable side effect.

## Debugging model

For static failures, follow verifier output from the named test to the referenced
file. For adoption failures, distinguish source-tree validation, manifest parsing,
target path safety, checksum conflicts, and filesystem writes. For Copilot
discovery failures, inspect paths/frontmatter first, then Chat Diagnostics and the
Agent Debug Log; repository tests cannot validate a running extension session.

## Decision considerations

Favor stable Codex primitives, low always-on context, transparent files,
standard-library tools, checksum-guarded updates, and explicit limitations over
platform simulations. Preview features require an optional fallback.

## Profile maintenance

- Owner: Framework maintainers.
- Last reviewed: 2026-08-12.
- Becomes stale when: Codex or VS Code customization paths/statuses change, the core
  file set changes, or adoption/verification behavior changes.
- Conflict behavior: Verify against source, current official documentation, and
  observed tool behavior; report and correct the profile before relying on it.
