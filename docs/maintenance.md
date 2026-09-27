# Maintainer procedures

These source-repository procedures load on demand from the [root instructions](../AGENTS.md#agent-workflow-source-repository).
Like the rest of the source-repository instructions, they must stay outside distributed consumer instructions.

## Changing canonical terminology

Before introducing, renaming, or materially redefining a canonical term:

- Determine the actual concept from current source, behavior, tests, and accepted decisions.
- Identify the bounded technical or domain context that owns it.
- Research established terminology using applicable primary standards, official technical documentation, strong engineering evidence, and peer-reviewed evidence when available.
- Compare alternatives by exact semantics and applicability.
- Prefer established or literal language only when its semantic precision earns its cognitive cost.
- State evidence strength and uncertainty honestly.

Update [`.agent-workflow/terminology.md`](../.agent-workflow/terminology.md) only after the terminology decision is accepted.
Keep behavior, architecture, authority, and terminology in their respective owning layers.
Do not force one term across genuinely different bounded contexts.

## Checkout state

Before changing branch, HEAD, or worktree checkout state:

- Record the starting state.
- If the task uses a separate worktree, identify its absolute path and branch clearly; switch the primary checkout only when safe.
- If a requested checkout change is unsafe, leave the work in place and report the blocker.

When finished, restore the original checkout only when the user explicitly requests it.
The [root checkout rules](../AGENTS.md#checkout-state) for inspection, work preservation, the final branch, and the handoff report still apply.
