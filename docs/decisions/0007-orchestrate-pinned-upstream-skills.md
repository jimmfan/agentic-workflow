# ADR-0007: Orchestrate pinned upstream skills

- Status: accepted
- Date: 2026-08-13

## Context

The framework had grown local versions of Teach, Decomposition, Review, and
implementation techniques that overlap with maintained public workflows. This
duplicated prompt bodies, created divergent terminology and artifacts, and
increased the always-maintained surface. At the same time, blindly tracking an
upstream branch would make behavior non-reproducible and could overwrite local
skills.

Research of `mattpocock/skills` stable tag `v1.2.3` and GitHub CLI 2.97.0 found
that `gh skill install` can select an exact nested directory, pin a tag, install
at project scope without a Git repository, copy adjacent resources, and inject
repository/path/ref/tree-SHA metadata. Project-scoped Codex and GitHub Copilot
skills share `.agents/skills`. Ordinary `gh skill update` skips pinned skills,
which provides the desired non-floating default.

## Decision

Make Agentic Workflow an orchestration and integration layer over a declarative
curated provider set. Pin `mattpocock/skills` tag `v1.2.3`, commit
`6acc160e4e0cd062dbbbd7a1b26ae92855edf07e`, and record every selected skill's
exact path, subtree SHA, and complete file inventory.

Select wayfinder, teach, research, to-spec, to-tickets, implement, tdd, and
code-review as routed capabilities. Install setup-matt-pocock-skills as the
explicit repository-configuration operation. Also install grilling,
domain-modeling, prototype, and codebase-design because selected skills compose
them directly. Install `triage` as a configuration dependency so setup emits the
triage-label vocabulary required by to-spec and to-tickets, but do not make
triage a normal user-facing route. Do not select diagnosing-bugs; preserve the
local Debugging skill's diagnosis-only authorization, external-signal handling,
and durable state semantics.

Represent capability selection, per-skill configuration requirements, and
per-host invocation policy as separate declaration dimensions. At the pinned
release, setup, Wayfinder, Teach, to-spec, to-tickets, implement, and triage are
user-only in both primary hosts; Research, TDD, Code Review, Grilling,
domain-modeling, prototype, and codebase-design are model-invocable. Validate
Codex semantics from each exact `agents/openai.yaml` and GitHub Copilot semantics
from each exact `SKILL.md` frontmatter. Keep all provider operations unavailable
on Claude Code because this package does not project them from `.agents/skills`
into Claude's native `.claude/skills` location.

Retain only local bounded Discovery, Debugging, Implementation integration, and
acceptance/integration Verification. Retire local Teach, Decomposition, and
Review plus their obsolete learning/ticket templates. Upstream artifacts and
identifiers remain canonical; framework state stores only pointers and return
targets.

Install providers through GitHub CLI 2.97.0 or newer with an authenticated
GitHub.com session. Preflight local and provider ownership before writes. Make
the package declaration own the canonical SHA-256 of every upstream file;
normalize an installed `SKILL.md` only by removing the exact GitHub-injected
provenance metadata after its full validation. Record created versus
pre-existing-compatible origins and installed checksums as local history, not
content authority. Never overwrite an incompatible same-named skill. Before
initial adoption, stage the exact pin independently and compare any pre-existing
directory against it rather than trusting mutable metadata or state hashes. The
inner provider-status check remains local once its exact framework package and
authenticated baseline are loaded; the public bootstrap still downloads the
package.

When a declaration changes, refuse unknown old-state skill names, stage the
complete new pin, authenticate existing declared directories against it,
downgrade retained directories to `preexisting-compatible`, and add only
missing declared skills. Never remove or replace an existing provider directory
in that transition. Removal considers only exact declaration names and deletes
only package-authentic, record-checksum-clean directories whose origin is
`created`; preserve incompatible, modified, extra-file, undeclared, and
pre-existing-compatible directories.

Provider versions never float. A maintainer upgrades only after reviewing a new
stable release, updating declaration identities, exercising live provider
compatibility, running the hermetic suite, and releasing a new framework
version. Do not use `--unpin` or `--force` as normal update behavior.

Classification remains automatic from normal intent even when execution is not.
For a selected user-only operation, return the exact `$skill-name` Codex or
`/skill-name` Copilot handoff and do not simulate the skill, create artifacts,
write state, or claim execution. Check setup prerequisites only for the selected
configuration-dependent workflow. When absent, select setup and return that same
kind of user-only handoff. Use Teach only for explicit sustained learning in a
dedicated learning workspace. Upstream instructions do not expand user
authorization.

Allow one dominant workflow or activity plus zero or more capabilities. A
capability can also be dominant when intent directly selects it; the declaration
does not encode one mutually exclusive skill per task. Supporting activity does
not itself transition the one durable active workflow.

## Consequences

The root policy becomes a compact capability router rather than a collection of
method summaries. Hosts discover compact skill metadata, while a detailed
provider body loads only when actually invoked; a user-only selection alone does
not load it. The installed on-disk footprint increases because complete
upstream directories are present, but the always-on prompt stays small and the
maintenance surface drops substantially.

Routing can truthfully identify the appropriate provider workflow on hosts that
require user invocation. That adds a short handoff round trip for user-only
skills, but preserves both ordinary-intent classification and upstream policy.
Claude Code can consume the root policy while provider execution remains
explicitly unsupported; avoiding a duplicate provider tree keeps ownership and
updates unambiguous.

Initial provider adoption gains GitHub CLI, authentication, and temporary exact
staging prerequisites even when same-named directories already exist. Normal
runtime and the inner status checks remain local after that baseline is recorded;
the public bootstrap still downloads the exact framework package. A same-pin
dependency-set change can retain authenticated directories and add only missing
ones. A future pin that changes canonical bytes instead fails closed and
requires explicit owner reconciliation or remove-then-install. This is more
deliberate than a generic package-manager update and preferable to silently
overwriting project-owned skills.

The framework 0.7.0 upgrade changes the curated set by adding `triage` while
retaining the v1.2.3 pin. Existing 0.6.0 targets therefore take the same staged,
authenticated provider-baseline update path even though the upstream version is
unchanged. Existing directories are retained and downgraded to
`preexisting-compatible`; only missing `triage` is added. This deterministically
records the complete new set without treating the declaration-schema change
itself as provider state.

Repository-local origin history is useful ownership evidence but is not
tamper-evident. A deliberate coordinated origin forgery can reclassify an exact,
unmodified canonical provider directory; the package-owned content identities
and declaration bounds still prevent deletion of modified, extra-file, or
undeclared content.

## Alternatives considered

- Continue local copies: avoids an install dependency but preserves duplicated
  maintenance, terminology drift, and weaker composition.
- Vendor upstream directories into this repository: reproducible, but makes the
  framework a fork/distribution of method bodies and obscures source metadata.
- Track upstream `main` or unpinned latest: simplest updates, but behavior changes
  without a framework review or release.
- Install only directly routed skill files: smaller footprint, but breaks
  adjacent-resource and nested-composition expectations.
- Replace local Debugging with diagnosing-bugs: more upstream delegation, but
  loses important authorization and non-test diagnostic boundaries.
