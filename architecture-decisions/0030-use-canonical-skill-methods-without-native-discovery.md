# ADR-0030: Use canonical skill methods without native discovery

- Status: accepted
- Date: 2026-09-18

## Context

Agent Workflow distributes canonical methods under `.agents/skills/` and historically allowed them to run only when a host exposed the corresponding skill in the current session.
That coupled method availability to native skill discovery even when a host could load the root routing policy and read ordinary repository files.

Claude Code illustrates the gap without defining it: current Claude Code can load `AGENTS.md` as project instructions, while its documented project-skill location is `.claude/skills/` rather than `.agents/skills/`.
Copying the curated tree into each provider-specific location would create duplicate maintained instructions and provider lifecycle surface.

Many curated methods are ordinary model instructions over repository files and common tools.
Some methods also require capabilities such as independent parallel reviewers or an interactive surface that a particular session may not provide.
Instruction readability therefore does not by itself establish method availability or execution.

## Decision

Keep host-native skill execution as the preferred path when the host exposes a selected skill.
When native exposure is absent, allow routing to use the canonical `.agents/skills/<name>/SKILL.md` description for selection and to read that file as repository instructions.
The agent may execute the method directly only when the canonical instructions are readable and every capability required for the current method is available.

Call the second path portable method execution in routing explanations.
This phrase distinguishes how instructions were loaded; it does not create a new framework state type or provider abstraction.
The ordinary route label continues to name the method that actually executed, while surrounding reporting must not imply native discovery, native invocation, or unavailable host features.

Selecting a method, reading its instructions, or checking capabilities is not execution.
Missing canonical instructions use the existing unavailable outcome.
A missing capability required by the method uses the existing unavailable or blocked outcome according to whether the capability cannot run or a prerequisite prevents it.
An optional skill may still fall back to Direct when Direct can truthfully satisfy the request.

## Consequences

Hosts with repository-file access can apply portable Agent Workflow methods without a duplicate skill tree.
Native hosts keep their existing skill mechanics and canonical installed content.
Authorization, project decision authority, evidence, durable-state ownership, composition, and route-reporting rules are unchanged.

Deterministic tests can establish the instruction contract and synthetic outcomes, but they do not prove live model compliance.
Live host evaluation remains separate evidence and must distinguish method execution from native skill invocation.

## Alternatives considered

- Copy curated skills into `.claude/skills/`: rejected because it duplicates canonical instructions and adds provider-specific lifecycle ownership.
- Add a general host/provider compatibility layer: rejected because current behavior needs only an instruction-source and capability distinction.
- Keep native exposure as the only availability test: rejected because it makes readable, executable methods unnecessarily unavailable.
- Treat every readable method as executable: rejected because it would falsely claim required native or session capabilities.

## Reconsideration trigger

Reconsider if supported hosts converge on one native skill location, repository-read execution proves unreliable in live evaluations, or a required host feature cannot be represented truthfully by the existing unavailable and blocked semantics.
