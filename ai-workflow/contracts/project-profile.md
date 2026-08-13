# Project profile contract

`ai-workflow/project-profile.md` is project-owned context. It specializes the
generic workflow policy without changing core skills. Keep it factual, concise, and free
of secret values. The profile is not a shell script; an agent may run a command
only after applying the safety gate below.

## Required headings

Every profile must contain these level-two headings, using `None` when a section
has no content:

1. `Purpose and success`
2. `Technology and architecture`
3. `Important paths`
4. `Terminology`
5. `Constraints and policy`
6. `Delivery workflow`
7. `Commands`
8. `Debugging model`
9. `Decision considerations`
10. `Profile maintenance`

Under `Important paths`, name the project's canonical location for durable
specifications when one exists, or state that none has been established. Specs
remain project-owned; workflow records link to them rather than copying them.
Also name the local implementation-ticket destination or the accepted native
tracker, or state that neither is established. Native issue bodies remain
canonical and are not mirrored into workflow state.

Under `Delivery workflow`, state when proportional independent review is
required and who may accept a review limitation. Projects may make review
stricter but must not let review replace executable Verification evidence.

The maintenance section identifies the owner, last review date, facts that make
the profile stale, and the action to take when reality conflicts with it. Source
code and live evidence remain authoritative for system behavior; this profile is
authoritative only for declared project policy until corrected.

## Command entry

Each command is a level-three heading containing a stable lowercase identifier:

```markdown
### `check-id`

- Purpose: Why this check exists.
- Action: `complete ready-to-run command`, or an exact manual check.
- Kind: `command` or `manual`.
- Working directory: Repository-relative directory, usually `.`.
- Prerequisites: Required tools and setup, or `None`.
- Environment: Required environment and credential names, never values, or `None`.
- Scope: `repository-local`, `host-local`, or `external`.
- Safety: `read-only`, `locally-mutating`, `externally-mutating`, or `destructive`.
- Approval required: `yes` or `no`.
- Timeout: Expected limit or duration, or `Not specified`.
- Success: Observable exit status, output, or behavior.
- Unavailable: Exact fallback or `Report blocked; do not substitute`.
- Side effects and reversal: Durable effects and cleanup, or `None`.
```

The four safety values mean:

- `read-only`: observes files or state and is not expected to alter durable state.
- `locally-mutating`: may create repository-local caches, build output, or test
  artifacts but does not change an external system.
- `externally-mutating`: changes a remote service, shared environment, deployed
  system, or other external state.
- `destructive`: deletes, overwrites, or makes data/state difficult to recover.

Scope records where the action observes or changes state:

- `repository-local`: only the consuming repository and its disposable outputs.
- `host-local`: the local machine outside the repository, such as a disposable
  local database or editor session.
- `external`: a network service, cloud account, remote host, shared environment,
  or any other system beyond the local host.

`externally-mutating` and `destructive` always require explicit human approval,
even if the entry incorrectly says otherwise. A destructive entry also needs an
exact target and recovery or reversal plan. Unknown or missing safety values do
not run. Any entry marked `Approval required: yes` waits for explicit approval,
including a read-only inspection. Every `external`-scope action also waits for
explicit approval, even when read-only. Safe checks may run automatically only
when relevant, not marked approval-required, and local in scope.
Creating, editing, closing, or otherwise mutating a native ticket is an external
action and follows the same explicit-approval rule unless a narrower accepted
project policy already grants that exact authority.
Commands are executable repository content, not inherently trusted, and must be
reviewed like code; never interpolate untrusted request text into a command.

## Optional extension

Projects may add sections and command fields. They must not redefine the safety
or scope values or weaken approval requirements. Domain-specific architecture,
diagnostic paths, terminology, and decision factors belong here rather than in
the reusable skills.
