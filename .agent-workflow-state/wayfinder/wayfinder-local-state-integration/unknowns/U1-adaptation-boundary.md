# U1: How should the pinned Wayfinder method be adapted to local state?

- Status: resolved
- Resolution mode: direct
- Blocked by: none
- Related: D1, D2, T1

## Question

What is the smallest mechanism that makes the full Wayfinder instruction set seen by a fresh Codex agent coherent without forking the upstream method or silently rewriting unknown provider content?

## Historical evidence for D1

- Before ADR-0022, the installed root and routing contracts made `.agent-workflow-state/wayfinder/<effort>/` canonical and defined U# as uncertainty, D# as durable decision, and T# as executable work. ADR-0022 later retired Wayfinder T# work items in favor of native `to-tickets` artifacts.
- Before ADR-0023, the projected pinned `wayfinder/SKILL.md` made tracker issues canonical, treated its tickets as decision questions, required tracker setup, and mandated tracker assignment/comment/close mechanics below the local override.
- At D1, the lifecycle overlay changed activation metadata and prepended local rules while leaving that conflicting upstream body below them.
- Current official Codex documentation says activation begins from skill metadata, but selection loads the full `SKILL.md`; it also says same-named skills are not merged.

## Resolution

Use [D2 — Own the runtime projection and stable effort boundary](../decisions/D2-own-runtime-projection.md). Validate the pinned upstream body before replacing it with the concise Agentic Workflow-owned runtime projection, and preserve unknown or modified bodies without writing. The projection retains the useful Wayfinder reasoning pattern while removing the contradictory tracker workflow and defining stable effort selection. [D1](../decisions/D1-fingerprinted-local-mode-overlay.md) is preserved as the superseded first resolution.
