# ADR-0017: Automate invocation for routed provider skills

- Status: accepted
- Date: 2026-08-16
- Amends: ADR-0007 and ADR-0013

## Context

Agentic Workflow routes normal user intent to specification, ticketing, and
implementation capabilities, but the pinned To Spec, To Tickets, and Implement
skills disable model invocation in both shared `SKILL.md` metadata and Codex
`agents/openai.yaml` metadata. The router could therefore select the right
capability while being unable to load its configured provider unless the user
already knew the exact `$skill-name` or `/skill-name` command. Host-native
fallback kept work possible but made provider selection ineffective and exposed
an avoidable implementation detail to users.

The upstream method bodies remain compatible with the framework. Only their
activation policy conflicts with router-owned selection. Setup, Teach, and
Triage are different: they are explicit configuration, sustained-learning, or
external issue-state-machine operations and are not normal automatic routes.

## Decision

Declare To Spec, To Tickets, and Implement implicit on Codex and GitHub Copilot
and unavailable on Claude Code. Keep Setup, Teach, and Triage user-only.

Apply a narrow `implicit-invocation-v1` adapter to every release-local staged
projection. The bundled input is the exact upstream projection required by
ADR-0018, before Agentic Workflow adapters. For each declared skill, require
pinned source metadata and exactly one recognized upstream activation value in
both host metadata files. Rewrite
`disable-model-invocation: true` to `false` and
`allow_implicit_invocation: false` to `true`. Preserve the provider method body
and all unrelated bytes. Apply the two-file update transactionally and fail
closed on missing, duplicated, or unexpected metadata before projecting a
partial staged provider set.

The invocation declaration remains authoritative. Provider instructions do not
expand authorization: implicit selection cannot independently authorize issue
publication, commits, external mutation, or destructive work.

## Consequences

Users can request a specification, tickets, or implementation in ordinary
language and receive the configured provider method without a manual command or
post-install edit. Re-running installation or update stages and adapts a fresh
copy of the upstream bundle, then reuses an exact installed effective projection;
differing target bytes are preserved as conflicts under ADR-0018.

The lifecycle now supports a second intentionally narrow adapter shape in
addition to Wayfinder's local-state adapter. This is justified by three concrete
routed skills with the same host-metadata conflict; it is not a general provider
patch language. A future provider release with changed metadata fails clearly
until the adapter is reviewed.

## Alternatives considered

- Preserve upstream user-only metadata: rejected because it prevents the router
  from executing the provider it selected.
- Ask users to edit downloaded skills: rejected because updates restore upstream
  metadata and create per-project drift.
- Override only router wording: rejected because hidden skills never reach the
  model for selection.
- Rewrite provider method bodies: rejected because the behavioral instructions
  are compatible and only activation metadata needs to differ.
