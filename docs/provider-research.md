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
Some are user-only and require exact `$skill-name` or `/skill-name` invocation.
Claude does not receive a `.claude/skills` projection in this release, so the
router uses host-native fallback there.

Wayfinder is the intentional exception to its upstream v1.2.3 invocation
policy. Agentic Workflow preserves the provider's planning methodology but
permits implicit invocation because Agentic Workflow owns workflow routing. The
declaration marks Wayfinder implicit for Codex and GitHub Copilot and unavailable
for Claude.

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

The pinned upstream metadata disables model invocation in `SKILL.md` and
`agents/openai.yaml`, while its discovery descriptions retain the upstream
“huge, more than one session” threshold. After a fresh install or during a later
lifecycle update, `providers.py` applies the declared Wayfinder adapter. It
inserts an authoritative local-mode section before the unchanged method body
and changes the four known invocation/selection scalars. It requires the pinned
method-body fingerprint, source metadata, and exact upstream or already-adapted
values; unknown or modified content is preserved without a partial write. This
makes the policy and configured local mechanics durable without vendoring or
rewriting the upstream method.

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
