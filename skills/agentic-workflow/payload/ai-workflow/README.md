# Installed Agentic Workflow

This directory is the reconstructable part of Agentic Workflow. Its purpose is
to supply the progressively loaded routing, state, provider, and template
contracts used by the compact root policy. Install/update may replace every file
here with current package bytes.

There is no current `.ai-workflow/state/` directory. Durable project-owned state
lives only under sibling `.ai-workflow-state/`. Lifecycle operations ensure that
directory exists but never create optional profile or workflow records, inventory its
contents, or remove it.

## Contents

- `routing.md`: detailed minimum-workflow selection, composition, invocation,
  fallback, authorization, evidence, and required route-marker rules.
- `providers.json`: the reviewed optional capability-to-provider declaration.
- `contracts/durable-state.md`: durable continuity, canonical artifact, conflict,
  and re-entry rules.
- `contracts/wayfinder-state.md`: lazily loaded canonical local Wayfinder map,
  U#/D#/T# identity, and progressive-loading rules.
- `contracts/project-profile.md`: optional advisory project-context rules.
- `templates/`: source material used only when an authorized workflow actually
  needs durable state.
- `install-manifest.json`: version/revision plus the small external/composite
  evidence required by safe update and removal.

The root policy and `routing.md` are the runtime. No hook, daemon, lifecycle
controller, or telemetry analyzer is installed.

## Ownership

`.ai-workflow/` is disposable. A missing, modified, extra, or obsolete file is
repairable with lifecycle `update`; no historical checksum investigation is
required. The distribution manifest records install targets, not duplicate
payload hashes; the installed runtime always uses current mapped source bytes.

`AGENTS.md` and `CLAUDE.md` live outside this directory because hosts require
root policy files. They contain one framework-managed region and one preserved
project region. Required local workflow skills similarly live under
`.agents/skills`. Unknown content at an unrecorded non-composite target blocks
installation instead of being overwritten.

Optional upstream providers may also live under `.agents/skills`, but they are
not framework-owned. Existing directories are preserved, provider failure does
not affect the core, and provider removal is manual. Missing declared provider
skills are staged and projected as a complete set; status remains incomplete
until every declared skill is usable. The declared Wayfinder adapter may insert
the authoritative local-mode instructions and update activation metadata only
when the pinned method body and exact expected values are recognized. Unknown
or modified provider content remains untouched and is reported.

Local Wayfinder data is a configured project-owned representation under
`.ai-workflow-state/wayfinder/`, never a distributed template or lifecycle-owned
tree. It uses the effort map for re-entry. Other durable workflows resume from
their canonical DEC, IMP, or DBG record; there is no global active index.

## Durable compatibility import

Only these old locations are recognized:

- `.ai-workflow/project-profile.md`
- `.ai-workflow/state/active.md` -> `.ai-workflow-state/legacy-active.md`
- `.ai-workflow/state/records/`
- `.ai-workflow/state/archive/`

Missing sources are ignored. An absent canonical destination receives the data,
an identical destination reconciles, and a conflicting or unsafe destination
stops while preserving both. The legacy active file is preserved but never
consulted as current state. Historical framework files such as
`.ai-workflow/state/README.md` are neither required nor recreated.

## Status and recovery

`healthy` means current core files match current desired state. `repairable`
means update can replace missing/drifted reconstructable or recorded managed
files. `unsafe/conflict` means an external collision, malformed composite, or
unsafe filesystem boundary needs explicit resolution.

Deleting `.ai-workflow/` and running update/install is a supported reconstruction
path. `.ai-workflow-state/` must remain in place. On removal, project state,
provider directories, pre-existing external files, and locally changed external
files are preserved.

Every user-facing final response ends with one compact route marker such as:

```text
[route: router -> debugging]
```

It is instruction-level observability, not telemetry or proof of execution, and
must not trigger additional workflow work.
