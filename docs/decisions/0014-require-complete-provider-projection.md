# ADR-0014: Require complete declared provider projection

- Status: accepted
- Date: 2026-08-16
- Amends: ADR-0010
- Amended by: ADR-0015

## Context

Agentic Workflow declares a pinned set of Matt Pocock skills for Codex and
GitHub Copilot under their shared `.agents/skills/` discovery location. The v0
lifecycle installed each missing skill directly into the target as an
independent best-effort operation. A rate limit, network error, or false-success
installer response could therefore leave a prefix of the declared inventory
visible while the manifest still described the full provider environment.

The development checkout demonstrated this failure with only setup, Wayfinder,
Teach, and Research present. Ten declared skills were absent, including
Wayfinder composition dependencies such as Grilling, Domain Modeling, and
Prototype. Automatically invoking Wayfinder in that state is unreliable.

## Decision

Treat the provider declaration as one desired projection inventory for every
host marked available at the shared discovery location. Existing same-named
directories remain independently owned and are never replaced. Install or
update handles the currently missing declared set as one small transaction:

1. install each exact pinned path into a same-filesystem temporary staging root;
2. require exactly the missing declared directory names, a usable `SKILL.md`,
   reviewed source metadata, Codex metadata, and invocation compatibility;
3. apply any declared Agentic Workflow provider adapter in staging;
4. recheck that every destination is still absent; and
5. move the complete staged set into `.agents/skills/`, rolling back moved
   directories if projection fails.

Any download, validation, inventory, or projection failure commits none of that
missing set. A later install/update retries the same missing inventory. Provider
failure still does not roll back or invalidate a successful core framework
installation, but provider status is explicitly incomplete until every declared
skill is usable and every adapter is ready.

Keep the mechanism deliberately narrow: no provider ownership database,
automatic replacement, provider upgrade engine, or automatic removal. Do not
expand the declared inventory without a separately demonstrated dependency.

## Consequences

Fresh installations cannot expose a partial Matt Pocock environment. Existing
partial installations converge on the next successful update without modifying
the provider directories already present. Wayfinder's declared composition
dependencies become available before the provider projection is reported ready.

The provider projection remains optional relative to core routing. When GitHub
CLI, authentication, or network access is unavailable, the core remains usable
and routing falls back truthfully, while status reports the provider projection
as incomplete rather than implying readiness.

The staging transaction protects only newly missing paths. It does not claim
ownership of pre-existing skills, replace them, inventory their full contents,
or delete them on removal.

## Alternatives considered

- Keep independent direct installs and rely on reruns: rejected because a
  partially visible dependency graph can be invoked before a successful rerun.
- Install the whole upstream repository with `--all`: rejected because it would
  expand the reviewed provider inventory beyond the skills intentionally
  declared by Agentic Workflow.
- Vendor the provider directories: rejected because it would fork upstream
  methodology and duplicate provider ownership.
- Restore the former checksum/provenance database: rejected because complete
  projection needs a staging boundary, not package-manager lifecycle state.
