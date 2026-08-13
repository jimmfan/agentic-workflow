# Curated upstream provider research

- Research date: 2026-08-13
- Upstream: [`mattpocock/skills`](https://github.com/mattpocock/skills)
- Latest stable release evaluated: [`v1.2.3`](https://github.com/mattpocock/skills/releases/tag/v1.2.3)
- Immutable commit: `6acc160e4e0cd062dbbbd7a1b26ae92855edf07e`
- GitHub CLI compatibility exercised: `2.97.0`

## Current framework before the refactor

The framework had one compact root router, seven bundled workflow skills, a
Python transactional bootstrap/adopter, and repository-native state. Its durable
authorization and ownership controls were strong, but local Teach,
Decomposition, Review, and parts of Implementation overlapped maintained public
skills. The always-on policy was 2,914 bytes and all seven local skill bodies
totaled 27,520 bytes.

## Evaluated upstream skills

Selected direct capabilities:

- `setup-matt-pocock-skills`: provider configuration lifecycle for tracker,
  domain, and optional triage labels;
- `wayfinder`: huge, foggy multi-session map and decision-ticket workflow;
- `teach`: sustained course workspace with mission, glossary, resources,
  lessons, and learning records;
- `research`: primary-source investigation and durable reports;
- `to-spec`: durable specification generation;
- `to-tickets`: dependency-aware implementation frontier;
- `implement`: implementation loop and composition owner;
- `tdd`: implementation-time test-first subflow;
- `code-review`: fixed-point Standards/Spec review.

Selected direct composition dependencies:

- `grilling`, `domain-modeling`, and `prototype` are invoked by Wayfinder;
- `codebase-design` and TDD's adjacent `tests.md`/`mocking.md` resources support
  the implementation/test composition.

Rejected as a framework replacement:

- `diagnosing-bugs` is useful but does not preserve the local workflow's
  diagnosis-only authorization, external/non-test signal model, and durable
  interruption/resume contract. It remains available only if separately and
  explicitly installed by a project; the framework does not silently substitute
  it.

The full selected provider directories occupy approximately 113 KB at this
release. That on-disk cost does not imply an equivalent prompt cost: agent hosts
discover skill metadata first and load full instructions on selection. The
root router remains under 5 KB and avoids copied method bodies. The expected
initial-context increase is the host's skill catalog metadata, roughly low
single-digit kilobytes, while detailed provider instructions remain on demand.

## Setup lifecycle findings

The setup skill is prompt-driven. It writes project-owned
`docs/agents/issue-tracker.md`, `docs/agents/domain.md`, optional
`docs/agents/triage-labels.md`, and may add a root `## Agent skills` block. It
therefore must not run invisibly during framework installation or on every
prompt. The adopted lifecycle is a visible first-use check before a
tracker-dependent workflow, followed by direct project configuration edits
unless the user intentionally switches/resets setup.

At `v1.2.3`, Wayfinder, to-spec, to-tickets, and code-review explicitly check
the tracker configuration or direct the agent to setup when it is absent.
Wayfinder can default to local Markdown, but the shared first-use setup rule
avoids inconsistent tracker/domain assumptions across a later composed route.

Teach similarly owns a persistent workspace. It is appropriate for explicit
sustained learning intent, not ordinary explanations. A dedicated learning
workspace prevents its course artifacts from polluting an engineering target.

## Codex and Copilot invocation findings

Both hosts discover project skills from `.agents/skills`. Codex uses
progressive disclosure: skill metadata is available for selection, while the
complete `SKILL.md` and adjacent resources are read when the skill is invoked;
users can explicitly name a skill with `$skill-name`. Upstream
`agents/openai.yaml` sets `allow_implicit_invocation: false` for Wayfinder,
Teach, to-spec, to-tickets, and implement, so the ai-workflow router must invoke
those selected capabilities explicitly instead of assuming the host will choose
them automatically. Research, TDD, and Code Review retain their upstream
implicit policy and are constrained by router composition rules.

GitHub Copilot likewise loads a selected skill's instructions and supports
explicit `/SKILL-NAME` invocation. Its skill frontmatter can disable automatic
model invocation with `disable-model-invocation`; ai-workflow does not patch
upstream frontmatter to add host-specific policy. The root router supplies the
shared selection contract instead. See the official
[Codex skills guide](https://learn.chatgpt.com/docs/build-skills) and
[GitHub Copilot CLI skill guide](https://docs.github.com/en/copilot/how-tos/copilot-cli/customize-copilot/add-skills).

## GitHub CLI provider-manager findings

The official [`gh skill install`](https://cli.github.com/manual/gh_skill_install)
contract supports exact nested paths, `--pin`, project/user scopes, custom
directories, and injected source tracking metadata. It documents that project
scope is shared by Codex, GitHub Copilot, and several other hosts at
`.agents/skills`. The official
[`gh skill update`](https://cli.github.com/manual/gh_skill_update) contract says
pinned skills are skipped unless explicitly unpinned.

Live tests used an official GitHub CLI 2.97.0 macOS arm64 archive after verifying
its published SHA-256 checksum. In disposable non-Git directories:

- exact-path project installation succeeded without `git init`;
- complete skill directories were copied, including adjacent files and
  subdirectories;
- `SKILL.md` received repository, path, pin/ref, and tree-SHA metadata;
- repeated installation reported the existing compatible skill rather than
  duplicating it;
- pinned ordinary update remained pinned;
- Codex and GitHub Copilot resolved to the same project directory.

An unauthenticated multi-skill attempt later reached GitHub's public API rate
limit. The manager therefore requires
[`gh auth status`](https://cli.github.com/manual/gh_auth_status) to succeed before
writing a missing provider set. Interactive login follows the official
[`gh auth login`](https://cli.github.com/manual/gh_auth_login) web flow;
automation may use `GH_TOKEN`.

## Compatibility and update contract

The provider declaration records repository, stable tag, immutable commit,
minimum GitHub CLI version, capability mapping, skill paths, subtree SHAs, and
complete file inventories. Installation additionally records file checksums and
whether each directory was framework-created or pre-existing-compatible.

Normal framework update does not float provider versions. A future provider
upgrade requires review of a new stable tag, regenerated path/tree/file
identities, live exact-path installation checks, hermetic lifecycle tests,
manifest refresh, and a framework release. Same-named incompatible or locally
changed skills fail closed. Removal preserves pre-existing and changed skills.

## Recommendation

Adopt the selected pinned provider set and retain only the framework behaviors
that are genuinely project-specific. This provides the clearest responsibility
boundary: upstream owns mature workflow methodology and native artifacts;
Agentic Workflow owns routing, pinning, safe lifecycle, authorization,
continuity pointers, and acceptance/integration verification.
