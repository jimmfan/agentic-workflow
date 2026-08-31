# Installed Agent Workflow

This directory is the reconstructable part of Agent Workflow. Its purpose is
to supply the progressively loaded routing policy, state contract, attribution,
and lifecycle evidence used by the compact root policy. Install/update may replace every
file here with current package bytes.

Durable project-owned state lives only under sibling `.agent-wayfinder/`. Install
and update may ensure that directory exists, but every lifecycle command otherwise
treats its contents as uninterpreted project-owned content: none seeds,
inventories, normalizes, migrates, rewrites, or removes them.

## Contents

- `routing.md`: detailed minimum-workflow selection, composition, invocation,
  fallback, action authorization, evidence, and required route-marker rules.
- `contracts/wayfinder-state.md`: lazily loaded map-first Wayfinder semantics for
  current maps, optional F#/D# ledgers, independently useful U#/E# files,
  identifiers, reconciliation, pruning, effort ending, and progressive loading.
- `install-manifest.json`: version/revision plus the small external/composite
  evidence and integrity digest required by safe update and removal.
- `THIRD_PARTY_NOTICES.md`: attribution and license terms for retained derived
  skills and the bounded historical transition fixture.

The root policy and `routing.md` are the runtime. No hook, daemon, lifecycle
controller, or telemetry analyzer is installed.

## Ownership

`.agent-workflow/` is framework-owned, reconstructable, and replaceable from
current declared package content. A missing, modified, extra, or obsolete file
is repairable with lifecycle `update`; no historical checksum investigation is
required. The distribution manifest records install targets, not duplicate
payload hashes; the installed runtime always uses current mapped source bytes.

`AGENTS.md` and `CLAUDE.md` live outside this directory because hosts require
root policy files. They contain one framework-owned region and one preserved
project region. Required local workflow skills similarly live under
`.agents/skills`. Unrecognized content at an unrecorded non-composite target blocks
installation instead of being overwritten.

The fifteen curated skills live directly under `.agents/skills`. Their declared
files are framework-owned reconstructable output; other skill directories
remain outside that boundary. Install/update reconciles all mapped skill files,
repairs missing or drifted declared files transactionally, and blocks on unsafe
paths. Remove deletes a declared external file only when valid install evidence
says the framework created it and its bytes still match the recorded digest.
Wayfinder and Research are directly distributed reviewed effective versions.

Local Wayfinder data is a configured project-owned durable representation under
`.agent-wayfinder/`, never a distributed template or framework-owned lifecycle
tree. A map may stand alone. The current default places F# fact records
containing supported, scoped, revisable conclusions in optional `facts.md` and
D# decision records containing choices determined directly by accepted project
policy or committed by the person, role, or valid delegate with project decision
authority in optional `decisions.md`.
U# unresolved question records and E# evidence
records with source, scope, observation, and limitations earn separate files
only when they are independently useful coordination or retrieval units. The map
summarizes current coordination state, conditions blocking particular work,
dependencies, and ready work, indexing rather than duplicating supporting
detail. When resuming, read the map before retrieving a relevant ledger section
or U#/E# artifact.

New default maps retain `Blockers and dependencies` and use `None` when no blocker
or dependency applies. Other inapplicable empty headings may be omitted, while
existing maps remain valid without that heading or marker. This is authoring
guidance, not a recognition requirement or migration trigger.

Fact records identify the source or records from which their scoped conclusion
was derived. Decision records identify the accepted project policy that determines their
choice or the person, role, or valid delegate with project decision authority who
commits it; evidence alone cannot commit that choice.

Before detailed decomposition, the map may state ready work directly. Substantial
decomposed work belongs to `to-tickets`; its ticket or ticket set
maintains ticket contents, dependencies, ordering, and readiness. The map links the ticket or ticket set
and may include the current ready-work reference without mirroring ticket-level state. See
`contracts/wayfinder-state.md` for the precise, lazily loaded semantics.
Discovery, Debugging, Research, Prototype, and Domain Modeling are specialists.
Each specialist may create the artifact designated to maintain the result or return evidence, but creates
no Agent Workflow durable coordination state. Implementation is a workflow
transition into execution.

## Status and recovery

`healthy` means current core files match current desired state. `repairable`
means update can replace missing/drifted reconstructable or recorded managed
files. `unsafe/conflict` means invalid install state, an external collision,
malformed composite, unsafe retirement, or unsafe filesystem boundary needs
explicit resolution.

Invalid install state fails closed for status, install, update, and remove.
Manual recovery must preserve `.agent-wayfinder/`, project-authored composite
regions, unrelated skills, and any external content lacking safe deletion
evidence before re-establishing an absent installation. Deleting
`.agent-workflow/` alone is not sufficient while a framework-managed composite
region remains. There is no automatic recovery path.

On removal, project state, unrelated skill directories, pre-existing external
files, and locally changed external files are preserved. Unchanged files
recorded as framework-created are deleted, and explicit full removal may end
lifecycle management while truthfully reporting preserved content.

Every user-facing final response ends with one compact route marker such as:

```text
[route: router -> debugging]
```

It is instruction-level observability, not telemetry or proof of execution, and
must not trigger additional workflow work.
