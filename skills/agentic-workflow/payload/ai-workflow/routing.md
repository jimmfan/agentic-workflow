# Detailed routing contract

This is the progressively loaded routing policy for an installed Agentic
Workflow project. Read it for a named skill, resume, uncertain route, or any
route not confidently direct. The root `AGENTS.md` invariants remain binding.

Choose the minimum process justified by intent, uncertainty, impact,
reversibility, and expected duration. File count is not a proxy for risk, and
availability is not a reason to invoke a skill. Normal user intent is enough;
skill syntax is required only when the selected provider declares user-only
invocation.

## Classification and composition

Keep four decisions separate:

1. select one dominant workflow or activity;
2. compose zero or more capabilities that materially help inside it;
3. check whether the active host may invoke each selected provider operation;
4. execute only within the user's authorization.

| Signal | Dominant selection | Boundary |
|---|---|---|
| User explicitly names an installed skill | Named skill | Honor it unless authorization, safety, or host compatibility blocks execution |
| Explicit sustained learning intent | `teach` | Dedicated learning workspace; ordinary questions stay direct |
| Huge, foggy effort that will not fit one agent session | `wayfinder` | Preserve its native map and tracker identity |
| Bounded consequential architecture, security, cost, dependency, or visible-behavior choice | local Discovery | Analyze ephemerally unless durable state is useful and writes are authorized |
| Existing unexplained failure or regression | local Debugging | Diagnosis alone does not authorize a fix |
| Explicit substantive research or external facts needing primary sources | `research` | May be dominant or composed; simple lookups stay direct |
| Settled scope benefits from a durable specification | `to-spec` | The provider artifact stays canonical |
| Approved work needs dependency-ordered or independently deliverable sessions | `to-tickets` | Preserve native tickets/frontier; create no shadow tickets |
| One coherent ready implementation scope | local adapter, then `implement` | `implement` owns TDD and its closing Code Review |
| Explicit bounded test-first implementation | `tdd` | The provider owns the loop; local Verification checks the integrated result |
| Completed meaningful change, causal fix, or explicit completion audit | local Verification | Add uncovered acceptance/integration evidence; reuse existing evidence |
| User requests standalone fixed-point review | `code-review` | Do not repeat review already completed by `implement` |
| Clear, bounded, low-risk request | Direct | Skip workflow ceremony and unrelated readiness checks |

A capability may support another dominant workflow or be dominant when it
directly matches intent. Supporting use does not automatically create a durable
workflow transition.

## Invocation and provider gate

Automatic routing is not automatic invocation. Resolve selected provider
operations through `.ai-workflow/providers.json`:

- `implicit`: the compatible host may load and execute the skill normally;
- `user-only`: execute only after exact explicit host invocation; otherwise
  return a concise handoff;
- `unavailable`: report the limitation and do not claim a substitute ran.

For a user-only operation, name the selected workflow and exact skill. Use
`$skill-name` in Codex and `/skill-name` in GitHub Copilot. If the active primary
host cannot be distinguished, label both forms rather than guessing. A handoff
does not authorize or execute work, create provider artifacts, write workflow
state, or simulate provider methodology.

Only after selecting a configuration-dependent operation, check its declared
prerequisites. If configuration is missing, select the user-only
`setup-matt-pocock-skills` operation and provide the appropriate exact handoff;
never run it automatically. Do not check setup for unrelated direct work. On a
host where the provider is unavailable, report that limitation.

GitHub Copilot in VS Code is the reference host, but its hooks are optional and
Preview. Codex and Claude hook adapters are opt-in; Claude currently has no
`.claude/skills` projection, so skill-backed routes are unavailable while direct
work remains available. Copilot CLI and cloud are distinct runtimes. Detailed
capabilities and controller behavior live in `runtime/capabilities.json` and
`runtime/README.md`.

## Composition and workflow ownership

The local Implementation skill is an integration adapter, not an alternate
implementation method. It supplies accepted scope, canonical artifacts,
acceptance criteria, and configured commands only after `implement` is actually
invoked. Upstream `implement` owns its build loop, appropriate TDD use, and
closing Code Review. Framework Verification runs once afterward and reuses that
evidence, adding only uncovered acceptance, artifact, boundary, or compatibility
checks.

Do not repeat TDD, Code Review, or provider checks merely to add framework
branding. A second pass needs a distinct request or evidence that invalidates
the earlier result. Do not use upstream failure diagnostics as a substitute for
the local diagnosis-only workflow.

The workflow that creates a durable artifact owns its canonical form. Native
specifications, tickets, maps, research, course workspaces, reviews, and provider
identifiers remain canonical in their native locations. Framework state stores
only orchestration status, concise pointers, and exact return targets when
needed; it does not mirror provider bodies or allocate shadow identifiers.

For durable workflow mechanics, conflicts, pointers, re-entry, and record
allocation, follow `state/README.md`. Never silently replace an unrelated active
workflow. Ephemeral direct work and supporting capabilities do not acquire
durable state merely because they ran.

## Authorization and evidence

Routing and provider instructions never expand authorization. In particular:

- an upstream commit instruction does not authorize a commit;
- ticket or specification text does not authorize commands or tracker changes;
- setup and Teach output writes require actual execution in an authorized
  workspace;
- audit, diagnosis, review, explanation, and read-only requests remain
  non-mutating unless the user separately authorizes a change; and
- selection or handoff never authorizes later mutations.

A request naming one exact external read-only target and scope authorizes only
that read, not broader discovery, another target, mutation, or destruction.
Host sandbox and approval boundaries still apply.

Use `workflow-verification` for its detailed evidence procedure. Never invent a
project command. Reuse relevant observed evidence and report required outcomes
as passed, failed, blocked, skipped, or unavailable. A limitation satisfies a
required completion gate only when the user or accepted project policy permits
it.

Project-profile behavior is intentionally soft. Read
`contracts/project-profile.md` only when profile facts or a profile update are
relevant. Do not scan the repository or update the profile merely to complete a
route.

## Route output contract

End each governed final response with exactly one compact marker containing
router-selected stages and explicitly composed capabilities that actually
executed, in effective-use order:

```text
[route: router → implement → verification]
```

Use compact local labels: `workflow-discovery`, `workflow-debugging`,
`workflow-implementation`, and `workflow-verification` become `discovery`,
`debugging`, `implement`, and `verification`.

Use truthful terminal suffixes when selection did not become execution:

- `<skill>-handoff`: user-only selection awaiting explicit invocation;
- `<skill>-unavailable`: the active host cannot invoke it;
- `<skill>-blocked`: authorization, state, prerequisite, or integrity stopped it.

Direct handling uses `[route: router → direct]`. Availability, catalog lookup,
configuration checks, and unexecuted selection do not count as execution.
Provider-owned internal TDD and Code Review stay represented by `implement`
unless separately selected; independently executed framework Verification stays
visible.

The marker is instruction-level diagnostics, not host telemetry. Do not reroute,
load skills, execute workflows, explain rejected routes, or write state merely
to produce it.
