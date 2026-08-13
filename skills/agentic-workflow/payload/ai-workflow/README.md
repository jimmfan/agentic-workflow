# Installed AI engineering workflow

This directory holds project-specific context and durable state for the
repository's AI engineering workflow. Shared always-on policy is the compact
root `AGENTS.md`, imported for Claude Code by root `CLAUDE.md`; detailed
workflows load from `.agents/skills/` only when relevant or when explicitly
invoked with
`/workflow-discovery`, `/workflow-teach`, `/workflow-decomposition`,
`/workflow-implementation`, `/workflow-debugging`, `/workflow-verification`, or
`/workflow-review`.

`project-profile.md` and `state/active.md` are project-owned. Complete the
profile before relying on project checks, including the canonical locations for
durable specifications and implementation tickets. State records link to
canonical specification and native-ticket bodies rather than copying them.
Framework updates never overwrite those files. Contracts, templates, skills,
the state contract, and this file are framework-owned; the generated
`install-manifest.json` records their installed
checksums, pre-install provenance, and source revision status.

Use the public bootstrap command documented by the framework repository to
inspect, update, or remove an installation. Lifecycle operations apply by
default; `--dry-run` prints a nonmutating plan. Locally changed framework files
cause an update conflict.
Removal preserves changed and pre-install files plus all project-owned content,
restores project instructions from clean composite `AGENTS.md` and `CLAUDE.md`
files, and removes the installation manifest. Removal requires the exact
installed version's source.

The host agent owns normal engineering, editing, commands, native subagents,
approvals, and verification. No external agent runtime is installed or required.
Promoting any lesson into shared policy, skills, profiles, decisions, or state is
a separate reviewable change.

The local Discovery and Teach skills are complete without third-party skills.
Separately installed upstream Wayfinder or Teach may be used only by explicit
user invocation under their native state and mutation contracts; if unavailable,
offer the local workflow. `IDP-NNNN` is an optional supplemental record for
meaningful recurring platform friction, not another routing stage.

Use Decomposition only after a canonical specification is approved and only
when dependency ordering or independent delivery spans multiple coherent
implementation sessions. Implementation may use test-first slices when a stable
observable seam and independently known behavior make them informative; other
work uses the strongest configured feedback loop. Verification owns executable
evidence, and proportional Review independently checks meaningful work for
specification fit, correctness, security, validation gaps, and unintended scope.

Do not put credentials or sensitive output in this directory. If a workflow
needs local transient material, use `.ai-workflow-local/` and add it to the
project's `.gitignore`.
