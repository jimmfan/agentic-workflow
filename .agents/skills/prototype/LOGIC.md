# Logic Prototype

A single, self-contained HTML file — a **shareable demo** — that lets anyone drive a state model by clicking buttons.
Use this when clicking through **business logic, state transitions, or data shape** will help someone assess cases that are hard to reason about on paper.

## When this is the right shape

- "I'm not sure if this state machine handles the edge case where X then Y."
- "Does this data model actually let me represent the case where..."
- "I want to click through how callers would use this API before writing it."
- Anything where someone wants to **press buttons and watch state change**.

If the question is "what should this look like" — wrong branch.
Use [UI.md](UI.md).

## Process

### 1. State the question

Before writing code, write down what state model and what question you're prototyping.
One paragraph, at the top of the demo (in a visible intro, not just a comment).

### 2. Isolate the logic in a portable module

Put the actual logic — the bit that's answering the question — in a single `<script>` block written as a small, pure module that could be lifted out and dropped into the real codebase later.
The page and logic remain prototype code until production adoption is authorized and verified.

The right shape depends on the question:

- **A pure reducer** — `(state, action) => state`.
  Good when actions are discrete events and state is a single value.
- **A state machine** — explicit states and transitions.
  Good when "which actions are even legal right now" is part of the question.
- **A small set of pure functions** over a plain data type.
  Good when there's no implicit current state — just transformations.
- **A class or module with a clear method surface** when the logic genuinely owns ongoing internal state.

Pick whichever shape best fits the question being asked, *not* whichever is easiest to wire to a page.
Keep it pure: no DOM, no `document`, no button handlers reaching inside it.
The page calls into it; nothing flows the other direction.

### 3. Build the shareable HTML file

One file, plain HTML/CSS/JS — no framework, no bundler, no server, everything inline so it opens by double-click and survives being emailed around.

Write it for a non-developer.
Every label is in **domain language**, not code — buttons and state read like the business, not the reducer.
Explain in plain words what's happening.

Lay it out with a clean hierarchy, top to bottom:

1. **Title and one-line explanation** of what this demo lets you explore (the question from step 1).
2. **Current state** — the full relevant state, rendered as a readable panel (labelled fields, not a raw JSON dump), re-rendered after every click so the change is visible.
   Where it helps a non-developer follow, call out what just changed.
3. **Free-play buttons** — one button per action, always available, so anyone can poke at the model in any order.
   Each click dispatches its action and re-renders the state.
4. **Guided walkthroughs** — a set of **scenarios**, one per tab.
   Each tab holds a short plain-language description of the scenario — the situation it sets up and what to watch for — and underneath it, the ordered **buttons to press** for that scenario.
   Each step is a real button: clicking it performs that action and moves to the next step.
   Starting a walkthrough resets to a known initial state so the scenario runs the same way every time.

Choose scenarios that demonstrate the awkward cases — the happy path, a tricky edge case, an attempt at something that should be illegal — the ones hard to reason about on paper.

Keep it beautiful but restrained: clean typography, generous spacing, one accent colour.
No animations, no gimmicks — nothing that competes with the state and the buttons.

### 4. Hand it over

Share or open the file so the user can explore the walkthroughs and free-play actions.
Use their observations to identify mistaken assumptions and add useful actions or scenarios.

### 5. Capture the answer and the prototype

Once the prototype has answered its question, capture the answer, then capture the prototype the way the [SKILL](SKILL.md) describes.
When authorized, retain the self-contained HTML as a runnable primary source on the throwaway branch.
Adopting the reducer, state machine, or functions into real code follows the skill's separate authorization and production-verification boundary.

Apply the [shared prototype rules](SKILL.md#rules-that-apply-to-both) for persistence, tests, scope, and production adoption.
Keep the HTML shell out of production; the logic module remains evidence for an authorized, verified implementation.
