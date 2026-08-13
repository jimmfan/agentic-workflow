# Architecture and ownership

## Purpose

The installed framework adds durable engineering workflow policy while leaving
execution, tools, sandboxing, approvals, and subagents with the host agent. It is
repository-native Markdown and JSON; no daemon, service, package registry, or
external agent runtime participates in normal work.

## Runtime path

```text
request
  -> root AGENTS.md router
      -> direct handling for clear, bounded, low-risk work
      -> Teach for a blocking knowledge gap
      -> Discovery for consequential unresolved choices
      -> Debugging for an unexplained failure
      -> Implementation for approved coherent work
      -> Decomposition only for dependency-ordered multi-session work
      -> Verification, then proportional independent Review
```

The compact root policy is always available. Detailed workflow bodies live in
`.agents/skills` and load only when relevant. Project facts and safe commands
live in `ai-workflow/project-profile.md`; durable resumption state lives under
`ai-workflow/state`.

## Distribution boundary

The source package is intentionally inert. Its resources do not mirror active
repository customization paths:

```text
payload/root/AGENTS.md.template  -> AGENTS.md
payload/skills/*/SKILL.md        -> .agents/skills/*/SKILL.md
payload/ai-workflow/...          -> ai-workflow/...
```

The distribution manifest records every source-to-target mapping and source
checksum. `bootstrap.py` resolves and downloads an immutable Git commit,
`verify_package.py` validates the package, and `adopt.py` preflights and applies
one lifecycle operation. Installed repositories do not need the source checkout
or bootstrap skill for runtime behavior.

## Ownership

- Framework-owned files are updated only when their currently installed managed
  content matches the recorded checksum.
- Project-owned seeds are created only when absent and never overwritten.
- An existing root `AGENTS.md` is byte-preserved behind explicit managed markers.
- A conflicting skill or framework path fails the whole operation before writes.
- The installation manifest records checksums, provenance, version, and immutable
  source revision.
- Writes are preflighted and performed as a rollback-capable transaction.

Removal restores a clean pre-existing `AGENTS.md`, deletes only unchanged files
created by the framework, preserves pre-existing or modified files, and always
preserves project-owned profile and state.

## State precedence

Accepted repository decisions and durable state outrank an active workflow
artifact, which outranks private agent memory and chat recollection. Durable
specifications remain project-owned documents at the location declared in the
project profile; workflow records link to them rather than copying them.
