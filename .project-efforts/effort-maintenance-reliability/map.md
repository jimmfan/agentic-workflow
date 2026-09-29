# Effort maintenance reliability

## Objective

Make agents keep Wayfinder efforts current during and after work without the user having to ask, and end or hand off efforts correctly once their work is delivered.

## Scope

Framework instructions, terminology, and ADRs that govern when effort state is maintained, who authorizes it, and how remaining work after delivery gets resumed.
Includes live validation of those instructions and the open decisions below.
Excludes consuming projects' own effort content and their policy on sensitive data in effort state (the user decided on 2026-09-27 that consumers own it, and removed the framework rule from PR #56), general routing changes unrelated to effort maintenance, and new runtime machinery unless a decision here adopts it.
On 2026-09-27 the user authorized creating this effort and the framework edits in [PR #56](https://github.com/jimmfan/agentic-workflow/pull/56); live model runs and external tracker or scheduler changes were not authorized.
Later on 2026-09-27 the user authorized applying the PR #56 audit recommendations and completing the terminology rename in the same PR.

## Ready work

- [PR #56](https://github.com/jimmfan/agentic-workflow/pull/56) merged on 2026-09-27 as `d82771e`; the items below remain.
- Decide [U1](unknowns.md#u1--how-should-required-work-after-delivery-get-resumed) and [U4](unknowns.md#u4--should-selecting-wayfinder-authorize-effort-maintenance-by-default) when ready; both need user input, not more evidence.
- Live validation is required by the objective but running it is not yet authorized.
  On 2026-09-27 jimmfan chose to treat it as the main test of routing reliability and to include one variant that moves Wayfinder selection ahead of the authority rules in the root policy ([context-efficiency map](../context-efficiency/map.md#ready-work)).
  Plan: one synthetic conversation of about ten turns in an unrelated domain, with maintenance authorized in turn 1, then a committed choice inside a question, pasted operator output, an agent-run read-only check that contradicts the map, a correction, and small talk.
  Controls: "discuss first", "no changes", already-saved information, a conversation with no earlier authorization, and one where routing selects the effort during authorized implementation; then a fresh reader session.
  Fix a small, matched number of baseline (pre-PR #56) and candidate runs before the first run, and grade saved meaning after every turn; one baseline success cannot show that the scenario fails to discriminate an intermittent failure.
  A roughly ten-turn conversation tests continuation across turns, not long accumulated context or compaction like the week-long E1 conversation.
  The incident host was Codex with a GPT model; results from another host apply only partially.

## Current state

PR #56 (merged 2026-09-27) changes the root policy, state contract, routing, terminology, several skills, and ADR-0011/0025/0027 so that authorized effort maintenance continues across turns, happens before each turn's final response when the effort changes, and ends efforts at delivery only when required work, including verification, is complete.
It also reserves "Wayfinder" for the method, names the stored files "effort state", and splits the root policy's Wayfinder section into selecting and maintaining an effort (audit findings 3 and 6 from 2026-09-27).
After the second audit on 2026-09-27, PR #56 also renames the state contract to `effort-state.md` and the ADR-0011 title, drops the glossary entry that defined "current user request" as the latest request, and drops the root-policy rule that searched `.project-efforts/` after every path rename.
On 2026-09-27 the user decided that when routing selects an effort without an explicit effort request, authorization for repository changes toward its objective also authorizes its effort maintenance; PR #56 records this in the root policy and ADR-0025.
Its deterministic package, evaluation-tooling, and wheel checks pass; its effect on agent behavior is unverified.
The diagnosis rests on [E1](evidence/E1-guidance-conversation-transcript.md), the pattern of maps outliving their merged PRs, and earlier evaluations whose fixture policy supplied the maintenance-authorization rule the framework lacked (commit message of [4e160a0](https://github.com/jimmfan/agentic-workflow/commit/4e160a0)).

A 2026-09-27 review of nine historical incidents ([E2](evidence/E2-historical-incident-summary.md)) against the source found most failures addressed only in instruction text, each fix added on or just after its incident and none checked live since.
Only the native skill exposure failure is verified fixed, for Claude Code on this source checkout: that session loaded Wayfinder from the `.claude/skills/` link.
Most incidents are missed coordination rather than excess persistence.
When a conversation authorizes no repository changes, current rules still have the agent propose rather than save ([U4](unknowns.md#u4--should-selecting-wayfinder-authorize-effort-maintenance-by-default)).
The resulting routing changes shipped in [PR #60](https://github.com/jimmfan/agentic-workflow/pull/60) (0.37.0) and are described in the [responsibility map](../workflow-responsibility-boundaries/map.md#current-state).
On 2026-09-29 jimmfan authorized a [state contract](../../.agent-workflow/contracts/effort-state.md#map-authoring) rule, on branch `claude/project-thread-mhsmmd` (0.38.0), to update maps in place and leave history to Git, after a review found three maps of 1,000 to 1,500 words with much of their length in dated narration.
The same review found the [Claude Code exposure map](../claude-code-source-exposure/map.md) still describing PR #59's delivered change as uncommitted, another map that outlived its delivery ([U1](unknowns.md#u1--how-should-required-work-after-delivery-get-resumed)).

Not yet specified: whether other authorization given earlier in a conversation should carry forward the way effort maintenance now does ([U2](unknowns.md#u2--should-other-earlier-authorization-carry-forward-across-turns)), and what to do with long-running efforts whose objectives never complete ([U3](unknowns.md#u3--should-long-running-efforts-without-an-achievable-objective-remain-efforts)).

## Areas and relationships

- The [root policy template](../../agent_workflow/install/AGENTS.md.template) carries the always-loaded continuity, authorization, and per-turn rules; the [state contract](../../.agent-workflow/contracts/effort-state.md) carries the procedure and ending rules; [terminology](../../.agent-workflow/terminology.md) defines effort maintenance and read-only request.
- The [language-coherence effort](../language-coherence/map.md) owns general terminology questions; this effort owns only terms that decide when effort state is maintained.
- The user decides U1–U4 and authorizes live runs, trackers, or schedulers.

## Dependencies

- Live validation needs authorization, a model host, and quota.
- Adopting a trigger mechanism under U1 needs U1's decision.

## Blockers

- Live validation: not authorized.
- Trigger mechanism: U1 unresolved.
- Saving without a separate go-ahead in conversations that authorize no repository changes: U4 unresolved.

## Key references

- [PR #56](https://github.com/jimmfan/agentic-workflow/pull/56)
- [Open decisions](unknowns.md)
- [Guidance conversation evidence](evidence/E1-guidance-conversation-transcript.md)
- [Historical incident summary](evidence/E2-historical-incident-summary.md)
- [Earlier preservation evaluations](../../evals/wayfinder-persistence/preservation-followups.md)
