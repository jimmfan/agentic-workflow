# Installed Agent Workflow

This directory is reconstructable Agent Workflow output. It supplies the
progressively loaded routing policy, state contract, and attribution used by the
compact root policy. Install and update replace the complete directory with
current package bytes.

Durable project-owned Wayfinder state may live under sibling
`.agent-wayfinder/`, but that tree is outside the lifecycle boundary. Lifecycle
commands do not directly traverse, interpret, or change it.

## Contents

- `routing.md`: detailed minimum-workflow selection, composition, handling of
  unavailable selected skills, action authorization, evidence, and required
  route-marker rules.
- `contracts/wayfinder-state.md`: lazily loaded map-first Wayfinder semantics for
  current maps, optional F#/D# ledgers, independently useful U#/E# files,
  identifiers, reconciliation, pruning, effort ending, and progressive loading.

The root policy and `routing.md` are the runtime. No hook, daemon, lifecycle
controller, or telemetry analyzer is installed.

## Third-party license

The curated `code-review`, `codebase-design`, `domain-modeling`, `grilling`,
`implement`, `prototype`, `research`, `tdd`, `to-spec`, `to-tickets`, and
`wayfinder` skills are copied from or derived from
[Matt Pocock's Skills for Real Engineers](https://github.com/mattpocock/skills),
release `v1.2.3`.

### MIT License

Copyright (c) 2026 Matt Pocock

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.


## Ownership

`.agent-workflow/` is framework-owned, reconstructable, and replaceable from
current package content. The ordinary distribution manifest is the current
source-to-target map; no installed manifest, content hashes, provenance record,
created-state bits, or history is written to a consuming repository.

`AGENTS.md` and `CLAUDE.md` live outside this directory because hosts require
root policy files. In `AGENTS.md`, one framework-owned region is bounded by the
logical managed-begin and managed-end lines; every byte outside it is preserved
as opaque project content. Repeated install and update keep exactly one such
region. The existing `CLAUDE.md` composite integration remains unchanged.
Required local workflow skills similarly live under `.agents/skills`.

The fifteen curated skills live directly under `.agents/skills`. Their current
directory names are reserved for Agent Workflow. Install and update replace
each complete current curated skill directory, including extra files, while
preserving unrelated skill directories. Remove deletes those current curated
directories. Before first adoption is recognizable, existing directories at
current curated names are listed together and require one confirmation before
replacement. Recognized installations converge them without prompting.
Wayfinder and Research are directly distributed maintained versions.

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

With no explicit target, the CLI uses the containing Git worktree root when Git
can discover one and otherwise uses the current directory. Explicit targets are
used directly. Repository state, `HEAD`, tracked changes, untracked files, and
ignore rules do not gate lifecycle operations.

The bootstrap selects the highest stable `vX.Y.Z` release tag, resolves it to an
immutable commit, and uses the lifecycle and payload from that one downloaded
snapshot. Ordinary framework updates do not require a separate CLI upgrade. An
explicit ref such as `--ref main` is an opt-in development or testing override.

First adoption recognizes an existing installation only from a valid managed
composite region or exact current `.agent-workflow/` surface. If no installation
is recognizable and current curated skill directories already exist, install or
update lists them and asks once before replacement. Noninteractive collisions
fail with the conflicting paths; ambiguous composite ownership still fails before
confirmation.

Before mutation, the lifecycle checks composite ownership and managed roots and
parents for malformed markers, symlink or unsupported entries, and escapes from
the target. Nested entries inside a replaceable managed directory are removed
through ordinary convergence. `status` reports managed drift or conflicts
without a repository-wide Git safety concept. There is no cross-surface
transaction, backup, rollback journal, migration engine, or automatic skill
retirement. If a filesystem failure leaves partial changes, resolve the reported
error and rerun the command to converge.

Install and update converge to the same current package state. Remove deletes
`.agent-workflow/` and the current curated skill directories, strips the managed
regions from `AGENTS.md` and `CLAUDE.md`, and deletes either composite file only
when no project-authored bytes remain. Unrelated skill directories and all
project-authored composite bytes remain.

There is no migration subsystem. Install and update replace this complete
directory, so obsolete framework files disappear through ordinary convergence.
Skill directories outside the current curated inventory remain untouched.

Every user-facing final response ends with one compact route marker such as:

```text
[route: router -> debugging]
```

It is instruction-level observability, not telemetry or proof of execution, and
must not trigger additional workflow work.
