# Test boundary

The v0 suite tests the behavior Agentic Workflow owns, rather than reproducing
optional provider internals or deferred runtime systems.

`test_lifecycle.py` covers:

- install/update/status/remove smoke behavior;
- current desired-state replacement for missing, drifted, extra, and obsolete
  `.ai-workflow/` files;
- byte-preservation of arbitrary `.ai-workflow-state/` contents across update,
  removal, and reinstall;
- narrow legacy durable-state migration and conflict preservation;
- composite project-region preservation and malformed-boundary rejection;
- external collision, symlink, filesystem-root, and deletion-evidence safety;
- provider failure isolation and preservation of existing provider content;
- cp1252-safe terminal output;
- strict CI rejection of stale generated checksums while runtime still accepts
  actual safe package bytes; and
- corrupt/traversing/link archive and minimum-runtime-file rejection.

`test_routing.py` validates that the decision catalog keeps dominant selection,
supporting capabilities, provider invocation, execution, authorization effects,
fallback, and blocked outcomes explicit. The optional route marker is checked as
instruction metadata, not telemetry.

`acceptance-scenarios.json` lists the end-to-end product acceptance cases.
`decision-contract-scenarios.json` retains representative routing and authority
decisions. Neither fixture claims a live editor, operating system, provider
network, or model was exercised.

From the source repository root, run:

```bash
python3 skills/agentic-workflow/scripts/verify_package.py --tests
```

The command is read-only unless `--refresh-manifest` is also supplied.
