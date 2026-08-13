# Official Codex, GitHub Copilot, and VS Code platform research

Inspected 2026-08-12 against current official VS Code and GitHub documentation.
The framework is Codex-first; this file evaluates how much of the repository
workflow can be reused by local GitHub Copilot in VS Code without a duplicate
policy or skill tree. It records documented support, not a live-session claim.

Primary Codex evidence is recorded separately in
[codex-research.md](codex-research.md), including `AGENTS.md`,
`.agents/skills` Agent Skills, native Subagents, app-server, sandbox, and
approvals. This file focuses on the Copilot portability delta.

## Feature status and design consequence

| Primitive | Status observed | Official source | Framework decision |
|---|---|---|---|
| Root `AGENTS.md` | Supported as an automatically applied workspace instruction; root support is stable/enabled by default, while nested files remain experimental | [VS Code custom instructions](https://code.visualstudio.com/docs/agent-customization/custom-instructions), [VS Code AI settings](https://code.visualstudio.com/docs/agents/reference/ai-settings) | Use the same compact root file as Codex. Do not create a framework `.github/copilot-instructions.md` duplicate or depend on nested precedence. |
| Agent Skills | Supported project locations include `.github/skills`, `.claude/skills`, and `.agents/skills`; skill metadata, bodies, and resources load progressively | [VS Code Agent Skills](https://code.visualstudio.com/docs/agent-customization/agent-skills), [VS Code 1.109](https://code.visualstudio.com/updates/v1_109), [GitHub Agent Skills](https://docs.github.com/en/copilot/how-tos/copilot-on-github/customize-copilot/customize-cloud-agent/add-skills) | Use only the canonical `.agents/skills/<name>/SKILL.md` tree shared with Codex. No `.github/skills` mirror is needed. |
| Skills as slash commands | Skills appear in the `/` menu by default and can also be selected semantically from their descriptions | [VS Code Agent Skills](https://code.visualstudio.com/docs/agent-customization/agent-skills#_use-skills-as-slash-commands) | The seven `workflow-*` skills provide an explicit fallback when automatic matching is uncertain. The Hermes skill may be discoverable, but Codex-parent delegation is not part of the Copilot subset. |
| Multiple instruction files | VS Code combines applicable instruction files and does not guarantee an order within the same category | [VS Code custom instructions](https://code.visualstudio.com/docs/agent-customization/custom-instructions#_types-of-instruction-files) | The framework owns only root `AGENTS.md`. A consuming project's existing Copilot-specific instructions remain project-owned and should be reviewed for conflict rather than copied into another framework tree. |
| File instructions | Stable conditional `*.instructions.md` support | [VS Code custom instructions](https://code.visualstudio.com/docs/agent-customization/custom-instructions) | Not required; focused Agent Skills provide the workflow loading boundary. |
| Forked skill context | Experimental and separately enabled | [VS Code Agent Skills](https://code.visualstudio.com/docs/agent-customization/agent-skills#_run-a-skill-in-a-forked-context-experimental) | Do not use `context: fork`; it is not a portable substitute for native Codex subagents. |
| Subagents | VS Code has host-specific subagent behavior and an experimental skill-fork path | [VS Code subagents](https://code.visualstudio.com/docs/agents/agents-and-tools#_subagents), [VS Code Agent Skills](https://code.visualstudio.com/docs/agent-customization/agent-skills#_run-a-skill-in-a-forked-context-experimental) | Do not require it for the Copilot subset or describe it as equivalent to native Codex subagents. |
| Custom agents and handoffs | Supported in VS Code; hooks and some related features have narrower or preview status, and handoffs are UI behavior | [VS Code custom agents](https://code.visualstudio.com/docs/agent-customization/custom-agents), [GitHub custom-agent configuration](https://docs.github.com/en/copilot/reference/custom-agents-configuration) | No custom agent is required. UI handoffs do not replace durable repository state. |
| Prompt files | Optional surface with differing availability across hosts | [VS Code prompt files](https://code.visualstudio.com/docs/agent-customization/prompt-files), [GitHub IDE instructions](https://docs.github.com/en/copilot/how-tos/configure-custom-instructions-in-your-ide/add-repository-instructions-in-your-ide?tool=vscode) | No prompt-file dependency; the seven workflow skills are the explicit interface. |
| Agent plugins | Supported packaging surface, but `chat.plugins.enabled` defaults to false and marketplace/local-location settings retain experimental status | [VS Code Agent Plugins](https://code.visualstudio.com/docs/agent-customization/agent-plugins), [VS Code AI settings](https://code.visualstudio.com/docs/agents/reference/ai-settings#_agent-plugins-settings) | Do not add a plugin to this MVP. Plain repository files remain simpler; plugins are only a future packaging option after an explicit distribution decision. |
| Agent Host | Active VS Code agent architecture with its own tool and session behavior | [VS Code Agent Host architecture](https://code.visualstudio.com/docs/agents/concepts/agent-host) | Reuse host-neutral policy and skills, but do not claim Codex sandbox, approval, or subagent equivalence. |
| Permissions and approvals | VS Code applies its own tool-permission and approval controls | [VS Code approvals and permissions](https://code.visualstudio.com/docs/agents/agent-tools#_tool-approval) | The shared command-safety policy still applies, but it cannot replace or weaken the host controls and is not evidence of a Codex-equivalent sandbox. |
| Customizations and diagnostics | VS Code exposes customization inspection and Chat Diagnostics; some debug views remain preview | [Customization overview](https://code.visualstudio.com/docs/agent-customization/overview), [Agent troubleshooting](https://code.visualstudio.com/docs/agents/agent-troubleshooting/troubleshooting) | Use diagnostics for live discovery verification; repository tests cannot prove a signed-in client loaded or followed the policy. |

## Portable subset

The supported Copilot subset consists of:

- the compact workflow and safety policy in root `AGENTS.md`;
- the seven Discovery, Teach, Decomposition, Implementation, Debugging,
  Verification, and Review skills under `.agents/skills`;
- project facts and configured commands in
  `ai-workflow/project-profile.md`;
- durable resumption and accepted records under `ai-workflow/state`; and
- the same rule that checks run, skipped checks, unavailable checks, and blocked
  checks are reported separately.

Copilot supplies its own agent loop, permissions, tools, and session semantics.
The portable subset does not promise native Codex subagents, Codex sandbox or
approval behavior, Codex app-server, or the Codex-parent Hermes adapter path.
Hermes may remain entirely absent without affecting the seven core workflows.
Because `.agents/skills` is shared, Copilot may still discover the optional
Hermes skill; its root and skill contracts explicitly stop instead of invoking
the Codex-parent adapter in that host. Discovery is not an execution claim.

## Relevant conventions and caveats

- `AGENTS.md` must be at the consuming workspace root for the stable shared
  behavior used here. Nested `AGENTS.md` discovery is not a framework dependency.
- Each skill uses `.agents/skills/<skill-name>/SKILL.md`; its frontmatter `name`
  matches the lowercase/hyphen directory, and its description states both
  capability and trigger conditions.
- Project skills live in `.github/skills`, `.claude/skills`, or `.agents/skills`;
  personal skills live in `~/.copilot/skills`, `~/.claude/skills`, or
  `~/.agents/skills`. This framework installs only project-scoped `.agents/skills`.
- Personal instructions outrank repository instructions, which outrank
  organization instructions. A live diagnostic must therefore inspect all
  applicable sources rather than assuming repository policy is the only input.
- VS Code loads a selected skill progressively: metadata first, then the body,
  then referenced resources. The framework therefore keeps detailed procedures
  out of always-on policy.
- `chat.useCustomizationsInParentRepositories` defaults to false. Adopt directly
  into the repository opened as the workspace root rather than relying on a
  parent repository's files.
- An existing project `.github/copilot-instructions.md` may coexist with root
  `AGENTS.md`, but both can enter the same request and ordering is not guaranteed.
  Keep project-specific content narrow and reconcile contradictory policy. The
  framework does not create, overwrite, or synchronize that `.github` file.
- Referencing another instruction file from `AGENTS.md` does not guarantee it is
  automatically included on every turn. Agent Skills are the intentional
  conditional-loading mechanism.
- No `.vscode/settings.json` override is required for the documented default
  root and skill locations.

## Live discovery verification

Official diagnostics have a running-session component that a repository-only
script cannot prove. Open the consuming repository root in a current stable VS
Code release with a signed-in GitHub Copilot Chat session. This is a read-only
client check:

1. Right-click Chat and choose **Diagnostics**.
2. Confirm root `AGENTS.md` and the `.agents/skills` entries are listed without
   load or frontmatter errors.
3. Type `/` and confirm the seven `workflow-*` skills appear.
4. Send a fresh bounded request and inspect Chat **References** for the root
   policy and the expected selected skill.
5. If discovery fails, use **Developer: Open Agent Debug Panel** or Chat's
   **Show Agent Debug Logs**, then check workspace root, trust, paths,
   frontmatter names, and the relevant customization settings.

This development workspace did not contain a signed-in Copilot extension, so
the above discovery and semantic-routing behavior remains unverified here. The
static verifier confirms file structure and contracts only. It does not convert
officially documented compatibility into a live test result.

## Relationship to Codex and Hermes research

Codex is the primary supported runtime; its official primitives and local
observations are recorded in [codex-research.md](codex-research.md). Hermes is an
optional Codex-owned research adapter with a separately pinned source audit,
private-learning boundary, and unavailable v0.20.0 `repo-read` gate documented
in [integrations/hermes.md](integrations/hermes.md). Neither optional Copilot use
nor Hermes availability changes the core repository policy or creates another
skill tree.
