# Provider evaluation and v0 lifecycle

## Purpose

Providers supply replaceable methods after the router selects a capability.
They do not select routes, grant action authorization or project decision
authority, define project-state safety, or control framework lifecycle.
The v0 objective is therefore compatibility and truthful fallback, not a second
package manager.

## Current reviewed provider

The declaration in
`skills/agent-workflow/payload/agent-workflow/providers.json` currently names
`mattpocock/skills` at tag `v1.2.3`, resolved and recorded as commit
`6acc160e4e0cd062dbbbd7a1b26ae92855edf07e`. It maps planning, learning,
research, specification, tickets, implementation, TDD, and Code Review
capabilities to upstream skills while retaining provider-native names,
invocation policies, and configuration requirements.

Codex and GitHub Copilot discover these project skills under `.agents/skills`.
Setup, Teach, and Triage remain user-only and require exact `$skill-name` or
`/skill-name` invocation. Agent Workflow adapts Wayfinder, To Spec, To
Tickets, and Implement for implicit invocation because they are normal router
destinations. Claude does not receive a `.claude/skills` provider-skill
projection in this
release, so the router uses host-native fallback there.

Wayfinder carries a method-body adaptation for Agent Workflow's framework-owned
runtime and the project's configured local Wayfinder representation. Research
carries a narrow output-policy adaptation: sourced findings return in chat by
default, standalone research files require an explicit user request, adopted
evidence goes directly to the ADR or product documentation designated to
maintain that lasting result, and raw research notes are never written into the
repository.
To Spec, To Tickets, and Implement need only an activation-metadata overlay;
their upstream method bodies remain unchanged.

### Invocation portability boundary

The portable [Agent Skills specification](https://agentskills.io/specification)
standardizes the `SKILL.md` directory, required `name` and `description`, and a
small set of optional fields. It does not standardize whether a model may select
a skill automatically. Its client implementation guide mentions filtering a
skill that opts out of model-driven activation only as an implementation
example. Invocation policy is therefore a host contract, not a portable
Agent Skills guarantee.

The reviewed provider carries both host controls needed by the currently
available provider projections:

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
  `/skill-name` invocation. Agent Workflow does not currently project provider
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

The local framework retains only materially distinct boundaries:

- bounded Discovery for local consequential choices;
- diagnosis-only Debugging;
- an Implementation integration that supplies accepted project context without
  copying the provider's method; and
- Verification for project acceptance and integration evidence.

The provider `implement` skill is responsible for its TDD and closing Code
Review stages. The framework does not mechanically repeat them.

The declared inventory also includes the provider's reviewed composition
dependencies. In particular, Wayfinder may delegate to `grilling`,
`domain-modeling`, and `prototype`; implementation composition uses `tdd`,
`code-review`, and `codebase-design`; and `triage` supports setup, specification,
and ticket workflows. A supported-host provider projection is complete only
when every declared directory is usable in `.agents/skills/`.

Wayfinder v1.2.3 defines a low-resolution map with Destination, Notes, Decisions
so far, Not yet specified, and Out of scope; it loads child decision tickets on
demand and derives the frontier from open, unblocked, unclaimed children. Its
default local-Markdown tracker stores those artifacts below `.scratch/`.
Agent Workflow deliberately maintains its framework-owned runtime, while the
project maintains its designated local representation under `.agent-wayfinder/`.
When resuming an effort, it reads the map first
and then only relevant optional U#/E#/F#/D# knowledge. The map summarizes current
coordination state, conditions blocking particular work, dependencies, and ready
work. Before detailed decomposition, the map may state ready work directly.
Substantial decomposition passes to the provider-native `to-tickets` ticket
artifact or ticket set, which maintains ticket contents, dependencies, ordering,
and readiness; the map links it without a shadow copy. The pinned release remains the
methodological source with reviewed provider provenance, while the local runtime
is an intentional derived runtime projection; see
[ADR-0010](../architecture-decisions/0010-separate-framework-output-from-project-owned-state.md)
and [ADR-0011](../architecture-decisions/0011-use-map-first-wayfinder-state.md).

The pinned upstream Wayfinder metadata disables model invocation in `SKILL.md`
and `agents/openai.yaml`, while its discovery descriptions retain the upstream
“huge, more than one session” threshold. During release-local staging,
`providers.py` applies the declared Wayfinder adapter. It requires the pinned
method-body fingerprint and source metadata, changes the four known invocation/
selection scalars, and replaces the upstream body with the package-owned runtime
source. Unrecognized bundled input or malformed framework-owned runtime instructions fail before
target mutation. The raw snapshot remains unchanged. Future upstream upgrades
are reviewed and useful method improvements are selectively ported rather than
automatically inherited.

Research uses the same pinned-input principle through
`research-chat-output-v1`. The adapter verifies the reviewed upstream method
body and source metadata, then projects the package-owned chat-first output
contract without modifying the bundled snapshot. Missing, changed, or malformed
input fails before provider mutation.

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
source metadata, and adapter preconditions needed for the installed provider
projection, then compares each effective directory with the target. The
maintainer gate—not end-user
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
quarantine copies. The finite declaration defines the lifecycle-managed set:
lifecycle may replace and remove those exact directories, while all other skill
names are preserved. The declared provider projection is reconstructable from
the current declaration; edits inside a declared directory are replaceable
rather than preserved as unique project information.

Implement and Code Review do not require issue-tracker configuration merely to
run. They can consume a supplied or repository-local specification, and Code
Review can explicitly report that no specification is available. To Spec and
To Tickets retain their issue-tracker prerequisite because publishing tracker
artifacts is their purpose.

## Selection and fallback

Provider availability does not determine routing. The router selects a
capability from intent, then resolves its provider. Host support, invocation
policy, configuration readiness, installed provider-projection status, and
host-native fallback remain distinct checks:

- `implicit`: the host may execute the installed skill normally;
- `user-only`: exact explicit invocation is required; and
- `unavailable`: do not claim provider execution.

When an optional provider is absent or cannot run, continue with normal
host-native capability and report the fallback when material. Stop with an exact
invocation instruction only when the user explicitly required that provider or
an actual
configuration/safety boundary prevents fallback.

Provider instructions grant neither action authorization nor project decision
authority. Host permission may technically allow an operation, but neither it
nor upstream text provides action authorization for commits, publication,
tracker mutation, setup writes, or a broader external scope, and neither commits
a project choice.

## Upgrade evaluation

A provider pin change is a source release decision, not an automatic target
upgrade. Generate a candidate outside the package with
`python3 skills/agent-workflow/scripts/refresh_provider_snapshot.py <output>`;
the maintainer-only command verifies that the annotated tag still resolves to
the declared commit, that the root and each installed skill tree belong to that
commit, and that referenced local resources stay within each selected skill
directory. It refuses to write a candidate inside the package.
Before replacing the checked-in snapshot:

1. inspect the maintained upstream release and upstream-native metadata;
2. compare the declared capability, invocation, and configuration contract;
3. verify that framework routing does not duplicate provider-defined stages;
4. review the generated inventory, license, checksum, and adapter compatibility;
5. update the declaration provenance, reviewed verifier identity, license hash,
   and snapshot checksum together;
6. run the repository release gate and temporary-project provider smoke tests;
7. document any user-visible compatibility change; and
8. verify that target update converges existing declared directories safely.

Live upstream/network validation must be reported as live evidence. Hermetic
fixtures prove only the local command and fallback boundaries.

## Deferred capabilities

Install/origin tracking beyond the declaration and multi-provider resolution are
deferred. Add one only after a concrete failure
shows it is necessary for project data safety or reliable routing and simpler
host/provider mechanisms are insufficient.
