# VS Code host support for a focused Wayfinder projection

Date researched: 2026-08-21

## Practical conclusion

VS Code can express a thin repository custom agent with a real tool allowlist,
but it cannot express a filesystem-path capability boundary. A repository agent
belongs under `.github/agents`, and its `tools` frontmatter can limit the agent
to named tools or aliases such as `read`, `search`, and `edit`; omitting
`tools` enables all available tools, while `tools: []` disables them all.
[VS Code's custom-agent reference](https://code.visualstudio.com/docs/agent-customization/custom-agents#_custom-agent-file-structure)
and [GitHub's shared custom-agent configuration reference](https://docs.github.com/en/copilot/reference/custom-agents-configuration#tools)
document that boundary.

For Phase 1, the smallest contract-valid capability projection is therefore a
VS Code-targeted `.agent.md` file with an explicit `read`, `search`, `edit`, and
`execute` allowlist. The repository's canonical Wayfinder state contract
requires atomic creation and removal of an empty effort lock directory and says
not to mutate when that operation is unavailable; VS Code documents `execute`
as its shell alias, while `edit` supplies no atomic directory operation. The
projection must therefore constrain terminal use by instruction to the lock
lifecycle, because the host cannot express that narrower capability. This
materially reduces the remaining write surface, but it does not make
`.agent-workflow-state/wayfinder/` a protected path: `edit` remains a broad
editing capability, `execute` remains a general shell capability, and the
supported frontmatter has no path-scoped allow or deny field. This is an
inference from the complete documented frontmatter and tool-filter semantics,
not a separately documented path-ACL guarantee.
[VS Code's field table](https://code.visualstudio.com/docs/agent-customization/custom-agents#_header-optional)
and [GitHub's tool-filter rules](https://docs.github.com/en/copilot/reference/custom-agents-configuration#tools)
are the underlying contracts.

A `PreToolUse` hook is the available deterministic interception point, but
hooks are Preview and do not currently provide a stable, fail-closed filesystem
guard. The narrowest *agent-scoped* form is a `hooks` block in the custom
agent's frontmatter, but it is separately Preview and requires
`chat.useCustomAgentHooks: true`, whose default is `false`. The automatically
loaded repository form is `.github/hooks/*.json`, but that applies to the
workspace rather than only the focused agent and is also consumed by other
Copilot surfaces. There is no documented stable, on-by-default, agent-scoped
hook option today.
[VS Code marks hooks Preview](https://code.visualstudio.com/docs/agent-customization/hooks#_agent-hooks-in-visual-studio-code-preview),
[documents the scopes](https://code.visualstudio.com/docs/agent-customization/hooks#_hook-file-locations),
and [documents the agent-scoped feature gate](https://code.visualstudio.com/docs/agent-customization/hooks#_agent-scoped-hooks).

The guard can reliably deny only the exact current tool names and input shapes
it recognizes, for example an explicit `apply_patch` delete targeting the
protected tree. It should not claim to catch indirect shell writes, new or
extension-contributed write tools, symlink/path indirection, hook launch or
timeout failure, or future schema changes. The current hook contract exposes a
tool-specific `tool_input` rather than a normalized filesystem operation, and
VS Code explicitly directs authors to inspect agent logs for each tool's schema.
[The hook payload reference](https://code.visualstudio.com/docs/agents/reference/hooks-reference#_pretooluse),
[the `updatedInput` guidance](https://code.visualstudio.com/docs/agents/reference/hooks-reference#_pretooluse-output),
and [the current built-in tool declarations](https://github.com/microsoft/vscode/blob/main/extensions/copilot/src/extension/tools/common/toolNames.ts#L19-L85)
establish the tool-shape limitation; [the current hook executor](https://github.com/microsoft/vscode/blob/main/extensions/copilot/src/platform/chat/node/hookExecutor.ts#L23-L145)
shows the launch and timeout failure behavior.

## Evidence labels

- **Documented**: explicitly stated by current first-party VS Code or GitHub
  documentation.
- **Source-observed**: visible in the current first-party VS Code source; useful
  for a focused experiment, but not a stable public compatibility promise.
- **Inferred**: a design implication drawn from cited documented or
  source-observed facts.
- **Unverified**: not established by the reviewed first-party material or a
  live host run.

## 1. Repository custom agents and capability restriction

### Locations and format

- **Documented.** VS Code's default workspace location is `.github/agents`; it
  also reads Claude-format agents from `.claude/agents`, uses
  `~/.copilot/agents` for user-level agents, and allows additional workspace
  locations through `chat.agentFilesLocations`. VS Code describes native files
  as `.agent.md` and also states that any `.md` file in `.github/agents` is
  detected. [VS Code's location and file-structure sections](https://code.visualstudio.com/docs/agent-customization/custom-agents#_custom-agent-file-locations)
  document these rules.
- **Documented.** GitHub's repository-level Copilot custom agents also live in
  `.github/agents`; its configuration reference recognizes both `.md` and
  `.agent.md` suffixes when deriving agent identity. The optional `target` field
  accepts `vscode` or `github-copilot`, and omission targets both environments.
  [GitHub's repository-level location](https://docs.github.com/en/copilot/concepts/agents/cloud-agent/about-custom-agents#where-you-can-configure-custom-agents)
  and [shared configuration table](https://docs.github.com/en/copilot/reference/custom-agents-configuration#yaml-frontmatter-properties)
  document this cross-surface format.

### Relevant frontmatter

VS Code currently documents these native frontmatter fields: `description`,
`name`, `argument-hint`, `tools`, `agents`, `model`, `user-invocable`,
`disable-model-invocation`, deprecated `infer`, `target`, `mcp-servers`,
`handoffs`, and Preview `hooks`. `tools` names built-in tools, tool sets, MCP
tools, or extension tools; `agents: []` prevents subagent use; unavailable tool
names are ignored. [The VS Code field table](https://code.visualstudio.com/docs/agent-customization/custom-agents#_header-optional)
is the direct reference.

GitHub makes the allowlist behavior explicit: omit `tools` or use `['*']` for
all available tools, list specific names to enable only those, and use `[]` for
none. The portable aliases include `execute` (shell), `read`, `edit`, `search`,
`agent`, `web`, and `todo`; GitHub notes that exact edit arguments can vary.
[GitHub's tools and alias tables](https://docs.github.com/en/copilot/reference/custom-agents-configuration#tools)
document these semantics.

- **Inferred from the local canonical contract and documented host tools.** A
  focused coordinator needs `read`/`search`/`edit` for reconciliation and
  `execute` for atomic effort-lock directory creation/removal. Neither `edit`
  nor `execute` can be narrowed to `.agent-workflow-state/wayfinder/` in
  frontmatter. The host therefore supplies a useful capability allowlist, not
  the needed path ACL or a lock-only terminal capability.
- **Documented limitation.** In local VS Code extension-host sessions, a prompt
  file's `tools` list takes precedence over the referenced or selected custom
  agent's list. Prompt files are not used by Agent Host sessions. A custom-agent
  tool list is consequently not a universal enforcement boundary across every
  VS Code session shape. [VS Code's tool-priority rules](https://code.visualstudio.com/docs/agent-customization/prompt-files#_tool-list-priority)
  and [Agent Host note](https://code.visualstudio.com/docs/agent-customization/prompt-files#_use-prompt-files-in-vs-code)
  document the distinction.

### Stability

- **Documented status.** The current VS Code custom-agent page does not mark
  custom agents themselves Preview; it marks the Agent Customizations editor
  and the `hooks` frontmatter field Preview. GitHub's current preview warning
  for custom agents names JetBrains, Eclipse, and Xcode, not VS Code.
  [VS Code's custom-agent page](https://code.visualstudio.com/docs/agent-customization/custom-agents)
  and [GitHub's status note](https://docs.github.com/en/copilot/reference/custom-agents-configuration)
  are the reviewed status sources. This supports saying "not currently marked
  Preview in VS Code," not inventing a separate GA guarantee.

## 2. Hooks and `PreToolUse`

### Configuration and supported locations

- **Documented.** VS Code loads team-shared workspace hooks from
  `.github/hooks/*.json`; it also lists `.claude/settings.json`,
  `.claude/settings.local.json`, `~/.copilot/hooks`, and
  `~/.claude/settings.json`, plus custom paths configured through
  `chat.hookFilesLocations`. Plugins may contribute `hooks.json` or
  `hooks/hooks.json`. [VS Code's hook-location table](https://code.visualstudio.com/docs/agent-customization/hooks#_hook-file-locations)
  is the source.
- **Documented.** A native VS Code file contains a `hooks` object whose event
  names map to command arrays, for example `PreToolUse` with `type: "command"`
  and `command`. Entries may also specify `windows`, `linux`, `osx`, `cwd`,
  `env`, and a seconds-based `timeout` whose default is 30. The extension-host
  platform selects the OS-specific override in remote development too.
  [VS Code's configuration section](https://code.visualstudio.com/docs/agent-customization/hooks#_hook-configuration-format)
  and [command-property reference](https://code.visualstudio.com/docs/agents/reference/hooks-reference#_hook-command-properties)
  document the shape.
- **Documented compatibility boundary.** VS Code parses Copilot CLI's
  lower-camel event names such as `preToolUse` and maps `bash`/`powershell` to
  its OS-specific command fields. GitHub's CLI/cloud format uses `version: 1`
  and is also loaded from `.github/hooks/*.json`, but has surface-specific
  payload and execution semantics. A shared repository hook must therefore
  deliberately normalize the supported host formats rather than assume one
  representation. [VS Code's Copilot CLI compatibility note](https://code.visualstudio.com/docs/agent-customization/hooks#_how-does-vs-code-handle-copilot-cli-hook-configurations)
  and [GitHub's hook reference](https://docs.github.com/en/copilot/reference/hooks-reference#hook-configuration-format)
  document both sides.

### Input representation

Every VS Code hook receives JSON on standard input with `timestamp`, optional
`cwd`, optional `session_id`, `hook_event_name`, and optional
`transcript_path`. `PreToolUse` adds `tool_name`, tool-specific `tool_input`,
and `tool_use_id`. VS Code warns that the transcript format is not a stable hook
API and says to prefer the documented fields. [The common-input documentation](https://code.visualstudio.com/docs/agent-customization/hooks#_common-input-fields)
and [PreToolUse reference](https://code.visualstudio.com/docs/agents/reference/hooks-reference#_pretooluse-input)
define this payload.

The tool representation is not normalized across hosts or tools. VS Code uses
camelCase inside its tool inputs and tool names such as `create_file` and
`replace_string_in_file`, unlike Claude's input properties and names; VS Code
currently ignores Claude matcher values, so the script itself must filter all
calls. [VS Code's Claude-hook compatibility section](https://code.visualstudio.com/docs/agent-customization/hooks#_how-does-vs-code-handle-claude-code-hook-configurations)
documents all three limitations.

**Source-observed.** The current built-in names include `apply_patch`,
`create_file`, `replace_string_in_file`, `multi_replace_string_in_file`, and
`run_in_terminal`. The current `apply_patch` schema places a textual patch in
`tool_input.input`, and that patch format supports Add, Update, and Delete
actions. [The current VS Code tool-name source](https://github.com/microsoft/vscode/blob/main/extensions/copilot/src/extension/tools/common/toolNames.ts#L19-L85)
and [current `apply_patch` declaration](https://github.com/microsoft/vscode/blob/main/extensions/copilot/package.json#L419-L438)
support a version-pinned test fixture; because hooks and tool schemas can
change, they should not be treated as a permanent public ABI.

### Deny and stop semantics

For one tool call, the precise response is exit `0` with:

```json
{
  "hookSpecificOutput": {
    "hookEventName": "PreToolUse",
    "permissionDecision": "deny",
    "permissionDecisionReason": "Protected Wayfinder state cannot be deleted"
  }
}
```

`permissionDecision` accepts `allow`, `ask`, or `deny`; when multiple hooks run,
the most restrictive result wins in the order `deny`, `ask`, `allow`.
[The PreToolUse output contract](https://code.visualstudio.com/docs/agents/reference/hooks-reference#_pretooluse-output)
documents this behavior.

Exit code `2` is also blocking and exposes stderr to the model. Other nonzero
codes are non-blocking warnings. Top-level `continue: false` stops the whole
agent session and is intentionally more drastic than denying one tool call;
when mechanisms conflict, the most restrictive wins. [VS Code's exit and
control-flow reference](https://code.visualstudio.com/docs/agent-customization/hooks#_choosing-how-to-return-data)
documents these distinctions.

## 3. Consequences for the Phase 1 durable-state guard

The current host supports a useful, deliberately narrow experiment, not a hard
security boundary:

- **Inferred recommendation.** Put the tool allowlist on the VS Code custom
  agent. Include `execute` only because the canonical mutation lock requires
  it, instruct the coordinator to use it only for that lifecycle, and omit
  every unnecessary extension/MCP/subagent tool. This is the smallest
  contract-valid set, but the instruction does not turn the general shell into
  a lock-only capability. [The alias semantics](https://docs.github.com/en/copilot/reference/custom-agents-configuration#tool-aliases)
  and [VS Code least-privilege guidance](https://code.visualstudio.com/docs/agent-customization/custom-agents#_security-considerations)
  support this conclusion.
- **Inferred implementation choice.** If the guard must run only for focused
  Wayfinder, an agent-frontmatter `PreToolUse` is the narrowest scope, at the
  cost of enabling a false-by-default Preview setting. If repository-wide
  protection is acceptable, `.github/hooks/*.json` loads automatically and
  avoids that extra setting, but it runs for all agents and Copilot surfaces.
  The host has no option that combines agent-only scope, on-by-default loading,
  and non-Preview stability. [The documented scope and gate](https://code.visualstudio.com/docs/agent-customization/hooks#_agent-scoped-hooks)
  establish the tradeoff.
- **Inferred guard boundary.** Recognize and deny only an explicit Delete action
  for an effort `map.md` in the exact current `apply_patch` schema. Allow create,
  update, ordinary replacement, and child retirement so legitimate
  reconciliation remains possible. Do not broaden this into a shell parser or
  semantic authorization engine; consequently, terminal-side deletion remains
  outside the guard. The [current patch schema](https://github.com/microsoft/vscode/blob/main/extensions/copilot/package.json#L419-L438)
  gives one bounded representation; the [hook schema guidance](https://code.visualstudio.com/docs/agents/reference/hooks-reference#_pretooluse-output)
  explains why each supported tool needs its own validated shape.
- **Documented limitation.** A hook that can be edited by the same agent can be
  modified and executed during the run, and hooks execute with VS Code's own
  permissions. VS Code recommends preventing automatic edits to hook scripts.
  [VS Code's safety warning](https://code.visualstudio.com/docs/agent-customization/hooks#_safety)
  and [security section](https://code.visualstudio.com/docs/agent-customization/hooks#_security-considerations)
  state these risks.
- **Documented limitation.** Hooks are Preview, may be disabled by an
  organization, and VS Code treats non-`2` failures as non-blocking. The guard
  must therefore be described and tested as defense in depth, not as protection
  equivalent to filesystem permissions or a sandbox. [VS Code's Preview/admin
  warning](https://code.visualstudio.com/docs/agent-customization/hooks#_agent-hooks-in-visual-studio-code-preview)
  and [exit semantics](https://code.visualstudio.com/docs/agent-customization/hooks#_exit-codes)
  establish this constraint.
- **Source-observed limitation.** The current VS Code executor turns command
  launch failure into a non-blocking result, terminates timed-out hooks, and
  treats the resulting non-`2` exit as non-blocking; its default timeout is 30
  seconds. This is current-source evidence, not a stable API promise.
  [The current executor implementation](https://github.com/microsoft/vscode/blob/main/extensions/copilot/src/platform/chat/node/hookExecutor.ts#L13-L145)
  shows these branches.
- **Unverified.** No live VS Code build was exercised in this research. Before
  relying on the guard, inspect the current Agent Debug Logs for each allowed
  write tool, pin fixtures to the observed names and input schemas, and include
  negative tests for unknown write-capable tools and hook failure. VS Code
  itself directs authors to use the logs for actual schemas and hook
  diagnostics. [The schema guidance](https://code.visualstudio.com/docs/agents/reference/hooks-reference#_pretooluse-output)
  and [hook diagnostics instructions](https://code.visualstudio.com/docs/agent-customization/hooks#_view-hook-diagnostics)
  support that validation step.

The practical stopping rule is sharp: if Phase 1 requires protection against
*all* ways any VS Code tool or shell command could mutate the protected tree,
the current hook representation is insufficient without a real filesystem or
sandbox boundary. If Phase 1 requires only a tested guard against a small set of
explicit destructive calls available to a tightly allowlisted focused agent,
the host can support that bounded experiment.
