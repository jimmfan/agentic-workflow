# ADR-0007: Orchestrate pinned upstream skills

- Status: partially superseded by ADR-0010, ADR-0011, ADR-0012, and ADR-0013
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

Make Agentic Workflow an orchestration and integration layer over a declarative,
optional provider set. Pin `mattpocock/skills` tag `v1.2.3` and record every
selected skill's path, invocation policy, and configuration requirements.

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
from installed provider metadata. Keep provider execution unavailable on Claude
Code because this package does not project skills from `.agents/skills` into
Claude's native `.claude/skills` location; host-native work remains available.

Retain only local bounded Discovery, Debugging, Implementation integration, and
acceptance/integration Verification. Retire local Teach, Decomposition, and
Review plus their obsolete learning/ticket templates. Upstream artifacts and
identifiers remain canonical; framework state stores only pointers and return
targets.

Install providers through GitHub CLI 2.97.0 or newer with an authenticated
GitHub.com session. Install the framework independently, then attempt provider
installation. Make the package declaration own the pinned repository, tag,
skill paths, invocation policy, and configuration requirements. Validate
required source/path/ref and invocation metadata after staging. Reject every
same-named directory when no provider ownership state exists. After activation,
record checksums of the bytes actually installed and use them to detect later
local modifications. Inner provider status remains local.

When a declaration changes, use local provider state as the ownership and
cleanliness baseline. Preserve the origin of retained matches, add genuinely
missing skills, and replace an incompatible directory only when state says
`created` or `reconstructed` and all recorded file checksums remain clean.
Preserve modified and pre-existing-compatible directories. Stage and validate
new provider bytes before mutation. Recreate a missing managed directory
normally, even when the provider baseline itself is unchanged. Removal deletes
only state-recorded, checksum-clean directories whose origin is `created` and
preserves incompatible, reconstructed, modified, extra-file, and
pre-existing-compatible directories.

Provider versions never float. A maintainer upgrades only after reviewing a new
stable release, updating declaration identities, exercising live provider
compatibility, running the hermetic suite, and releasing a new framework
version. Do not use `--unpin` or `--force` as normal update behavior.

Classification remains automatic from normal intent even when execution is not.
For a preferred user-only or unavailable provider, continue with host-native
capability unless the user explicitly required that provider or a genuine
configuration/safety boundary blocks work. In those blocking cases, return the
exact `$skill-name` or `/skill-name` handoff and do not simulate the skill,
create provider artifacts, write provider state, or claim execution. Use Teach
only for explicit sustained learning. Upstream instructions do not expand user
authorization.

Allow one dominant workflow or activity plus zero or more capabilities. A
capability can also be dominant when intent directly selects it; the declaration
does not encode one mutually exclusive skill per task. Supporting activity does
not itself create another durable record. ADR-0012 supersedes the former global
active-workflow constraint.

## Consequences

The root policy becomes a compact capability router rather than a collection of
method summaries. Hosts discover compact skill metadata, while a detailed
provider body loads only when actually invoked; a user-only selection alone does
not load it. The installed on-disk footprint increases because complete
upstream directories are present, but the always-on prompt stays small and the
maintenance surface drops substantially.

Routing can truthfully identify a useful provider while allowing normal work to
continue through host-native capability when that provider cannot run. Explicit
provider requests still receive an exact handoff. Claude Code can consume the
root policy while provider execution remains unsupported; avoiding a duplicate
provider tree keeps ownership and updates unambiguous.

Optional provider adoption gains GitHub CLI, authentication, and temporary pinned
staging prerequisites; framework adoption does not depend on them. Same-named
directories without provider state require manual reconciliation. Normal
runtime and the inner status checks remain local after that baseline is recorded;
the public bootstrap still downloads the exact framework package. A supported
cross-version update can retain locally recorded directories, add missing ones,
and migrate changed pinned bytes without manual deletion when ownership and
cleanliness are proven. Modified and pre-existing provider directories still
require explicit owner reconciliation. This is more deliberate than a generic
package-manager update and does not silently overwrite project-owned skills.

The framework 0.7.0 upgrade changes the curated set by adding `triage` while
retaining the v1.2.3 pin. Existing 0.6.0 targets therefore take the staged,
locally validated provider-baseline update path even though the upstream version is
unchanged. Existing clean directories are retained with their established
origins; only missing `triage` is added. This deterministically records the
new set without treating the declaration-schema change itself as provider state.

Repository-local origin and installed-hash history is useful ownership evidence
but is not tamper-evident. Deliberate coordinated state forgery can reclassify a
directory or its bytes. This accepted local-trust boundary keeps ordinary local
edits, extra files, and undeclared directories outside automatic replacement or
deletion without turning provider installation into source-file auditing.

## Later amendment

ADR-0013 supersedes this ADR's Wayfinder invocation-policy conclusion while
leaving the pinned provider, methodology ownership, other skill policies, and
host compatibility boundaries intact. Agentic Workflow now declares Wayfinder
implicit on Codex and GitHub Copilot and applies a narrow metadata overlay
during provider installation/update because the framework owns routing.

ADR-0015 later extends this into a fingerprinted local-mode adapter because
Codex loads the full provider body after selection. The upstream reasoning
method remains unchanged; the inserted adapter makes the accepted local storage
and U#/D#/T# lifecycle authoritative over incompatible tracker mechanics.

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
