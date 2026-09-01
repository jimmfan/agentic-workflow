---
name: agent-workflow
description: Install, update, inspect, or safely remove the Agent Workflow router and its directly distributed curated skills in a project.
license: MIT
---

# Agent Workflow bootstrap

Use this skill only for adoption and lifecycle maintenance. It installs a compact
instruction router that keeps simple work direct and progressively loads one
useful workflow for consequential work. Successful adoption installs the exact
fifteen-skill curated surface mapped by the package.

## Ownership contract

- `.agent-workflow/` is framework-owned and reconstructable after adoption.
  Install/update replace the complete directory from current package bytes;
  remove deletes it. On first adoption, a pre-existing `.agent-workflow/` that
  is not recognized as an existing Agent Workflow installation blocks adoption
  instead of being replaced.
- Each current curated `.agents/skills/<name>/` directory is framework-owned and
  reconstructable. Install/update replace the complete named directory, including
  deleting extra files inside it; remove deletes it. Unrelated skill directories
  remain untouched. Current curated names are reserved after adoption, so move or
  rename any project-owned skill with the same name before installing.
- `.agent-wayfinder/` and every entry under it are project-owned durable data.
  Lifecycle operations do not directly traverse, interpret, or change it.
  Repository-wide Git cleanliness checks may still observe changes under it.
- `AGENTS.md` is composite. Replace only one unambiguous managed region and
  preserve every byte outside it as opaque project content. Stop on unknown,
  partial, duplicate, interleaved, or reordered marker layouts. Both composite
  parsers accept logical LF or CRLF marker lines; the existing `CLAUDE.md`
  output protocol remains unchanged.

The ordinary distribution manifest is only the current source-to-target map.
There is no installed manifest, content-integrity state, origin or deletion
provenance, historical inventory, automatic retirement, backup tree,
cross-surface transaction, or rollback mechanism. Git is the recovery boundary.

## Lifecycle commands

Run these from this skill directory, or use absolute script and target paths.
Except for `status` and `--dry-run`, they persistently change the named target:

```bash
python3 scripts/lifecycle.py install /path/to/project
python3 scripts/lifecycle.py update /path/to/project
python3 scripts/lifecycle.py status /path/to/project
python3 scripts/lifecycle.py remove /path/to/project
```

The target must be exactly a Git worktree root with a valid `HEAD`. Before
`install`, `update`, or `remove`, the full tracked and untracked worktree must be
clean, no managed destination may be ignored, and no managed root or parent may
be a symlink, special entry, or escape from the worktree. These commands stop
before mutation when a gate fails. `status` is read-only and does not require a
clean worktree, but reports any condition that would block mutation. All
entrypoints require Python 3.11 or newer.

Use the packaged `agent-workflow` CLI for normal end-user installation. It uses
the bootstrap transport, which resolves an immutable revision and validates
archive paths, types, counts, sizes, modes, and minimum runtime files before
calling this lifecycle.

`install` and `update` use the same convergence operation: replace
`.agent-workflow/`, replace every current curated skill directory, and update
managed composite regions while preserving project bytes and unrelated skills.
Repeated convergence leaves exactly one managed block in each composite file.
`remove` deletes those current managed directories and removes the composite
regions, deleting a composite file only when no project bytes remain. `--dry-run`
reports the operation without changing the target.

There is no migration subsystem. Complete replacement of `.agent-workflow/`
removes obsolete framework files during ordinary convergence, so a clean
existing installation needs no preliminary cleanup commit. Skill directories
outside the current curated inventory remain untouched; do not add a historical
retired-name list.

Writes are intentionally not globally transactional. If an ordinary write fails
mid-operation, the command reports that partial changes may exist and directs the
operator to inspect `git status`, restore with Git, and retry from a clean
worktree.

## Release verification

Maintainers run this read-only gate from the skill directory:

```bash
python3 scripts/verify_package.py --tests
```

It checks the current source-to-target mapping, package safety, complete curated
skill directories, attribution, a small set of load-bearing routing and skill
contracts, checked-in projection equality, and acceptance tests.
Ordinary edits to already mapped payload files require no metadata refresh.
After adding, removing, or remapping a packaged file, inspect the diff and then
refresh only the generated manifest:

```bash
python3 scripts/verify_package.py --refresh-manifest --tests
```

Never refresh metadata to hide an unexplained change, create installation
history, or touch `.agent-wayfinder/` as a lifecycle repair.
