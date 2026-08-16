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

- `.ai-workflow/` is framework-owned and reconstructable. Install/update may
  replace the directory from current package bytes.
- `.ai-workflow-state/` and every entry under it are project-owned durable data.
  Create the directory when absent during install/update, but never seed,
  inventory, checksum, rewrite, or remove its contents.
- `AGENTS.md` and `CLAUDE.md` are composite. Replace only the unambiguous managed
  region and preserve project-region bytes. Stop on partial, duplicate, or
  reordered markers.
- Other required external integrations are created when absent, reused when
  exactly matching, and blocked when unknown content differs. The small install
  manifest records only evidence needed for safe external deletion.
- Provider directories are optional and independent. Preserve every existing
  same-named directory and every provider directory on remove. A narrowly
  declared Wayfinder adapter may update only a recognized pinned method body and
  exact activation metadata; unknown or modified content is never rewritten.

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

Install/update first preflight durable migrations, composite boundaries,
external collisions, and target symlinks. They then stage the new
`.ai-workflow/`, apply rollback-protected external writes, swap the framework
directory, and verify current desired bytes. Missing or drifted reconstructable
files are replaced without historical checksum forensics.

The only compatibility imports are:

- `.ai-workflow/project-profile.md` ->
  `.ai-workflow-state/project-profile.md`
- `.ai-workflow/state/active.md` -> `.ai-workflow-state/legacy-active.md`
- `.ai-workflow/state/records/` -> `.ai-workflow-state/records/`
- `.ai-workflow/state/archive/` -> `.ai-workflow-state/archive/`

Ignore a missing source. Move to an absent destination, accept an identical
destination, and stop while preserving both sides on a differing or unsafe
destination. `legacy-active.md` preserves historical bytes only; current
workflows never create, read, or update it. Never recreate
`.ai-workflow/state/README.md`.

After core success, lifecycle makes a best-effort provider install for missing
declared skills with `gh skill install`. GitHub CLI absence, authentication,
network, or provider failure is a warning and never rolls back or invalidates
the core. The complete missing declared set is staged, validated, and projected
together, so a failed attempt exposes none of that set. Update does not replace
existing provider directories. It may apply the declared Wayfinder local-mode
adapter only when pinned source metadata, the method-body fingerprint, adapter
markers, and exact activation metadata are recognized; unexpected bytes are
preserved and reported without a partial write.
Provider status is incomplete until every declared skill is usable. Remove
explains that provider cleanup is manual because v0 keeps no provider ownership
database.

`status` is read-only and reports core `healthy`, `repairable`, or
`unsafe/conflict`. Missing optional state files and providers are normal. A
repairable result should be fixed with `update`; a conflict requires resolving
the named project-content or unsafe-path boundary first.

`remove` migrates named legacy durable state, removes managed composite regions,
deletes only unchanged external files recorded as framework-created, removes
`.ai-workflow/`, and preserves `.ai-workflow-state/`, changed/pre-existing
external files, and providers.

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
`.ai-workflow-state/` as a lifecycle repair.
