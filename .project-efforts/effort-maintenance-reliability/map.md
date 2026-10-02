# Effort maintenance reliability

## Objective

Make agents keep Wayfinder efforts current during and after work without the user having to ask, and end or hand off efforts correctly once their work is delivered.

## Scope

Framework instructions, terminology, and ADRs that govern when effort state is maintained, who authorizes it, and how remaining work after delivery gets resumed.
Includes live validation of those instructions and the open decisions below.
Excludes consuming projects' own effort content and their policy on sensitive data in effort state (the user decided on 2026-09-27 that consumers own it, and removed the framework rule from PR #56), general routing changes unrelated to effort maintenance, and new runtime machinery unless a decision here adopts it.
On 2026-09-27 the user authorized creating this effort and the framework edits in [PR #56](https://github.com/jimmfan/agentic-workflow/pull/56); live model runs and external tracker or scheduler changes were not authorized.
Later on 2026-09-27 the user authorized applying the PR #56 audit recommendations and completing the terminology rename in the same PR.
On 2026-09-30 jimmfan chose how required work after delivery gets resumed (see Current state) and authorized delivering that rule on a branch with the 0.39.0 findings-loop changes; live model runs remain unauthorized.

## Ready work

- [PR #56](https://github.com/jimmfan/agentic-workflow/pull/56) merged on 2026-09-27 as `d82771e`; the items below remain.
- Decide [U4](unknowns.md#u4--should-selecting-wayfinder-authorize-effort-maintenance-by-default) when ready; it needs user input, not more evidence.
- After the 0.40.0 route-conflict fixes merge, restructure the standing efforts to jimmfan's U3 decision (see Current state) on a separate branch: move their lasting decisions into ADRs, slim their maps, separate their lanes, and keep the multi-turn live test owned only by this effort.
- Live validation is required by the objective but running it is not yet authorized.
  On 2026-09-27 jimmfan chose to treat it as the main test of routing reliability and to include one variant that moves Wayfinder selection ahead of the authority rules in the root policy ([context-efficiency map](../context-efficiency/map.md#ready-work)).
  Plan: one synthetic conversation of about ten turns in an unrelated domain, with maintenance authorized in turn 1, then a committed choice inside a question, pasted operator output, an agent-run read-only check that contradicts the map, a correction, and small talk.
  Controls: "discuss first", "no changes", already-saved information, a conversation with no earlier authorization, and one where routing selects the effort during authorized implementation; then a fresh reader session.
  Fix a small, matched number of baseline (pre-PR #56) and candidate runs before the first run, and grade saved meaning after every turn; one baseline success cannot show that the scenario fails to discriminate an intermittent failure.
  A roughly ten-turn conversation tests continuation across turns, not long accumulated context or compaction like the week-long E1 conversation; [U5](unknowns.md#u5--does-host-context-compaction-count-as-a-continuation-boundary) asks whether compaction needs its own arm.
  Include a delivery that leaves required work, to check the delivery-ending rule below.
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
Since 0.38.0 the [state contract](../../.agent-workflow/contracts/effort-state.md#map-authoring) tells authors to replace superseded map statements in place and leave history to Git, because dated narration had grown three maps to between 1,091 and 1,543 words.
The Claude Code exposure map also outlived its delivery: it described PR #59's merged change as uncommitted until jimmfan had that effort ended on 2026-10-01.
Since 0.39.0 the [state contract](../../.agent-workflow/contracts/effort-state.md#keep-or-end-the-effort) has a delivery that keeps an effort open state its remaining work and exact resume prompt in the final response and pull request description, so the person merging sees it; like the other instruction-only fixes, its effect is unverified live.
On 2026-10-01 jimmfan dropped the agent-offered tracker issue or reminder because nothing in a session triggers it; if maps keep outliving their deliveries, a separate host or GitHub job triggered by the merge is the candidate, not more agent instructions.

On 2026-10-01 jimmfan decided that the standing [language-coherence](../language-coherence/map.md), [workflow-responsibility-boundaries](../workflow-responsibility-boundaries/map.md), and [context-efficiency](../context-efficiency/map.md) efforts stay open, because models keep changing and the project must remember what it decided and what it tunes toward.
Lasting decisions belong in ADRs whose reconsideration triggers name the check to rerun after a model or host change.
Each standing map keeps only its open questions, tuning targets, links to per-model results, and a resume condition for model or host changes, in a lane distinct from the other efforts.
Nothing in a session detects a model change, so jimmfan starts that resumption.

Not yet specified: whether other authorization given earlier in a conversation should carry forward the way effort maintenance now does ([U2](unknowns.md#u2--should-other-earlier-authorization-carry-forward-across-turns)).

## Areas and relationships

- The [root policy template](../../agent_workflow/install/AGENTS.md.template) carries the always-loaded continuity, authorization, and per-turn rules; the [state contract](../../.agent-workflow/contracts/effort-state.md) carries the procedure and ending rules; [terminology](../../.agent-workflow/terminology.md) defines effort maintenance and read-only request.
- The [language-coherence effort](../language-coherence/map.md) owns general terminology questions; this effort owns only terms that decide when effort state is maintained.
- The user decides U2, U4, and U5 and authorizes live runs, trackers, or schedulers.

## Dependencies

- Live validation needs authorization, a model host, and quota.

## Blockers

- Live validation: not authorized.
- Saving without a separate go-ahead in conversations that authorize no repository changes: U4 unresolved.

## Key references

- [PR #56](https://github.com/jimmfan/agentic-workflow/pull/56)
- [Open decisions](unknowns.md)
- [Guidance conversation evidence](evidence/E1-guidance-conversation-transcript.md)
- [Historical incident summary](evidence/E2-historical-incident-summary.md)
- [Earlier preservation evaluations](../../evals/wayfinder-persistence/preservation-followups.md)
