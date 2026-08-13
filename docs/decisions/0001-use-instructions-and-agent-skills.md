# ADR-0001: Use a compact router and Agent Skills

- Status: superseded by ADR-0004
- Date: 2026-08-11

## Context

The framework needs low always-on context, stable local Copilot support, explicit
workflow invocation, and no service. Prompt files remain preview and can be
ignored by Agent Host sessions; duplicating instructions in `AGENTS.md` would add
context without a distinct role.

## Decision

Use one `.github/copilot-instructions.md` router and five repository Agent Skills.
Keep project facts and durable state in ordinary Markdown read conditionally. Do
not require a custom agent, prompt files, nested instructions, hooks, forked skill
contexts, or UI handoffs.

This decision described the initial Copilot-first layout. ADR-0004 preserves its
progressive-disclosure principle but makes Codex primary, adopts shared root
`AGENTS.md`, moves the single skill tree to `.agents/skills`, and adds an
optional Hermes adapter.

## Consequences

The design uses stable progressive loading and works without optional features.
Routing remains model/instruction-driven rather than deterministic, and discovery
must be checked in a running VS Code session. A future custom agent can be added
as an optional UI role without changing state contracts.

## Alternatives considered

- A large always-on instruction: simpler file layout but persistent token cost.
- Prompt-file commands: explicit but preview and unavailable in some sessions.
- A custom-agent-only orchestrator: adds a role selection step and no persistence.
- A service or extension: stronger mechanics but disproportionate maintenance.
