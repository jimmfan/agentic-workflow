# ADR-0030: Use a thin focused VS Code Wayfinder projection

- Status: accepted
- Date: 2026-08-21
- Preserves: ADR-0023, ADR-0025, ADR-0027, ADR-0028, and ADR-0029

## Context

The current Wayfinder runtime is a portable provider projection used by a
general-purpose agent after routing selects Wayfinder. Phase 1 tests whether a
native VS Code custom agent with a narrower role and capability set improves
durable project understanding without adding another methodology, state model,
or future worker architecture.

VS Code repository custom agents can allowlist tools but cannot restrict edit
access by filesystem path. Repository `PreToolUse` hooks can deny recognized
tool calls, but hooks are Preview, apply workspace-wide, receive tool-specific
input schemas, and are not a filesystem or sandbox boundary. Agent-scoped hooks
are also Preview and disabled by default. These facts support a bounded
experiment, not a general security or authorization layer.

## Decision

Install one thin VS Code custom agent at
`.github/agents/wayfinder.agent.md`. It references the canonical installed
Wayfinder skill and state contract instead of copying their detailed semantics.
Its host-specific instructions only sharpen progressive navigation, evidence
and authority distinctions, missing-knowledge recognition, sole Wayfinder state
writing, and the ready-work boundary.

Allow only the portable `read`, `search`, `edit`, and `execute` tool sets.
`execute` is required because the canonical state contract forbids mutation
unless the coordinator can atomically create and remove the empty effort lock
directory; the projection instructs the agent to use the terminal only for that
lock lifecycle. Disable subagent invocation in both directions. Do not expose
web, MCP, extension, or handoff capabilities. Preserve the existing router and
provider invocation; Phase 1 adds no automatic handoff to the custom agent.

Extend the existing VS Code hook configuration with one repository-wide
`PreToolUse` command. The command recognizes only the exact current built-in
`apply_patch` name and input shape. It denies an explicit `*** Delete File:`
action targeting an effort's `map.md`, which is the contract's durable re-entry
point and has an in-place completion/supersession lifecycle. It permits Add and
Update patches and child-file retirement, so legitimate reconciliation remains
possible. The successful Phase 0 `SessionStart` route-marker hook remains
unchanged.

Treat the guard as defense in depth. It does not parse shell commands, detect
indirect writes, protect against unknown or extension-contributed tools,
resolve symlinks, survive disabled or failed hooks, prevent edits to the hook
itself, or replace host approval, sandbox, or filesystem controls. Unknown
representations fail open rather than being guessed at.

Evaluate the hypothesis with the existing behavioral harness. Add blind cases
for clean resume, stale-state conflict, domain-to-architecture navigation,
authority, missing knowledge, and implementation readiness, plus deterministic
allowed/denied guard cases. Run the same behavioral cases against baseline and
focused adapters when a live VS Code adapter is available; deterministic tests
do not claim live-editor behavior.

## Consequences

The portable Wayfinder runtime and state contract remain canonical, while the
VS Code file is small and replaceable. Capability restriction removes network,
external-service, and subagent actions from ordinary focused sessions, but broad
edit access remains necessary for map reconciliation. The mutation-lock
contract also forces access to a general terminal tool because VS Code exposes
no atomic directory-lock capability; the instruction-level lock-only
restriction is not a capability boundary.

The repository hook also runs for other VS Code agents. Its narrow predicate
should rarely affect them, but this is a host limitation rather than focused
agent isolation. Universal durable-state protection would require a real
filesystem or sandbox boundary and is outside Phase 1.

No baseline-versus-focused behavioral conclusion exists until both conditions
are run in a live host. The deterministic suite establishes packaging, prompt
boundaries, scenario integrity, and the current recognized hook behavior only.

## Alternatives considered

- Copy the full runtime into the custom-agent body: rejected because it creates
  a second drifting Wayfinder methodology.
- Remove `edit`: rejected because Wayfinder could not reconcile its legitimate
  durable state.
- Omit `execute`: rejected because `edit` cannot atomically create the empty
  mutation-lock directory and the state contract says not to mutate when that
  operation is unavailable. A general shell parser remains outside the
  experiment, so terminal-side state deletion is a documented guard gap.
- Use only an agent-scoped hook: rejected because it requires a false-by-default
  Preview setting; the repository hook is automatically discovered and its
  workspace-wide scope is documented.
- Claim hard path protection: rejected because the host exposes no path-scoped
  capability or stable fail-closed hook boundary.
