# Installed Agentic Workflow

This directory is the reconstructable part of Agentic Workflow. Its purpose is
to supply the progressively loaded routing, state, provider, and template
contracts used by the compact root policy. Install/update may replace every file
here with current package bytes.

There is no current `.agent-workflow/state/` directory. Durable project-owned state
lives only under sibling `.agent-workflow-state/`. Lifecycle operations ensure that
directory exists but never create optional profile or workflow records, inventory its
contents, or remove it.

## Contents

- `routing.md`: detailed minimum-workflow selection, composition, invocation,
  fallback, authorization, evidence, and required route-marker rules.
- `providers.json`: the reviewed optional capability-to-provider declaration.
- `contracts/durable-state.md`: durable continuity, canonical artifact, conflict,
  and re-entry rules.
- `contracts/wayfinder-state.md`: lazily loaded map-first Wayfinder semantics for
  optional U#/E#/F#/D# knowledge and progressive loading.
- `contracts/project-profile.md`: optional advisory project-context rules.
- `templates/`: source material used only when an authorized workflow actually
  needs durable state.
- `install-manifest.json`: version/revision plus the small external/composite
  evidence required by safe update and removal.

The root policy and `routing.md` are the runtime. No hook, daemon, lifecycle
controller, or telemetry analyzer is installed.

## Ownership

`.agent-workflow/` is disposable. A missing, modified, extra, or obsolete file is
repairable with lifecycle `update`; no historical checksum investigation is
required. The distribution manifest records install targets, not duplicate
payload hashes; the installed runtime always uses current mapped source bytes.

`AGENTS.md` and `CLAUDE.md` live outside this directory because hosts require
root policy files. They contain one framework-managed region and one preserved
project region. Required local workflow skills similarly live under
`.agents/skills`. Unknown content at an unrecorded non-composite target blocks
installation instead of being overwritten.

Optional upstream providers also live under `.agents/skills`. The finite set
declared in `providers.json` is framework-owned reconstructable output; other
skill directories remain outside that boundary. Install/update stages the
complete declared projection, repairs missing or different declared directories
transactionally, and blocks on unsafe paths. Remove deletes exactly the declared
set. Provider failure does not affect the core. The Wayfinder and invocation
adapters require recognized pinned input before target mutation. Wayfinder's
effective body is an Agentic Workflow-owned runtime projection derived from the
unchanged pinned upstream snapshot.

Local Wayfinder data is a configured project-owned representation under
`.agent-workflow-state/wayfinder/`, never a distributed template or lifecycle-owned
tree. A map may stand alone; optional children preserve unresolved questions,
independently useful evidence, established facts, and committed decisions. The
map owns current state, blockers, dependencies, and next work. Substantial
decomposed work belongs to `to-tickets`, not Wayfinder. See
`contracts/wayfinder-state.md` for the precise, lazily loaded semantics. Other
durable workflows resume from their canonical DEC, IMP, or DBG record; there is
no global active index.

## Status and recovery

`healthy` means current core files match current desired state. `repairable`
means update can replace missing/drifted reconstructable or recorded managed
files. `unsafe/conflict` means an external collision, malformed composite, or
unsafe filesystem boundary needs explicit resolution.

Deleting `.agent-workflow/` and running update/install is a supported reconstruction
path. `.agent-workflow-state/` must remain in place. On removal, project state,
unrelated skill directories, pre-existing external files, and locally changed
external files are preserved; declared provider directories are deleted.

Every user-facing final response ends with one compact route marker such as:

```text
[route: router -> debugging]
```

It is instruction-level observability, not telemetry or proof of execution, and
must not trigger additional workflow work.
