# ADR-0025: Preserve human authority across workflows

- Status: accepted
- Date: 2026-08-18

## Context

Agentic Workflow distinguishes provider execution, repository evidence, and
user authorization, but no current architecture decision directly governs a
choice whose substance requires human or project authority. Without an explicit
boundary, an agent can correctly avoid a D# yet still smuggle an assumed answer
into a specification, implementation ticket, or implementation plan.

This is cross-cutting rather than Wayfinder-specific. Intent, preference,
approval, prioritization, policy ownership, and other authority-dependent
choices can block Discovery, Wayfinder, specifications, tickets, or
implementation.

## Decision

When a choice requires human or project authority, an agent must not decide it
on the human's behalf. It surfaces the concrete question, explains why that
authority is required, and states what the answer will unblock. Until an
authoritative answer or accepted project artifact exists, the choice remains
explicitly unresolved or blocked.

An assumption, proposal, default, precedent, or model preference cannot become
an accepted decision, specification requirement, implementation ticket, or
implementation direction merely because progress would be convenient. Provider
instructions and workflow state do not expand decision authority.

This rule does not require human approval for every technical judgment. Agents
may make evidence-backed choices inside authority already delegated by the user
or accepted project policy. The gate applies when the choice itself belongs to a
human or project authority.

## Consequences

The root installed policy carries one concise invariant because violating this
boundary can cause cross-cutting authorization and truthfulness failures.
Workflow-specific instructions may explain how to preserve the blocker or
resume after an answer, but they do not create separate authority models.

Behavioral tests should observe the public question and prohibited downstream
artifacts rather than require hidden reasoning or one exact workflow trace.

## Alternatives considered

- Keep the rule only in Wayfinder: rejected because specifications, tickets,
  and implementation can fabricate the same authority-dependent choice.
- Treat every unresolved choice as requiring human approval: rejected because
  it would block ordinary delegated technical judgment and add ceremony.
