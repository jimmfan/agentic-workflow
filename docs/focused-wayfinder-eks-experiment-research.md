# Focused Wayfinder EKS experiment preparation research

- Date researched: 2026-08-21
- Agentic Workflow branch: `wayfinder-replace`
- Branch revision examined: `1ac833d08640ff5eb5246355273c4105fb40e5bf`
- Scope: Phase 1 focused VS Code Wayfinder projection, canonical dependencies,
  consuming-project installation, and live-host executability from the current
  Codex environment

## Practical conclusion

The Phase 1 focused Wayfinder is implemented as a thin VS Code repository custom
agent, not a second Wayfinder implementation. It references the same installed
canonical Wayfinder runtime and state contract used by the general-agent route.
The distributable package installs all three pieces: the custom-agent wrapper,
the state contract, and the provider-projected Wayfinder skill. Therefore a fair
A/B preparation should install the exact same Agentic Workflow package into both
frozen EKS copies and vary only the selected VS Code agent: general Agent mode
for A, `Wayfinder` for B.

The source repository records Phase 1 as implemented and deterministically
verified, but explicitly says no live VS Code baseline-versus-focused run has
occurred. This Codex environment can inspect the VS Code CLI, but it does not
provide an interactive/capturable VS Code Copilot chat surface, and the installed
extension inventory does not list GitHub Copilot. The actual custom-agent
condition should consequently be run manually in VS Code rather than simulated
here.

## Evidence labels

- **Repository fact**: directly established by a versioned source, contract,
  decision, manifest, or project-owned state file in this checkout.
- **Environment observation**: observed from a read-only command in the current
  execution environment.
- **Inference**: an experimental or operational conclusion drawn from those
  facts and observations.

## 1. Current Phase 1 state

- **Repository fact.** `wayfinder-replace` currently points at commit
  `1ac833d08640ff5eb5246355273c4105fb40e5bf`. The package and payload versions
  are both `0.19.1`. The installed manifest also reports framework version
  `0.19.1`, although this source checkout was installed from the local package
  and therefore records `unreleased-local-package` rather than the Git commit as
  its own installed source revision. Sources: `git rev-parse HEAD`,
  [`skills/agentic-workflow/VERSION`](../skills/agentic-workflow/VERSION),
  [`skills/agentic-workflow/payload/VERSION`](../skills/agentic-workflow/payload/VERSION),
  and [the installed manifest](../.agent-workflow/install-manifest.json#L27-L38).
- **Repository fact.** ADR-0030 accepts one thin custom agent at
  `.github/agents/wayfinder.agent.md`. It keeps the portable runtime and state
  contract canonical, adds no automatic handoff, allows only `read`, `search`,
  `edit`, and `execute`, and disables subagent invocation. It also says no
  baseline-versus-focused conclusion exists until both conditions run in a live
  host. Source: [ADR-0030](../architecture-decisions/0030-use-thin-focused-vscode-wayfinder-projection.md#L22-L59)
  and its [live-run limitation](../architecture-decisions/0030-use-thin-focused-vscode-wayfinder-projection.md#L61-L78).
- **Repository fact.** The current effort map says the custom agent, hook, and
  distributable artifacts are synchronized and the deterministic gate passed,
  but the behavioral hypothesis remains inconclusive because no live VS Code
  A/B run was performed. It names a matched general/focused run with model,
  permissions, fixture revision, and evaluator held fixed as the next work.
  Source: [focused projection map](../.agent-workflow-state/wayfinder/focused-wayfinder-vscode-projection/map.md#L28-L64).
- **Repository fact.** The behavioral documentation likewise says the generic
  command runner cannot select a VS Code custom agent and forbids a comparison
  claim until a real host adapter supplies both conditions. Source:
  [Phase 1 comparison contract](behavioral-testing.md#L120-L137).

## 2. What the focused projection carries and derives from

The dependency chain is intentionally short:

```text
.github/agents/wayfinder.agent.md
    ├── references .agents/skills/wayfinder/SKILL.md
    │       └── body projected from runtime-projections/wayfinder.md
    │           over pinned mattpocock/skills Wayfinder metadata
    └── references .agent-workflow/contracts/wayfinder-state.md
```

- **Repository fact.** The VS Code custom agent is a 33-line host wrapper. Its
  frontmatter names `Wayfinder`, targets VS Code, allowlists
  `read/search/edit/execute`, and disables subagents and model invocation. Its
  body directly links the canonical runtime and state contract, adds progressive
  domain-to-detail navigation, preserves evidence/authority distinctions, limits
  terminal use to the mutation-lock lifecycle, and stops at the ready-work
  boundary. Source: [installed focused agent](../.github/agents/wayfinder.agent.md#L1-L33).
- **Repository fact.** The wrapper's packaged source and installed file are
  byte-identical in this checkout (both SHA-256
  `6e76192cccc8399e9ee94cc6bf9a87ca5c3c5229cf0bfd59e45450f58ca949d8`).
  The distribution manifest explicitly maps the former to the latter. Sources:
  [payload agent](../skills/agentic-workflow/payload/agents/vscode-wayfinder.agent.md)
  and [distribution mapping](../skills/agentic-workflow/payload/distribution/manifest.json#L55-L62).
- **Repository fact.** The effective canonical Wayfinder runtime identifies
  Wayfinder as the sole framework-owned durable coordinator, requires routing
  before state inspection, makes `map.md` the low-resolution re-entry point,
  prefers progressive specialist use only when material, distinguishes human
  authority from agent inference, and hands off only coherent ready scopes.
  Source: [installed canonical Wayfinder runtime](../.agents/skills/wayfinder/SKILL.md#L12-L42)
  and [frontier/handoff rules](../.agents/skills/wayfinder/SKILL.md#L99-L138).
- **Repository fact.** The provider declaration pins `mattpocock/skills` at tag
  `v1.2.3` and commit `6acc160e4e0cd062dbbbd7a1b26ae92855edf07e`, and declares the
  `wayfinder-runtime-projection-v1` adapter with
  `runtime-projections/wayfinder.md` as its projection source. Source:
  [provider declaration](../skills/agentic-workflow/payload/agent-workflow/providers.json#L47-L85).
- **Repository fact.** Provider setup first copies the checksummed bundled
  upstream snapshot to staging, validates the expected upstream body hash, then
  replaces the upstream body with the owned runtime projection while preserving
  and adapting pinned provenance/invocation metadata. It validates the effective
  staged result before transactionally reconciling the declared skill
  directories. Source: [adapter validation and rewrite](../skills/agentic-workflow/scripts/providers.py#L281-L397)
  and [staging/reconciliation](../skills/agentic-workflow/scripts/providers.py#L476-L511).
- **Repository fact.** The state contract—not the custom-agent wrapper—owns
  project-native effort identity, progressive loading, `map.md` plus optional
  U/E/F/D files, authority, mutation locking, reconciliation, settlement, and
  lifecycle. It permits `map.md` alone, creates child directories lazily, and
  forbids state writes for read-only work. Source: [state responsibility and
  ownership](../.agent-workflow/contracts/wayfinder-state.md#L18-L33),
  [locations and write threshold](../.agent-workflow/contracts/wayfinder-state.md#L124-L158),
  and [progressive loading](../.agent-workflow/contracts/wayfinder-state.md#L250-L267).
- **Repository fact.** The repository-level hook configuration applies both the
  Phase 0 route-marker reminder and a narrow `PreToolUse` guard. The guard denies
  only an explicit current-shape `apply_patch` deletion of an effort `map.md`;
  ADR-0030 explicitly treats it as defense in depth rather than a filesystem or
  authorization boundary. Sources: [hook configuration](../.github/hooks/agentic-workflow-route-marker.json)
  and [ADR-0030 guard boundary](../architecture-decisions/0030-use-thin-focused-vscode-wayfinder-projection.md#L39-L52).

### A/B consequence

- **Inference.** No Agentic Workflow repository file should differ between A and
  B. Both should contain the custom-agent wrapper, canonical runtime, state
  contract, root policy, hooks, and provider projection produced from the same
  package bytes. A does not select the wrapper and allows the general agent to
  route normally; B explicitly selects the `Wayfinder` custom agent. Removing
  the wrapper from A would add an unnecessary repository-content confound.
- **Inference.** The repository-wide hook is a controlled constant, not part of
  the treatment difference, because it applies in both workspaces. The intended
  treatment is the focused host wrapper and its tool/role restriction.

## 3. Installation/bootstrap path for disposable consuming projects

- **Repository fact.** The supported local lifecycle entrypoint is
  `python3 scripts/lifecycle.py install /path/to/project`; Python 3.11 or newer
  is required. Install/update preflight collisions and symlinks, stage the core
  payload, preserve composite project bytes, replace reconstructable framework
  state, create but never seed `.agent-workflow-state/`, then perform best-effort
  offline provider projection. Source: [bootstrap skill lifecycle contract](../skills/agentic-workflow/SKILL.md#L36-L72).
- **Repository fact.** The distribution manifest installs the state contract to
  `.agent-workflow/contracts/wayfinder-state.md`, the custom agent to
  `.github/agents/wayfinder.agent.md`, the hook configuration to `.github/hooks/`,
  and managed regions into `AGENTS.md` and `CLAUDE.md`. Source:
  [distribution manifest](../skills/agentic-workflow/payload/distribution/manifest.json#L1-L73).
- **Repository fact.** Core lifecycle completes before provider projection;
  provider failure is a warning and leaves core routing usable. Source:
  [`lifecycle.py`](../skills/agentic-workflow/scripts/lifecycle.py#L39-L69).
- **Repository fact.** Core adoption composes only the marked regions of
  `AGENTS.md`/`CLAUDE.md`, creates an empty durable-state directory when absent,
  transactionally writes external integrations, swaps `.agent-workflow/`, and
  verifies desired bytes. Unknown conflicting external content blocks the
  required target instead of being overwritten. Source:
  [`adopt.py` composition/collision rules](../skills/agentic-workflow/scripts/adopt.py#L393-L473)
  and [reconciliation transaction](../skills/agentic-workflow/scripts/adopt.py#L493-L534).
- **Repository fact.** The public bootstrap defaults to `main`, but accepts a
  branch, tag, or full 40-character commit via `--ref`; it resolves non-SHA refs
  to an immutable commit, downloads that archive, validates paths, entry types,
  counts, sizes, and modes, and invokes lifecycle with the resolved revision.
  Source: [`bootstrap.py`](../skills/agentic-workflow/scripts/bootstrap.py#L21-L39),
  [revision resolution](../skills/agentic-workflow/scripts/bootstrap.py#L74-L95),
  and [lifecycle invocation](../skills/agentic-workflow/scripts/bootstrap.py#L190-L243).

### Reproducible preparation recommendation

- **Inference.** For local disposable copies prepared from this checkout, use
  the current package's lifecycle script for both targets and pass the same
  explicit branch commit as `--source-revision`:

  ```bash
  python3 skills/agentic-workflow/scripts/lifecycle.py install /absolute/path/to/A \
    --source-revision 1ac833d08640ff5eb5246355273c4105fb40e5bf
  python3 skills/agentic-workflow/scripts/lifecycle.py install /absolute/path/to/B \
    --source-revision 1ac833d08640ff5eb5246355273c4105fb40e5bf
  ```

  This avoids a network/main-branch confound and records the same immutable
  source identity in both install manifests. It is valid only while the package
  bytes used are the bytes at that commit; verify the source checkout and target
  snapshots before running the chats.
- **Inference.** The public alternative is to run the bootstrap with
  `--ref 1ac833d08640ff5eb5246355273c4105fb40e5bf` against both targets, provided
  that commit remains fetchable from the configured GitHub repository. Do not
  use the bootstrap's default `main` for this branch experiment.

## 4. Can this environment execute the actual VS Code custom agent?

- **Environment observation.** `/opt/homebrew/bin/code` is present and reports
  VS Code `1.133.0`. `code chat --help` accepts `--mode <mode>` and describes the
  mode as `ask`, `edit`, `agent`, or a custom-mode identifier. It is a UI-opening
  command; the help exposes no headless output/transcript option.
- **Environment observation.** `code agent --help` exposes commands for managing
  Agent Host servers and sessions (`host`, `ps`, `stop`, `kill`, `logs`, and
  `endpoints`) but no command for starting a chat turn with a selected repository
  custom agent and capturing its result.
- **Environment observation.** `code --list-extensions --show-versions` returned
  an extension list containing `openai.chatgpt` but neither `github.copilot` nor
  `github.copilot-chat`. The command also reported a sandbox permission error
  while attempting to create a VS Code log directory, so this observation should
  not be generalized beyond this execution environment.
- **Repository fact.** Existing project research explicitly labels live VS Code
  behavior unverified, and the behavioral runner requires a separately
  credentialed host adapter for editor-host behavior. Sources:
  [focused host research](vscode-focused-wayfinder-research.md#L261-L268) and
  [behavioral-test limitations](behavioral-testing.md#L276-L293).
- **Inference.** This Codex session cannot truthfully execute and capture the
  actual B condition. Launching a GUI command would still require a user to
  select/confirm the agent, model, permissions, and chat, and the current tool
  surface cannot capture complete final text, tool calls, file reads, elapsed
  time, and usage as a controlled result. The A and B runs should be performed
  manually in fresh VS Code Copilot chats, preserving the repositories after
  each run for evidence collection.

## Experimental implications

- Freeze the EKS source once, duplicate that exact snapshot, and install the
  exact same Agentic Workflow commit into each copy.
- Keep the custom-agent file present in both copies. Vary only general Agent mode
  versus explicitly selected `Wayfinder` mode.
- Use the exact same model, permissions, prompt, and fresh-chat starting state.
- Treat any missing live telemetry as missing evidence rather than reconstructing
  it from the final prose.
- Do not claim the focused condition ran until VS Code actually selected and
  executed `.github/agents/wayfinder.agent.md`.

## 5. Personalization and memory isolation

- **Documented host fact.** VS Code's preview local memory tool is enabled by
  default, user memory persists across workspaces, and its first 200 lines are
  automatically added to new sessions. The tool can be disabled with
  `chat.tools.memory.enabled`. Source: [VS Code memory documentation](https://code.visualstudio.com/docs/agents/run/memory).
- **Documented host fact.** GitHub-hosted Copilot Memory can contain both
  repository facts and user-level preferences. A user can disable it from
  GitHub **Copilot settings > Features > Copilot Memory** without deleting the
  stored memories. Source: [GitHub personal Copilot Memory controls](https://docs.github.com/en/copilot/how-tos/use-copilot-agents/copilot-memory/manage-for-yourself).
- **Documented host fact.** VS Code can discover user-profile and
  organization-level instruction/customization files. Organization instruction
  and custom-agent discovery can be disabled, parent-repository customization
  discovery has its own setting, and Chat customization diagnostics reports
  loaded customizations and errors. Sources: [VS Code AI settings](https://code.visualstudio.com/docs/agents/reference/ai-settings)
  and [custom-instruction diagnostics](https://code.visualstudio.com/docs/agent-customization/custom-instructions).
- **Inference.** The strongest practical matched setup is one temporary Empty
  VS Code Profile used for both runs, with Settings Sync off, local memory and
  Copilot Memory disabled, organization customizations disabled, and parent
  customization discovery and session-history sync disabled. The profile should contain only the
  Copilot capability required to run the experiment; workspace-owned EKS and
  Agentic Workflow instructions remain intentional inputs.
- **Inference.** Isolation should be audited from Chat customization diagnostics
  and the exported Agent Debug request/context evidence. If a hidden memory or
  preference still appears, the affected run is qualified or invalid rather
  than silently treated as clean. Existing user-owned memories should not be
  deleted merely to prepare a disposable evaluation.
