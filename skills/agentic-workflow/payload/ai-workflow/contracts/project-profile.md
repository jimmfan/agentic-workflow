# Project profile contract

`.ai-workflow-state/project-profile.md` is optional, project-owned advisory context: a
concise cache of verified facts and pointers likely to help future work. It is
not a versioned structured artifact, chat log, task journal, speculative
architecture document, README copy, source-of-truth replacement, or place for
secret values. The profile is not a shell script; an agent may run a recorded
command only after applying the safety gate below.

Lifecycle operations seed the current template only when the profile is absent.
They preserve every existing profile byte-for-byte during install, update, and
removal. A newer template never requires an existing profile to migrate.

## Presence and initialization

Readiness classification is deliberately permissive:

- `missing`: the file does not exist;
- `uninitialized`: a readable profile contains the advisory
  `Initialization: uninitialized` marker;
- `present`: any other readable, non-empty UTF-8 regular file;
- `empty`: the file contains only whitespace;
- `unreadable`: its bytes cannot be read or decoded as UTF-8; and
- `unsafe`: the path traverses a symlink, has a non-directory parent, or is not
  a regular file.

These states do not validate semantic quality. In particular, `present` means
only that advisory context exists. Heading names, order, and counts are not a
schema, and an initialization marker is not required in an existing populated
profile.

The installed template uses `Initialization: uninitialized` and `None` for
unknown sections. The marker is an advisory signal, not a format version. Missing,
empty, or uninitialized project context does not prevent unrelated direct work
and is not framework corruption.

For a mature existing repository, initialize the profile once from verified
repository evidence. Keep the investigation bounded to useful canonical files
and relevant live checks; do not scan the entire repository merely to populate
the profile. Remove or change the uninitialized marker after recording checked
facts. A new or intentionally sparse repository may remain uninitialized until
reusable context exists.

After initialization, update the profile progressively when normal work
naturally establishes information that is all three of:

1. verified;
2. durable rather than task-specific; and
3. likely to be useful in future work.

Do not add temporary workflow state, conversational notes, speculative claims,
ephemeral implementation detail, secrets, copied documentation, or facts better
represented by a canonical file and a short pointer. Do not perform a
repository-wide rescan on each task. If repository writes are not authorized,
report the candidate fact without editing the profile.

Knowledge precedence is:

1. live and source evidence for current behavior;
2. accepted ADRs and domain documentation for domain decisions;
3. provider-native artifacts for outputs owned by a provider workflow; and
4. this concise cache and its pointers.

When the profile conflicts with a higher-precedence source, verify and report
the conflict before relying on the profile, then update it only when writes are
authorized. The workflow that creates a durable artifact owns its canonical
artifact; the profile may point to that artifact but does not require or create
a duplicate.

## Suggested contents

The shipped template currently suggests these sections:

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

Under `Important paths`, record concise pointers to useful paths and canonical
artifacts. A specification may be canonical in a tracker, at an intentional
project documentation path, or in another provider-native location according to
the workflow that created it. Record the accepted native tracker or local
implementation-ticket destination when established. Do not impose one framework
path or mirror issue/specification bodies into workflow state.

Under `Delivery workflow`, state when proportional independent review is
required and who may accept a review limitation. Projects may make review
stricter but must not let review replace executable Verification evidence.

Projects may rename, reorder, omit, or extend these sections. Agents should use
the readable context that is relevant rather than rejecting the document for
format differences.

When present, the maintenance section can identify the owner, last review date,
facts that make the profile stale, and the action to take when reality conflicts
with it. While uninitialized, its value may remain `None`.

Under `Commands`, `None` means that no project check has been configured yet.
Report verification as blocked rather than inventing a command.

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
not run. A current user request that explicitly names a specific external
read-only target and scope (for example, one issue in one repository) authorizes
that exact inspection without a redundant second approval, including when the
entry says `Approval required: yes`. It does not authorize reading unrelated
targets, expanding to another repository, or making any external change. Other
external reads wait for explicit approval. Safe local checks may run
automatically only when relevant and not marked approval-required.
Creating, editing, closing, or otherwise mutating a native ticket is an external
action and always requires explicit mutation authority unless a narrower
accepted project policy already grants that exact authority. Authorization for
an external read never supplies that mutation authority.
Commands are executable repository content, not inherently trusted, and must be
reviewed like code; never interpolate untrusted request text into a command.

## Optional extension

Projects may add sections and command fields. They must not redefine the safety
or scope values or weaken approval requirements. Domain-specific architecture,
diagnostic paths, terminology, and decision factors belong here rather than in
the reusable skills.
