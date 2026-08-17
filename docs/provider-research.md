# Provider evaluation and v0 lifecycle

## Purpose

Providers supply replaceable methods after the router selects a capability. They
do not own routing, authorization, project-state safety, or framework lifecycle.
The v0 objective is therefore compatibility and truthful fallback, not a second
package manager.

## Current reviewed provider

The declaration in
`skills/agentic-workflow/payload/ai-workflow/providers.json` currently names
`mattpocock/skills` at immutable tag `v1.2.3`. It maps planning, learning,
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
under `.ai-workflow-state/wayfinder/` instead, with stable U#/D#/T# children and
the map itself as the re-entry point. Decision and investigation questions map
to U#, durable project choices map to D#, and concrete executable work maps to
T# only when it exists. This is a storage, re-entry, and item-lifecycle
adaptation, not a copied planning method or provider fork; see ADR-0011 and
ADR-0015.

The pinned upstream Wayfinder metadata disables model invocation in `SKILL.md`
and `agents/openai.yaml`, while its discovery descriptions retain the upstream
“huge, more than one session” threshold. After a fresh install or during a later
lifecycle update, `providers.py` applies the declared Wayfinder adapter. It
inserts an authoritative local-mode section before the unchanged method body
and changes the four known invocation/selection scalars. It requires the pinned
method-body fingerprint, source metadata, and exact upstream or already-adapted
values; unknown or modified content is preserved without a partial write. This
makes the policy and configured local mechanics durable without vendoring or
rewriting the upstream method.

To Spec, To Tickets, and Implement use the narrower
`implicit-invocation-v1` adapter. Fresh installation and later updates accept
exactly one upstream or already-adapted activation scalar in each host metadata
file, rewrite upstream user-only values to implicit values, and reject missing,
duplicated, or unexpected values before projecting a partial provider set. The
adapter verifies pinned source metadata and does not alter the provider method
body. Setup, Teach, and Triage retain their upstream user-only metadata.

## Installation policy

After core reconciliation succeeds, `providers.py` inspects declared destination
names. It stages every currently missing exact path with `gh skill install` at
the reviewed repository pin, validates the complete missing inventory and host
metadata, applies declared adapters, then projects the staged directories
together. Existing same-named directories, including incompatible or partially
installed ones, are preserved.

Provider installation is best-effort. Missing GitHub CLI support, authentication,
network access, or an upstream install failure yields a warning while the core
router and local workflows remain ready. A failed attempt commits none of the
missing set. Update retries the missing set and safely reconciles declared
provider adapters on present directories. Status returns an incomplete provider
result while any declared skill is missing, incompatible, or awaiting an
adapter; lifecycle continues to report core health separately.

The framework records no provider hashes, provenance history, origin states,
quarantine copies, or update transaction. Remove never deletes provider
directories automatically. A user who wants provider cleanup inspects and
removes the corresponding `.agents/skills/<name>` path manually. This deliberate
limitation prevents v0 lifecycle code from claiming ownership it cannot prove.

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
upgrade. Before changing it:

1. inspect the maintained upstream release and native metadata;
2. compare the declared capability, invocation, and configuration contract;
3. verify that framework routing does not duplicate provider-owned stages;
4. run the repository release gate and temporary-project provider smoke tests;
5. document any user-visible compatibility change; and
6. keep existing provider directories preserved during target updates.

Live upstream/network validation must be reported as live evidence. Hermetic
fixtures prove only the local command and fallback boundaries.

## Deferred capabilities

Automatic provider upgrades, integrity inventories, rollback, removal, and
multi-provider resolution are deferred. Add one only after a concrete failure
shows it is necessary for project data safety or reliable routing and simpler
host/provider mechanisms are insufficient.
