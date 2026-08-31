# Verification model

Verification is split so stale release bookkeeping cannot block safe end-user
reconciliation.

## Consumer safety

`bootstrap.py` is the public download boundary. Before executing package code it
resolves mutable refs to an immutable commit and rejects corrupt or oversized
archives, excessive package contents, excessive whole-archive parsing,
absolute/traversing/duplicate paths, links, special entries, unreviewed modes,
filesystem-root targets, and packages missing the minimum lifecycle files.
The archive is streamed, and unrelated repository entries do not consume the
tighter distributable-package member allowance. These checks prevent unsafe
extraction and execution.

The bootstrap does not run the full package verifier. Runtime reconciliation
requires the current source-to-target mapping, readable current source files,
valid install-state integrity, and safe target boundaries. The one exact
pinned-main transition additionally validates its immutable declaration and
complete former-tree proof before mutation. Attribution and frozen-fixture
self-verification remain maintainer-gate concerns. The distribution manifest
does not duplicate payload content hashes.

## Maintainer and CI gate

Run this read-only command from the **source repository root** in Bash on macOS,
Linux, WSL, or inside a Linux-based devcontainer. Zsh and similar POSIX shells
are also expected to work:

```bash
python3 skills/agent-workflow/scripts/verify_package.py --tests
```

It checks:

- Python syntax, package structure, regular-file modes, and synchronized versions;
- the exact current source-to-target mapping and synchronized version;
- the exact allowed authored payload, root-template, fifteen-skill, and
  thirty-four-skill-file inventories;
- absence of executable or host-customization content in the
  activation-sensitive payload namespace;
- directly distributed skill inventory and frontmatter, support-file closure,
  local references, complete attribution, frozen-fixture integrity, and
  production transition-proof parity;
- the source-only terminology glossary and project-language policy remain
  present, scoped, and absent from the distributed payload;
- current Agent Workflow-owned Wayfinder surfaces distinguish records from
  represented questions, evidence, conclusions, and choices; project-choice
  commitment from action authorization and host permission; route selection from
  truthful reporting of skill use, material execution, and completion evidence;
  and lifecycle ownership from durability and reconstructability;
- local Markdown links and behavioral scenario validation;
- lifecycle, install-state integrity, transaction rollback, data-safety, routing, cp1252, bootstrap, and
  stale-release-metadata tests;
- human-authored TOML behavioral scenario schema and fixture references; and
- deterministic behavior-harness, Wayfinder scenario, evaluator, and fixture
  reset tests.

Success ends with:

```text
OK: Agent Workflow package verification passed.
```

The pre-merge CI job then runs the repository evaluation-tooling tests as a
separate deterministic, network-free step:

```bash
python3 -m unittest discover -s evals/tests -p 'test_*.py' -v
```

They remain separate because `evals/` is repository tooling, not part of the
distributable package.

## Release tags

`skills/agent-workflow/VERSION` is the sole authored framework version and the
human-controlled release switch. Ordinary changes can reach `main` without
changing it. The distribution manifest contains only package mappings; a
version-only change does not require refreshing it. Adoption reads the version
directly from the package and records it in generated install metadata. After
the deterministic verifier succeeds on a push to `main`, a `VERSION` change
requests one annotated release tag on that exact verified commit.

The release job accepts only the package's `x.y.z` format, requires the version
to be greater than every existing semantic release tag, and refuses to reuse or
move an existing `vX.Y.Z` tag. It serializes release attempts and pushes only
the new tag without force. The first version increase after this workflow
reaches `main` will establish the first trustworthy release-tag baseline;
earlier history is intentionally not backfilled.

Do not create the release tag manually while preparing a branch; the verified
`main` workflow owns tag creation.

After intentionally adding, removing, or remapping a packaged payload file,
first inspect the diff. Then run this persistent refresh from the **source
repository root**:

```bash
python3 skills/agent-workflow/scripts/verify_package.py --refresh-manifest --tests
```

The refresh rewrites only
`skills/agent-workflow/payload/distribution/manifest.json`, then runs the same
gate. Ordinary edits to an already mapped payload file do not require a refresh.
Revert an unwanted refresh with version control. Do not refresh metadata to
conceal an unexplained mapping or version difference.

## Acceptance boundary

The suite prioritizes behavior that matters before 1.0:

- missing and drifted `.agent-workflow/` files are restored from current desired
  state, and obsolete internal files disappear;
- arbitrary unrecognized project-owned `.agent-wayfinder/` contents survive
  install, status, update, remove, reinstall, and repair of directly distributed
  skill files byte-for-byte;
- recognized local Wayfinder maps, F#/D# ledgers, and U#/E# files survive the
  same lifecycle sequence without schema interpretation or normalization;
- project regions in `AGENTS.md` and `CLAUDE.md` survive update and removal;
- malformed composite markers and unrecognized external collisions stop before
  partial mutation;
- symlink/root/archive traversal boundaries remain enforced;
- a source archive with more than 500 unrelated entries still installs when the
  package is within bounds, while excessive package contents and the separate
  whole-archive ceiling still fail closed;
- a fresh bootstrap archive installs all fifteen curated skills without GitHub
  CLI, Git, npm, npx, authentication, or network access;
- the maintainer gate binds the exact direct inventory and MIT attribution to
  the retained `v1.2.3` derived skills while distinguishing fixture-only former
  bytes;
- the raw `proof.json` byte stream is pinned by SHA-256 before parsing; the
  frozen fixture then verifies every path, entry type, and file digest before
  use and matches the immutable production proof for the fourteen former roots;
- only the exact pinned-main former installation transitions; declaration drift,
  missing or unexpected descendants, altered files, symlinks, special entries,
  and unsafe roots fail with zero mutation;
- a successful exact transition retains eleven derived skills, deletes Setup,
  Teach, and Triage, retires the former declaration, preserves four valid
  workflow `created` bits, and writes integrity-protected current state;
- fresh install records absent files as created and exact pre-existing files as
  not created; repair preserves that bit, and unknown differing content blocks;
- update repairs missing or drifted declared files, while retirement requires a
  missing target or matching framework-created evidence and otherwise aborts
  atomically;
- malformed, truncated, duplicate-key, bad-digest, invalid-type, invalid-path,
  or invalid-encoding install state fails closed for every lifecycle command;
- both injected transaction failures restore an identical canonical snapshot of
  bytes, entry types, existence, empty directories, and relevant modes;
- status is read-only and uses update's preflight, so `repairable` means update
  can actually complete;
- ASCII output remains writable on a cp1252 console; and
- mapped payload content changes require no metadata refresh, while an added,
  removed, or remapped payload file fails the release gate until the explicit
  install map is refreshed.

Wayfinder state contracts separately cover a valid map-only effort; creating and
appending current F# and D# ledger sections; allocating above the highest current
same-type identifier; rejecting malformed or duplicate identifiers; and
pruning only the selected section after bounded reference reconciliation. They
also cover empty-ledger removal, changed-state rejection, no-overwrite child
creation, separate U#/E# files, readable section anchors, and progressive
retrieval of relevant detail without an arbitrary file count.

Unrecognized-content coverage proves unmatched project-owned bytes remain unchanged
and are not treated as current references or allocation state. Identity-like
malformed entries and exact filesystem collisions are rejected. Lifecycle
preservation exercises install, update, status, remove, reinstall, and repair of
directly distributed skill files byte-for-byte.
The behavioral suite also keeps implementation tickets and other work-item
records out of Wayfinder, resumes relevant efforts
from the map, reconciles affected state after implementation,
excludes unrelated detail and efforts, reports outdated state without changing it during read-only work,
stops on unresolved reconciliation conflicts, and keeps unrelated efforts out
of a direct route.

The routing catalog separately covers direct work, standalone Discovery, direct
Wayfinder ready work, specialist-supported resolution of consequential issues,
the workflow transition from Wayfinder to Implementation, interrupted-specialist
session continuation from the map, direct continuation when an optional skill is
unavailable, an explicit user-invocation handoff, external read scope, and
responsibility for specifications, decisions, tickets, research findings,
prototypes, domain-model updates, and review reports. It is an executable
contract check, not proof that live skill discovery by an editor or host was
exercised.

## Useful failure diagnostics

If the gate fails:

1. use the first reported error or failed test as the primary diagnostic;
2. for stale metadata, inspect payload inventory, mapping, and version changes
   before refreshing;
3. for a lifecycle fixture, rerun that named `unittest` from the source root
   with `python3 -m unittest ...`; generated Python caches are ignored by Git
   and package verification and need no manual cleanup;
4. for an exact-transition fixture failure, inspect the frozen proof and pinned
   provenance; never regenerate it by installing the current package and editing
   it backward; and
5. never delete `.agent-wayfinder/` or unrecognized external content to make a test
   pass.

The deterministic GitHub Actions gate runs on Ubuntu. Native PowerShell and CMD
execution is outside the supported platform contract; Git Bash on native
Windows is best-effort. Do not claim live validation of host or editor skill
discovery, or of a host extension, unless it was actually performed and reported
separately.

## Behavioral layers

The same pre-merge command includes deterministic behavioral contract and
fixture tests. Live model runs remain opt-in because they require credentials,
may access external sources, consume quota, and are nondeterministic. Run and
interpret them using [Behavioral testing](behavioral-testing.md); never represent
their absence as a deterministic gate failure or a simulated fixture as live
agent evidence.
