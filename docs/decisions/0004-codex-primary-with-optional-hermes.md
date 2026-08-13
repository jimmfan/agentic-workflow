# ADR-0004: Codex primary with optional Hermes research

- Status: accepted
- Date: 2026-08-11
- Supersedes: ADR-0001 layout decision

## Context

The first implementation targeted local GitHub Copilot. The refined workflow
needs a first-class Codex experience, cheap Copilot portability, and optional
Hermes capabilities without a second policy tree, mandatory agent hop, alternate
model provider, concurrent editor, or unsafe repository boundary.

Hermes v0.20.0 supports an `openai-codex` provider and open-format skills, but
its native `file` toolset combines reads and writes. Its optional Codex
app-server runtime cannot select `:read-only` end to end through the public
Hermes CLI/config path at the audited release. Its migration ignores
`CODEX_HOME`: an ordinary process home can couple it to normal Codex
configuration, while an isolated process home makes migration and the runtime
target two different private Codex directories.

## Decision

Use a compact shared root `AGENTS.md` and one canonical `.agents/skills` tree.
Codex is the default agent loop and owns repository work, native subagents,
sandboxing, approvals, implementation, and verification. Current Copilot
surfaces also discover both locations, so no duplicate Copilot instruction or
skill tree is needed.

Provide one disabled-by-default Hermes skill plus a standard-library adapter.
The implemented `research` level runs the exact audited Hermes/OpenAI-Codex
combination outside the repository with only `web,memory,skills`, validates a
bounded result, and detects repository changes. A dedicated Hermes root plus
private process `HOME` and `CODEX_HOME` prevents the research path from importing
or refreshing normal Codex credentials/configuration. Profile-private
self-improvement remains available; external skill directories stay empty and
learned skill writes require profile-local approval. Parent Codex verifies and
synthesizes.

Recognize `repo-read` as a capability level but return unavailable for v0.20.0.
Do not enable write-capable Hermes repository work. Do not install, authenticate,
update, or reconfigure Hermes during framework adoption or ordinary fallback.

## Consequences

Codex-only mode remains complete. Copilot gets a host-neutral subset without
duplicated workflow bodies. Hermes adds useful bounded web research only after a
separate user-local install/profile/auth flow. Native Hermes private memory and
skill proposals do not become repository truth.

The `research` boundary minimizes capabilities and detects working-tree changes;
it is not an OS sandbox. Live Hermes execution and prompt-size measurement remain
unverified until the separate installation/authentication prerequisites are met.
The app-server `repo-read` design must be re-audited and pass negative write
canaries before a future release can enable it.

## Alternatives considered

- Hermes as a mandatory orchestrator: rejected because it reverses ownership and
  makes core engineering depend on an optional runtime.
- Direct shared Hermes `external_dirs`: rejected because foreground skill tools
  can modify those directories.
- Hermes native `file` toolset: rejected because it bundles write and patch
  capabilities with reads.
- Codex app-server `:read-only` at v0.20.0: rejected because the public Hermes
  path does not reliably select or isolate that profile.
- A generic agent plugin/RPC framework: rejected as unnecessary maintenance.
