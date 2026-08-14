# Package tests

The suite proves that one public lifecycle safely coordinates the local payload
and exact pinned provider declaration without depending on live GitHub state.
Hermetic provider fixtures reproduce `gh skill` metadata and complete directory
shapes; live CLI compatibility is documented separately in
`docs/provider-research.md`.

Run the full release gate from the **macOS host Terminal at this repository
root** with Python 3.11 or newer. It is read-only for tracked source files and
automatically removes its temporary projects and archives:

```bash
python3 skills/agentic-workflow/scripts/verify_package.py --tests
```

Success ends with `OK: distributable package is internally consistent.` The
suite covers payload install/update/status/remove, provider pin and metadata
validation, adjacent resources, pre-existing/modified ownership, missing CLI
and auth preflight, post-preflight rollback, state-path injection, retired local
workflow migration, non-Git targets, path-independent packages, archive safety,
and POSIX/Windows mode semantics.

`route-observability-scenarios.json` contains five interactive contract cases
for Wayfinder, Implementation, multi-stage routing, effective-use filtering,
and the no-extra-execution guarantee. Static verification checks their exact
line format and centralized policy wiring; replay them in a consuming host to
test instruction compliance end to end.

Acceptance scenario 19 and the Wayfinder ownership checks cover native
identifier/label pass-through, absence of framework aliases, external tracker
IDs, retention of genuinely local record types, and exclusion of the detailed
legend from always-on context.

`test_observability.py` covers standard OTLP and current raw JSONL ingestion,
nested-agent token accounting, current VS Code and CLI skill encodings,
content/repository suppression, lower-fidelity Agent Debug provenance,
duplicate snapshots, incomplete tails, fallback totals, deterministic output,
tags, missing optional capability degradation, UTF-8 BOMs, Windows CRLF and
Windows-style paths, Unix LF, Linux/macOS paths, and visible unknown-schema
failure. All fixtures are local and content-free; the suite neither enables
telemetry nor contacts an agent host. These fixtures establish cross-platform
design coverage, not live Windows or Linux validation.

If the suite fails, start with the first named invariant or test. Do not refresh
the manifest to mask an unexplained payload difference. No reversal is normally
needed because test targets are temporary; if a Python interruption leaves a
directory named `agentic-workflow-test-*` under the system temporary directory,
inspect that exact directory before removing it.
