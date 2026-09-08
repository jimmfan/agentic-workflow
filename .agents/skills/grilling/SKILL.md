---
description: Grill the user through interdependent choices requiring human input or project decision authority that materially shape downstream work. Also use when the user explicitly asks to be grilled or stress-test a plan, decision, or idea.
name: grilling
---
Work through relevant unresolved choices that require human input or project decision authority until you reach a shared understanding.
When the user explicitly requests thorough grilling, examine the relevant assumptions, alternatives, and consequences in depth.
Reuse settled choices, choices determined by accepted project policy, and technical judgment already delegated to the agent.
Map the remaining choices as a **design tree**: each decision branches into the decisions that depend on it.

Work the tree in **rounds**.
The **frontier** is the relevant unresolved human-owned decisions whose prerequisites are already settled — the questions you can ask _now_ without guessing at answers you haven't heard yet.
Ask the whole frontier in one round: number each question and give your recommended answer.
Then wait for the user's answers before the next round.

Each question should be formatted like so:

```
❓ **Q1** - **<question title>**: <question body, might be multiple paragraphs, including multiple choices>

➡️ <your recommended answer>
```

Each round the user answers reshapes the tree — settled decisions push the frontier outward and unblock questions that depended on them.
Recompute the frontier and ask the next round.
A question whose answer depends on another question still open in this round belongs to a _later_ round, not this one.

Look up accessible facts before asking the user for information available from the environment or sources.
Look up facts directly when that satisfies the evidence need; delegate when available and useful for independent exploration.
A running exploration is an unsettled prerequisite, so only downstream questions wait for its result — ask the rest of the frontier now.
Put choices requiring human input or project decision authority to the appropriate person and wait for those answers.

Finish when the relevant design tree is resolved to the agreed scope, with no required choice silently assumed.
State the shared understanding and any explicitly deferred question with its affected boundary; obtain confirmation where material understanding or a required choice remains unsettled.
Applying those choices still requires action authorization from the request or accepted project policy.
