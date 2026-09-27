# E2 — Historical routing and effort-maintenance incidents, August–September 2026

Source: a summary jimmfan pasted into a Claude Code conversation on 2026-09-27, prepared by an agent in another environment from jimmfan's photos and recollection of agent conversations between 2026-08-17 and 2026-09-26.
The photos, conversations, and traces are not retained in this repository.

Scope: nine incidents across consuming projects and hosts; workplace-specific details were omitted by the summary and are not reconstructed here.

## Observation

1. 2026-09-24: the agent took a Direct route on a concrete code change although the requested outcome needed later coordinated work and acceptance evidence, and only assessed Wayfinder after a reminder; it blamed confusing a clear bounded plan with work needing durable coordination.
2. 2026-09-14, route `router → Wayfinder → workflow-debugging` on a job-failure diagnosis and fix: evidence was saved to the effort only after jimmfan asked twice; the agent said "independently useful evidence" was left as a judgment call.
3. 2026-09-20 to 2026-09-27: guidance turns left an existing effort stale; see [E1](E1-guidance-conversation-transcript.md).
4. 2026-09-19: the Wayfinder skill was not exposed natively because it existed only under `.agents/skills/`, and the agent also read terminology only after writing effort state and placed completed work under Ready work.
5. 2026-08-19: under a then-current rule that read-only requests never write Wayfinder state, the agent treated "discovery and strategy task … do not modify production code or configuration" as excluding Wayfinder despite recognizing coordination signals.
6. 2026-09-02: after diagnostic evidence and next-step options, the agent ended with `[route: router → direct]`, and jimmfan had to ask it to start an effort.
7. 2026-09-23: the opposite failure; jimmfan's saved guidance told agents to skip F# records for self-contained wording fixes and D# records for routine edits.
8. 2026-08-17 to 2026-08-19: the route marker was not shown by default, and an agent described it as "a label, not a behavior change".
9. 2026-09-26: jimmfan suspected that short evaluation prompts miss failures that appear only in long, possibly overloaded conversations.

Limitations: the photos were partial views, and quotes were visually transcribed; agent explanations are retrospective claims, not established causes.
Installed framework versions, exposed skills, models, and tool traces are unknown for every incident.
The summary was supplied as starting evidence, not an exhaustive list.
