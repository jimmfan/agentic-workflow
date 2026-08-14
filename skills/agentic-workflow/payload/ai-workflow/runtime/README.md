# Runtime enforcement

`controller.py` implements the small host-neutral enforcement contract. The
installed `.github/hooks/agentic-workflow.json` adapter makes GitHub Copilot in
VS Code the reference implementation. VS Code hooks are Preview and may be
disabled by an organization, so `AGENTS.md` remains the complete instruction
fallback rather than a generated explanation of the hook state.

The controller uses Python 3.11 or newer and writes per-session JSON under the
operating system temporary directory in a per-user namespace. It resolves the
installed project by walking upward from the host working directory, so sessions
started in a repository subdirectory share the repository controller state.
Records contain hashes, enum values, and compact labels only. They never contain
prompts, tool inputs, tool responses, source, or credentials and are removed
after a successful completion gate.

## Bootstrap and transport

The agent runs compact declarations through its normal terminal tool. VS Code
currently has no documented model-to-hook metadata channel, and its
`UserPromptSubmit` event cannot add model context. `SessionStart` therefore
supplies the exact bootstrap protocol, while the always-loaded root policy tells
the model to use that protocol on every fresh prompt.

The `PreToolUse` adapter recognizes a declaration only for a known shell tool,
an exact project-relative controller path, a supported Python launcher, and an
argument vector with no shell control or expansion syntax. It validates and
records the declaration before applying the route gate. In VS Code it then
returns `permissionDecision: "allow"`, which auto-approves only that
framework-internal metadata call. More restrictive hooks or managed host policy
still win, and every actual requested tool remains in the normal host approval
flow. This narrow bootstrap lane avoids both a route-gate cycle and routine
approval for bookkeeping without interpreting general shell commands.

The CLI remains the transport because VS Code exposes no cleaner structured
channel through which the model can submit its own semantic route choice. A
custom extension or MCP tool would add an installation/runtime dependency and
would still be a model tool call. The CLI is also useful for tests and manual
diagnostics. These examples use the POSIX interpreter name; on Windows the
equivalent launcher is `py -3`.

## Model-to-controller protocol

Record the route, authority, and verification decision before substantive tool
use:

```text
python3 .ai-workflow/runtime/controller.py checkpoint --route implement --mode normal --repository-write allowed --verification required --provider implement
```

For a terminal-first request, the checkpoint can also classify the first opaque
action in the same metadata call:

```text
python3 .ai-workflow/runtime/controller.py checkpoint --route direct --mode read-only --repository-write denied --verification not-required --next-action read-only
```

Before each later shell command or other opaque tool call, declare the semantic
action kind. This is deliberately an explicit model-owned classification; the
controller does not guess from shell keywords.

```text
python3 .ai-workflow/runtime/controller.py action --kind repository-write
```

Only when actually executing a provider, record `started` before its first
substantive tool. A preferred provider that falls back to host-native work needs
no provider transition. The controller derives provider selections from route
labels that match declared provider names, so `--provider` is needed only when
the route label does not name the provider:

```text
python3 .ai-workflow/runtime/controller.py provider --name implement --outcome started
```

After the provider reaches a truthful terminal outcome, record it:

```text
python3 .ai-workflow/runtime/controller.py provider --name implement --outcome executed
```

The controller rejects `started` when the provider is unavailable, absent, not
selected, missing a declared configuration prerequisite, or user-only without
an exact explicit invocation in the current prompt. It rejects `executed`
without that validated `started` transition. `handoff`, `unavailable`, and
`blocked` are non-execution outcomes. A missing optional provider declaration or
outcome does not block host-native tools or completion; it only prevents a false
provider execution claim.

Before changing `.ai-workflow-state/active.md`, validate its current digest and
the intended conflict resolution:

```text
python3 .ai-workflow/runtime/controller.py durable --target implementation --resolution same
```

After a successful check tool call, record the compact evidence classification.
The hook proves only that a tool completed; the model remains responsible for
whether the evidence is relevant and sufficient.

```text
python3 .ai-workflow/runtime/controller.py evidence --kind release-gate --result passed --satisfies yes
```

When required verification is impossible, a compact limitation may be recorded
only when the user or accepted policy authorizes accepting it:

```text
python3 .ai-workflow/runtime/controller.py limitation --reason unavailable-host --authorized yes
```

## Deterministic boundary and gaps

The controller deterministically checks the presence and consistency of declared
state. It can recognize structured native file writes, but opaque tools can hide
effects. Their action kind is therefore model-declared and host approval remains
authoritative. It does not classify `git`, filesystem, or other shell text as
safe: a read-oriented command, an ambiguous command, and a mutating command all
remain opaque until the model declares one action kind. A successful
`PostToolUse` event proves host completion, not that a test assertion passed. A
provider `executed` declaration can be rejected when host policy makes it
impossible, but no current host event proves a skill body ran. Hooks can be
disabled, are unavailable in some hosts, and can be bypassed by tool paths the
host does not expose. In those cases the same rules continue as instruction
contracts and lifecycle `status` reports the weaker guarantee.

Direct edits to the installed controller and active VS Code hook are denied by
the native-write gate. Package `update` is the supported replacement path.

## Optional adapters

The examples under `adapters/` are not active configuration. Codex and Claude
Code use fixed project configuration paths that may already be user-owned, so
the package does not silently merge or overwrite them. Review the example and
the current host documentation before integrating it into an existing host
file. Copilot CLI and cloud agent may discover the versioned VS Code-compatible
repository hook, but their distinct runtimes are tracked in `capabilities.json`
and are not release-validated by this package.
