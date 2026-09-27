# Effort maintenance reliability

## Objective

Make agents keep Wayfinder efforts current during and after work without the user having to ask, and end or hand off efforts correctly once their work is delivered.

## Scope

Framework instructions, terminology, and ADRs that govern when effort state is maintained, who authorizes it, and how remaining work after delivery gets resumed.
Includes live validation of those instructions and the open decisions below.
Excludes consuming projects' own effort content and their policy on sensitive data in effort state (the user decided on 2026-09-27 that consumers own it, and removed the framework rule from PR #56), general routing changes unrelated to effort maintenance, and new runtime machinery unless a decision here adopts it.
On 2026-09-27 the user authorized creating this effort and the framework edits in [PR #56](https://github.com/jimmfan/agentic-workflow/pull/56); live model runs and external tracker or scheduler changes were not authorized.

## Ready work

- Review and merge [PR #56](https://github.com/jimmfan/agentic-workflow/pull/56) (user).
- Decide [U1](unknowns.md#u1--how-should-required-work-after-delivery-get-resumed) when ready; it needs user input, not more evidence.
- Live validation is required by the objective but not yet authorized.
  Plan: one synthetic conversation of about ten turns in an unrelated domain, with maintenance authorized in turn 1, then a committed choice inside a question, pasted operator output, an agent-run read-only check that contradicts the map, a correction, and small talk.
  Controls: "discuss first", "no changes", already-saved information, and a conversation with no earlier authorization; then a fresh reader session.
  Run the pre-PR #56 baseline once first and stop if it saves everything, because the scenario would not discriminate.
  Then run baseline and PR #56 twice each and grade saved meaning after every turn.
  The incident host was Codex with a GPT model; results from another host apply only partially.

## Current state

PR #56 changes the root policy, state contract, routing, terminology, several skills, and ADR-0011/0025/0027 so that authorized effort maintenance continues across turns, happens before each turn's final response when the effort changes, and ends efforts at delivery only when required work, including verification, is complete.
It also reserves "Wayfinder" for the method, names the stored files "effort state", and splits the root policy's Wayfinder section into selecting and maintaining an effort (audit findings 3 and 6 from 2026-09-27).
Its deterministic package, evaluation-tooling, and wheel checks pass; its effect on agent behavior is unverified.
The diagnosis rests on [E1](evidence/E1-guidance-conversation-transcript.md), the pattern of maps outliving their merged PRs, and earlier evaluations whose fixture policy supplied the maintenance-authorization rule the framework lacked (commit message of [4e160a0](https://github.com/jimmfan/agentic-workflow/commit/4e160a0)).

Not yet specified: whether other authorization given earlier in a conversation should carry forward the way effort maintenance now does ([U2](unknowns.md#u2--should-other-earlier-authorization-carry-forward-across-turns)), and what to do with long-running efforts whose objectives never complete ([U3](unknowns.md#u3--should-long-running-efforts-without-an-achievable-objective-remain-efforts)).

## Areas and relationships

- The [root policy template](../../agent_workflow/install/AGENTS.md.template) carries the always-loaded continuity, authorization, and per-turn rules; the [state contract](../../.agent-workflow/contracts/wayfinder-state.md) carries the procedure and ending rules; [terminology](../../.agent-workflow/terminology.md) defines effort maintenance, read-only request, and current user request.
- The [language-coherence effort](../language-coherence/map.md) owns general terminology questions; this effort owns only terms that decide when effort state is maintained.
- The user decides U1–U3 and authorizes live runs, trackers, or schedulers.

## Dependencies

- Live validation needs authorization, a model host, and quota.
- Adopting a trigger mechanism under U1 needs U1's decision.

## Blockers

- Live validation: not authorized.
- Trigger mechanism: U1 unresolved.
- Nothing currently blocks review of PR #56.

## Key references

- [PR #56](https://github.com/jimmfan/agentic-workflow/pull/56)
- [Open decisions](unknowns.md)
- [Incident evidence](evidence/E1-guidance-conversation-transcript.md)
- [Earlier preservation evaluations](../../evals/wayfinder-persistence/preservation-followups.md)
