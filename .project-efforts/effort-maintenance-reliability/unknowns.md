## U2 — Should other earlier authorization carry forward across turns?

Why it matters: [ADR-0025](../../architecture-decisions/0025-preserve-authority-at-consequential-boundaries.md) now carries earlier authorization forward only for effort maintenance, and "current user request" remains undefined for other writes, such as a commit authorized in an earlier turn.
Resolution: user decision; broadening affects authorization boundaries, which the project treats as a pre-1.0 priority.
On 2026-10-14 jimmfan deferred it because no incident shows a need; revisit if an agent re-asks for an action the user already authorized earlier in the same conversation.

## U5 — Does host context compaction count as a continuation boundary?

Why it matters: hosts such as Codex and Claude Code replace older turns with a summary near the context limit, and the Wayfinder hard signal names only continuation across sessions or agents.
The root policy ranks live source and accepted artifacts above summaries, but no evidence shows agents rereading the map or repository after compaction instead of trusting the summary.
Superpowers reports controllers re-running completed tasks after compaction as its most expensive observed failure ([subagent-driven-development](https://github.com/obra/superpowers/blob/main/skills/subagent-driven-development/SKILL.md), 2026-09-30); no incident here involves compaction.

Options:

1. Treat compaction as a session boundary for the hard signal; long sessions would select Wayfinder more often.
2. Keep the current rule and verify that agents apply it after compaction.
3. Add a record that supports resumption after compaction; this requires reconsidering [ADR-0028](../../architecture-decisions/0028-use-wayfinder-as-sole-durable-coordinator.md) with evidence.

Resolution: on 2026-10-14 jimmfan chose to add a compaction arm to the planned multi-turn test and to keep option 2 unless that arm shows agents trusting the summary over the map or repository.
