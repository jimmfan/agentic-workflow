# Codex-first AI engineering workflow

This repository provides a lightweight, reviewable workflow for AI-assisted
engineering. It solves two recurring problems: using the same heavyweight
process for every request, and losing decisions or safety boundaries in chat
history. A compact root policy routes each request to only the process it needs,
while progressively loaded skills, a project profile, and durable Markdown state
preserve the important context.

The successful default outcome is a complete Codex workflow with no service,
daemon, package registry, or Hermes dependency. Codex keeps its normal agent
loop, sandbox, approvals, tools, and native subagents; the framework supplies
workflow policy rather than replacing those controls.

## Usable modes

| Mode | Current status | Expected behavior |
|---|---|---|
| Codex only | Primary and complete | Codex routes, explores, plans, edits, debugs, delegates to native Codex subagents when useful, and verifies under its existing sandbox and approval policy. Hermes may be absent. |
| Codex + Hermes `research` | Optional adapter implemented; separate pinned installation, profile setup, authentication, and network authorization required | Parent Codex may delegate a substantial separable external investigation. Hermes receives no repository tools, returns a structured result, and keeps learning artifacts in its private profile. Live Hermes execution was not available in this development workspace. |
| Hermes `repo-read` | Recognized but unavailable for audited Hermes v0.20.0 | The adapter fails closed. The release's Codex app-server path cannot reliably select and isolate the `:read-only` permission profile end to end. |
| Manual Hermes entry | Optional external-research session documented, not a Codex delegation substitute | A user can run the dedicated profile in its private workspace. This bypasses the adapter's structured-result and repository-snapshot checks and is not supported for local repository work. |
| GitHub Copilot in VS Code | Cheap portable subset | Current VS Code recognizes root `AGENTS.md` and `.agents/skills`. The seven core workflows, project profile, state, and command contract are portable; Codex-native subagent behavior and Codex-parent Hermes delegation are not part of this subset. Interactive discovery was not verified in this workspace. |

See [Codex research](docs/codex-research.md), the
[Hermes integration and release audit](docs/integrations/hermes.md), and
[Copilot portability research](docs/platform-research.md) for the evidence and
limits behind these statements.

## Architecture

- `AGENTS.md` is the compact, always-loaded, shared workflow policy.
- `.agents/skills/workflow-*` contains on-demand Discovery, Teach,
  Decomposition, Implementation, Debugging, Verification, and Review procedures.
- `.agents/skills/hermes-delegation` describes the optional, bounded Hermes
  research path; it is never required for normal work.
- `ai-workflow/project-profile.md` supplies project technology, architecture,
  policy, diagnostics, and safe command definitions without enlarging the root
  policy.
- `ai-workflow/state/active.md` and typed records preserve decisions, pending
  questions, interrupted workflows, exact resume targets, and optional IDP
  opportunities. Durable specifications remain project-owned documents linked
  from state rather than copied into it. Substantial multi-session work may use
  canonical dependency tickets and an actionable frontier; coherent one-session
  work does not.
- `scripts/adopt.py` copies and updates framework-owned files using checksums;
  project-owned profile and state files are seeded once and never overwritten.

The routing and execution choices are detailed in
[docs/routing.md](docs/routing.md), the component and ownership boundaries are in
[docs/architecture.md](docs/architecture.md), and accepted design choices are in
[docs/decisions](docs/decisions).

## Requirements and trust boundary

Core use requires a current Codex surface that discovers repository `AGENTS.md`
and Agent Skills. Python 3.9 or newer is required only for adoption and static
verification; runtime policy is Markdown and JSON. The adopter commands below
run on the macOS host and do not install or reconfigure Codex, Hermes, Copilot,
or another model provider.

Hermes is optional and disabled when absent or incompatible. Framework adoption
never runs the official Hermes installer because that installer may offer to
install system packages and may change shell startup files. The separate,
explicit, user-local procedure, including authentication, side effects,
verification, disablement, and removal, is in
[docs/integrations/hermes.md](docs/integrations/hermes.md).

Current stable VS Code with GitHub Copilot Chat can consume the shared root
policy and skill tree. That portability does not make Copilot the primary
runtime and does not imply that every Codex-specific sandbox, approval, subagent,
or adapter behavior is reproduced there.

Skills and configured commands are repository content with the same execution
and prompt-injection trust concerns as other shared automation. Review changes,
use least privilege, and never put credentials or raw sensitive output in the
profile, state, or delegated request.

## Adopt into a project

Adoption places the shared policy, canonical skills, contracts, templates, and
optional-but-inert Hermes adapter assets in a consuming repository. The dry run
exists so the exact ownership changes can be reviewed before anything persists.

Run every command in this section in the **macOS host Terminal**, with the
current directory set to this framework repository. Do not run them in a VS Code
terminal inside a Dev Container unless both the framework and target repository
are mounted at the exact absolute paths supplied.

First, preview installation. This is read-only and reports each file it would
create, preserve, or reject:

```bash
python3 scripts/adopt.py install /absolute/path/to/consuming-project
```

After reviewing the plan, apply it. This persistently creates framework-owned
files and `ai-workflow/install-manifest.json`, and creates project-owned seed
files only when they are absent:

```bash
python3 scripts/adopt.py install /absolute/path/to/consuming-project --apply
```

If the target already has a differing `AGENTS.md`, the installer preserves its
original bytes as the project-owned portion and adds framework policy inside
explicit managed markers. A byte-identical pre-existing policy is adopted with
`preexisting-identical` provenance and preserved on removal. A different
existing skill with a reserved framework name is a blocking conflict and is
never overwritten. The optional Hermes files are inert: installation does not
install, authenticate, start, or configure Hermes.

Next, edit the consuming project's `ai-workflow/project-profile.md` in the host
editor with verified project facts and complete command entries. This is a
persistent, project-owned customization that updates do not overwrite. Name any
required credential variables, but do not record their values.

Verify installation from the same **macOS host Terminal** and framework source
directory. This is read-only. Success prints `Installation is clean.` and exits
0; modified or missing managed content exits 1, and malformed installation state
exits 2:

```bash
python3 scripts/adopt.py status /absolute/path/to/consuming-project
```

Then open the consuming repository root in Codex and start a fresh task. Confirm
that the root policy is applied and that the `workflow-*` skills are discoverable
before relying on automatic routing. For the optional Copilot subset, open the
same root in stable VS Code, right-click Chat, choose **Diagnostics**, and check
that `AGENTS.md` and `.agents/skills` load without errors; also inspect Chat
**References** and the `/` skill menu. These checks are read-only and validate
the running client rather than only the filesystem.

## Normal use

Ask Codex normally. The policy selects the minimum justified workflow, or invoke
`workflow-discovery`, `workflow-teach`, `workflow-decomposition`,
`workflow-implementation`, `workflow-debugging`, `workflow-verification`, or
`workflow-review` explicitly. Small, clear, low-risk work stays in the parent
Codex task. Approved work is decomposed only when multiple dependency-ordered or
independently deliverable sessions justify tickets. Meaningful completion keeps
Verification as the executable-evidence owner and adds proportional independent
Review; trivial edits need only a parent sanity check. Bounded independent
engineering work may use native Codex subagents, while the parent still owns
synthesis, decisions, edits, finding disposition, and final verification.

The local Discovery and Teach workflows require no third-party installation.
When separately installed, upstream `/wayfinder` is an explicit opt-in only for
a foggy multi-session effort, and upstream `/teach` only for a multi-session
learning project in a dedicated workspace. Their native artifacts stay
canonical. If an explicitly requested skill is unavailable, the router explains
that and offers the local workflow.

Hermes is considered only for a substantial separable external/general
investigation whose benefit exceeds handoff cost. If status is disabled or
incompatible, Codex continues without it. The implemented `research` path needs
explicit network-read authorization; `repo-read` and write-capable repository
delegation are unavailable. See the complete operational procedure in
[docs/integrations/hermes.md](docs/integrations/hermes.md).

Project commands do not become equally safe merely because they are configured.
Read-only repository-local checks may run when relevant unless their profile
entry requires approval. Every explicitly approval-required action,
external-scope action, external mutation, and destructive action waits for
specific authorization. Missing commands are reported as verification gaps
rather than guessed.

Repository truth outranks model memory and chat recollection. Hermes-created
memory, learned skills, curator changes, and other self-improvement artifacts
remain profile-local. Promotion into `AGENTS.md`, `.agents/skills`, the project
profile, a decision, or durable state is a separate reviewable Codex change that
requires reusable evidence, duplication and staleness review, and the narrowest
appropriate destination.

## Update

Updating replaces only unchanged framework-owned content and leaves project
profile, durable state, and preserved project policy untouched. Obtain the newer
framework source by the same method used for this copy and inspect its release or
source revision first.

Run the following in the **macOS host Terminal** at the newer framework source
root. The first command is read-only and shows the proposed update. The second
persistently applies it:

```bash
python3 scripts/adopt.py update /absolute/path/to/consuming-project
python3 scripts/adopt.py update /absolute/path/to/consuming-project --apply
```

The updater changes only framework-owned files whose current managed content
still matches the previous installation. Existing project instructions in a
composite `AGENTS.md` remain byte-preserved. A customized managed block or skill
stops the whole update before any write. A byte-identical file that predated
installation also blocks a content-changing update because the updater will not
silently take ownership. Reconcile such a collision explicitly, preferably by
moving stable project facts into project-owned scope, then rerun the dry run.

New project seeds are created only when absent. Retired or reclassified
framework paths are preserved byte-for-byte as project-owned, and downgrades
are refused. In particular, an older `.github/copilot-instructions.md` or
`.github/skills` path is not automatically deleted or stripped based only on an
old target-controlled manifest. Review it for still-needed project guidance and
remove or reconcile it in a separate explicit change if it is obsolete.
Updates preflight every target and roll back ordinary Python-visible write
failures; a machine crash or failing storage can still require version-control
recovery. Afterward, rerun `status` and the relevant fresh-task or client
discovery check. Reversal is removal with the exact installed framework version,
or restoration from version control if the host failed outside the transaction
boundary.

## Remove or reverse adoption

Removal uses the exact installed source version and its ownership set so a
target-controlled manifest cannot authorize unrelated deletion. From the
**macOS host Terminal** at that exact framework version's source root, first
preview the removal. This is read-only:

```bash
python3 scripts/adopt.py remove /absolute/path/to/consuming-project
```

After reviewing the exact paths, apply removal. This persistently deletes only
unchanged files created by the framework and the installation manifest:

```bash
python3 scripts/adopt.py remove /absolute/path/to/consuming-project --apply
```

A clean composite `AGENTS.md` is restored to its exact original project content.
Files that predated installation, locally modified framework files, the project
profile, and durable state are preserved. Deleted framework files are recovered
by reinstalling the recorded version. A 40-character source revision is exactly
reproducible only when recorded without a `-dirty` suffix;
`unreleased-local-source` and `-dirty` installations require the original source
copy for exact recovery.

Removing the optional adapter files does not uninstall Hermes because adoption
never installed it. Hermes profile and installation reversal are separate and
documented in [docs/integrations/hermes.md](docs/integrations/hermes.md). To erase
project-owned profile or state, review and delete those exact paths separately;
the adopter intentionally does not automate that potentially destructive step.

## Verify this framework repository

The verifier checks structure, skill metadata, state and command contracts,
acceptance-catalog completeness, generic-core boundaries, context duplication,
adopter safety, Hermes compatibility gates, and adapter simulations. It does not
turn a test double into a live Hermes claim or a static artifact check into proof
of model routing.

Run it in the **macOS host Terminal** from this repository root. It makes no
persistent repository change; temporary test repositories are created under the
system temporary directory and removed automatically:

```bash
python3 scripts/verify_framework.py
```

Success is exit status 0 and a final
`OK: all framework verification checks passed.` line. If it fails, the named
check and referenced artifact are the best first diagnostic; correct that
artifact and rerun. Live Codex/Copilot routing and live Hermes execution remain
separate checks with their prerequisites and honest status recorded in
[docs/verification.md](docs/verification.md) and
[tests/README.md](tests/README.md).

## Limitations

Routing is instruction-driven, not a deterministic policy engine. Agent Skills
are progressively disclosed, but their descriptions still consume a small amount
of discovery context. UI handoffs are not durable state. The updater does not
merge customized managed blocks or same-named skills. Transaction rollback does
not cover machine crashes or failing storage. The Hermes mutation snapshot is
defense in depth, not an operating-system sandbox, and no live Hermes result is
claimed from this development environment.

There is no external issue tracker, database, daemon, extension, telemetry, or
secret store. This framework's original content is available under the
[MIT License](LICENSE.md). Public Matt Pocock skill sources were inspected as
design references but were not installed, executed, or copied; attribution,
comparison decisions, and immutable revisions are in the
[reference research](docs/reference-research.md). The separately audited Hermes
source and license are documented in the
[optional integration guide](docs/integrations/hermes.md); no Hermes source is
redistributed here.

The checksummed adopter is more distribution machinery than the original
4–8-file version-1 target envisioned. It is retained because it is an already
tested, reversible later refinement; it is not part of runtime routing and is
not evidence that the source repository itself meets that original file-count
preference. The historical requirement to show a structure before implementation
cannot be verified retroactively.
