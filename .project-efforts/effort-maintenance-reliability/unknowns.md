## U2 — Should other earlier authorization carry forward across turns?

Why it matters: [ADR-0025](../../architecture-decisions/0025-preserve-authority-at-consequential-boundaries.md) now carries earlier authorization forward only for effort maintenance, and "current user request" remains undefined for other writes, such as a commit authorized in an earlier turn.
Resolution: user decision; broadening affects authorization boundaries, which the project treats as a pre-1.0 priority.

## U3 — Should long-running efforts without an achievable objective remain efforts?

Why it matters: the [language-coherence](../language-coherence/map.md), [workflow-responsibility-boundaries](../workflow-responsibility-boundaries/map.md), and [context-efficiency](../context-efficiency/map.md) objectives describe ongoing upkeep, so the ending rule never applies and their maps go stale unless someone asks.
Options: keep them with explicit resume conditions, or move their open questions and findings into their owning documents and end them.
Resolution: user decision.

## U4 — Should selecting Wayfinder authorize effort maintenance by default?

Why it matters: under the root policy, when routing selects an effort in a conversation that authorizes no repository changes, such as diagnosis, discussion, or strategy, the agent reports what needs preserving and waits, so jimmfan must still act (incidents 5 and 6 in [E2](evidence/E2-historical-incident-summary.md)).
A default that authorizes effort maintenance on selection unless the user asks for no changes or to discuss first would remove that step but widen an authorization boundary that [ADR-0025](../../architecture-decisions/0025-preserve-authority-at-consequential-boundaries.md) governs; it is related to but narrower than [U2](#u2--should-other-earlier-authorization-carry-forward-across-turns).
Resolution: user decision.

## U5 — Does host context compaction count as a continuation boundary?

Why it matters: hosts such as Codex and Claude Code replace older turns with a summary near the context limit, and the Wayfinder hard signal names only continuation across sessions or agents.
The root policy ranks live source and accepted artifacts above summaries, but no evidence shows agents rereading the map or repository after compaction instead of trusting the summary.
Superpowers reports controllers re-running completed tasks after compaction as its most expensive observed failure ([subagent-driven-development](https://github.com/obra/superpowers/blob/main/skills/subagent-driven-development/SKILL.md), 2026-09-30); no incident here involves compaction.

Options:

1. Treat compaction as a session boundary for the hard signal; long sessions would select Wayfinder more often.
2. Keep the current rule and verify that agents apply it after compaction.
3. Add a record that supports resumption after compaction; this requires reconsidering [ADR-0028](../../architecture-decisions/0028-use-wayfinder-as-sole-durable-coordinator.md) with evidence.

Resolution: live evidence from a compaction arm in the planned multi-turn test, then user decision.
