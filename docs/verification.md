# Verification model

Verification is split so stale release bookkeeping cannot block safe end-user
reconciliation.

## Consumer safety

`bootstrap.py` is the public download boundary. Before executing package code it
resolves mutable refs to an immutable commit and rejects corrupt or oversized
archives, excessive entries, absolute/traversing/duplicate paths, links, special
entries, unreviewed modes, filesystem-root targets, and packages missing the
minimum lifecycle files. These checks prevent unsafe extraction and execution.

The bootstrap does not run the full package verifier. Runtime reconciliation
requires only the current source-to-target mapping and readable current source
files. The distribution manifest does not duplicate payload content hashes.

## Maintainer and CI gate

Run this read-only command from the **source repository root** in the macOS/Linux
host Terminal or the VS Code Dev Container terminal that owns the checkout:

```bash
python3 skills/agentic-workflow/scripts/verify_package.py --tests
```

It checks:

- Python syntax, package structure, regular-file modes, and synchronized versions;
- the exact current source-to-target mapping and synchronized version;
- absence of deferred controller, hook, and observability payloads;
- routing, authorization, durable-state, and provider declaration contracts;
- local Markdown links plus the lifecycle-acceptance and routing-decision JSON
  catalog schemas;
- lifecycle, data-safety, routing, provider-isolation, cp1252, bootstrap, and
  stale-release-metadata tests;
- human-authored TOML behavioral scenario schema and fixture references; and
- deterministic behavioral contract, evaluator, reset, and fixture lifecycle
  tests.

Success ends with:

```text
OK: Agentic Workflow package verification passed.
```

After intentionally adding, removing, or remapping a packaged payload file, or
changing the framework version, first inspect the diff. Then run this persistent
refresh from the **source repository root**:

```bash
python3 skills/agentic-workflow/scripts/verify_package.py --refresh-manifest --tests
```

The refresh rewrites only
`skills/agentic-workflow/payload/distribution/manifest.json`, then runs the same
gate. Ordinary edits to an already mapped payload file do not require a refresh.
Revert an unwanted refresh with version control. Do not refresh metadata to
conceal an unexplained mapping or version difference.

## Acceptance boundary

The suite prioritizes behavior that matters before 1.0:

- missing and drifted `.ai-workflow/` files are restored from current desired
  state, and obsolete internal files disappear;
- absent historical paths, including `.ai-workflow/state/README.md`, are normal;
- arbitrary `.ai-workflow-state/` contents survive install, update, remove, and
  reinstall byte-for-byte;
- no current active-index template is installed, while an old
  `.ai-workflow/state/active.md` survives as inert `legacy-active.md` data;
- canonical local Wayfinder maps and human-edited child Markdown survive the
  same lifecycle sequence without schema validation or normalization;
- named legacy durable state migrates only to an absent or identical destination,
  while conflicts preserve both sides and stop;
- project regions in `AGENTS.md` and `CLAUDE.md` survive update and removal;
- malformed composite markers and unknown external collisions stop before
  partial mutation;
- symlink/root/archive traversal boundaries remain enforced;
- provider failure leaves a successful core install usable;
- a fresh bootstrap archive projects all 14 declared provider skills with an
  empty `PATH`, proving runtime setup does not require GitHub CLI, Git, npm,
  npx, authentication, or network access;
- the bundled provider checksum, exact inventory, resolved commit provenance,
  per-skill source metadata, local-reference closure, and MIT license are bound
  to the exact reviewed release identity;
- the installed source-checkout provider declaration must match the packaged
  declaration, while the maintainer refresh command refuses package-local output;
- update completes an exact partial projection, exact existing directories are
  reused, and any modified, extra-file, malformed, or older same-named
  directory is preserved as a conflict that blocks every missing provider write;
- the Wayfinder local-mode adapter applies in release-local staging, while
  changed target bytes are preserved and status remains read-only;
- the implicit-invocation adapter automatically exposes To Spec, To Tickets,
  and Implement from the bundled projection, is idempotent,
  keeps Setup, Teach, and Triage user-only, and rejects unexpected activation
  metadata without a partial provider projection;
- ASCII output remains writable on a cp1252 console; and
- mapped payload content changes require no metadata refresh, while an added,
  removed, or remapped payload file fails the release gate until the explicit
  install map is refreshed.

Behavioral contracts separately cover creating the local Wayfinder map plus
U#/D#/T# children, resuming only relevant map state, reconciling the affected
map and ticket after implementation, progressively excluding an unrelated child
and effort, reporting stale state without mutation during read-only work,
stopping on an unresolved reconciliation conflict, and keeping an unrelated
existing effort out of a direct route.

The routing catalog separately covers direct work, local workflow selection,
host-native fallback, explicit provider handoff, record-based resume, external
read scope, and provider-artifact ownership. It is an executable contract
check, not proof that a live editor or provider service was exercised.

## Useful failure diagnostics

If the gate fails:

1. use the first reported error or failed test as the primary diagnostic;
2. for stale metadata, inspect payload inventory, mapping, and version changes
   before refreshing;
3. for a lifecycle fixture, rerun that named `unittest` from the source root;
4. for a release snapshot refresh issue, run the maintainer command in a
   networked environment with GitHub CLI authentication; ordinary target
   install/update must remain fully offline; and
5. never delete `.ai-workflow-state/` or unknown external content to make a test
   pass.

No live Windows, editor, provider-network, or host-extension validation should
be claimed unless it was actually performed and reported separately.

## Behavioral layers

The same pre-merge command includes deterministic behavioral contract and
fixture tests. Live model runs remain opt-in because they require credentials,
may access external sources, consume quota, and are nondeterministic. Run and
interpret them using [Behavioral testing](behavioral-testing.md); never represent
their absence as a deterministic gate failure or a simulated fixture as live
agent evidence.
