# Curated skills

Agent Workflow distributes fifteen curated skills directly through the ordinary
package payload and current distribution map. Those skill directories are the
single maintained runtime representation.

## Inventory

The installed surface under `.agents/skills/` is exactly:

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

The first eleven are copied from or derived from Matt Pocock's Skills for Real
Engineers release `v1.2.3`. Agent Workflow maintains their effective
installed versions and preserves complete copyright and MIT license attribution
in the installed `.agent-workflow/README.md`. Historical skill inventories are not
part of the current runtime.

`wayfinder` and `research` preserve Agent Workflow's maintained contracts.
`research` returns cited findings in chat by default and writes a repository
file only after an explicit authorized request. `wayfinder` remains the sole
durable coordinator under `.agent-wayfinder/`. `implement` owns its inner build,
TDD, and `code-review` loop; `workflow-implementation` remains the outer
transition into execution and independent acceptance verification.

## Discovery and invocation

Codex and GitHub Copilot discover project skills under `.agents/skills`. The
portable [Agent Skills specification](https://agentskills.io/specification)
defines the skill directory and basic frontmatter but does not standardize
automatic model invocation. Agent Workflow preserves each complete skill
directory, including `SKILL.md` frontmatter and `agents/openai.yaml` when present;
hosts interpret those files and decide which skills are exposed in a session.
See the [Codex skill documentation](https://developers.openai.com/codex/skills),
[VS Code Agent Skills documentation](https://code.visualstudio.com/docs/agent-customization/agent-skills),
and [Claude Code skills documentation](https://code.claude.com/docs/en/skills).

At runtime, use only the skills exposed in the current session and follow the
selected skill's instructions. Never claim that a skill ran unless its method
ran. Deterministic fixtures validate the packaged files and mappings; live host
discovery remains unverified unless separately exercised.

## Tracker and publication boundary

`to-spec` and `to-tickets` use a destination named by the user or documented by
the project and publish only when authorized; otherwise they return the complete
draft in chat. Neither invents a local destination, label, or status.

`code-review` treats tracker access as optional source lookup. It continues when
the fixed point and specification are otherwise available and never blocks the
Standards axis solely because tracker access is absent.

## Lifecycle and maintenance

The ordinary distribution manifest is only the current source-to-target map.
Each current curated skill name is reserved for Agent Workflow: install and
update replace that complete directory with current package bytes, including any
extra files inside it, and preserve unrelated skill directories. Remove deletes
the complete current curated skill directories. No installed manifest, content
hash, provenance record, created-state bit, retirement history, migration proof,
or rollback journal participates in this lifecycle.

If no existing Agent Workflow installation is recognizable, existing directories
at current curated names are first-adoption collisions. Install and update list
the complete conflicting directories and ask once before replacement; `y` or
`yes` proceeds, while a decline or noninteractive invocation stops before
mutation. A valid managed composite region or an exact current
`.agent-workflow/` surface recognizes an installation, after which current
curated directories converge automatically without confirmation. Remove refuses
current curated-name directory collisions when no installation is recognizable.

Mutating commands accept any explicit existing non-root target directory. With
no target, the CLI may use Git only to discover the containing worktree root;
repository state does not gate the lifecycle. Preflight rejects symlinks,
unsupported entry types, and path escapes at managed roots or parents, plus
malformed composite markers. Nested entries inside a replaceable directory are
removed through ordinary convergence. Complete replacement of
`.agent-workflow/` removes obsolete files, while skill directories outside the
current curated inventory remain untouched. Lifecycle code does not directly
traverse, interpret, or change `.agent-wayfinder/`.

When maintaining a derived skill, edit the effective payload directly, preserve
its complete declared directory and local references, classify every prose
change, keep attribution complete, and run the package verifier. Upstream
network research is optional maintainer evidence, never a runtime requirement.
