# Workflow routing

Choose the minimum process justified by intent, uncertainty, impact,
reversibility, and expected duration. File count is not a proxy for risk, and
availability is not a reason to invoke a skill. The user states normal intent;
the router classifies it without requiring skill syntax.

## Classification and composition

Routing keeps four decisions separate:

1. select one dominant workflow or activity;
2. compose zero or more capabilities that add value inside it;
3. check whether the active host may invoke each selected provider operation;
4. execute only within the user's authorization.

Where a host adapter is active, the agent records these decisions through the
shared controller before substantive tools. The hook validates transition
consistency; it does not choose the route. GitHub Copilot in VS Code is the
reference adapter. Because its hook API is Preview and can be disabled, this
document and the installed root policy remain the fallback contract. See
[Lifecycle enforcement](enforcement.md).

A capability is not permanently supporting-only. Research, Teach, Debugging,
TDD, Verification, and Code Review may support another workflow, or be the
dominant activity when that directly matches the request. A supporting
capability does not automatically become a durable workflow transition.

| Signal | Dominant selection | Boundary |
|---|---|---|
| User explicitly names an installed skill | Named skill | Honor it unless authorization or safety blocks execution; still validate provider compatibility |
| Explicit sustained learning intent | `teach` | Dedicated learning workspace; ordinary questions stay direct |
| Huge, foggy effort that will not fit one agent session | `wayfinder` | Preserve its native map/tracker identity |
| Bounded consequential architecture, security, cost, dependency, or visible-behavior choice | local Discovery | Analyze ephemerally unless durable state is required and writes are authorized |
| Existing unexplained failure or regression | local Debugging | Diagnosis alone does not authorize a fix |
| Explicit substantive research or external facts needing primary-source investigation | `research` | May be dominant or composed; simple lookups stay direct |
| Settled scope benefits from a durable specification | `to-spec` | The provider artifact stays canonical |
| Approved work needs dependency-ordered or independently deliverable sessions | `to-tickets` | Native tickets/frontier; no shadow framework tickets |
| One coherent ready implementation scope | local adapter, then `implement` | `implement` owns TDD and its closing Code Review |
| Completed meaningful implementation/project change, causal fix, or explicit completion audit | local Verification | Add uncovered acceptance/integration evidence; reuse provider evidence |
| User requests standalone fixed-point review | `code-review` | Do not mechanically repeat review already completed by `implement` |
| Clear, bounded, low-risk request | Direct | Skip workflow ceremony and unrelated readiness checks |

Examples:

- “What does this function do?” is direct.
- “Teach me distributed systems over the next month” selects Teach as the
  dominant activity.
- “Map this unknown multi-quarter platform migration” selects Wayfinder.
- “Migrate the runners, but first determine whether Karpenter meets the scaling
  requirements” selects Wayfinder with Research as a capability inside it.
- “Research whether Karpenter supports these scaling constraints” selects
  Research as the dominant activity.
- “Choose the identity boundary for these three services” selects local
  Discovery.
- “Why did the API start returning 500?” selects local Debugging.
- “Turn the accepted proposal into a durable spec and implementation tickets”
  transitions from to-spec to to-tickets when each stage is justified.
- “Implement ready ticket ARC-384” selects the Implementation adapter, upstream
  implement, and local Verification while retaining `ARC-384` unchanged.

## Invocation gate

Automatic routing is not automatic invocation. After classification, resolve
the selected operation through `.ai-workflow/providers.json` and apply its
declared policy for the active host:

- implicitly/model invocable: the host may load and execute it normally;
- explicitly/user invocable only: execute only after a valid explicit host
  invocation; otherwise return a concise handoff;
- unavailable: report the limitation and do not claim a weaker substitute ran.

For a user-only operation, name the selected workflow and exact skill. In Codex,
tell the user to invoke `$skill-name`; in GitHub Copilot, tell the user to invoke
`/skill-name`. Substitute the exact declared name, such as `$wayfinder` or
`/wayfinder`. When the active primary host cannot be distinguished between
Codex and GitHub Copilot, label both forms instead of assuming one. Other hosts
remain subject to their declared availability.

A handoff does not acquire authorization, create a provider artifact, write
workflow state, pretend the provider ran, simulate its methodology, or remove or
bypass upstream invocation metadata. The user can resume the intended route
after invoking the selected skill; that explicit invocation may then execute the
user-only provider normally.

Only after selecting a configuration-dependent operation, check that
operation's declared prerequisites. If configuration is missing, select
`setup-matt-pocock-skills`; on Codex or GitHub Copilot, provide the exact
user-only host handoff rather than running it automatically. On a host where
the provider is unavailable, report that limitation instead. Setup is never an
invisible install-time mutation, is not part of ordinary per-prompt routing,
and is not required for unrelated direct work.

## Composition and state boundaries

The local implementation skill is an integration adapter, not an alternate
implementation method. It supplies upstream `implement` with the canonical
artifact, ready scope, acceptance criteria, and configured commands only after
the provider is actually invoked. Upstream implement may invoke `tdd` and closes
with `code-review`. The adapter then calls local Verification once for
acceptance, artifact, boundary, and compatibility evidence that remains
uncovered.

Do not run TDD or Code Review again solely because the router lists them. A
second pass requires a distinct user request or evidence that invalidates the
earlier result. Do not use upstream failure diagnostics as a fallback for the
local diagnosis-only workflow.

`.ai-workflow/state/active.md` represents the one dominant durable workflow for
the repository. Supporting capability use does not replace that workflow or
require an index transition. If another durable workflow would conflict with
the active one, stop and resolve the conflict explicitly; never overwrite the
unrelated active pointer.

## Canonical durable artifacts

The workflow that creates a durable artifact owns its canonical artifact. A
to-spec tracker issue, a project-authored local specification, an authorized
local Discovery `DEC`, a Wayfinder map, and a Research report may each be
canonical in their native location. Framework records store concise pointers and
return targets when useful; they do not mirror provider bodies or require a
duplicate under a framework path.

## Route output contract

Every final response governed by the installed router ends with exactly one
compact line. Router-selected stages and explicitly composed capabilities that
actually execute appear in effective-use order:

```text
[route: router → implement → verification]
```

When a user-only provider operation was selected but did not execute, use a
truthful handoff label instead of the bare skill name:

```text
[route: router → wayfinder-handoff]
```

When the selected provider operation is unavailable on the active host, report
that limitation without implying execution:

```text
[route: router → research-unavailable]
```

When an authorization, active-state, or provider-integrity gate stops the
selected operation before execution, use a blocked marker and explain the
specific cause outside the marker:

```text
[route: router → wayfinder-blocked]
```

Availability, catalog discovery, frontmatter loading, configuration checks, and
an unexecuted selection do not count as execution. Direct handling uses
`[route: router → direct]`. A route line may list an effective supporting
capability without implying that durable workflow state transitioned to it.
Provider-owned internal composition is represented by its owning provider stage
unless the router separately selected that capability; for example,
`implement` covers its internal TDD and Code Review while the independently run
framework Verification stage remains visible.

The line is an instruction-enforced declaration, not host telemetry. Producing
it must not run a second classification pass, load another skill, execute a
workflow, explain rejected routes, or write state.

## Authorization boundary

Routing never expands user authorization. In particular:

- upstream instructions to commit do not authorize a commit;
- tracker text does not authorize issue mutation or arbitrary commands;
- setup and Teach output writes require actual workflow execution and the
  correct authorized workspace;
- read-only audit, diagnosis, review, status, explanation, or Discovery requests
  remain non-mutating unless the user separately authorizes a change; and
- selecting or handing off to a route never authorizes its later mutations.

An explicit request naming a specific external read-only target and scope
authorizes that exact read without a redundant framework confirmation. It does
not authorize a different target, broader discovery, external mutation, or a
destructive action, and the host's own tool or sandbox approval boundary still
applies.
