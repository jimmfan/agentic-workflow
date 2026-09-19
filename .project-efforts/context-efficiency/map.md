# Context efficiency

## Objective

Maintain efficient context loading and state reconstruction while preserving correct routing, continuity, evidence use, authorization, and behavior.
Lower token usage is a possible benefit, not a substitute for a correct result.

## Scope

Agent Workflow instruction loading, relevant-state reconstruction, tool-output pressure, and evidence-supported opportunities to avoid unnecessary context.
The initial authorization covers source and existing-evidence investigation and this effort's coordination state; it excludes framework, runtime, test, and evaluator changes and new model runs.
Generic performance work, prose shortening, arbitrary token targets, and speculative cleanup are excluded.

Resume during relevant authorized work; this map neither schedules monitoring nor makes unrelated tasks relevant.
The [language effort](../language-coherence/map.md) owns consequential wording consistency, and the [responsibility effort](../workflow-responsibility-boundaries/map.md) owns method and handoff boundaries.
Link shared concerns to their existing owner instead of duplicating questions here.

## Ready work

The initial source and evidence audit is complete; no supported framework optimization is ready for implementation.
The next proposed investigation is to recover a campaign's original traces, verify their recorded hashes, and inspect loading and output patterns alongside stage outcomes using the existing offline analyzer.
That follow-up needs available matching evidence and authorization for its scope; a new controlled model comparison would require separate authorization and a defined hypothesis.

## Current state

The accepted [Direct-first architecture](../../architecture-decisions/0027-use-direct-first-progressive-routing.md) remains the baseline.
No actionable efficiency defect was established in the inspected sources and existing reports; this does not demonstrate that current behavior is efficient.

The intended loading sequence is:

- **Entry:** root policy and exposed skill descriptions support initial selection from intent, with the smallest delegated read-only reconnaissance when evidence is insufficient.
- **Composition:** [detailed routing](../../.agent-workflow/routing.md) loads when composition, availability, artifact ownership, handoff, or resumption guidance materially matters; selected skill instructions load when needed.
- **Coordination:** [Wayfinder](../../.agents/skills/wayfinder/SKILL.md) loads its [state contract](../../.agent-workflow/contracts/wayfinder-state.md), resumes from the matching map, and follows only relevant supporting state and maintaining artifacts.
  An unrelated effort or a skill's availability does not justify loading it.

These are intended boundaries, not a measurement of host-injected instructions or actual reads in every session.
Always-available authority rules, targeted rereads before mutation, saved-result readback, required evidence reconstruction, and independent review have correctness purposes.
A repeated read can also be necessary after mutation or context loss; repetition alone is not waste.

The [persistence comparison](../../evals/wayfinder-persistence/REPORT.md#observed-cost-and-evidence-limits) records historical input/cache/output counters, elapsed time, and tool-request observations across three conditions.
Costs differed, but behavioral outcomes also differed, including an incomplete coding task in the condition with lower input usage.
One trajectory per case and condition, fixed execution order, cache effects, and service latency prevent treating those totals as a stable current efficiency improvement or regression.
The report's overall comparative conclusion is inconclusive; it does not attribute costs to particular files.

The [remaining-behavior report](../../evals/remaining-audit-behavior/REPORT.md) provides additional selected loading observations and usage, with incomplete coverage and failed intended isolation.
Its observations do not establish a fully isolated behavioral pass or a causal framework cost defect.
On 2026-09-17, all seven subject raw trace paths recorded in its [results](../../evals/remaining-audit-behavior/results.json) were unavailable locally, as was `/tmp/persistence-quality-final-4`, the persistence report's recorded run root.
Compact results remain usable within their stated limits; fresh trace analysis cannot currently reproduce loading sequences from those locations.
This availability check does not establish that no copies exist elsewhere.
The 2026-09-19 [follow-up evidence inventory](../../evals/wayfinder-persistence/preservation-followups.md#raw-evidence-availability) confirms those older run roots remain absent and identifies available raw evidence for distinct later comparisons, with verified retained hashes where inventories exist.
That evidence makes a bounded offline loading investigation possible when separately scoped; it does not reconstruct the missing older traces or establish a current efficiency defect.

## Areas and relationships

- **Policy and delivery:** [root policy](../../AGENTS.md), [consumer template](../../agent_workflow/install/AGENTS.md.template), routing, and selected skills own loading obligations; [architecture](../../docs/architecture.md#instruction-runtime) explains their interaction.
  Source inspection alone cannot quantify host context overhead.
- **Continuity:** maps summarize the current route; supporting records and accepted artifacts preserve necessary detail under the state contract.
  The [persistence report](../../evals/wayfinder-persistence/REPORT.md) retains the completed reconciliation campaign; this effort interprets cost evidence without reopening its scope.
- **Measurement:** [token forensics](../../evals/token_forensics/README.md#evidence-boundaries) distinguishes exact counters and trace-embedded events, derived uncached input and repeated commands, and heuristic file-read/search/context-pressure indicators.
  File reads inferred from commands are not operating-system access observations; output bytes are not tokens, and later input cannot be assigned exactly to a particular tool result.
- **Behavior:** [progressive-loading controls](../../tests/test_wayfinder_behavior.py) reject synthetic unrelated-state use; [test ownership](../../tests/README.md) explains their limits.
  [Routing smoke](../../evals/routing-smoke/README.md#what-it-measures) exposes requested-resource order, prompt bytes, and available adapter usage, not host discovery or actual skill invocation.
  Existing campaign limitations remain with their [maintaining effort](../remaining-behavior-evidence/map.md).

## Dependencies

Any proposed comparison must distinguish total processed input, cached and uncached input, context occupancy, output and reasoning tokens, latency, and monetary cost.
Cached input and reasoning output are subsets, not extra additive charges; cumulative processed input is not simultaneous context occupancy.
Keep unavailable measurements unavailable and label heuristics and hypotheses explicitly.

Establish task, framework revision, model and reasoning effort, host/harness configuration, observable cache conditions, and completion quality before interpreting differences.
Judge any optimization jointly on correctness, required-context preservation, resumption quality, cost, and loading behavior.
A cheaper result that loses required behavior is a regression.

## Blockers

No unresolved dependency prevents completion of this initial audit.
The older campaigns' recorded raw evidence is unavailable for deeper offline attribution; later comparison evidence is locally available as linked above.
Current reports leave actual context occupancy, per-file causal cost, and stable current-framework efficiency unestablished.
Whether any repeated read or broad output is avoidable remains an investigation question, not a confirmed defect.

## Key references

- [Map-first state decision](../../architecture-decisions/0011-use-map-first-wayfinder-state.md).
- [Persistence compact results and trace fingerprints](../../evals/wayfinder-persistence/results/final-4-result.json).
- [Persistence frozen configuration](../../evals/wayfinder-persistence/results/final-4-freeze.json).
- [Verification and evidence limits](../../docs/verification.md).
