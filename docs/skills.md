# Curated skills

Agent Workflow distributes fifteen curated skills from the authored `.agents/skills/` tree through the current distribution map.
Those skill directories are the single maintained runtime representation.

Each discoverable package under `.agents/skills/` is a skill.
See [Workflow routing](routing.md) for how a skill participates in a route.

## Inventory

The canonical inventory under `.agents/skills/` is exactly:

- `wayfinder`
- `research`
- `to-spec`
- `to-tickets`
- `implement`
- `tdd`
- `code-review`
- `grilling`
- `domain-modeling`
- `prototype`
- `codebase-design`
- `workflow-debugging`
- `workflow-discovery`
- `workflow-implementation`
- `workflow-verification`

The first eleven are copied from or derived from Matt Pocock's Skills for Real Engineers release `v1.2.3`.
Agent Workflow maintains their effective installed versions and preserves complete copyright and MIT license attribution in the installed `.agent-workflow/README.md`.
Historical skill inventories are not part of the current runtime.

`wayfinder` and `research` preserve Agent Workflow's maintained contracts.
`research` returns cited findings in chat by default and writes a repository file only after an explicit authorized request.
`wayfinder` remains the sole durable coordinator under `.project-efforts/`.
`workflow-discovery` analyzes one bounded consequential choice and its alternatives, evidence, tradeoffs, reversibility, consequences, authority, and uncertainty; a lasting architecture decision remains in the project record designated to maintain it.
`domain-modeling` maintains domain concepts, terminology and ubiquitous language, domain or context boundaries, domain responsibilities and relationships, and the applicable `CONTEXT.md` or `CONTEXT-MAP.md` model.
It does not own generic implementation or module architecture, all project structure, Wayfinder's effort-specific areas and relationships, or a generic architecture-decision store.
`implement` owns its inner build, TDD, and `code-review` loop; `workflow-implementation` remains the outer transition into execution and independent acceptance verification.
Its closing review covers the attributed implementation changes through the current working tree, using the supplied request, acceptance criteria, baseline, and pre-edit context.
Standalone Code Review preserves the requested range semantics; an explicitly committed-only review excludes pending work.

## Method boundaries

`to-spec` synthesizes the supported scope and testing decisions already available; it labels proposals and unresolved matters without turning synthesis into an interview or approval.
`tdd` reuses agreed test seams and keeps its red-to-green method; integration tests alone do not select it.
Codebase Design's vocabulary applies to deep-module analysis and preserves distinct project concepts such as services and APIs.
The module under test may expose an application-internal caller interface; its private implementation remains behind that interface.
Deepening retains useful behavior and failure coverage before old tests are removed.

`grilling` works through relevant unresolved choices requiring human input in dependency-aware rounds, with thoroughness when requested.
`to-tickets` cuts across applicable layers and records genuine ticket and external prerequisites; ticket drafting does not authorize execution.
Expand–contract is appropriate when compatibility or independent transitions require coexistence, while a safely verifiable bounded change may be atomic.

`prototype` offers interactive logic demos and UI exploration; CLI and infrastructure experiments may use Direct or existing methods.
Prototype evidence informs production work, whose adoption and verification remain separate from authorization to commit or publish.
Research and factual lookup can run synchronously when their evidence requirements are met; required independent or parallel methods retain that requirement and report unavailable capability honestly.

## Discovery and invocation

Codex and GitHub Copilot discover project skills under `.agents/skills`.
The portable [Agent Skills specification](https://agentskills.io/specification) defines each skill through `SKILL.md` frontmatter and instructions but does not standardize automatic model invocation.
Agent Workflow maintains complete `SKILL.md`-based directories and their referenced support files; hosts interpret those files and decide which skills are exposed in a session.
See the [Codex skill documentation](https://developers.openai.com/codex/skills), [VS Code Agent Skills documentation](https://code.visualstudio.com/docs/agent-customization/agent-skills), and [Claude Code skills documentation](https://code.claude.com/docs/en/skills).

At runtime, use only the skills exposed in the current session and follow the selected skill's instructions.
Never claim that a skill ran unless its method ran.
Deterministic fixtures validate the packaged files and mappings; live host discovery remains unverified unless separately exercised.

## Tracker and publication boundary

`to-spec` and `to-tickets` use a destination named by the user or documented by the project and publish only when authorized; otherwise they return the complete draft in chat.
Neither invents a local destination, label, or status.

`code-review` treats tracker access as optional source lookup.
It uses the supplied request or specification before artifact discovery and never blocks the Standards axis solely because tracker access is absent.
Missing required inputs or independent reviewers remain explicit coverage gaps; subsequent verification reuses covered evidence.

## Lifecycle and maintenance

The ordinary distribution manifest is only the current source-to-target map.
Each current curated skill name is reserved for Agent Workflow: install and update replace that complete directory with current package bytes, including any extra files inside it, and preserve unrelated skill directories.
Remove deletes the complete current curated skill directories.
No installed manifest, content hash, provenance record, created-state bit, retirement history, migration proof, or rollback journal participates in this lifecycle.

Install and update replace current curated-name directories unconditionally after the concrete managed-path and composite preflight; they perform no installation recognition or interaction.
Remove alone refuses current curated-name directory collisions when no installation is recognizable.

Mutating commands accept any explicit existing non-root target directory.
With no target, the CLI may use Git only to discover the containing worktree root; repository state does not gate the lifecycle.
Preflight rejects symlinks, unsupported entry types, and path escapes at managed roots or parents, plus malformed composite markers.
Nested entries inside a replaceable directory are removed through ordinary convergence.
Complete replacement of `.agent-workflow/` removes obsolete files, while skill directories outside the current curated inventory remain untouched.
Lifecycle code does not directly traverse, interpret, or change `.project-efforts/`.

When maintaining a derived skill, edit its canonical `.agents/skills/<name>/` directory directly, preserve its complete declared directory and local references, classify every prose change, keep attribution complete, and run the package verifier.
Upstream network research is optional maintainer evidence, never a runtime requirement.
