# Context efficiency

## Objective

Maintain efficient context loading and state reconstruction while preserving correct routing, continuity, evidence use, authorization, and behavior.
Lower token usage is a possible benefit, not a substitute for a correct result.

## Scope

Agent Workflow instruction loading, relevant-state reconstruction, tool-output pressure, and evidence-supported opportunities to avoid unnecessary context.
Generic performance work, prose shortening, arbitrary token targets, and speculative cleanup are excluded.
The initial authorization covered source and existing-evidence investigation and this effort's state, not framework, runtime, test, or evaluator changes or new model runs.
jimmfan later authorized the changes delivered in [PR #57](https://github.com/jimmfan/agentic-workflow/pull/57) and [PR #60](https://github.com/jimmfan/agentic-workflow/pull/60) (both 2026-09-27) and, on 2026-09-29, the agent-clarity changes on branch `claude/project-thread-mhsmmd` (`VERSION` 0.38.0).
None of these authorized rewriting the root policy's routing or authority rules or new model runs.

Resume during relevant authorized work; this map neither schedules monitoring nor makes unrelated tasks relevant.
The [language effort](../language-coherence/map.md) owns consequential wording consistency, and the [responsibility effort](../workflow-responsibility-boundaries/map.md) owns method and handoff boundaries; link shared concerns to them instead of duplicating questions here.

## Ready work

No framework optimization is ready without new evidence.
The next steps, each needing its own authorization:

- Record a repeated live baseline on one large and one small model using the [routing smoke cases](../../evals/routing-smoke/README.md), which cover each hard signal, opt-out, explicit use, and one near miss (at most two cases per run).
  jimmfan authorized this on 2026-09-27, but it could not run in that session's dev container because neither a `claude` nor a `codex` CLI was installed.
  Authorization boundaries and ambiguous unnamed-effort resumption remain outside this routing-only harness.
- Run the live multi-turn comparison planned in the [effort maintenance map](../effort-maintenance-reliability/map.md#ready-work), the main test of the context tradeoff because the cited research locates the largest degradation in multi-turn conversations.
  On 2026-09-27 jimmfan chose to include one variant that moves Wayfinder selection ahead of the authority rules in the root policy.
- Only if that baseline shows no regression, condense the root policy.
  A 2026-09-27 draft reached about 828 words from 1,144 while keeping every [ADR-0025](../../architecture-decisions/0025-preserve-authority-at-consequential-boundaries.md) authority rule and the [ADR-0027](../../architecture-decisions/0027-use-direct-first-progressive-routing.md) always-loaded signals; it was not retained, but its signal-precedence rule shipped separately in PR #60.
  The 2026-09-29 review adds wording candidates for that pass: the unqualified "commands" in the action-authorization rule, the soft signal "Durable distinctions across record or state categories", and "selection did not become equivalent execution".
- Recover a campaign's original traces, verify their recorded hashes, and inspect loading and output patterns alongside stage outcomes with the existing offline analyzer, when matching evidence is available.

## Current state

The accepted [Direct-first architecture](../../architecture-decisions/0027-use-direct-first-progressive-routing.md) remains the baseline, and jimmfan decided on 2026-09-27 to keep the full Wayfinder signal list with explicit precedence, drop the proposed workflow re-entry limit, and keep the root policy lean.

Word counts, not token, cache, or runtime measurements:

- As of 0.38.0 the Wayfinder selection path (skill, state contract, detailed routing, and terminology) is about 6,500 words before any effort file; record work adds the 1,072-word [records contract](../../.agent-workflow/contracts/effort-records.md).
- Splitting out that records contract in PR #60 removed about 1,000 words from map-only resumption; the 0.38.0 glossary entries added about 270 words to terminology, which loads only when a framework term matters.
- [Source-document tests](../../tests/test_source_documents.py) cap the distributed root policy at 1,200 words and the source-only part at 1,250 as a growth guard, not as evidence of improvement; PR #57 added these caps after moving source-only details to [maintainer procedures](../../docs/maintenance.md) and other owners.
  The distributed factual-accuracy rule stayed because Codex's `gpt_5_codex_prompt.md` on `openai/codex` `main`, fetched 2026-09-27, lacks it.
- The 2026-09-29 review found the state contract's rare-operation sections (reference search before renaming or pruning, answer interpretation, ending, scoped acceptance) total about 620 words.
  They were not split out, because the ending rules guard the delivery-ending behavior the effort-maintenance effort is fixing.
  The larger avoidable resume cost was map size: this map held 1,543 words, much of it dated history, before the same review trimmed it, so the state contract now tells authors to update maps in place and leave history to Git.

Research reviewed on 2026-09-27 bears on the trade between context load and Wayfinder selection:

- Longer input lowers reasoning accuracy well below context limits ([Levy et al., ACL 2024](https://arxiv.org/abs/2402.14848): 0.92 to 0.68 on average by 3,000 tokens).
- Accuracy falls as the number of instructions grows, and earlier instructions are followed more reliably ([Harada et al., EMNLP 2025](https://arxiv.org/abs/2509.21051); [IFScale preprint](https://arxiv.org/abs/2507.11538)).
- Multi-turn conversations lose 39% on average against single-turn, and early assumptions persist uncorrected; consolidating state into a fresh start recovers most of it ([Laban et al., 2025](https://arxiv.org/abs/2505.06120)).
- Ambiguous choices between options are a common selection failure, and on-demand loading improves selection ([Anthropic context engineering](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents); [Anthropic tool search](https://www.anthropic.com/engineering/advanced-tool-use), vendor claims).
- Prompt caching lowers cost and latency but does not change outputs, so cached instruction text still carries the quality cost ([Claude prompt caching](https://platform.claude.com/docs/en/build-with-claude/prompt-caching)).

No reviewed study measures a workflow router's trigger count against selection precision, so applying these results here is inference.

The [architecture overview](../../docs/architecture.md#instruction-runtime) maintains the intended loading sequence; it is not a measurement of host-injected instructions or actual reads.
Authority rules that stay loaded, targeted rereads before mutation, saved-result readback, required evidence reconstruction, and independent review have correctness purposes, so repetition alone is not waste.

Existing cost evidence is inconclusive.
The [persistence comparison](../../evals/wayfinder-persistence/REPORT.md#observed-cost-and-evidence-limits) found costs that differed alongside different behavioral outcomes, from one trajectory per case and condition, and does not attribute cost to particular files.
The [remaining-behavior report](../../evals/remaining-audit-behavior/REPORT.md) adds selected loading observations with incomplete coverage and failed isolation.
The older campaigns' raw traces were unavailable locally on 2026-09-17; the [2026-09-19 evidence inventory](../../evals/wayfinder-persistence/preservation-followups.md#raw-evidence-availability) identifies available raw evidence for later comparisons, which would support a separately scoped offline loading investigation.

## Areas and relationships

- **Policy and delivery:** the [root policy](../../AGENTS.md), [consumer template](../../agent_workflow/install/AGENTS.md.template), routing, and selected skills own loading obligations; source inspection alone cannot quantify host context overhead.
- **Continuity:** maps summarize the current route; supporting records and maintaining artifacts hold necessary detail under the [state contract](../../.agent-workflow/contracts/effort-state.md).
- **Measurement:** [token forensics](../../evals/token_forensics/README.md#evidence-boundaries) separates exact counters from derived and heuristic indicators; file reads inferred from commands are not operating-system observations, and output bytes are not tokens.
  [Routing smoke](../../evals/routing-smoke/README.md#what-it-measures) exposes requested-resource order, prompt bytes, and available adapter usage, not host discovery or actual skill invocation.
- **Behavior:** [progressive-loading controls](../../tests/test_wayfinder_behavior.py) reject synthetic unrelated-state use within the limits in [test ownership](../../tests/README.md); campaign limitations stay with the [remaining-behavior effort](../remaining-behavior-evidence/map.md).

## Dependencies

Any proposed comparison must distinguish total processed input, cached and uncached input, context occupancy, output and reasoning tokens, latency, and monetary cost.
Cached input and reasoning output are subsets, not extra additive charges; cumulative processed input is not simultaneous context occupancy.
Keep unavailable measurements unavailable and label heuristics and hypotheses explicitly.

A new controlled model comparison also needs a defined hypothesis.
Establish task, framework revision, model and reasoning effort, host/harness configuration, observable cache conditions, and completion quality before interpreting differences.
Judge any optimization jointly on correctness, required-context preservation, resumption quality, cost, and loading behavior; a cheaper result that loses required behavior is a regression.

## Blockers

- Live baseline and multi-turn comparison: need a host with a `claude` or `codex` CLI and model access, and authorization for the run.
- Root-policy condensing: waits on that baseline, as jimmfan decided on 2026-09-27.
- Deeper cost attribution: actual context occupancy, per-file causal cost, and stable current-framework efficiency remain unestablished, and the older campaigns' raw evidence is unavailable.
  Whether any repeated read or broad output is avoidable remains an investigation question, not a confirmed defect.

## Key references

- [Map-first state decision](../../architecture-decisions/0011-use-map-first-wayfinder-state.md).
- [Persistence compact results and trace fingerprints](../../evals/wayfinder-persistence/results/final-4-result.json).
- [Persistence frozen configuration](../../evals/wayfinder-persistence/results/final-4-freeze.json).
- [Verification and evidence limits](../../docs/verification.md).
