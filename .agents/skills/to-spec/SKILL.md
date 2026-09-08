---
description: Turn the current conversation into a spec — no interview, just synthesis of what you've already discussed.
name: to-spec
---
This skill takes the current conversation context and codebase understanding and produces a spec.
Do NOT interview the user — just synthesize what you already know.

Use a publication destination named by the user or documented by the project.
Publish only when the current request or accepted project policy authorizes it; otherwise return the complete draft in chat.
Do not invent a local destination, label, or status.

## Process

1. Explore the repo to understand the current state of the codebase, if you haven't already.
   Use the project's domain glossary vocabulary throughout the spec, and respect any ADRs in the area you're touching.

2. Reuse scope and testing decisions accepted in the request, conversation, project artifacts, or invoking workflow.
   Describe the modules under test and their agreed caller-facing seams.
   Prefer existing seams that can verify the supported behavior.
   Mark missing decisions as unresolved and any suggested seams or scope as proposals; do not turn inference into agreement or start an interview.

3. Write the spec using the template below.

<spec-template>

## Problem Statement

The problem that the user is facing, from the user's perspective.

## Solution

The solution to the problem, from the user's perspective.

## User Stories

A numbered list covering the supported in-scope behavior completely, without duplicate stories or speculative expansion.
Each user story should be in the format of:

1. As an <actor>, I want a <feature>, so that <benefit>

<user-story-example>
1. As a mobile bank customer, I want to see balance on my accounts, so that I can make better informed decisions about my spending
</user-story-example>

Include distinct actors, outcomes, and consequential failure or edge cases supported by the conversation and accepted artifacts.
Keep unresolved scope questions in Further Notes rather than inventing stories to fill them.

## Implementation Decisions

A list of implementation decisions that were made.
Distinguish accepted decisions from proposals and unresolved matters; writing the spec does not approve them.
This can include:

- The modules that will be built/modified
- The interfaces of those modules that will be modified
- Technical clarifications from the developer
- Architectural decisions
- Schema changes
- API contracts
- Specific interactions

Do NOT include specific file paths or code snippets.
They may end up being outdated very quickly.

Exception: if a prototype produced a snippet that encodes a decision more precisely than prose can (state machine, reducer, schema, type shape), inline it within the relevant decision and note briefly that it came from a prototype.
Trim to the decision-rich parts — not a working demo, just the important bits.

## Testing Decisions

A list of testing decisions that were made.
Include:

- A description of what makes a good test (test caller-observable behavior of the module under test, not private implementation details)
- Which modules will be tested
- Prior art for the tests (i.e. similar types of tests in the codebase)

## Out of Scope

A description of the things that are out of scope for this spec.

## Further Notes

Any further notes about the feature.
Include consequential unresolved questions and the boundaries they affect, without inventing answers or approval.

</spec-template>
