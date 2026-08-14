# Installed Agentic Workflow

This directory is the reconstructable part of Agentic Workflow. Its purpose is
to supply the progressively loaded routing, state, provider, and template
contracts used by the compact root policy. Install/update may replace every file
here with current package bytes.

There is no current `.ai-workflow/state/` directory. Durable project-owned state
lives only under sibling `.ai-workflow-state/`. Lifecycle operations ensure that
directory exists but never create optional profile/active files, inventory its
contents, or remove it.

## Contents

- `routing.md`: detailed minimum-workflow selection, composition, invocation,
  fallback, authorization, evidence, and optional route-marker rules.
- `providers.json`: the reviewed optional capability-to-provider declaration.
- `contracts/durable-state.md`: durable continuity, canonical artifact, conflict,
  and re-entry rules.
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
required. Generated source checksums are maintainer release metadata and are not
consulted by the installed runtime.

`AGENTS.md` and `CLAUDE.md` live outside this directory because hosts require
root policy files. They contain one framework-managed region and one preserved
project region. Required local workflow skills similarly live under
`.agents/skills`. Unknown content at an unrecorded non-composite target blocks
installation instead of being overwritten.

Optional upstream providers may also live under `.agents/skills`, but they are
not framework-owned. Existing directories are preserved, provider failure does
not affect the core, and provider removal is manual.

## Durable compatibility import

Only these old locations are recognized:

- `.ai-workflow/project-profile.md`
- `.ai-workflow/state/active.md`
- `.ai-workflow/state/records/`
- `.ai-workflow/state/archive/`

Missing sources are ignored. An absent canonical destination receives the data,
an identical destination reconciles, and a conflicting or unsafe destination
stops while preserving both. Historical framework files such as
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

Optional route visibility uses one compact response marker such as:

```text
[route: router -> debugging]
```

It is instruction-level metadata, not telemetry or proof of execution.
