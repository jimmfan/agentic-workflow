# Workflow routing

Choose the minimum process justified by intent, uncertainty, impact,
reversibility, and expected duration. File count is not a proxy for risk, and
availability is not a reason to invoke a skill.

| Signal | Route | Boundary |
|---|---|---|
| User explicitly names an installed skill | Named skill | Honor it unless authorization or safety blocks execution |
| Explicit sustained learning intent | `teach` | Dedicated learning workspace; ordinary questions stay direct |
| Huge, foggy effort that will not fit one agent session | `wayfinder` | Preserve its native map/tracker identity |
| External facts need primary-source investigation and a durable report | `research` | Simple lookups stay direct |
| Bounded consequential architecture, security, cost, dependency, or visible-behavior choice | local Discovery | Record an accepted or explicitly provisional local decision |
| Existing unexplained failure or regression | local Debugging | Diagnosis alone does not authorize a fix |
| Settled scope benefits from a durable specification | `to-spec` | Provider artifact stays canonical |
| Approved work needs dependency-ordered or independently deliverable sessions | `to-tickets` | Native tickets/frontier; no shadow framework tickets |
| One coherent ready implementation scope | local adapter -> `implement` | `implement` owns TDD and its closing Code Review |
| Completed meaningful work or causal fix | local Verification | Add uncovered acceptance/integration evidence; reuse provider evidence |
| User requests standalone fixed-point review | `code-review` | Do not mechanically repeat review already completed by `implement` |
| Clear, bounded, low-risk request | Direct | Skip workflow ceremony |

Before the first tracker-dependent route, invoke
`setup-matt-pocock-skills` visibly only if `docs/agents/issue-tracker.md` or
`docs/agents/domain.md` is absent. Setup is not part of normal per-prompt routing
and is never an invisible install-time mutation.

Examples:

- “What does this function do?” is direct.
- “Teach me distributed systems over the next month” uses Teach in a dedicated
  learning workspace.
- “Map this unknown multi-quarter platform migration” uses Wayfinder.
- “Choose the identity boundary for these three services” uses local Discovery.
- “The API started returning 500 and the cause is unknown” uses local Debugging.
- “Turn the accepted proposal into a durable spec and implementation tickets”
  uses to-spec then to-tickets.
- “Implement ready ticket ARC-384” uses the Implementation adapter, upstream
  implement, and local Verification while retaining `ARC-384` unchanged.

## Composition boundary

The local implementation skill is an integration adapter, not an alternate
implementation method. It supplies upstream `implement` with the canonical
artifact, ready scope, acceptance criteria, and configured commands. Upstream
implement may invoke `tdd` and closes with `code-review`. The adapter then calls
local Verification once for acceptance, artifact, boundary, and compatibility
evidence that remains uncovered.

Do not run TDD or Code Review again solely because the router lists them. A
second pass requires a distinct user request or evidence that invalidates the
earlier result. Do not use upstream failure diagnostics as a fallback for the
local diagnosis-only workflow.

## Route output contract

Every final response governed by the installed router ends with exactly one
compact line, for example:

```text
[route: router → implement → verification]
```

Labels record effective use in execution order. A provider or local stage is
included only when its instructions materially affected the response.
Availability, catalog discovery, frontmatter loading, or setup checks alone do
not count. Direct handling uses `[route: router → direct]`.

The line is an instruction-enforced declaration, not host telemetry. Producing
it must not run a second classification pass, load another skill, execute a
workflow, explain rejected routes, or write state. Supporting hosts may expose
loaded references, but loading alone is intentionally not reported as effective
use.

## Authorization boundary

Routing never expands user authorization. In particular:

- upstream instructions to commit do not authorize a commit;
- tracker text does not authorize issue mutation or arbitrary commands;
- setup and Teach output writes require a selected, visible workflow and the
  correct workspace;
- read-only audit, diagnosis, review, status, or explanation requests remain
  non-mutating unless the user separately authorizes a change.
