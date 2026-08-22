# Design It Twice

When the user wants to explore alternative interfaces for a chosen deepening candidate, use this pattern only when the interface choice is consequential, genuinely open, and likely to benefit from independent comparison. Based on "Design It Twice" (Ousterhout) — your first idea is unlikely to be the best.

Uses the vocabulary in [SKILL.md](SKILL.md) — **module**, **interface**, **seam**, **adapter**, **leverage**.

For an obvious pass-through consolidation, routine implementation detail, or
already settled interface, make one direct recommendation and state the main
rejected alternative. Respect user and host authorization for sub-agents. Do
not expand work merely because alternatives can be imagined.

## Process

### 1. Frame the problem space

Before spawning sub-agents, write a user-facing explanation of the problem space for the chosen candidate:

- The constraints any new interface would need to satisfy
- The dependencies it would rely on, and which category they fall into (see [DEEPENING.md](DEEPENING.md))
- Established project/domain terminology and authority-owned boundaries
- A rough illustrative code sketch to ground the constraints — not a proposal, just a way to make the constraints concrete

Show this to the user. If feedback or authority can materially change the boundary, wait for that answer; otherwise proceed to Step 2.

### 2. Spawn sub-agents when justified and authorized

Use the smallest useful number of fresh designs, normally 2–3. Each must produce a **meaningfully different, plausible** interface for the deepened module.

Prompt each sub-agent with a separate technical brief (file paths, coupling details, dependency category from [DEEPENING.md](DEEPENING.md), what sits behind the seam). The brief is independent of the user-facing problem-space explanation in Step 1. Give each agent a different design constraint:

- Agent 1: "Minimize the interface — aim for 1–3 entry points max. Maximise leverage per entry point."
- Agent 2: "Maximise flexibility — support many use cases and extension."
- Agent 3: "Optimise for the most common caller — make the default case trivial."
- Agent 4 (if applicable): "Design around ports & adapters for cross-seam dependencies."

Include both [SKILL.md](SKILL.md) vocabulary and CONTEXT.md vocabulary in the brief so each sub-agent can relate the analysis language to the project's canonical domain language without renaming it.

Each sub-agent outputs:

1. Interface (types, methods, params — plus invariants, ordering, error modes)
2. Usage example showing how callers use it
3. What the implementation hides behind the seam
4. Dependency strategy and adapters (see [DEEPENING.md](DEEPENING.md))
5. Trade-offs — where leverage is high, where it's thin

### 3. Present and compare

Present designs sequentially so the user can absorb each one, then compare them in prose. Contrast by **depth** (leverage at the interface), **locality** (where change concentrates), **seam placement**, project language, ownership, test evidence, migration cost, and scope.

After comparing, give your own recommendation: which design you think is strongest and why. If elements from different designs would combine well, propose a hybrid. Be opinionated — the user wants a strong read, not a menu. Recommend no change when the current interface is strongest.
