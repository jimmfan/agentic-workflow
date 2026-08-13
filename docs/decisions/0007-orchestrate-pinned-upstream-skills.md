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

Select setup-matt-pocock-skills, wayfinder, teach, research, to-spec,
to-tickets, implement, tdd, and code-review as routed capabilities. Also install
grilling, domain-modeling, prototype, and codebase-design because selected
skills compose them directly. Do not select diagnosing-bugs; preserve the local
Debugging skill's diagnosis-only authorization, external-signal handling, and
durable state semantics.

Retain only local bounded Discovery, Debugging, Implementation integration, and
acceptance/integration Verification. Retire local Teach, Decomposition, and
Review plus their obsolete learning/ticket templates. Upstream artifacts and
identifiers remain canonical; framework state stores only pointers and return
targets.

Install providers through GitHub CLI 2.90.0 or newer with an authenticated
GitHub.com session. Preflight local and provider ownership before writes. Record
created versus pre-existing-compatible origins and all file checksums. Never
overwrite an incompatible same-named skill. Status remains local. Removal
deletes only clean framework-created provider directories and first binds state
to the exact declaration.

Provider versions never float. A maintainer upgrades only after reviewing a new
stable release, updating declaration identities, exercising live provider
compatibility, running the hermetic suite, and releasing a new framework
version. Do not use `--unpin` or `--force` as normal update behavior.

Run setup visibly only before the first tracker-dependent workflow when its
project configuration is absent. Use Teach only for explicit sustained learning
in a dedicated learning workspace. Upstream instructions do not expand user
authorization.

## Consequences

The root policy becomes a compact capability router rather than a collection of
method summaries. Detailed provider bodies are progressively discovered only
when selected. The installed on-disk footprint increases because complete
upstream directories are present, but the always-on prompt stays small and the
maintenance surface drops substantially.

Fresh dependency installation gains GitHub CLI and authentication prerequisites.
Normal runtime and status do not need network access. A provider upgrade is more
deliberate than running a generic package-manager update, and pre-existing
compatible dependencies may require explicit owner action when a future pin
changes. These costs are preferable to silent drift or overwriting project-owned
skills.

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
