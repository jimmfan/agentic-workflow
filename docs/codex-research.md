# Official OpenAI Codex research

Inspected 2026-08-11 from the current official Codex manual and local Codex CLI
0.144.6. This file records platform facts that shaped the implementation; it is
not runtime policy.

## Supported primitives and decisions

| Primitive | Current evidence | Framework decision |
|---|---|---|
| `AGENTS.md` | Codex loads global guidance, then one file per directory from repository root to current directory; closer guidance overrides earlier text. The combined default limit is 32 KiB. [Official guide](https://learn.chatgpt.com/docs/agent-configuration/agents-md) | Use one compact repository-authoritative root file shared directly with Copilot. Parent Codex conveys only the bounded delegation contract to Hermes; it does not expose this file as writable child context. No nested override is required by the core. |
| Agent Skills | Repository skills use `.agents/skills`; metadata is discovered first, the body loads only when selected, and references/scripts load on demand. Symlinked skill directories are supported. [Official guide](https://learn.chatgpt.com/docs/build-skills) | Keep one canonical `.agents/skills` tree with six focused skills. Avoid eager copies or a large router. |
| Subagents | Enabled by default in current releases; parent collects results; children inherit sandbox/approval context. Parallel work consumes additional tokens and write-heavy concurrency needs care. [Official guide](https://learn.chatgpt.com/docs/agent-configuration/subagents) | Prefer native Codex subagents for bounded engineering exploration/review; one capable parent owns synthesis and edits. |
| Custom agents | Project agents can live under `.codex/agents/*.toml`; the standalone configuration-layer format may evolve. [Official subagent guide](https://learn.chatgpt.com/docs/agent-configuration/subagents#custom-agents) | Not required. The workflow skills and built-in agents are smaller and stable enough. |
| Project configuration | Trusted projects may use `.codex/config.toml`; relative paths resolve from `.codex`. [Config basics](https://learn.chatgpt.com/docs/config-file/config-basic), [advanced config](https://learn.chatgpt.com/docs/config-file/config-advanced) | No repository Codex config is needed for routing. Avoid changing user/provider settings. |
| Memories | Local memories are optional, generated under `CODEX_HOME`, and off by default. Official guidance says required team rules belong in checked-in instructions/docs. [Official memories guide](https://learn.chatgpt.com/docs/customization/memories) | Repository decisions/state outrank both Codex and Hermes memory. The framework does not enable memories. |
| MCP | Codex supports local stdio and remote HTTP MCP servers with project or user config and per-tool approvals. [Official MCP guide](https://learn.chatgpt.com/docs/extend/mcp) | No MCP server is needed. A small subprocess adapter is easier to audit and remove. |
| `codex exec` | Supported non-interactive interface; default sandbox is read-only, `--ephemeral` avoids session rollout persistence, JSON/schema output is supported, and an unsurfaceable new approval fails. [Official guide](https://learn.chatgpt.com/docs/non-interactive-mode) | Suitable for a future Hermes-first bounded Codex child with recursion guards, but not needed for Codex-first Hermes research. |
| App-server | Official deep-integration protocol over stdio JSONL; WebSocket transport and CLI command are described as experimental/unsupported for production. [Official guide](https://learn.chatgpt.com/docs/app-server) | Evaluate Hermes's integration but do not make it the default or a `repo-read` claim without an end-to-end profile guarantee. |
| Sandbox and approvals | Filesystem sandbox policy and approval policy are separate. Workspace-write protects sensitive repository control paths, including `.git`, `.agents`, and `.codex`, unless explicitly configured. [Sandbox](https://learn.chatgpt.com/docs/sandboxing), [approvals/security](https://learn.chatgpt.com/docs/agent-approvals-security) | Preserve Codex's sandbox/approval ownership. An optional child never weakens it or substitutes Hermes approvals. |

## Local observations

Read-only CLI inspection reported `codex-cli 0.144.6`. `codex features list`
reported `multi_agent` stable/enabled and `memories` experimental/disabled.
`codex app-server --help` labels the command experimental. `codex exec --help`
exposed `--sandbox read-only`, `--ephemeral`, JSON output, output schemas, and
`--ignore-user-config`. These observations describe this machine on the
inspection date; they are not minimum-version claims for downstream projects.

The current workspace sandbox treated `.agents` and `.codex` as protected
repository paths, so creating the canonical skill directories required a scoped
approval. That is expected separation between instruction discovery and agent
authorization: discoverable policy does not grant permission to rewrite itself.

## Stable versus optional

The runtime design depends only on root `AGENTS.md`, repository Agent Skills,
ordinary Markdown/JSON state, and the host's existing tool/sandbox model. Native
subagents are preferred but optional per task. Custom agents, memories, MCP,
app-server, plugins, and `codex exec` are not required for core operation.

OpenAI documents no direct Hermes import or Hermes-specific integration. All
Hermes compatibility claims therefore come from the separately pinned Hermes
release and are kept behind the optional adapter.
