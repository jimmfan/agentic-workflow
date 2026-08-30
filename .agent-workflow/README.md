# Installed Agent Workflow

This directory is the reconstructable part of Agent Workflow. Its purpose is
to supply the progressively loaded routing policy, state contract, and provider
configuration used by the compact root policy. Install/update may replace every
file here with current package bytes.

Durable project-owned state lives only under sibling `.agent-wayfinder/`. Install
and update may ensure that directory exists, but every lifecycle command otherwise
treats its contents as opaque: none seeds, inventories, normalizes, migrates,
rewrites, or removes them.

## Contents

- `routing.md`: detailed minimum-workflow selection, composition, invocation,
  fallback, authorization, evidence, and required route-marker rules.
- `providers.json`: the reviewed optional capability-to-provider declaration.
- `contracts/wayfinder-state.md`: lazily loaded map-first Wayfinder semantics for
  current maps, optional F#/D# ledgers, independently useful U#/E# files,
  identifiers, reconciliation, pruning, effort ending, and progressive loading.
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
effective body is an Agent Workflow-owned runtime projection derived from the
unchanged pinned upstream snapshot.

Local Wayfinder data is a configured project-owned representation under
`.agent-wayfinder/`, never a distributed template or lifecycle-owned
tree. A map may stand alone. The current default places supported F# facts in
optional `facts.md` and committed D# decisions in optional `decisions.md`, while
unresolved U# questions and substantial E# evidence earn separate files only
when they are independently useful coordination or retrieval units. The map
summarizes current coordination state, conditions blocking particular work,
dependencies, and ready work, indexing rather than duplicating supporting
detail. When resuming, read the map before retrieving a relevant ledger section
or U#/E# artifact.

Facts require traceable provenance, and decisions require responsible project
authority rather than evidence alone.

Before detailed decomposition, the map may state ready work directly. Substantial
decomposed work belongs to `to-tickets`, whose ticket artifact or ticket set owns
ticket contents, dependencies, ordering, and readiness. The map links that artifact
and may summarize the current ready handoff without mirroring ticket-level state. See
`contracts/wayfinder-state.md` for the precise, lazily loaded semantics.
Discovery, Debugging, Research, Prototype, and Domain Modeling remain stateless
specialists. Implementation is an execution handoff. Specialists create no
separate framework continuity records.

## Status and recovery

`healthy` means current core files match current desired state. `repairable`
means update can replace missing/drifted reconstructable or recorded managed
files. `unsafe/conflict` means an external collision, malformed composite, or
unsafe filesystem boundary needs explicit resolution.

Deleting `.agent-workflow/` and running update/install is a supported reconstruction
path. `.agent-wayfinder/` must remain in place. On removal, project state,
unrelated skill directories, pre-existing external files, and locally changed
external files are preserved; declared provider directories are deleted.

Every user-facing final response ends with one compact route marker such as:

```text
[route: router -> debugging]
```

It is instruction-level observability, not telemetry or proof of execution, and
must not trigger additional workflow work.
