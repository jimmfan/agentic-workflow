# ADR-0030: Use canonical skill methods without native discovery

- Status: accepted
- Date: 2026-09-18

## Context

Agent Workflow distributes canonical methods under `.agents/skills/` and historically allowed them to run only when a host exposed the corresponding skill in the current session.
That coupled method availability to native skill discovery even when a host could load the root routing policy and read ordinary repository files.

Claude Code illustrates the gap without defining it: current Claude Code can load `AGENTS.md` as project instructions, while its documented project-skill location is `.claude/skills/` rather than `.agents/skills/`.
Copying the curated tree into each provider-specific location would create duplicate maintained instructions and provider lifecycle surface.

Many curated methods are ordinary model instructions over repository files and common tools.
Some methods also require tools or host features such as independent parallel reviewers or an interactive surface that a particular session may not provide.
Instruction readability therefore does not by itself establish method availability or execution.

## Decision

Use one selected skill method regardless of how its canonical instructions are obtained.
When the host exposes the selected skill, the host loads those instructions through its native skill mechanism.
When the host does not expose the selected skill, allow routing to use the canonical `.agents/skills/<name>/SKILL.md` description for selection and to read that file directly as repository instructions.
The selected method may run only when every tool or host feature it requires for the request can run.

The ordinary route label continues to name the method that actually executed, not how its instructions were loaded.
Reporting after a repository read must not imply native discovery, loading, or invocation, or claim that unavailable host features ran.

Selecting a method or reading its instructions is not execution.
Missing canonical instructions use the existing unavailable outcome.
A required tool or host feature that does not exist or cannot run makes the method unavailable.
When required support exists and could run, authorization, project state, a required input or prerequisite, or an integrity condition may instead block progress.
An optional skill may still fall back to Direct when Direct can truthfully satisfy the request.

## Consequences

Hosts with repository-file access can use canonical Agent Workflow instructions without a duplicate skill tree.
Native hosts keep their existing skill mechanics and canonical installed content.
Authorization, project decision authority, evidence, durable-state ownership, composition, and route-reporting rules are unchanged.

Deterministic tests can establish the instruction contract and synthetic outcomes, but they do not prove live model compliance.
Live host evaluation remains separate evidence and must distinguish method execution from native skill invocation.

## Alternatives considered

- Copy curated skills into `.claude/skills/`: rejected because it duplicates canonical instructions and adds provider-specific lifecycle ownership.
- Add a general host/provider compatibility layer: rejected because current behavior needs only two literal ways to obtain the same canonical instructions.
- Keep native exposure as the only availability test: rejected because it makes readable, executable methods unnecessarily unavailable.
- Treat every readable method as executable: rejected because a required tool or host feature may not exist or may be unable to run.

## Reconsideration trigger

Reconsider if supported hosts converge on one native skill location, repository-read instruction loading proves unreliable in live evaluations, or a required host feature cannot be represented truthfully by the existing unavailable and blocked semantics.
