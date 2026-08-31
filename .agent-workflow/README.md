# Installed Agent Workflow

This directory is reconstructable Agent Workflow output. It supplies the
progressively loaded routing policy, state contract, and attribution used by the
compact root policy. Install and update replace the complete directory with
current package bytes.

Durable project-owned Wayfinder state may live under sibling
`.agent-wayfinder/`, but that tree is outside the lifecycle boundary. Lifecycle
commands do not directly traverse, interpret, or change it. The repository-wide
Git cleanliness check may still report changes there as part of a dirty
worktree.

## Contents

- `routing.md`: detailed minimum-workflow selection, composition, handling of
  unavailable selected skills, action authorization, evidence, and required
  route-marker rules.
- `contracts/wayfinder-state.md`: lazily loaded map-first Wayfinder semantics for
  current maps, optional F#/D# ledgers, independently useful U#/E# files,
  identifiers, reconciliation, pruning, effort ending, and progressive loading.
- `THIRD_PARTY_NOTICES.md`: attribution and license terms for retained derived
  skills.

The root policy and `routing.md` are the runtime. No hook, daemon, lifecycle
controller, or telemetry analyzer is installed.

## Ownership

`.agent-workflow/` is framework-owned, reconstructable, and replaceable from
current package content. The ordinary distribution manifest is the current
source-to-target map; no installed manifest, content hashes, provenance record,
created-state bits, or history is written to a consuming repository.

`AGENTS.md` and `CLAUDE.md` live outside this directory because hosts require
root policy files. They contain one framework-owned region and one preserved
project region. Required local workflow skills similarly live under
`.agents/skills`.

The fifteen curated skills live directly under `.agents/skills`. Their current
directory names are reserved for Agent Workflow. Install and update replace
each complete current curated skill directory, including extra files, while
preserving unrelated skill directories. Remove deletes those current curated
directories. A pre-existing conflicting skill must be moved or renamed before
install. Wayfinder and Research are directly distributed maintained versions.

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

Before detailed decomposition, the map may state ready work directly. A durable
ticket or ticket set created by `to-tickets` maintains ticket contents,
dependencies, ordering, and readiness. The map links that durable ticket or
ticket set and may include the current ready-work reference without mirroring
ticket-level state; a chat-only draft remains session-local. See
`contracts/wayfinder-state.md` for the precise, lazily loaded semantics.
Discovery, Debugging, Research, Prototype, and Domain Modeling are specialists.
Specialists retain their methods and create no Agent Workflow durable
coordination state. Implementation is a workflow transition into execution.

## Status and recovery

Install, update, and remove require the exact Git worktree root, a valid `HEAD`,
and a completely clean tracked and untracked worktree. Before mutation they
reject untracked files under managed surfaces, ignored managed destinations,
malformed managed markers, symlinks, special entries, and paths that escape the
worktree. `status` is read-only and reports safety blockers without requiring a
clean tree.

Git is the recovery mechanism. There is no cross-surface transaction, backup,
rollback journal, migration engine, or automatic skill retirement. A failure
after mutation can leave a partial worktree diff; inspect `git status`, restore
with Git as appropriate, and retry.

Install and update converge to the same current package state. Remove deletes
`.agent-workflow/` and the current curated skill directories, strips the managed
regions from `AGENTS.md` and `CLAUDE.md`, and deletes either composite file only
when no project-authored bytes remain. Unrelated skill directories and all
project-authored composite bytes remain.

Legacy `.agent-workflow/providers.json` and obsolete Setup, Teach, or Triage
skill directories are detected but never migrated. Remove the legacy
`.agent-workflow/` tree and obsolete skill directories in a separate Git cleanup
commit, then install the current framework.

Every user-facing final response ends with one compact route marker such as:

```text
[route: router -> debugging]
```

It is instruction-level observability, not telemetry or proof of execution, and
must not trigger additional workflow work.
