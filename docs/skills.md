# Curated skills

Agent Workflow distributes fifteen reviewed skills directly through the ordinary
package payload and lifecycle manifest. Those mapped files are the single
maintained runtime representation.

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
Engineers release `v1.2.3`. Agent Workflow maintains their reviewed effective
installed versions and preserves complete copyright and MIT license attribution
in the installed `THIRD_PARTY_NOTICES.md`. The frozen exact-transition fixture
also attributes historical `setup-matt-pocock-skills`, `teach`, and `triage`
bytes; those three are not current runtime skills.

`wayfinder` and `research` preserve Agent Workflow's reviewed effective contracts.
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

`to-spec` and `to-tickets` resolve a publication destination in this order:

1. the current request;
2. project instructions;
3. existing project-owned tracker configuration, including
   `docs/agents/issue-tracker.md`;
4. otherwise no inferred destination.

Conflicting applicable sources require clarification. A known destination does
not authorize a mutation. Without both a destination and authorization, each
skill returns the complete draft in chat, creates no temporary repository file,
and stops before publication. Labels, statuses, and blocking links require both
project-defined semantics and authorization for that mutation.

`code-review` treats tracker access as optional source lookup. It continues when
the fixed point and specification are otherwise available, never blocks the
Standards axis solely because tracker access is absent, and returns its report
in chat unless publication is separately authorized.

## Lifecycle and maintenance

Manifest-mapped skill files are framework-owned and reconstructable. Install and
update restore missing or drifted declared files to current package bytes and
preserve unrelated skill directories. Removal deletes an external file only
when valid install evidence says the framework created it and its current bytes
match the recorded digest.

One immutable proof supports the exact former installation inherited from the
pinned main commit. It is not a generalized migration system. Any near match
fails closed before mutation. Current install state uses a canonical integrity
digest and distinguishes absent, valid, and invalid state.

When maintaining a derived skill, edit the effective payload directly, preserve
its complete declared directory and local references, classify every prose
change, keep attribution complete, and run the package verifier. Upstream
network research is optional maintainer evidence, never a runtime requirement.
