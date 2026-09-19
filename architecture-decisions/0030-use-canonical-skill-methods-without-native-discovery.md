# ADR-0030: Use canonical skill methods without native discovery

- Status: accepted
- Date: 2026-09-18

## Context

Agent Workflow distributes canonical methods under `.agents/skills/` and historically allowed them to run only when a host exposed the corresponding skill in the current session.
That coupled method availability to native skill discovery even when a host could load the root routing policy and read ordinary repository files.

Claude Code illustrates the gap without defining it: current Claude Code can load `AGENTS.md` as project instructions, while its documented project-skill location is `.claude/skills/` rather than `.agents/skills/`.
Copying the curated tree into each provider-specific location would create duplicate maintained instructions and provider lifecycle surface.

Many curated methods are ordinary model instructions over repository files and common tools.
Reading those instructions does not supply missing execution support.

## Decision

Use one selected skill method regardless of how its canonical instructions are obtained.
When the host exposes the selected skill, the host loads those instructions through its native skill mechanism.
When the host does not expose the selected skill, allow routing to use the canonical `.agents/skills/<name>/SKILL.md` description for selection and to read that file directly as repository instructions.
The loading path does not change the selected method's requirements or turn a repository read into native invocation.
Existing execution, availability, blocking, Direct-fallback, and reporting rules remain in the [routing policy](../.agent-workflow/routing.md#use-selected-skills).

## Consequences

Hosts with repository-file access can use canonical Agent Workflow instructions without a duplicate skill tree.
Native hosts keep their existing skill mechanics and canonical installed content.
Authorization, project decision authority, evidence, durable-state ownership, composition, and route-reporting rules are unchanged.

Deterministic tests check canonical references and distribution; instruction meaning also requires review.
The [live protocol](../evals/portable-skill-routing/README.md) tests method compliance and reporting on Claude Code.
Whether additional host-specific safeguards improve behavior remains an evaluation question.

## Alternatives considered

- Copy curated skills into `.claude/skills/`: rejected because it duplicates canonical instructions and adds provider-specific lifecycle ownership.
- Add a general host/provider compatibility layer: rejected because current behavior needs only two literal ways to obtain the same canonical instructions.
- Keep native exposure as the only availability test: rejected because it makes readable, executable methods unnecessarily unavailable.
- Treat every readable method as executable: rejected because a required tool or host feature may not exist or may be unable to run.

## Reconsideration trigger

Reconsider if supported hosts converge on one native skill location, repository-read instruction loading proves unreliable in live evaluations, or a required host feature cannot be represented truthfully by the existing unavailable and blocked semantics.
