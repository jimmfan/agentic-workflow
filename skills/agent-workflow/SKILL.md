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

- `.agent-workflow/` is framework-owned and reconstructable. Install/update may
  replace the directory from current package bytes.
- `.agent-wayfinder/` and every entry under it are project-owned durable data.
  Create the directory when absent during install/update, but never seed,
  inventory, checksum, rewrite, or remove its contents.
- `AGENTS.md` and `CLAUDE.md` are composite. Replace only the unambiguous managed
  region and preserve project-region bytes. Stop on partial, duplicate, or
  reordered markers.
- Other required external integrations are created when absent, reused when
  exactly matching, and blocked when unknown content differs. The small install
  manifest records only evidence needed for safe external deletion.
- Declared curated skill files are framework-owned reconstructable output.
  Install/update restores those exact files to current package bytes while
  preserving every unrelated skill directory. Remove deletes an external file
  only when valid evidence says the framework created it and current bytes still
  match the recorded managed digest.

Do not treat a missing previously recorded target, stale framework version,
different valid source revision, or durable project content as package
corruption. Invalid install state fails closed and is never treated as an empty
installation. Current desired package bytes are authoritative after preflight.

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
Python 3.11 or newer. Use the packaged `agent-workflow` CLI for normal end-user
installation. It delegates to the bootstrap transport, which resolves an
immutable revision and validates archive paths, types, counts, sizes, modes,
and minimum runtime files.

Install/update first preflight install-state integrity, composite boundaries,
external collisions, retirements, symlinks, and special entries. They then stage the new
`.agent-workflow/`, apply rollback-protected external writes, swap the framework
directory, and verify current desired bytes. Missing or drifted reconstructable
files are replaced without historical checksum forensics.

One explicitly bounded transition recognizes only the exact pinned-main former
installation using an immutable declaration digest and complete no-follow proof
of all fourteen former skill trees. Only after complete proof does the same
transaction transfer eleven retained trees, remove Setup, Teach, and Triage,
retire the former declaration, and write current integrity-protected install
state. Any near match is an unsafe conflict with no mutation.

Fresh install and ordinary update distribute fifteen curated skills directly
from the ordinary payload. Missing or drifted declared files are repaired
together. A retirement conflict aborts before any target or manifest changes.

`status` is read-only and reports core `healthy`, `repairable`, or
`unsafe/conflict`. A missing desired target is repairable; malformed, truncated,
duplicate-key, bad-digest, or unsafe install state is a conflict. A repairable
result should be fixed with `update`; a conflict requires conservative manual
resolution of the named state or filesystem boundary first.

`remove` removes managed composite regions,
deletes only unchanged external files recorded as framework-created, removes
`.agent-workflow/`, and preserves `.agent-wayfinder/`, changed/pre-existing
external files, and unrelated skills.

## Release verification

Maintainers run this read-only gate from the skill directory:

```bash
python3 scripts/verify_package.py --tests
```

It strictly checks the explicit source-to-target mapping, synchronized versions,
package safety, routing and skill contracts, exact transition proof,
attribution, documentation, and acceptance tests.
Ordinary edits to already mapped payload files require no metadata refresh.
After adding, removing, or remapping a packaged file, or changing the framework
version, inspect the diff and then refresh only the generated manifest:

```bash
python3 scripts/verify_package.py --refresh-manifest --tests
```

Never refresh metadata to hide an unexplained change, edit install evidence to
force deletion, call `adopt.py` alone for a public network install, or delete
`.agent-wayfinder/` as a lifecycle repair.
