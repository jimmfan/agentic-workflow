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
requires only the current source-to-target mapping and readable current source
files. Optional provider setup similarly validates only the inventory, safe
filesystem shape, references, metadata, and adapter preconditions needed to
project usable skills. Release checksum, provenance, and license bookkeeping is
left to the maintainer gate. The distribution manifest does not duplicate
payload content hashes.

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
- absence of deferred controller, hook, and observability payloads;
- routing, authorization, durable-state, and provider declaration contracts;
- thin-router word budgets and deterministic positive/negative escalation
  contracts (not live model-routing proof);
- local Markdown links plus the lifecycle-acceptance and routing-decision JSON
  catalog schemas;
- lifecycle, data-safety, routing, provider-isolation, cp1252, bootstrap, and
  stale-release-metadata tests;
- human-authored TOML behavioral scenario schema and fixture references; and
- deterministic behavioral contract, evaluator, reset, and fixture lifecycle
  tests.

Success ends with:

```text
OK: Agent Workflow package verification passed.
```

After intentionally adding, removing, or remapping a packaged payload file, or
changing the framework version, first inspect the diff. Then run this persistent
refresh from the **source repository root**:

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
- arbitrary `.agent-wayfinder/` contents survive install, update, remove, and
  reinstall byte-for-byte;
- canonical local Wayfinder maps and human-edited child Markdown survive the
  same lifecycle sequence without schema validation or normalization;
- project regions in `AGENTS.md` and `CLAUDE.md` survive update and removal;
- malformed composite markers and unknown external collisions stop before
  partial mutation;
- symlink/root/archive traversal boundaries remain enforced;
- a source archive with more than 500 unrelated entries still installs when the
  package is within bounds, while excessive package contents and the separate
  whole-archive ceiling still fail closed;
- provider failure leaves a successful core install usable;
- a fresh bootstrap archive projects all 14 declared provider skills with an
  empty `PATH`, proving runtime setup does not require GitHub CLI, Git, npm,
  npx, authentication, or network access;
- the maintainer gate binds the bundled provider checksum, exact inventory,
  resolved commit provenance, per-skill source metadata, local-reference
  closure, and MIT license to the exact reviewed release identity without
  turning those release checks into an end-user runtime gate;
- the installed source-checkout provider declaration must match the packaged
  declaration, while the maintainer refresh command refuses package-local output;
- update completes an exact partial projection, reuses exact existing
  directories, and replaces modified, extra-file, malformed, raw-upstream, or
  older declared directories as one rollback-protected transaction;
- unsafe declared paths block provider mutation, remove deletes only the
  declared projection, and unrelated skill directories are preserved;
- the unchanged raw Wayfinder snapshot is recognized before the owned runtime
  body is projected in release-local staging, while changed target bytes are
  repaired and status remains read-only;
- the implicit-invocation adapter automatically exposes To Spec, To Tickets,
  and Implement from the bundled projection, is idempotent,
  keeps Setup, Teach, and Triage user-only, and rejects unexpected activation
  metadata without a partial provider projection;
- ASCII output remains writable on a cp1252 console; and
- mapped payload content changes require no metadata refresh, while an added,
  removed, or remapped payload file fails the release gate until the explicit
  install map is refreshed.

Behavioral contracts separately cover creating map-first Wayfinder state with
optional U#/E#/F#/D# children, keeping implementation work-item artifacts out of
Wayfinder, resuming relevant map state, reconciling affected state after
implementation, progressively excluding unrelated children and efforts,
reporting stale state without mutation during read-only work, stopping on
unresolved reconciliation conflicts, and keeping unrelated efforts out of a
direct route.

The frozen `wayfinder-local-state-smoke-v1` campaign and its archived results
retain the former U/D/T rubric for reproducibility. They are historical evidence,
not the current Wayfinder acceptance contract; do not edit or reuse that frozen
grader to claim coverage of the map-first U/E/F/D model.

The routing catalog separately covers direct work, standalone Discovery,
direct and specialist-backed Wayfinder frontiers, Wayfinder-to-Implementation
handoff, interrupted-specialist re-entry from the map, host-native fallback,
explicit provider handoff, external read scope, and provider-artifact
ownership. It is an executable contract check, not proof that a live editor or
provider service was exercised.

## Useful failure diagnostics

If the gate fails:

1. use the first reported error or failed test as the primary diagnostic;
2. for stale metadata, inspect payload inventory, mapping, and version changes
   before refreshing;
3. for a lifecycle fixture, rerun that named `unittest` from the source root
   with `python3 -m unittest ...`; generated Python caches are ignored by Git
   and package verification and need no manual cleanup;
4. for a release snapshot refresh issue, run the maintainer command in a
   networked environment with GitHub CLI authentication; ordinary target
   install/update must remain fully offline; and
5. never delete `.agent-wayfinder/` or unknown external content to make a test
   pass.

The deterministic GitHub Actions gate runs on Ubuntu. Native PowerShell and CMD
execution is outside the supported platform contract; Git Bash on native
Windows is best-effort. Do not claim live validation of any host, editor,
provider network, or host extension unless it was actually performed and
reported separately.

## Behavioral layers

The same pre-merge command includes deterministic behavioral contract and
fixture tests. Live model runs remain opt-in because they require credentials,
may access external sources, consume quota, and are nondeterministic. Run and
interpret them using [Behavioral testing](behavioral-testing.md); never represent
their absence as a deterministic gate failure or a simulated fixture as live
agent evidence.
