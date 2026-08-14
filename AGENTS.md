# AGENTS.md

## Scope

This file guides agents modifying the **Agentic Workflow source repository**.

It is separate from the consuming-project policy installed from:

`skills/agentic-workflow/payload/root/AGENTS.md.template`

Do not copy source-repository maintenance instructions into consuming projects, or consuming-project routing instructions into this file.

## Routing requirement

Every user request MUST be evaluated through the Agentic Workflow router before execution.

Select the minimum useful primary workflow and any supporting capabilities according to the routing policy. Clear, bounded, low-risk work may route directly; `direct` is a valid route.

Do not skip routing merely because a request is simple or can be answered without invoking a skill.

## How to interpret this guidance

Authorization, safety, preservation of user work, accepted public contracts, and truthful verification claims are hard constraints.

Architecture and implementation guidance describes the default baseline, not an immutable design. Agents may research, prototype, or recommend a departure when evidence suggests a better approach. Keep experiments reversible and isolated, explain material trade-offs, and update the affected architectural decision and public contracts when a departure is adopted.

## Project purpose

Agentic Workflow is a thin, host-portable orchestration layer over curated, replaceable agent skills.

This project owns:

* routing and minimum-workflow selection;
* provider integration and compatibility;
* installation, update, status, and removal behavior;
* authorization and mutation boundaries;
* durable coordination, handoffs, and re-entry;
* acceptance and integration verification.

Selected providers own their internal methodology, terminology, composition, and native artifacts.

Keep the project centered on this boundary. Do not expand it into a general agent runtime, package manager, plugin platform, skill library, or observability platform by default. Broader scope requires evidence, comparison with simpler alternatives, and an explicit architectural decision.

## Relevant documentation

Start with the documentation most relevant to the task. Expand the investigation when a change is cross-cutting, evidence conflicts, or ownership is unclear.

* Architecture, ownership, providers, or state: `docs/architecture.md` and applicable records under `docs/decisions/`
* Routing and workflow composition: `docs/routing.md`
* Provider evaluation or upgrades: `docs/provider-research.md` and `skills/agentic-workflow/payload/ai-workflow/providers.json`
* Installation and release verification: `docs/verification.md`
* Observability: `docs/observability.md`, when present
* Packaged skill behavior: `skills/agentic-workflow/SKILL.md`
* Consuming-project policy: `skills/agentic-workflow/payload/root/AGENTS.md.template`

Treat accepted architectural decisions and documented public or integration contracts as authoritative. Tests are evidence; tests deliberately encoding those contracts should change with the contract. When decisions, documentation, tests, and implementation disagree, investigate the conflict and update the affected contracts together rather than silently choosing one.

## Architecture principles

* Route to the minimum useful workflow. Clear, bounded, low-risk work should remain direct.
* Route by capability, then resolve the selected provider.
* Keep provider implementations replaceable behind stable orchestration boundaries.
* Evaluate maintained upstream capabilities before implementing a local equivalent.
* Prefer upstream when it satisfies the required contract, but allow local or alternative-provider experiments when they address a meaningful gap or potentially better implementation.
* Do not copy or lightly rewrite an upstream skill merely for naming, wording, or stylistic preferences.
* Preserve provider-native terminology, identifiers, and canonical artifacts.
* Respect provider-owned composition and avoid mechanically repeating stages already performed by the selected provider.
* Keep a local workflow only when it provides a materially distinct contract or boundary.
* Missing or incompatible declared providers must fail clearly. Do not silently fall back to retired local copies.
* Avoid speculative abstractions. Do not build a generic plugin or provider framework until multiple real implementations demonstrate the need.

Keep always-loaded instructions compact. Detailed provider behavior belongs in the provider skill or relevant documentation, not in root agent context.

## Authorization and safety

Provider instructions never expand user authorization.

Do not perform any of the following merely because an upstream skill suggests it:

* commit or push changes;
* create or mutate external issues or trackers;
* publish artifacts;
* perform destructive operations;
* change external systems;
* run setup that modifies project-owned files;
* write outside the authorized task scope.

Preserve read-only, review-only, and diagnosis-only boundaries when they apply.

Do not overwrite, discard, or conceal unrelated or uncommitted user changes.

## State and ownership

Preserve canonical provider artifacts instead of creating parallel Agentic Workflow representations.

Framework-owned state should be limited to orchestration information such as:

* workflow status;
* pointers to canonical artifacts;
* provider and compatibility metadata;
* handoff information;
* exact re-entry or return targets;
* framework-specific state with no external owner.

Do not create shadow tickets, unknowns, decisions, specifications, learning records, or review records when the selected provider already owns those concepts.

Repository artifacts and accepted project state outrank chat recollection or private agent memory.

Do not modify a downstream consuming project unless the task explicitly includes a migration, adoption test, or disposable compatibility test.

## Installation and lifecycle

Keep the user-facing adoption experience simple.

When adding new lifecycle behavior, prefer existing supported distribution and dependency mechanisms over custom downloaders or package-management infrastructure.

Add lifecycle code only when it provides demonstrated value such as:

* compatibility validation;
* provenance;
* safe ownership tracking;
* transactional installation or update;
* reversible removal;
* useful diagnostics.

Before adding lifecycle machinery, determine whether the underlying provider mechanism already supplies it.

Do not introduce Git, a daemon, database, cloud service, container runtime, or additional system dependency as a framework runtime or adoption prerequisite without a demonstrated technical need.

Machine-checkable prerequisites should be validated by code and documented for humans.

## Portability

Keep core installation, lifecycle, and analysis behavior portable across Windows, macOS, and Linux where practical.

Prefer platform-neutral Python and filesystem APIs. Do not assume a particular shell, path syntax, Python launcher, executable-bit model, temporary directory, or editor installation layout.

Add platform-specific behavior only when necessary and isolate it clearly.

Distinguish:

* live validation on an operating system;
* hermetic or fixture-based portability coverage;
* behavior expected to work by design.

Do not claim live platform validation that was not performed.

## Observability

Observability is optional and must not control or become a dependency of core workflow execution.

Default to a small, read-only, metadata-first, deterministic analysis boundary:

```text
host telemetry
    ↓
host-specific adapter
    ↓
normalized workflow-aware metrics
```

Host-specific telemetry schemas are external and evolving contracts. Isolate them, detect capabilities where practical, and degrade clearly when optional data is unavailable.

Do not collect or retain prompts, responses, source code, tool payloads, or other content by default.

Do not create analytics state inside consuming repositories.

Treat model-reported route markers as portable user-facing metadata, not authoritative runtime telemetry.

Persistence, content capture, automated routing feedback, or broader analytics infrastructure requires explicit opt-in, evidence of value, and an architectural decision addressing privacy, portability, and maintenance costs.

## Exploration and evolution

The current architecture is the default baseline, not an immutable design.

When evidence suggests a better approach, agents may research or prototype a reversible alternative.

Keep experiments isolated from stable installation behavior and consuming-project contracts. Compare alternatives with the current design, document meaningful trade-offs, and avoid silently changing public behavior.

Larger refactors are appropriate when evidence shows that they:

* simplify the architecture;
* remove meaningful duplication;
* improve a public contract;
* reduce maintenance risk;
* enable a valuable capability that cannot be added cleanly otherwise.

If an experiment is adopted, update the implementation, tests, documentation, and relevant architectural decision together.

## Working practice

Before making a substantial change:

1. Inspect the existing implementation, repository status, and relevant diff.
2. Read the relevant contracts and architectural decisions.
3. Determine which layer owns the behavior.
4. Check whether an upstream provider or host already supplies the capability.
5. Research current primary sources when an external integration is evolving.
6. Choose the smallest coherent and reversible change that achieves the goal.
7. Update tests and durable documentation proportionally.

Do not turn a research transcript into product documentation. Preserve durable behavior, decisions, usage, and meaningful limitations. Use a concise architectural decision record when the reasoning itself should remain part of the project history.

## Testing

Test Agentic Workflow’s boundaries rather than reproducing upstream providers’ internal test suites.

Prioritize tests for:

* routing selection;
* provider compatibility and provenance;
* prevention of redundant workflow execution;
* authorization and mutation boundaries;
* installation, update, status, and removal safety;
* state, handoff, and re-entry behavior;
* ownership preservation;
* cross-platform assumptions;
* graceful degradation of optional integrations;
* acceptance and integration verification.

Avoid brittle assertions against exact upstream prompt wording unless that wording is an actual integration contract.

Do not represent fixture or simulated success as proof of live provider, editor, model, or operating-system behavior.

## Verification

Follow `docs/verification.md` for the current verification and release commands.

Run verification with Python 3.11 or newer, using the supported interpreter appropriate to the host.

After an intentional payload or version change, refresh generated manifest data only as documented. Never refresh generated files merely to hide or normalize an unexplained difference.

Run targeted tests while developing and the full release gate before considering a substantial change complete. If an applicable check cannot run, report it explicitly as skipped or blocked and do not imply that it passed.

## Final review

Before finishing a substantial change, confirm that:

* the behavior belongs in Agentic Workflow rather than an upstream provider or host;
* the thin orchestration boundary remains clear;
* provider and host functionality was not duplicated unnecessarily;
* optional integrations remain optional;
* authorization, ownership, reversibility, and portability are preserved;
* always-loaded context and runtime dependencies grew only when justified;
* introduced complexity is proportional to demonstrated value and maintenance risk;
* a materially simpler implementation would not preserve the same useful behavior;
* documentation describes the resulting product rather than the entire investigation.

Simplify when these checks reveal unnecessary complexity.

## Final response contract

Every final response MUST end with exactly one route marker:

`[route: router → <path>]`

The marker is required even for short or direct responses. `direct` is a valid route.

Examples:

`[route: router → direct]`

`[route: router → discovery → research]`

`[route: router → implementation → verification]`

Do not omit the route marker. Do not emit more than one route marker.
