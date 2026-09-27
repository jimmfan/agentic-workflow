# E1 — Guidance conversation where effort state fell behind

Source: a user-supplied, user-facing export of a Codex conversation (reported model: a GPT model at extra-high reasoning), 2026-09-20 to 2026-09-27, shared with Claude on 2026-09-27.
The export is not retained in this repository; tool calls, reasoning, and injected context were excluded from it.

Scope: one consuming project guiding an infrastructure setup through user-supplied checkpoints, with an existing effort that the user had asked the agent to establish and reconcile.

## Observation

- The agent wrote effort state only in turns that contained or directly followed an explicit write instruction or an implementation step.
- In question- or guidance-shaped turns it did not write, even when the turn carried a committed user choice, a user-supplied checkpoint, or its own live read-only check that contradicted the map; one such turn was framed "This will be read-only."
- It deferred recording committed choices because an unrelated naming proposal still needed implementation.
- When it finally wrote, after the user asked, it recorded a setting it had itself verified earlier as only operator-reported and pending verification.
- Route markers reported `wayfinder` in turns where the map was only read for context.
- When challenged, it attributed the omission to treating the exchange as guidance-only and over-applying read-only rules; that explanation is after the fact.

Limitations: one conversation; no tool traces or reasoning; the installed framework version in that project is unknown.
Credentials, account identifiers, and personal identifiers from the export are intentionally omitted.
The pattern supports, but does not prove, the authorization-scope diagnosis addressed by [PR #56](https://github.com/jimmfan/agentic-workflow/pull/56).
