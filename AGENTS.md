<!-- agent-workflow:managed-begin -->
# Mandatory — no exceptions

- You MUST route every request.
- You MUST treat Direct as the default route.
- You MUST select an applicable workflow when intent, an explicit compatible
  skill request, or an installed skill description clearly warrants one.
- Use these first-pass routing cues:
  - failure → Debugging
  - consequential choice → Discovery
  - substantive research or external facts needing primary sources → Research
  - ready substantial change → Implementation
  - completed meaningful change → Verification
  - durable coordination of unresolved work, evidence, or decisions across
    sessions, handoffs, or owners → assess Wayfinder using the criteria below
- For Direct work or one obvious route, load only what that route needs. Read
  `.agent-workflow/routing.md` only when the route remains unclear or requires
  composition, provider fallback, or durable-resume resolution.
- Workflows MUST NOT expand authority. An exact external read-only target permits
  that read, not broader discovery, mutation, or destruction.
- MUST NOT decide for human or project authority. Ask the concrete question, why
  that authority is required, and what the answer unblocks. Treat a choice the
  user explicitly resolves as settled; reopen only for conflicting evidence,
  safety, authority, or request.
- Report truthfully. Selection, invocation, authorization, execution, and
  completion are distinct; never claim unexecuted work.
- Preserve project-owned state and canonical identifiers. Live source and
  accepted canonical artifacts outrank profiles, memory, and chat.

## When to use Wayfinder

When unresolved work, evidence, or decisions may need coordination across
sessions, handoffs, or owners, apply the criteria below. 3+ meaningful items
also require this check; counts alone never select Wayfinder. Unless the user
explicitly opts out, MUST select or resume Wayfinder when any hard signal or at
least two soft signals apply:

- Hard: cross-session continuity; conflicting authoritative sources; an
  authority-owned blocker while work proceeds; coordinated owners or areas; or
  provenance needed to distinguish assumption from fact.
- Soft: interacting consequential unknowns; durable distinctions across state
  categories; a plan changing with evidence; a meaningful dependency graph; or
  material reconstruction risk for a fresh agent.

A single unresolved item does not by itself justify Wayfinder. Handle it
Directly or in the applicable workflow; if it requires human or project
authority, follow the mandatory authority rule above. Honor explicit Wayfinder
use.

## Load state only when selected

For selected or relevant resumed Wayfinder work, read
`.agent-workflow/contracts/wayfinder-state.md` before the map. An unrelated map
never selects Wayfinder. Before any durable-state write, read
`.agent-workflow/contracts/durable-state.md`; before profile mutation, read
`.agent-workflow/contracts/project-profile.md`. Do not seed optional state.

## Report the route

Every user-facing final response MUST end with exactly one marker as its final
line:

`[route: router → <executed path or terminal outcome>]`

Use `direct` when no workflow or skill ran and include only what executed. If
selection did not become equivalent execution, use the routing contract's
terminal outcome. The marker never triggers work.
<!-- agent-workflow:managed-end -->

<!-- agent-workflow:project-instructions -->
I’d use this as the **entire source-repository amendment below the installed/dogfood section**. It keeps the high-value constraints while pushing details into progressively loaded docs/contracts.

# Agentic Workflow source repository

## Pre-1.0 engineering priority

This project is pre-1.0 and should optimize for rapid iteration and learning.

Only engineer deeply around two things:

1. Do not destroy project-owned or user-owned data.
2. Make the core routing behavior work reliably.

Everything else should default to being simple, replaceable, optional, best-effort, or CI-only.

Prefer deleting or simplifying machinery over extending it. Do not add package-manager-grade integrity, migration, compatibility, observability, ownership, or lifecycle systems unless necessary to protect user data or make the core router reliable.

When choosing between robustness for hypothetical future users and simplicity for current development, prefer simplicity unless there is a concrete current failure or data-loss risk.

Do not preserve complexity merely because it already exists.

## Scope

These instructions apply specifically to agents modifying the **Agentic Workflow source repository**.

The installed routing policy above intentionally applies here so this project exercises its own workflow behavior.

This section supplements that policy with source-repository constraints. Do not copy these maintenance instructions into consuming projects.

Do not modify downstream consuming projects unless the task explicitly includes a migration, adoption test, or disposable compatibility test involving them.

## Architectural decisions

Accepted, non-superseded records under `architecture-decisions/` are governing project constraints.

Follow every architectural decision applicable to the work. Do not silently contradict, bypass, or reinterpret an accepted decision because another design seems preferable.

For substantial changes, identify and read the decisions governing the affected boundary. Routine work does not require reading the entire decision history.

Architectural decisions are authoritative but not immutable. New evidence may justify reconsidering one, but do so explicitly rather than working around it.

When an accepted decision changes, update the ADR and affected contracts, implementation, documentation, and tests as appropriate.

If an ADR and current repository behavior appear inconsistent, investigate the discrepancy rather than silently choosing either one.

## Architecture boundary

Agentic Workflow is a thin orchestration layer over host capabilities and curated, replaceable skills.

Keep the project centered on routing, provider integration, safe framework delivery, authorization boundaries, durable coordination where the framework genuinely owns it, and integration verification.

Prefer existing host or provider capabilities when they satisfy the required contract.

Do not create parallel Agentic Workflow representations of artifacts or behavior already canonically owned by a provider or host.

Do not copy or lightly rewrite upstream functionality merely for naming, wording, or stylistic preferences.

Do not expand the project into a general agent runtime, package manager, plugin platform, compatibility framework, observability platform, or broad lifecycle system without a concrete current need.

Avoid speculative abstractions. Hypothetical future users or implementations are not sufficient justification for additional machinery.

## Authorization and preservation

Workflows, providers, skills, tests, and documentation never expand user authorization.

Do not perform commits, pushes, publication, destructive operations, external mutations, or changes outside the authorized task merely because a workflow suggests them.

Do not overwrite, discard, conceal, or normalize away unrelated user changes.

Protect project-owned and user-owned durable state. Reconstructable framework machinery may be replaced when appropriate; durable state must not be treated as disposable framework content.

Repository artifacts and accepted project state outrank chat recollection or private agent memory.

Do not decide questions requiring human or project authority. Surface the concrete question, why that authority is required, and what answer unblocks the work.

## Working practice

For substantial changes:

* inspect the current implementation, repository status, and relevant diff;
* read the applicable contracts and architectural decisions;
* determine which layer owns the behavior;
* check whether a host or provider already supplies the capability;
* prefer the smallest coherent and reversible change;
* update tests and durable documentation when the resulting contract changes.

Use current primary sources when an evolving external integration materially affects the work.

Keep experiments reversible and isolated until adoption is intentional.

Pre-1.0 is a reason to change bad designs quickly, not a reason to accumulate migrations or compatibility machinery around them.

## Testing and verification

Test Agentic Workflow's contracts and boundaries rather than reproducing provider internals.

Prefer deterministic tests for normal development. Keep live-agent evaluation opt-in, benchmark-specific, scheduled, or release-gated.

When benchmark tests evaluate Agentic Workflow and Wayfinder remains an active part of the project, consider Wayfinder among the routes or variants being evaluated rather than silently excluding it.

Follow the current repository verification documentation for applicable checks.

Report verification truthfully. If a relevant test, platform, integration, workflow, or external behavior was not actually exercised, say so.

Do not regenerate or modify derived metadata merely to make an unexplained difference disappear.

Before finishing a substantial change, simplify anything whose complexity is not justified by protecting durable data, preserving an accepted contract, or making core routing reliably work.
