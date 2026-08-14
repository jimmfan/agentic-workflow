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
and POSIX/Windows mode semantics. It also proves transactional payload
post-check rollback, manifest-derived seed cleanup, retention of pre-existing
empty parent directories, and exact package-owned predecessor authentication.
Negative cases cover changed/omitted current records, forged retired paths,
unauthenticated restoration bytes, and provider identity drift that generated
manifest refresh cannot bless. Lifecycle coverage also proves that fresh root
policies expose byte-preserved project regions, legacy framework-created
`CLAUDE.md` files and exact pre-existing imports migrate without losing setup
edits or removal identity, recorded framework revisions fail closed and bind
status/removal to the exact loaded package, pre-existing provider bodies are
rejected without ownership state, installer-transformed bytes are recorded at
install time, ordinary local edits and forged extra-file inventories remain
protected, declaration updates reject unknown old names and never replace an
unowned directory, provider removal rolls back a failed quarantine
transaction before commit and reports/retains a cleanup failure after commit,
and project readiness observations remain separate from
payload/provider integrity. Profile fixtures cover the canonical uninitialized
seed, permissive readable-content classification, empty/unreadable/unsafe paths,
and byte preservation without lifecycle migration; existing project-owned
profiles are never rewritten. Ownership fixtures prove that `.ai-workflow/` is
reconstructable, `.ai-workflow-state/` survives install/update/remove/reinstall,
`active.md` is not created until needed, legacy durable paths are reported but
never moved, and exact surviving provider/integration files can reconstruct
conservative ownership after framework-directory deletion.

`test_controller.py` exercises the host-neutral enforcement core directly. It
covers actionable session bootstrap, exact-declaration auto-approval and
lookalike rejection, per-prompt route reset, the pre-execution route checkpoint,
direct/read-only terminal work, ambiguous and mutating opaque commands,
diagnosis-mode native write denial, truthful user-only provider execution,
digest-bound durable-state conflict resolution, evidence-linked completion,
strict existing active-state validation plus safe first creation, metadata-only
transient state outside the repository, and one-block Stop loop prevention. Static checks
validate the active VS Code Preview adapter and keep Codex, Claude Code, Copilot
CLI, and Copilot cloud capability claims distinct. This is hermetic contract
coverage, not proof that a live host loaded its hooks or suppressed an approval
dialog.

Workflow contract tests keep the installed root policy within its orchestration
kernel budget and verify that detailed routing, invocation, composition, host,
state, verification, and route-label behavior remains available from the
managed progressive routing contract. Lifecycle tests inspect both the composed
installed `AGENTS.md` and `.ai-workflow/routing.md`.

Synthetic historical-package fixtures receive explicit fixture-only
accepted-predecessor records in their copied new package. They exercise the
planner without expanding production trust. Hermetic bootstrap packages also
receive a fixture-only provider identity lock matching their deterministic
source bodies; production `--refresh-manifest` never rewrites the reviewed
provider lock.

`route-observability-scenarios.json` covers direct handling, dominant workflows,
workflow-plus-capability composition, user-only handoffs, setup/profile
readiness, read-only behavior, and the no-extra-execution guarantee.
`decision-contract-scenarios.json` records the corresponding semantic decision
categories independently of scenario numbering. Static verification checks
their invocation, authorization, state-effect, line-format, and centralized
policy contracts; replay the route cases in a consuming host to test instruction
compliance end to end.

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
