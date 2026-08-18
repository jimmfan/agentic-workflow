---
name: agentic-workflow
description: Install, update, inspect, or safely remove the Agentic Workflow router and its optional curated provider skills in a project.
license: MIT
---

# Agentic Workflow bootstrap

Use this skill only for adoption and lifecycle maintenance. It installs a compact
instruction router that keeps simple work direct and progressively loads one
useful workflow for consequential work. Successful adoption leaves core routing
usable even when every optional provider is unavailable.

## Ownership contract

- `.agent-workflow/` is framework-owned and reconstructable. Install/update may
  replace the directory from current package bytes.
- `.agent-workflow-state/` and every entry under it are project-owned durable data.
  Create the directory when absent during install/update, but never seed,
  inventory, checksum, rewrite, or remove its contents.
- `AGENTS.md` and `CLAUDE.md` are composite. Replace only the unambiguous managed
  region and preserve project-region bytes. Stop on partial, duplicate, or
  reordered markers.
- Other required external integrations are created when absent, reused when
  exactly matching, and blocked when unknown content differs. The small install
  manifest records only evidence needed for safe external deletion.
- The finite provider set declared by the package is framework-owned,
  reconstructable output. Install/update may replace those exact directories,
  and remove deletes them; every unrelated skill directory is preserved. Apply
  adapters only to recognized pinned input in staging before target mutation.

Do not treat a missing historical file, old manifest detail, optional profile,
durable record, provider, or setup file as package corruption. Current desired
state is authoritative.

## Lifecycle commands

Run these from this skill directory, or use absolute script and target paths.
Except for `status` and `--dry-run`, they persistently change the named target:

```bash
python3 scripts/lifecycle.py install /path/to/project
python3 scripts/lifecycle.py update /path/to/project
python3 scripts/lifecycle.py status /path/to/project
python3 scripts/lifecycle.py remove /path/to/project
```

The target must be an existing non-root directory. All entrypoints require
Python 3.11 or newer. Use the public README bootstrap for normal end-user
installation because it resolves an immutable revision and validates archive
paths, types, counts, sizes, modes, and minimum runtime files.

Install/update first preflight composite boundaries, external collisions, and
target symlinks. They then stage the new
`.agent-workflow/`, apply rollback-protected external writes, swap the framework
directory, and verify current desired bytes. Missing or drifted reconstructable
files are replaced without historical checksum forensics.

After core success, lifecycle makes a best-effort offline projection from the
release's bundled, checksummed provider snapshot. It stages all 14 declared
skills, applies the Wayfinder local-mode and routed implicit-invocation adapters,
validates the effective projection, and reconciles every repairable declaration
together.
Runtime provider setup needs no GitHub CLI, Git, npm, npx, authentication, or
network access.

The 14 declared directories are framework-owned reconstructable output. An
exact directory is reused; a missing or different declared directory is
repaired from staging, and an unsafe path blocks the complete provider change.
Provider failure remains a warning and never rolls back or invalidates the core.
Status is incomplete until all 14 effective directories match. Remove deletes
exactly those declarations and preserves unrelated skill directories.

`status` is read-only and reports core `healthy`, `repairable`, or
`unsafe/conflict`. Missing optional state files and providers are normal. A
repairable result should be fixed with `update`; an unsafe path requires
resolving the named filesystem boundary first.

`remove` removes managed composite regions,
deletes only unchanged external files recorded as framework-created, removes
`.agent-workflow/`, and preserves `.agent-workflow-state/`, changed/pre-existing
external files, and unrelated skills.

## Release verification

Maintainers run this read-only gate from the skill directory:

```bash
python3 scripts/verify_package.py --tests
```

It strictly checks the explicit source-to-target mapping, synchronized versions,
package safety, routing/provider contracts, documentation, and acceptance tests.
Ordinary edits to already mapped payload files require no metadata refresh.
After adding, removing, or remapping a packaged file, or changing the framework
version, inspect the diff and then refresh only the generated manifest:

```bash
python3 scripts/verify_package.py --refresh-manifest --tests
```

Never refresh metadata to hide an unexplained change, edit install evidence to
force deletion, call `adopt.py` alone for a public network install, or delete
`.agent-workflow-state/` as a lifecycle repair.
