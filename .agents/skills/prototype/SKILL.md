---
description: Explore a design question through a throwaway interactive logic or state-model demo, or contrasting UI variants. Use when clicking through behavior or comparing screens would answer the question; CLI and infrastructure experiments may use Direct or existing methods.
name: prototype
---
# Prototype

A prototype is **throwaway code that answers a question**.
This skill's methods answer questions through interactive logic demos or UI exploration.
Use Direct or another suitable existing method for experiments whose evidence does not benefit from either shape; CLI and infrastructure experiments need not become HTML.

## Pick a branch

Identify which question is being answered — from the user's prompt, the surrounding code, or by asking if the user is around:

- **"Does this logic / state model feel right?"**
  → [LOGIC.md](LOGIC.md).
  Build a single shareable HTML file — free-play buttons plus tabbed guided walkthroughs — that pushes the state machine through cases that are hard to reason about on paper, and that a non-developer can drive.
- **"What should this look like?"**
  → [UI.md](UI.md).
  Generate several radically different UI variations on a single route, switchable via a URL search param and a floating bottom bar.

Choose a branch only when its interaction can answer the question.
Infer the shape from the request and code when supported, and state any material assumption; a backend location alone does not require an HTML logic demo.

## Rules that apply to both

1. **Throwaway from day one, and clearly marked as such.**
   Locate the prototype code close to where it will actually be used (next to the module or page it's prototyping for) so context is obvious — but name it so a casual reader can see it's a prototype, not production.
   For throwaway UI routes, obey whatever routing convention the project already uses; don't invent a new top-level structure.
2. **Trivial to run.**
   A UI prototype starts from one command in the project's task runner — `pnpm <name>`, `python <path>`, `bun <path>`, etc.
   A logic demo is a single HTML file the user double-clicks.
   Either way, no thinking required to start it.
3. **No persistence by default.**
   State lives in memory.
   Persistence is the thing the prototype is _checking_, not something it should depend on.
   If the question explicitly involves a database, hit a scratch DB or a local file with a clear "PROTOTYPE — wipe me" name.
   Keep mutations isolated from real systems and data; UI actions use stubs, and any real-data reads remain within the authorized scope.
4. **Skip the polish.**
   No tests, no error handling beyond what makes the prototype _runnable_, no abstractions.
   The point is to learn something fast.
5. **Surface the state.**
   After every action (logic) or on every variant switch (UI), print or render the full relevant state so the user can see what changed.
6. **Report the answer and preserve useful evidence.**
   Report the question, observed result, and limitations to the user.
   Prototype work alone does not authorize production adoption, commits, or publication.
   When authorized, preserve the prototype as a primary source on a named throwaway branch and put a usable reference and the answer in the designated issue or artifact.
   Before authorized production adoption, implement the accepted decision to production standards and verify the affected behavior and boundaries.
   Keep throwaway demo code and unused variants out of the production result.
