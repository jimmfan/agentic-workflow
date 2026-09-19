# Agent Workflow runtime resources

In the Agent Workflow source repository, this directory is authored canonical framework content.
In consuming repositories, the same paths hold reconstructable framework output.
It supplies the progressively loaded routing policy, terminology, state contract, and attribution used by the compact root policy.
Install and update replace the complete consuming-project directory with current snapshot bytes.

Durable project-owned Wayfinder state may live under sibling `.project-efforts/`, but that tree is outside the lifecycle boundary.
Lifecycle commands do not directly traverse, interpret, or change it.

## Contents

- `routing.md`: detailed minimum-workflow selection, composition, handling of unavailable selected skills, action authorization, evidence, and required route-marker rules.
- `terminology.md`: the single canonical source for Agent Workflow term meanings, consulted when a framework-specific term materially affects interpretation or behavior.
- `contracts/wayfinder-state.md`: lazily loaded map-first Wayfinder semantics for current maps, optional U#/F#/D# ledgers, independently useful E# files, identifiers, reconciliation, pruning, effort ending, and progressive loading.

The root policy loads routing, terminology, and specialized contracts progressively.
No hook, daemon, lifecycle controller, or telemetry analyzer is installed.

## Third-party license

The curated `code-review`, `codebase-design`, `domain-modeling`, `grilling`, `implement`, `prototype`, `research`, `tdd`, `to-spec`, `to-tickets`, and `wayfinder` skills are copied from or derived from [Matt Pocock's Skills for Real Engineers](https://github.com/mattpocock/skills), release `v1.2.3`.

### MIT License

Copyright (c) 2026 Matt Pocock

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.


## Ownership

In consuming repositories, `.agent-workflow/` is framework-owned, reconstructable, and replaceable from current snapshot content.
The ordinary distribution manifest is the current source-to-target map; no installed manifest, content hashes, provenance record, created-state bits, or history is written to a consuming repository.

`AGENTS.md` and `CLAUDE.md` live outside this directory because hosts require root policy files.
In `AGENTS.md`, one framework-owned region is bounded by the logical managed-begin and managed-end lines; every byte outside it is preserved as opaque project content.
Repeated install and update keep exactly one such region.
The existing `CLAUDE.md` composite integration remains unchanged.
The current curated skills live directly under `.agents/skills`.
Hosts with native support may expose those skills through their normal skill mechanism.
When they do not, the root and detailed routing policies may read the canonical `SKILL.md` files as repository instructions and execute only the method parts supported by current capabilities; this is not native skill invocation.
Their current directory names are reserved for Agent Workflow.
Install and update replace each complete current curated skill directory, including extra files, while preserving unrelated skill directories.
Remove deletes those current curated directories.
Existing content at those reserved names is ordinary install/update convergence input.
Wayfinder and Research are directly distributed maintained versions.

Wayfinder keeps project-owned durable coordination under `.project-efforts/`, outside framework lifecycle ownership.
A map can stand alone and links supporting records and lasting artifacts when needed.
The [state contract](contracts/wayfinder-state.md) owns record formats, selective preservation, resumption, map authoring, and map-versus-ticket responsibilities.
Specialist methods and their handoffs follow [detailed routing](routing.md); specialists create no separate Agent Workflow durable coordination state.

## Status and recovery

With no explicit target, the CLI uses the containing Git worktree root when Git can discover one and otherwise uses the current directory.
Explicit targets are used directly.
Repository state, `HEAD`, tracked changes, untracked files, and ignore rules do not gate lifecycle operations.

The bootstrap selects the highest stable `vX.Y.Z` release tag, resolves it to an immutable commit, and uses the lifecycle and payload from that one downloaded snapshot.
Ordinary framework updates do not require a separate CLI upgrade.
An explicit ref such as `--ref main` is an opt-in development or testing override.

Before mutation, the lifecycle checks composite ownership and managed roots and parents for malformed markers, symlink or unsupported entries, and escapes from the target.
Nested entries inside a replaceable managed directory are removed through ordinary convergence.
`status` reports managed drift or conflicts without a repository-wide Git safety concept.
There is no cross-surface transaction, backup, rollback journal, migration engine, or automatic skill retirement.
If a filesystem failure leaves partial changes, resolve the reported error and rerun the command to converge.

Install and update converge to the same current package state.
Remove deletes `.agent-workflow/` and the current curated skill directories, strips the managed regions from `AGENTS.md` and `CLAUDE.md`, and deletes either composite file only when no project-authored bytes remain.
Unrelated skill directories and all project-authored composite bytes remain.

If current curated-name directories exist but no Agent Workflow installation is recognizable, remove refuses before mutation rather than assuming those directories are framework-owned.

There is no migration subsystem.
Install and update replace this complete directory, so obsolete framework files disappear through ordinary convergence.
Skill directories outside the current curated inventory remain untouched.

Every user-facing final response ends with one compact route marker such as:

```text
[route: router -> debugging]
```

It is instruction-level observability, not telemetry or proof of execution, and must not trigger additional workflow work.
