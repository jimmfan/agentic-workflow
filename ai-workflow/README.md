# Installed AI engineering workflow

This directory holds project-specific context and durable state for the
repository's AI engineering workflow. Shared always-on policy is the compact
root `AGENTS.md`; detailed workflows load from `.agents/skills/` only when
relevant or when explicitly invoked with
`/workflow-discovery`, `/workflow-teach`, `/workflow-decomposition`,
`/workflow-implementation`, `/workflow-debugging`, `/workflow-verification`,
`/workflow-review`, or the optional `/hermes-delegation` adapter.

`project-profile.md` and `state/active.md` are project-owned. Complete the
profile before relying on project checks, including the canonical locations for
durable specifications and implementation tickets. State records link to
canonical specification and native-ticket bodies rather than copying them.
Framework updates never overwrite those files. Contracts,
templates, skills, this file, and `VERSION` are
framework-owned; the generated `install-manifest.json` records their installed
checksums, pre-install provenance, and source revision status.

Use the framework source repository's `scripts/adopt.py` to inspect, update, or
remove an installation. Every mutation requires `--apply`; without it the tool
prints a dry-run plan. Locally changed framework files cause an update conflict.
Removal preserves changed and pre-install files plus all project-owned content,
restores project instructions from a clean composite `AGENTS.md`, and removes
the installation manifest. Removal requires the exact installed version's
source.

Codex owns normal engineering, editing, commands, native subagents, approvals,
and verification. Hermes is absent-safe and optional. Its implemented
`research` level receives no repository tools; the `repo-read` level is disabled
for the audited Hermes release. Hermes-private memories and staged learned skills
stay outside the repository. Promoting any lesson into shared policy, skills,
profiles, decisions, or state is a separate reviewable Codex change.

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
