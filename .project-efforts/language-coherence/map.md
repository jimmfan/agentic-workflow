# Language coherence

## Objective

Keep consequential terminology and instruction-language questions understandable and resumable as Agent Workflow evolves, preserving the distinction between inconsistent meaning and useful contextual repetition.

## Scope

Framework term meanings, normative wording, and authored-to-consumer language consistency where differences could change behavior or create competing maintenance obligations.
The initial task authorized a bounded source audit and effort state; framework, glossary, documentation, test, and evaluator corrections and live evaluations were outside it.
jimmfan later authorized the instruction-meaning corrections merged in [PR #54](https://github.com/jimmfan/agentic-workflow/pull/54) on 2026-09-20 and, on 2026-09-29, the glossary additions on branch `claude/project-thread-mhsmmd` (0.38.0).
Architecture, runtime behavior, interfaces, data formats, ownership, evaluation design, and live evaluations remain outside this effort.

The completed domain-language normalization is maintained in canonical terminology, the state contract, and the [map-authoring report](../../evals/map-authoring/REPORT.md); it merged through PRs #13, #14, and #31.
This standing effort retains future consequential language questions without reopening those accepted choices or turning an optional live smoke into required implementation work.
The map-authoring live acceptance gap remains unaccepted and unresolved in its report.
The [responsibility-boundary effort](../workflow-responsibility-boundaries/map.md) addresses who owns responsibilities and handoffs; this effort addresses whether language consistently expresses intended meanings and obligations.
Keep one detailed owner for each question and link shared concerns rather than duplicating them.

Resume only during relevant authorized work that materially changes a represented meaning, instruction, or evidence claim.
This map is not self-updating, a second glossary, a normative instruction source, or a requirement to audit unrelated work.
Style-only rewrites, ordinary repetition, generic code deduplication, and speculative cleanup are excluded.

## Ready work

No language correction or live evaluation is ready.
Replacing the root policy's long authority phrases with the new glossary terms waits on the live baseline that gates root-policy condensing in the [context-efficiency effort](../context-efficiency/map.md#ready-work).

## Current state

**Glossary additions (2026-09-29).**
The earlier audit found no consequential terminology defect in the surfaces it inspected, but the 2026-09-29 review found that several of the most-used framework terms had no definitions.
The root policy and contracts rely on Direct, action authorization, accepted project policy, committed project choices, and maintaining artifacts, and none had a [terminology](../../.agent-workflow/terminology.md) entry, while the glossary defined U# and F# but not E# or D#.
Those seven entries now exist, restating meanings already set by [ADR-0025](../../architecture-decisions/0025-preserve-authority-at-consequential-boundaries.md), [ADR-0027](../../architecture-decisions/0027-use-direct-first-progressive-routing.md), [ADR-0028](../../architecture-decisions/0028-use-wayfinder-as-sole-durable-coordinator.md), routing, and the [records contract](../../.agent-workflow/contracts/effort-records.md) without renaming anything.
The first 2026-09-29 report proposed five of them under the terminology change procedure; E# and D# came from the deeper review that followed.
Shorter replacement names for the authority phrases, such as "decision owner", were considered and not introduced, because renaming a canonical term needs the [terminology change procedure](../../docs/maintenance.md#changing-canonical-terminology) and would change the gated root policy.

**PR #54 corrections.**
Implementation had literally prohibited reporting actual execution, and Prototype's blanket persistence statement conflicted with its scratch-database exception.
Implementation now permits reporting execution only after actually executing the method; Prototype states the in-memory default and allows scratch persistence when persistence is part of the question.
The snippet rule in `to-spec` and `to-tickets` requires both prototype origin and greater precision in the snippet itself.
Independent Standards and Spec reviews and the deterministic, package, and delivery checks passed at `25626ef`; no live evaluation was performed, and clearer wording does not establish improved agent behavior.
The token-forensics `skills_materially_invoked` schema concern remains deferred in that PR.

These repetitions have supported purposes and do not currently justify consolidation:

- **Truthfulness across scopes:** the [root policy](../../AGENTS.md) and [consumer template](../../agent_workflow/install/AGENTS.md.template) prioritize factual accuracy over output completion; [Code Review](../../.agents/skills/code-review/SKILL.md) and [spec synthesis](../../.agents/skills/to-spec/SKILL.md) keep narrower applications to unavailable reviewers and unresolved scope.
- **Authority at different loading boundaries:** [ADR-0025](../../architecture-decisions/0025-preserve-authority-at-consequential-boundaries.md) explains why the always-loaded root policy carries authority rules, while [Discovery](../../.agents/skills/workflow-discovery/SKILL.md#resolve-the-decision) and [Debugging](../../.agents/skills/workflow-debugging/SKILL.md#fix-and-verify) apply them at their own triggers and timing.
  Removing the root obligation would leave work before specialist loading without it, and removing the contextual clauses could lose their trigger or timing.
- **Meaning versus operation:** [terminology](../../.agent-workflow/terminology.md) defines dependencies and blockers; the [state contract](../../.agent-workflow/contracts/effort-state.md#dependencies-and-readiness) applies them to scoped readiness and persistence.
- **Different contexts and history:** [Domain Modeling](../../.agents/skills/domain-modeling/SKILL.md) maintains project domain language, while [Codebase Design](../../.agents/skills/codebase-design/SKILL.md#glossary) supplies module-design vocabulary under [ADR-0029](../../architecture-decisions/0029-distribute-canonical-framework-terminology.md); former paths in the [reinstall guidance](../../README.md#one-time-reinstall-for-the-repository-layout-release) and ADR history are explicitly historical.

The Debugging-to-build handoff question formerly noted here was resolved by the handoff shipped in PR #59; the [responsibility map](../workflow-responsibility-boundaries/map.md#current-state) keeps its rationale.

## Areas and relationships

- **Definitions:** [canonical terminology](../../.agent-workflow/terminology.md) maintains shared framework meanings; [ADR-0029](../../architecture-decisions/0029-distribute-canonical-framework-terminology.md) separates them from specialized behavior and project-owned domain models.
- **Obligations and context:** the [root-policy template](../../agent_workflow/install/AGENTS.md.template), [routing](../../.agent-workflow/routing.md), [state contract](../../.agent-workflow/contracts/effort-state.md), and [selected skills](../../.agents/skills/) maintain their respective rules; the [architecture overview](../../docs/architecture.md#instruction-runtime) explains why some obligations must stay loaded before detailed instructions.
- **Delivery:** the [manifest](../../agent_workflow/install/manifest.json) maps canonical files to their consumer paths; [package verification](../../agent_workflow/verify_package.py) checks root and template synchronization, and [distribution tests](../../tests/test_direct_distribution.py) exercise byte-for-byte delivery.
- **Evidence:** [term-inventory tests](../../tests/test_routing.py) protect canonical names without fixing definitions to exact prose; [test ownership](../../tests/README.md) separates delivery observations, literal interfaces, evaluator controls, and live evidence.
  The removed [instruction-coherence controls](https://github.com/jimmfan/agentic-workflow/blob/92d3304473b0fbebdcb6ab08b41bbad1d9710a50/tests/test_instruction_coherence.py) remain historical evidence only; their success did not establish semantic equivalence or agent compliance.

## Blockers

No unresolved dependency blocks this effort's current work.
Reliable agent interpretation remains unproven by source inspection and deterministic controls; no live evaluation was performed.
Existing campaign limitations remain with their maintaining reports and efforts.
