# Automatic Wayfinder delegation: empirical evidence and repository implications

- Date: 2026-08-21
- Question: Should a general coding agent automatically delegate durable coordination to a focused Wayfinder subagent, or should the project return to the simpler main-branch design and retain only selected branch improvements?
- Source policy: Primary sources only: research papers, official product documentation/source, and this repository's own recorded live evidence.

## Executive conclusion

The evidence supports abandoning **automatic General-to-Wayfinder delegation as a product requirement in the current VS Code host** and returning to main's simpler design, where the General agent applies the portable Wayfinder method inline after routing selects it.

That conclusion is narrower than “multi-agent systems do not work.” Empirical work shows real multi-agent gains when tasks are highly parallelizable, workers have independent scopes, coordination is explicit, and outputs can be mechanically integrated and verified. Durable coordination in this repository has the opposite shape: it is sequential, context-sensitive work over a shared canonical map, with authority and schema constraints that must survive the handoff. Current VS Code subagents are stateless, receive a bounded task, and return only a final summary to a model-driven parent. VS Code makes a custom agent *available* for invocation but does not expose a deterministic semantic-routing contract.

The branch's live failure is therefore consistent with established evidence rather than an isolated prompt bug: eligibility did not cause delegation; explicit prompting restored delegation but the parent repeated work; isolated context lost part of the state contract; and the child wrote invalid statuses. More orchestration instructions might improve one fixture, but the literature says such prompt-level repairs do not remove the underlying coordination, context, verification, and termination failure classes.

The defensible hybrid is:

1. restore main's Direct-first portable router and inline Wayfinder execution as the default;
2. retain the branch's improved Wayfinder state model, authority/decision boundaries, progressive navigation, and deterministic contract tests;
3. optionally retain a **manually selected** focused VS Code Wayfinder agent with model invocation disabled; and
4. use subagents only for explicit, bounded, independently verifiable work such as parallel research or orthogonal review—not as the mandatory carrier of canonical durable coordination.

## What the empirical evidence actually establishes

### Multi-agent gains are conditional on task shape

Google Research evaluated 180 configurations spanning one single-agent and four multi-agent architectures, three model families, and four benchmarks. Centralized coordination improved a parallelizable financial-analysis benchmark by 80.9% relative to a single agent, but every multi-agent design degraded performance by 39–70% on the sequential PlanCraft benchmark. The study also found a growing coordination tax as tool count increased; independent-agent designs amplified errors by up to 17.2 times, while a centralized orchestrator reduced but did not eliminate amplification (4.4 times). These are controlled benchmark results, not a proof about this repository, but they establish that decomposition, sequential dependence, tool density, and orchestration topology materially determine whether more agents help ([paper](https://arxiv.org/abs/2512.08296), [Google Research summary](https://research.google/blog/towards-a-science-of-scaling-agent-systems-when-and-why-agent-systems-work/)).

The strongest recent software-engineering result is similarly conditional. Geng and Neubig's Centralized Asynchronous Isolated Delegation (CAID) improved accuracy over single-agent baselines by 26.7 percentage points absolute on PaperBench and 14.3 points on Commit0. The system does not rely on an informal semantic handoff: it creates a dependency-aware plan, gives workers isolated workspaces, integrates through branch-and-merge, and performs executable test-based verification. The paper begins from observed failures of ordinary multi-agent coding—interfering edits, dependency synchronization, and incoherent integration—and succeeds by adding explicit software-engineering coordination mechanisms ([paper, revision of 2026-07-08](https://arxiv.org/abs/2603.21489), [official implementation](https://github.com/JiayiGeng/CAID)).

Anthropic's production research system supplies a useful positive boundary case. Its internal evaluation found a lead-agent-plus-subagents system outperformed single-agent Claude Opus 4 by 90.2% on breadth-first research, where agents could pursue independent searches in parallel. Anthropic also reports roughly 15 times the token use of ordinary chat, early duplication and coverage gaps from vague delegation, and that domains requiring shared context or many dependencies are poor fits; it explicitly identifies most coding as less parallelizable than research. This is first-party production evidence rather than a peer-reviewed controlled study, so its exact effect size should not be generalized, but its fit criteria agree with the controlled studies ([Anthropic engineering report](https://www.anthropic.com/engineering/multi-agent-research-system)).

**Proven:** Multi-agent architectures can materially outperform single agents on parallelizable and long-horizon decomposable tasks when the architecture supplies isolation, explicit ownership, integration, and verification.

**Not proven:** Merely exposing a specialized subagent, or asking a parent model to choose it semantically, improves software-engineering reliability. None of the positive studies validates that design.

### Coordination, duplication, context, and verification failures are recurring empirical classes

The peer-reviewed MAST study developed its taxonomy through rigorous analysis of 150 traces from seven multi-agent systems, including software-engineering systems MetaGPT, ChatDev, and HyperAgent; the released dataset contains more than 1,600 annotated traces. Six expert annotators derived 14 failure modes with strong final inter-annotator agreement (Cohen's kappa 0.88). The observed distribution was not dominated by a single model mistake: specification/system-design failures accounted for 41.77%, inter-agent misalignment for 36.94%, and verification/termination failures for 21.30% ([NeurIPS 2025 proceedings](https://proceedings.neurips.cc/paper_files/paper/2025/hash/b1041e52d3be19f0a9bc491657488e4a-Abstract-Datasets_and_Benchmarks_Track.html), [full paper](https://arxiv.org/abs/2503.13657), [open data and evaluator](https://github.com/multi-agent-systems-failure-taxonomy/MAST)).

The specific modes closely match the risks in the current branch:

- repeated steps: 17.14%;
- failure to follow task requirements: 10.98%;
- context loss: 3.33%;
- failure to recognize completion: 9.82%;
- proceeding on wrong assumptions without clarification: 11.65%;
- reasoning/action mismatch: 13.98%;
- premature termination: 7.82%;
- missing or incomplete verification: 6.82%; and
- incorrect verification: 6.66%.

The authors' role-specification intervention improved ChatDev, but their broader conclusion was that simple prompt fixes were insufficient and more fundamental system-design changes were required. ChatDev reached only 33.33% correctness on their ProgramDev benchmark before intervention. The percentages describe occurrences in the study corpus rather than probabilities for a new system, but they establish that duplicated work, context fragmentation, instruction non-adherence, and weak verification are recurring multi-agent system phenomena, including in software development.

A peer-reviewed software-engineering baseline points in the same direction from the opposite side. Agentless uses fixed localization, repair, and validation stages instead of letting an autonomous agent choose future actions and tools. On SWE-bench Lite it resolved 96 issues (32.00%) at a reported average cost of $0.70, outperforming the open-source agent systems compared at the time. This does not prove fixed workflows always win, but it demonstrates that complexity itself is not evidence of capability and that a simple, inspectable workflow can be a strong baseline ([FSE 2025 paper](https://lingming.cs.illinois.edu/publications/fse2025.pdf), [artifact](https://github.com/OpenAutoCoder/Agentless)).

**Proven:** Current multi-agent systems repeatedly exhibit the same classes of failures seen in the live regression, and simple workflow baselines can be competitive or better.

**Inference:** When a task's value comes from preserving one coherent authoritative context, splitting it across a parent and a stateless child adds a failure surface without adding the parallel capacity that justified the successful multi-agent systems.

## What VS Code and Copilot actually guarantee

The current official VS Code subagent documentation is explicit about the execution model:

- the main agent decides when isolated context helps;
- it passes only the relevant subtask to a new subagent;
- each invocation is stateless and the parent cannot send follow-up messages to that same child; and
- the parent receives only the child's final result, not the child's working context ([VS Code: Subagents](https://code.visualstudio.com/docs/agents/run/subagents)).

The same documentation says `disable-model-invocation: false` makes a custom agent available for use as a subagent. It does not say that availability requires the main model to call it for matching tasks. It warns that similar names or descriptions can cause the model to select an unintended agent and recommends explicit `agents` restrictions and coordinator instructions for consistent behavior. The official product flow therefore remains model-mediated tool selection, not deterministic routing.

The custom-agent schema reinforces this distinction. `user-invocable` controls picker availability; `disable-model-invocation` prevents another agent from invoking the custom agent; `agents` constrains which child definitions are exposed; and handoffs are user-visible transition buttons after a response ([VS Code: Custom agents](https://code.visualstudio.com/docs/agent-customization/custom-agents), [official VS Code source specification](https://github.com/microsoft/vscode/blob/main/src/vs/sessions/copilot-customizations-spec.md)). These are discovery, permission, and interaction controls. They do not define a semantic dispatch predicate such as “if the portable router selects Wayfinder, invoke this exact child once and do no overlapping work.”

GitHub's cloud-agent configuration uses the phrase “automatically using this custom agent based on task context” for the same flag, while VS Code's local documentation describes a model choosing a subagent from request, context, and available agents ([GitHub custom-agent configuration](https://docs.github.com/en/copilot/reference/custom-agents-configuration), [GitHub Copilot in IDEs](https://docs.github.com/en/copilot/how-tos/chat-with-copilot/chat-in-ide)). Neither publishes a deterministic classifier, precedence rule, conformance test, or semantic-routing guarantee. The surface and host must therefore be recorded carefully; cloud-agent wording cannot be promoted into a local VS Code guarantee.

Official VS Code documentation does provide deterministic lifecycle hooks: hooks run configured commands at defined lifecycle points regardless of what the model decides. That is appropriate for narrow enforcement, observation, and validation, but it does not turn the model's semantic decision into a deterministic one ([VS Code: Agent hooks](https://code.visualstudio.com/docs/agents/reference/hooks-reference)).

**Proven:** VS Code supports custom agents, manual selection, model-initiated subagents, scoped agent availability, explicit coordinator instructions, handoffs, and deterministic lifecycle hooks.

**Not guaranteed:** Automatic semantic selection of the correct custom agent, exactly-once invocation, full child-context transfer to the parent, non-duplication after return, or adherence to a repository-defined state schema.

## Repository-specific evidence

The Basic Phase 2 live-host runs are stronger evidence for this product decision than general benchmark averages because they exercise the exact host and contract:

1. At commit `3c80dfc`, a neutral Wayfinder-positive case ran inline in General with no `SubagentStart`. This falsified the premise that model-invocation metadata plus description completed the automatic bridge.
2. Adding an always-on General-parent instruction caused a real `Wayfinder` child to start, but General made eight tool calls after the child returned and substantially repeated its investigation.
3. In the combined positive case, the child read only the first 360 lines of the state contract and wrote `contradicted` and `unresolved`, neither of which is an allowed status. The contract requires fact status `current | disputed | stale` and unknown status `open | resolved`.
4. Direct and Debugging negative controls correctly avoided Wayfinder and durable-state mutation.
5. All 147 deterministic tests passed while the live positive behavior still failed. The tests proved packaging and static contracts, not semantic selection or live state correctness.

The first two observations are recorded in the amended [ADR-0031](../architecture-decisions/0031-enable-focused-wayfinder-model-invocation.md); the exact run summary supplied with this research task records the remaining outcomes, and the [Basic Phase 2 protocol](../evals/manual-vscode/basic-phase2-wayfinder-smoke-v1/protocol.md) defines the status and live-event checks used to judge them. They instantiate four independently documented failure classes: routing/role selection failure, repeated steps, context loss, and failure to follow output requirements. The exact invalid status values are repository evidence, not a claim derived from the external papers.

The repeated parent investigation is also structurally understandable from the official host contract. A parent receives only a summary from a stateless child. If it needs source-grade confidence before answering or continuing, re-reading is locally rational. An instruction saying “do not repeat work” conflicts with the parent's need to verify a lossy result; it cannot create shared working context or a mechanically trusted result artifact.

## Decision inference for Agent Workflow

### Why automatic Wayfinder is the wrong fit

Wayfinder is not an independent worker task. It owns the canonical coordination view: current facts, unknowns, decisions, dependencies, authority boundaries, evidence precedence, and the ready frontier. Updating that view is sequential and stateful. The useful output is not merely a prose recommendation; it is a valid reconciliation of a shared durable artifact against current repository evidence.

Automatic subagent delegation adds two model-dependent boundaries:

```text
General semantic route choice
        ↓
model-chosen subagent/tool invocation
        ↓
isolated Wayfinder context and state mutation
        ↓
lossy final summary
        ↓
General interpretation, possible re-reading, and continuation
```

Main's inline design has one model context and one routing boundary. It can progressively load the Wayfinder contract only when selected, mutate the map, and continue with the same evidence. The branch's automatic design does not reduce semantic work; it relocates it across a lossy handoff and then asks the parent not to verify too much.

This makes automatic Wayfinder a **dead end under the current product objective and host contract**: no demonstrated outcome gain offsets the new routing, handoff, duplication, and schema risks. It is not proven impossible to engineer, but further prompt stacking would be research into a new orchestration runtime—the kind of complexity this pre-1.0 repository explicitly rejects unless needed for data protection or reliable core routing.

### What to retain from this branch

The following changes do not depend on automatic delegation and are supported by either the evidence or the repository's own contracts:

| Branch capability | Recommendation | Reason |
| --- | --- | --- |
| Thin, Direct-first, evidence-triggered routing | Retain | Reduces context and preserves one explicit semantic router; consistent with simple strong baselines. |
| Wayfinder as the sole framework-owned durable coordinator | Retain | Avoids parallel continuity stores and reduces coordination ambiguity. |
| Material decision context, authority preservation, and ready-frontier gating | Retain | These protect project/user decisions and durable state, independent of agent topology. |
| Refined Wayfinder state statuses, reconciliation rules, and deterministic behavioral tests | Retain | Directly addresses schema and stale-state risks; useful for inline and manual operation. |
| Progressive domain → territory → architecture navigation | Retain | Controls context without requiring a parent/child split. |
| Focused VS Code Wayfinder custom agent | Retain only as optional/manual | Manual selection is a documented host capability and preserves a useful least-capability persona for users who deliberately want an isolated coordination pass. Set `disable-model-invocation: true`; keep it user-invocable. |
| Narrow state-deletion guard and route-observation hooks | Retain only if they remain small and independently useful | Hooks can deterministically observe or deny recognized events, but remain defense in depth rather than routing or filesystem guarantees. |
| Phase 1/2 evaluation fixtures and live protocol | Retain selectively as historical/optional regression material | They capture valuable evidence; they should not make automatic delegation a supported product contract. |
| Managed `.github/copilot-instructions.md` automatic parent bridge | Remove | It restored a child call but did not prevent duplicate work or invalid state, and it creates host-specific always-on complexity. |
| `disable-model-invocation: false` as the default Wayfinder projection | Revert | It exposes a nondeterministic path with no proven product benefit. |
| Basic Phase 2 automatic-delegation acceptance requirement | Retire or mark superseded | The exact gate has failed for reasons predicted by external and local evidence. |

This is a recommendation, not an implementation plan. The branch contains many changes beyond focused-agent work, so the safe engineering operation is not a wholesale reset. Port or preserve the selected contract, test, and documentation changes deliberately while superseding ADR-0031 and the automatic portion of ADR-0030.

### Evidence that still justifies focused or explicit agents

Abandoning automatic Wayfinder does not imply deleting focused agents or subagent support:

- VS Code officially supports manual custom-agent selection and user-controlled handoffs, which remove the hidden classifier from the boundary.
- A manually selected Wayfinder persona can expose fewer tools, block nested agents, and focus instructions without asking General to infer an invisible transition.
- Explicit subagents remain well supported for independent parallel research, orthogonal code review, or bounded exploration whose result is advisory and can be synthesized or mechanically checked.
- CAID shows a path for future multi-agent implementation work if this project later needs it: isolated worktrees, dependency-aware delegation, explicit integration, and executable verification—not shared-worktree semantic role switching.
- Anthropic's research result supports parallel subagents when breadth and separate context windows are the actual bottlenecks; it simultaneously argues against using that pattern for tightly dependent shared-context coding work.

The useful distinction is therefore **manual or structurally explicit specialization versus automatic semantic delegation**. The former is supported. The latter is the failed product hypothesis.

## What evidence would justify reopening automatic delegation

Reconsideration should require more than a new prompt or a single passing demo. At minimum:

1. a documented host contract or deterministic mechanism that binds the portable route decision to one exact focused invocation;
2. a result channel that carries a complete, machine-checkable Wayfinder mutation/result rather than only a prose summary, or a persistent child that supports clarification;
3. schema validation that rejects invalid statuses before durable writes are accepted;
4. clear ownership that prevents parent/child duplicate investigation and competing state mutation;
5. repeated A/B evaluation against the inline main-branch baseline on representative positive, negative, stale-state, authority, and combined cases;
6. measured benefit in correctness, recovery, or resource use large enough to pay for the added host-specific machinery; and
7. no regression in Direct and specialist routes.

Until those conditions exist, the empirical default should be the simpler main-branch architecture plus the topology-independent branch improvements listed above.

## Evidence quality and limits

- MAST was published in the NeurIPS 2025 Datasets and Benchmarks Track and is broad and empirically annotated, but its failure percentages are descriptive of sampled failing traces, not prospective failure probabilities for Wayfinder.
- Agentless was peer reviewed at FSE 2025, but its SWE-bench comparison reflects models and systems available at that time.
- The Google scaling and CAID results are 2025/2026 preprints as of this report; they are controlled and reproducible enough to inform design, but should not be described as settled universal laws.
- Anthropic's figures are internal first-party evaluations and may not reproduce on other models or tasks.
- The repository's live runs are few, but they have high direct relevance and include negative controls. Their conclusion is appropriately bounded: the current automatic Wayfinder bridge failed its own gate.

Taken together, the evidence is strong enough for a pre-1.0 product decision: stop investing in automatic Wayfinder delegation now, preserve the good durable-coordination work, and keep explicit/manual specialization available where its boundary is visible and intentional.
