# ADR 0009: Use a host-neutral lifecycle controller with VS Code as reference

- Status: Accepted
- Date: 2026-08-14

## Context

Agentic Workflow contains hard rules whose truth previously depended entirely
on model compliance: route before action, diagnosis-only write denial, truthful
provider execution claims, durable-state conflict handling, and evidence before
completion. The supported hosts now expose lifecycle hooks, but their schemas,
trust models, event coverage, failure behavior, and configuration ownership
differ. GitHub Copilot in VS Code is the product's primary runtime, and its hooks
are currently Preview.

A Codex-shaped runtime would make the primary host a compatibility layer. A
lowest-common-denominator design would discard useful deterministic checks.
Parsing shell text would be brittle and would incorrectly move semantic
judgment into policy code.

## Decision

Adopt a small shared Python controller and thin host adapters. GitHub Copilot in
VS Code is the active reference adapter. Codex and Claude Code receive opt-in
templates because their fixed project hook files may be user-owned. Copilot CLI
and cloud remain separately described and instruction-only until their distinct
contracts justify active adapters.

The controller enforces declared lifecycle consistency and observable native
tool boundaries. The model chooses routes, classifies opaque actions, decides
verification relevance, and judges evidence sufficiency. Instruction-driven
behavior remains complete and authoritative when hooks do not run.

Transient controller state is metadata-only and stored outside the repository.
Durable workflow state and provider-native artifacts retain their existing
ownership. Package lifecycle owns active adapter installation, update, status,
and removal.

## Consequences

The primary host gains deterministic denial for high-value observable failures
without becoming a hard dependency on a Preview API. Codex and Claude can add
stronger optional enforcement without changing the common semantic contract.
Status must report capability separately from integrity.

The result is not a security boundary. Opaque action declarations can be false,
host coverage can be incomplete, and PostToolUse cannot establish semantic test
success. The root instruction contract therefore remains necessary, and public
claims use `partial` rather than `fully enforced`.

The active hook file has a unique lifecycle-owned path. CLI/cloud may discover
that versioned file, but their runtime guarantee remains separately unvalidated.
Secondary adapters are not automatically merged into user-owned fixed
configuration files. Direct native edits to the controller/active hook are
denied; package update is the supported mutation path.
