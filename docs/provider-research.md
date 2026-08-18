# Provider evaluation and v0 lifecycle

## Purpose

Providers supply replaceable methods after the router selects a capability. They
do not own routing, authorization, project-state safety, or framework lifecycle.
The v0 objective is therefore compatibility and truthful fallback, not a second
package manager.

## Current reviewed provider

The declaration in
`skills/agentic-workflow/payload/agent-workflow/providers.json` currently names
`mattpocock/skills` at tag `v1.2.3`, resolved and recorded as commit
`6acc160e4e0cd062dbbbd7a1b26ae92855edf07e`. It maps planning, learning,
research, specification, tickets, implementation, TDD, and Code Review
capabilities to upstream skills while retaining provider-native names,
invocation policies, and configuration requirements.

Codex and GitHub Copilot discover these project skills under `.agents/skills`.
Setup, Teach, and Triage remain user-only and require exact `$skill-name` or
`/skill-name` invocation. Agentic Workflow adapts Wayfinder, To Spec, To
Tickets, and Implement for implicit invocation because they are normal router
destinations. Claude does not receive a `.claude/skills` projection in this
release, so the router uses host-native fallback there.

Wayfinder also carries a method-body adaptation for Agentic Workflow's canonical
local state. The other three routed skills need only an activation-metadata
overlay: their upstream method bodies remain unchanged.

### Invocation portability boundary

The portable [Agent Skills specification](https://agentskills.io/specification)
standardizes the `SKILL.md` directory, required `name` and `description`, and a
small set of optional fields. It does not standardize whether a model may select
a skill automatically. Its client implementation guide mentions filtering a
skill that opts out of model-driven activation only as an implementation
example. Invocation ownership is therefore a host contract, not a portable
Agent Skills guarantee.

The reviewed provider carries both host controls needed by the currently
available projections:

- Codex reads `agents/openai.yaml` as product-specific machine/harness metadata.
  `policy.allow_implicit_invocation: false` keeps the skill out of implicit
  model context while preserving explicit `$skill-name` invocation. The other
  current `interface` fields are presentation metadata, while `dependencies`
  can declare MCP requirements. See the
  [Codex source reference](https://github.com/openai/codex/blob/main/codex-rs/skills/src/assets/samples/skill-creator/references/openai_yaml.md)
  and [Codex skill documentation](https://developers.openai.com/codex/skills).
- GitHub Copilot in VS Code reads `disable-model-invocation` from `SKILL.md`.
  `true` keeps the slash command available but sets automatic loading to no.
  The [VS Code Agent Skills documentation](https://code.visualstudio.com/docs/agent-customization/agent-skills)
  documents `.agents/skills`, this field, and explicit `/skill-name` invocation;
  the [Copilot CLI reference](https://docs.github.com/en/copilot/reference/copilot-cli-reference/cli-command-reference)
  documents the same field and default independently.
- Claude Code documents the same `disable-model-invocation` spelling as a
  Claude Code extension that hides a user-only skill from Claude until explicit
  `/skill-name` invocation. Agentic Workflow does not currently project provider
  skills to `.claude/skills`, so this release still marks provider execution
  unavailable there rather than claiming that retained frontmatter alone makes
  the provider available. See the
  [Claude Code skills documentation](https://code.claude.com/docs/en/skills).

This evidence establishes the required explicit-only behavior for Codex and
GitHub Copilot VS Code/CLI at the documented host boundary. It does not prove a
live editor/model run, and the GitHub cloud-agent and code-review documentation
does not separately state how `disable-model-invocation` is enforced for skills.
Do not generalize the VS Code/CLI evidence into a live claim for every Copilot
surface. Changing the model selected inside Copilot does not change the
documented host metadata contract; treating that as identical live behavior
across models remains an inference until the matrix is exercised.

The detailed evidence, artifact inventory, compatibility table, and manual
matrix procedure live in
[Host invocation portability research](host-invocation-portability-research.md).

The local framework retains only materially distinct boundaries:

- bounded Discovery for local consequential decisions;
- diagnosis-only Debugging;
- an Implementation adapter that supplies accepted project context without
  copying the provider's method; and
- Verification for project acceptance and integration evidence.

The provider `implement` skill owns its TDD and closing Code Review stages. The
framework does not mechanically repeat them.

The declared inventory also includes the provider's reviewed composition
dependencies. In particular, Wayfinder may delegate to `grilling`,
`domain-modeling`, and `prototype`; implementation composition uses `tdd`,
`code-review`, and `codebase-design`; and `triage` supports setup, specification,
and ticket workflows. A supported-host projection is complete only when every
declared directory is usable in `.agents/skills/`.

Wayfinder v1.2.3 defines a low-resolution map with Destination, Notes, Decisions
so far, Not yet specified, and Out of scope; it loads child decision tickets on
demand and derives the frontier from open, unblocked, unclaimed children. Its
default local-Markdown tracker stores those artifacts below `.scratch/`.
Agentic Workflow deliberately configures its canonical local representation
under `.agent-workflow-state/wayfinder/` instead, with the map itself as the
re-entry point and optional U#/E#/F#/D# knowledge. The map owns current state,
blockers, dependencies, and next work. Substantial decomposition passes to the
native `to-tickets` output without a shadow copy. Older T# state requires manual
map migration before resume. This is a storage, re-entry, and item-lifecycle
adaptation, not a copied planning method or provider fork; see ADR-0011,
ADR-0020, and ADR-0022.

The pinned upstream Wayfinder metadata disables model invocation in `SKILL.md`
and `agents/openai.yaml`, while its discovery descriptions retain the upstream
“huge, more than one session” threshold. During release-local staging,
`providers.py` applies the declared Wayfinder adapter. It
inserts an authoritative local-mode section before the unchanged method body
and changes the four known invocation/selection scalars. It requires the pinned
method-body fingerprint, source metadata, and exact upstream or already-adapted
values; unknown bundled input fails before target mutation. This
makes the policy and configured local mechanics durable without rewriting the
upstream method.

To Spec, To Tickets, and Implement use the narrower
`implicit-invocation-v1` adapter. Release-local staging accepts
exactly one upstream or already-adapted activation scalar in each host metadata
file, rewrite upstream user-only values to implicit values, and reject missing,
duplicated, or unexpected values before projecting a partial provider set. The
adapter verifies pinned source metadata and does not alter the provider method
body. Setup, Teach, and Triage retain their upstream user-only metadata.

## Installation policy

After core reconciliation succeeds, `providers.py` stages the bundled 14-skill
snapshot, validates the inventory, safe filesystem shape, local references,
source metadata, and adapter preconditions needed for projection, then compares
each effective directory with the target. The maintainer gate—not end-user
lifecycle—validates the declared checksum, provenance, and MIT license against
the reviewed release identity. Runtime setup is fully offline and requires no
provider installer or package manager.

Exact existing directories are reused. Missing or different declared
directories are repairable and replaced from same-filesystem staging as one
small transaction; an unsafe declared path blocks the whole change. Status
performs the same comparison without target writes; lifecycle continues to
report core health separately. Unrelated skill directories are never included
in the transaction. A post-commit recovery-directory cleanup failure reports a
warning and its exact path without falsely claiming the target mutation failed.

The framework records no target origin states, installed-file history, or
quarantine copies. The finite declaration is the ownership proof: lifecycle
may replace and remove those exact directories, while all other skill names are
preserved. Edits inside a declared directory are disposable.

Implement and Code Review do not require issue-tracker configuration merely to
run. They can consume a supplied or repository-local specification, and Code
Review can explicitly report that no specification is available. To Spec and
To Tickets retain their issue-tracker prerequisite because publishing tracker
artifacts is their purpose.

## Selection and fallback

Provider availability does not determine routing. The router selects a capability
from intent, then resolves whether the active host can invoke its provider:

- `implicit`: the host may execute the installed skill normally;
- `user-only`: exact explicit invocation is required; and
- `unavailable`: do not claim provider execution.

When an optional provider is absent or cannot run, continue with normal
host-native capability and report the fallback when material. Stop with an exact
handoff only when the user explicitly required that provider or an actual
configuration/safety boundary prevents fallback.

Provider instructions never expand user authorization. In particular, upstream
text cannot authorize commits, publication, tracker mutation, setup writes, or a
broader external scope.

## Upgrade evaluation

A provider pin change is a source release decision, not an automatic target
upgrade. Generate a candidate outside the package with
`python3 skills/agentic-workflow/scripts/refresh_provider_snapshot.py <output>`;
the maintainer-only command verifies that the annotated tag still resolves to
the declared commit, that the root and each installed skill tree belong to that
commit, and that referenced local resources stay within each selected skill
directory. It refuses to write a candidate inside the package.
Before replacing the checked-in snapshot:

1. inspect the maintained upstream release and native metadata;
2. compare the declared capability, invocation, and configuration contract;
3. verify that framework routing does not duplicate provider-owned stages;
4. review the generated inventory, license, checksum, and adapter compatibility;
5. update the declaration provenance, reviewed verifier identity, license hash,
   and snapshot checksum together;
6. run the repository release gate and temporary-project provider smoke tests;
7. document any user-visible compatibility change; and
8. verify that target update converges existing declared directories safely.

Live upstream/network validation must be reported as live evidence. Hermetic
fixtures prove only the local command and fallback boundaries.

## Deferred capabilities

Ownership tracking beyond the declaration and multi-provider resolution are
deferred. Add one only after a concrete failure
shows it is necessary for project data safety or reliable routing and simpler
host/provider mechanisms are insufficient.
