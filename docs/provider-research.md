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

Selected configuration dependency:

- `triage` enables setup to provision the shared triage-label vocabulary used
  by `to-spec` and `to-tickets`. It is installed at the same immutable pin, but
  is not exposed as a root-routed framework capability.

Rejected as a framework replacement:

- `diagnosing-bugs` is useful but does not preserve the local workflow's
  diagnosis-only authorization, external/non-test signal model, and durable
  interruption/resume contract. It remains available only if separately and
  explicitly installed by a project; the framework does not silently substitute
  it.
The full selected provider directories occupy approximately 132 KB at this
release. That on-disk cost does not imply an equivalent prompt cost: agent hosts
discover skill metadata first and load full instructions only on actual
invocation, not on a user-only route selection. The
root router remains under 5 KB and avoids copied method bodies. The expected
initial-context increase is the host's skill catalog metadata, roughly low
single-digit kilobytes, while detailed provider instructions remain on demand.

## Setup lifecycle findings

The setup skill is prompt-driven. It writes project-owned
`docs/agents/issue-tracker.md`, `docs/agents/domain.md`, and may add a root
`## Agent skills` block. At `v1.2.3`, it writes
`docs/agents/triage-labels.md` only when the `triage` skill is installed. The
declaration therefore models issue-tracker and domain configuration as
provisioned by setup, and triage labels as both provisioned by setup and enabled
by triage. Setup must not run invisibly during framework installation or on
every prompt. On Codex or GitHub Copilot, explicit setup produces a visible
user-only handoff. Ordinary work that does not genuinely require setup continues
host-natively.

At `v1.2.3`, Wayfinder requires domain and tracker configuration; code-review
requires the tracker; and to-spec and to-tickets require domain, tracker, and
the triage-label vocabulary. The framework declares `implement`'s effective
tracker prerequisite as well because the pinned workflow always closes with
code-review; this prevents configuration discovery after implementation has
already started. Requirements are declared per selected operation, including
that one direct composition dependency, so routing can distinguish selection
from readiness without duplicating provider methods.

Teach similarly owns a persistent workspace. It is appropriate for explicit
sustained learning intent, not ordinary explanations. A dedicated learning
workspace prevents its course artifacts from polluting an engineering target.

## Host discovery and invocation findings

Codex and GitHub Copilot discover project skills from `.agents/skills`. Codex
uses `$skill-name` for explicit invocation and reads
`agents/openai.yaml:policy.allow_implicit_invocation`; GitHub Copilot uses
`/skill-name` and reads `SKILL.md:disable-model-invocation`. For the selected
pin, setup, Wayfinder, Teach, to-spec, to-tickets, implement, and triage are
user-only on both supported hosts. Research, TDD, Code Review, grilling,
domain-modeling, prototype, and codebase-design remain implicitly invocable.
The provider manager verifies required invocation metadata after installation
and rejects a provider execution claim when that metadata disagrees with the
declaration.

Claude Code discovers project skills from `.claude/skills`, not the installed
`.agents/skills` location. The root `CLAUDE.md` import makes framework policy
available to Claude Code but does not project either the four local workflow
skills or the provider directories into its native discovery path. Every
provider execution is therefore unavailable on Claude Code for this release;
normal host-native handling remains available. See the official
[Codex skills guide](https://learn.chatgpt.com/docs/build-skills),
[GitHub Copilot CLI reference](https://docs.github.com/en/copilot/reference/copilot-cli-reference/cli-command-reference),
[VS Code agent skills guide](https://code.visualstudio.com/docs/agent-customization/agent-skills),
and [Claude Code skills guide](https://code.claude.com/docs/en/skills).

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
initial adoption or a provider-baseline change. Interactive login follows the
official [`gh auth login`](https://cli.github.com/manual/gh_auth_login) web flow;
automation may use `GH_TOKEN`.

## Compatibility and update contract

The provider declaration records repository, stable tag, minimum GitHub CLI
version, capability mapping, skill paths, invocation policy, and configuration
requirements. Installation validates required repository/path/ref and
invocation metadata, then records checksums of the bytes that GitHub CLI actually
installed. Those hashes detect later local modifications. Fresh adoption
rejects any same-named directory without provider ownership state rather than
adopting or overwriting it.

Normal framework update does not float provider versions. A future provider
upgrade requires review of a new stable tag, live exact-path installation
checks, hermetic lifecycle tests, manifest refresh, and a framework release. On
a declaration change, target update uses local provider state as the ownership
and cleanliness baseline. Every present directory is checked against its
recorded installed-file SHA-256 values before staging.

Retained exact matches preserve their existing origin; missing declared skills
are added. Changed provider bytes are replaced only for checksum-clean
directories recorded as framework-created or reconstructed. Modified,
pre-existing-compatible, unknown, partial, and inconsistent directories are
preserved, and conflicts are reported before mutation. New provider bytes are
staged and validated before applying a transition. A missing managed directory
is also recreated during a same-baseline update. Removal remains bounded to
local provider-state ownership and preserves pre-existing, reconstructed,
incompatible, modified, and extra-file skills.

The repository-local origin and installed-hash records are historical ownership
evidence, not a tamper-evident trust anchor. Coordinated state forgery can
reclassify a provider directory or its bytes. Ordinary edits remain protected
by recorded-hash comparison, while extra files remain outside the recorded
installed inventory.

## Recommendation

Adopt the selected pinned provider set and retain only the framework behaviors
that are genuinely project-specific. This provides the clearest responsibility
boundary: upstream owns mature workflow methodology and native artifacts;
Agentic Workflow owns routing, pinning, safe lifecycle, authorization,
continuity pointers, and acceptance/integration verification.
