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
files. Generated source checksums are deliberately ignored at runtime.

## Maintainer and CI gate

Run this read-only command from the **source repository root** in the macOS/Linux
host Terminal or the VS Code Dev Container terminal that owns the checkout:

```bash
python3 skills/agentic-workflow/scripts/verify_package.py --tests
```

It checks:

- Python syntax, package structure, regular-file modes, and synchronized versions;
- the exact current generated mapping and source checksums;
- absence of deferred controller, hook, and observability payloads;
- routing, authorization, durable-state, and provider declaration contracts;
- local Markdown links and scenario-catalog structure; and
- lifecycle, data-safety, routing, provider-isolation, cp1252, bootstrap, and
  stale-release-metadata tests.

Success ends with:

```text
OK: Agentic Workflow package verification passed.
```

After an intentional payload or version change, first inspect the payload diff.
Then run this persistent refresh from the **source repository root**:

```bash
python3 skills/agentic-workflow/scripts/verify_package.py --refresh-manifest --tests
```

The refresh rewrites only
`skills/agentic-workflow/payload/distribution/manifest.json`, then runs the same
gate. Revert an unwanted refresh with version control. Do not refresh metadata
to conceal an unexplained source difference.

## Acceptance boundary

The suite prioritizes behavior that matters before 1.0:

- missing and drifted `.ai-workflow/` files are restored from current desired
  state, and obsolete internal files disappear;
- absent historical paths, including `.ai-workflow/state/README.md`, are normal;
- arbitrary `.ai-workflow-state/` contents survive install, update, remove, and
  reinstall byte-for-byte;
- named legacy durable state migrates only to an absent or identical destination,
  while conflicts preserve both sides and stop;
- project regions in `AGENTS.md` and `CLAUDE.md` survive update and removal;
- malformed composite markers and unknown external collisions stop before
  partial mutation;
- symlink/root/archive traversal boundaries remain enforced;
- provider failure leaves a successful core install usable;
- ASCII output remains writable on a cp1252 console; and
- stale generated checksums fail this release gate while runtime uses the actual
  safe package bytes.

The routing catalog separately covers direct work, local workflow selection,
host-native fallback, explicit provider handoff, active-state conflict, external
read scope, and provider-artifact ownership. It is an executable contract check,
not proof that a live editor or provider service was exercised.

## Useful failure diagnostics

If the gate fails:

1. use the first reported error or failed test as the primary diagnostic;
2. for stale metadata, inspect source and version changes before refreshing;
3. for a lifecycle fixture, rerun that named `unittest` from the source root;
4. for a live provider issue, verify `gh skill install --help` and authentication
   in the environment that owns the target; and
5. never delete `.ai-workflow-state/` or unknown external content to make a test
   pass.

No live Windows, editor, provider-network, or host-extension validation should
be claimed unless it was actually performed and reported separately.
