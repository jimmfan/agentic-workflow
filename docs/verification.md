# Verification report

Verified 2026-08-12 in the macOS host workspace at
`/Users/james/Desktop/projects/agent-instructions`.

## Purpose and outcome

The verification goal was to implement the approved post-audit v0 refinements
without replacing working architecture: durable decomposition for substantial
multi-session work, stronger debugging feedback, optional evidence-driven TDD,
and proportional independent review. The result preserves the project-owned
specification, existing Debugging and Implementation-to-Verification ownership,
lightweight direct routing, and every Codex/Hermes safety boundary.

| Mode | Status | Evidence |
|---|---|---|
| Codex only | Implemented and deterministic checks pass | Root policy, seven core workflow skills, project profiles, typed durable state, command contract, routing catalogs, and adopter lifecycle are present. Hermes is not needed. |
| Hermes `disabled` | Default and tested | Missing, incompatible, unconfigured, or unauthenticated Hermes leaves the core workflow operational. No optional process starts during normal work. |
| Hermes `research` | Implemented and executable-double tested; not live-tested | The adapter attests the official source/layout, exact provider and tool allowlist, isolated profile/configuration, bounded result contract, and repository immutability. A real Hermes model turn was not run. |
| Hermes `repo-read` | Recognized but intentionally unavailable for audited v0.20.0 | The adapter returns exit status 4 before starting Hermes. Source and disposable protocol checks found no clean end-to-end propagation of Codex `:read-only`; the underlying Codex-only primitive works, but that does not prove the Hermes boundary. |
| Write-capable Hermes repository delegation | Excluded | Parent Codex or a native Codex subagent owns repository inspection and all edits. |
| GitHub Copilot subset | Documented/static; live client unverified | Official formats are used, but this host had no installed signed-in Copilot client for discovery or semantic checks. |

Hermes self-improvement remains available inside its isolated profile: private
memory and curator maintenance may be automatic, and learned-skill changes are
approval-staged. `skills.external_dirs` is empty, so shared `AGENTS.md`,
`.agents/skills`, profiles, decisions, and durable state are not learning
targets. Promotion into shared policy is a separate parent-Codex change that
requires reusable evidence, duplication/staleness review, narrow placement, an
explicit diff, and normal verification.

## Requirements compliance audit

| Material requirement area | Status | Audit result |
|---|---|---|
| Repository-native workflow; no application, daemon, service, or mandatory runtime | Satisfied | Runtime policy is Markdown/JSON plus optional local scripts. Core workflows do not depend on Hermes, Wayfinder, Teach, Superpowers, a database, or a service. |
| Minimum-process routing, knowledge-vs-decision distinction, and lightweight direct work | Satisfied | Root policy and focused skills route explicit learning, consequential choices, unexplained failures, meaningful implementation, verification, and bounded direct tasks separately. |
| Discovery, Teach, Decomposition, Plan/Build/Verify, Review, systematic debugging, and durable resume | Satisfied after targeted implementation | Seven local workflow skills have bounded ownership; `active.md` and typed records preserve exact cross-chat transitions. Decomposition and Review are conditional rather than universal stages. |
| Human control of consequential decisions | Satisfied after audit fix | A consequential decision is accepted only by the user or named project policy; autonomous progress can create only a visible provisional choice with a review trigger. |
| Current upstream skill integration | Satisfied | Wayfinder and Teach remain explicit-only. `/to-tickets` and `/code-review` are explicit optional native contracts; `/to-spec` and `/implement` remain excluded. `diagnosing-bugs`, `tdd`, and `writing-for-agents` contribute mechanics or authoring guidance without becoming routes or dependencies. |
| Durable decisions, specifications, tickets, learning, and IDP opportunity capture | Satisfied | Specs stay project-owned and linked from state. Substantial approved work can use local `TKT-NNNN` records or canonical native issues, acyclic blockers, and an actionable frontier without copying ticket bodies into `IMP` records. `IDP-NNNN` remains supplemental and authorization-gated. |
| General core plus highly specialized project configuration | Satisfied | Generic-core checks reject domain/tool assumptions, while contrasting application and infrastructure profiles supply commands, architecture, policy, terminology, and diagnostic layers. |
| Current VS Code/Copilot repository conventions | Satisfied statically; live behavior unverified | Root `AGENTS.md` and `.agents/skills` match current official locations. Custom agents, prompt files, forked skills, and disabled-by-default plugins are unnecessary. A signed-in live Copilot session was unavailable. |
| Low normal context and one-agent default | Satisfied after simplification | Root policy is 2,740 bytes/47 lines; detailed bodies load conditionally. Hermes implementation detail remains outside always-loaded policy, and Copilot fails closed on the Codex-parent adapter. |
| EKS/ARC as an example rather than core coupling | Satisfied | Infrastructure specialization exists only in an illustrative project profile; an application profile exercises the same core. |
| Evidence-driven implementation without mandatory TDD or swarm | Satisfied | Test-first slices are optional only at stable observable seams with independently known behavior; declarative and infrastructure work may use a stronger configured validation loop. Review can use bounded independent readers, but the parent owns findings and completion. |
| Approximately 4–8 files and no premature distribution system | Partially satisfied; intentionally retained exception | The effective runtime nucleus is root policy, seven core skills, profile, and active state, while the source now has 52 files and the manifest has 25 framework-owned files plus two project seeds. The 695-line checked adopter is a tested later refinement required by subsequent scope, so deleting it would violate the instruction to preserve working components. |
| Copilot-first primary runtime | Intentionally superseded | The original target was Copilot-first; later explicit requirements made Codex the default and Copilot a portable subset. This audit preserves the later instruction. |
| Show structure before implementation | Not retrospectively verifiable | Architecture and loading ownership are documented now, but repository evidence cannot prove what was shown before historical implementation. |

## Environment observed

- Repository state: this directory was not a Git repository, so there is no Git
  diff, commit, or immutable local framework source revision to report.
- Python: 3.9.6.
- Codex CLI: not available on the current shell `PATH`. A verified 2026-08-11
  snapshot used 0.144.6 and reported native `multi_agent` stable and enabled,
  local memories experimental and disabled, and app-server labeled
  experimental; that snapshot is not a claim about every current installation.
- VS Code CLI: 1.129.1, arm64; no `github.copilot` or
  `github.copilot-chat` extension was listed.
- Hermes: absent from `PATH`.
- `rg`: absent from the current shell `PATH`; repository inspection used standard
  file tools where needed.
- `ffmpeg`: absent.

The official Hermes installer was not run. This host's Python is below the
release's 3.11 minimum, `ffmpeg` is absent, and the audited installer may use
platform package managers or install other prerequisites. No Hermes profile,
credential, shell-startup edit, gateway, service, daemon, or normal Codex
configuration change was created.

## Deterministic verification

The following read-only framework command was run from this repository root in
the macOS host environment:

```text
python3 scripts/verify_framework.py
```

It exited 0 and ended with:

```text
OK: all framework verification checks passed.
```

All 23 named groups passed:

1. required files;
2. Agent Skill metadata;
3. project profiles and command contract;
4. durable state contract;
5. 32-scenario acceptance catalog;
6. 30-scenario Codex/Hermes integration catalog;
7. generic core boundary and optional dependency absence;
8. always-on context budget and duplication;
9. Hermes schemas and `repo-read` compatibility gate;
10. Hermes optional, version, profile, and auth preflight simulations;
11. Hermes official runtime source and interpreter attestation;
12. Hermes structured result and exact invocation contract;
13. Hermes recursion, network, provider, and mutation guards;
14. distribution manifest and ownership;
15. adoption, conflict, update, and removal lifecycle;
16. existing policy merge and pre-install provenance;
17. tampered-manifest and partial-install guards;
18. ownership evolution and downgrade guards;
19. transaction rollback and dirty-source revision;
20. adoption symlink guards;
21. legacy Copilot-layout migration;
22. documentation, research, and licensing completeness; and
23. local Markdown links.

The Hermes fixtures cover unavailable and incompatible versions, exact profile
bytes, structural local authentication, official-layout source/interpreter
attestation, exact `openai-codex` provider selection, empty fallbacks, concrete
`web,memory,skills` tools, normal `chat -q -Q` lifecycle, recursion markers,
network authorization, bounded streaming output, strict structured results,
hostile URLs, private-environment isolation, timeout/interruption behavior, and
post-run repository guards. The mutation canaries cover file content, modes,
link counts, symlinks, and special entries such as FIFOs. The profile preflight
recursively rejects symlinks, hardlinks, and special entries that could alias a
shared target.

All adapter doubles and hostile repositories are created beneath automatically
deleted temporary directories. Production source attestation invokes trusted
`/usr/bin/git`; the exact audited commit result is simulated because a temporary
Git repository cannot manufacture that SHA. Wrong revisions, tracked changes,
untracked changes, and the exact Git arguments are tested. A real temporary Git
repository also verifies that the adapter's own status probe leaves its snapshot
byte-identical by disabling Git optional locks.

An in-memory `compile()` check passed for `scripts/adopt.py`,
`scripts/hermes_adapter.py`, and `scripts/verify_framework.py`. It creates no
bytecode files. Root `AGENTS.md` is 2,740 bytes and 47 lines, below the enforced
3,500-byte and 55-line budget.

## Audited external-skill boundary

A live read-only `git ls-remote` on 2026-08-12 and an isolated temporary clone
confirmed current `mattpocock/skills` main at
`84fdeffd12f2ee307994d1eb6feb48173b6e0502`, committed 2026-08-06 and declaring
bundle version 1.2.3. Wayfinder and Teach prohibit implicit invocation. Wayfinder owns an
issue-tracker or local-Markdown map and is intended only for foggy multi-session
work; Teach owns a dedicated multi-session teaching workspace and has no
automatic engineering-workflow return. The complete source-path and artifact
audit is in [the reference research](reference-research.md).

The temporary clone was read only, never installed or executed, and removed
after inspection, reclaiming 1.4 MB. The framework keeps smaller local workflows as defaults and
defines only explicit optional handoffs; it does not vendor or imitate native
map/course state. The same pinned revision supplied the approved comparison for
`to-spec`, `to-tickets`, `diagnosing-bugs`, `tdd`, `code-review`, `implement`,
and `writing-for-agents`; their dispositions are recorded in
[the reference research](reference-research.md) and ADR-0005.

## Audited Hermes/Codex boundary

Hermes v0.20.0 was audited at exact commit
`3c27eb6234bf91b8ceee9e9071591b31e9b148cb`. The audit covered installer effects,
profiles, authentication, provider fallback, toolsets, normal chat lifecycle,
memory, skill write approval, curator behavior, Codex app-server migration, and
permission-profile propagation. Immutable links and operational implications are
in [the Hermes integration guide](integrations/hermes.md).

The pinned app-server session builds a permission-profile mapping but does not
send it in `thread/start`. Its migration defaults to `:workspace`, ignores
`CODEX_HOME` when selecting the migration target, and can therefore touch normal
Codex configuration under an ordinary process `HOME`; using an isolated `HOME`
makes migration and the eventual `CODEX_HOME` runtime configuration diverge.
Those behaviors prevent a clean, attestable Hermes-to-Codex read-only boundary
in this release.

A disposable Codex 0.144.6 app-server canary showed that one isolated
`default_permissions = ":read-only"` configuration reports a read-only sandbox
and blocks shell-redirection writes. A duplicate `:read-only`/`:workspace`
top-level configuration was rejected. These checks prove the Codex primitive
and the reason for the fail-closed decision; they are not a live Hermes turn or
an end-to-end negative `apply_patch` test.

## Scenario status

The catalogs contain 70 cases: 32 core workflow cases, 30 Codex/Hermes
integration cases, three explicit `repo-read` cases, and five private-learning
cases. Static verification checks their schema, identifiers, policy coverage,
and their alignment with the documented runtime boundaries. Manual and live
evaluation requirements are intentionally classified separately in
[the acceptance guide](../tests/README.md); an executable double is not reported
as a live Hermes pass.

Independent read-only forward tests exercised seven representative routes:
trivial direct work, meaningful coherent implementation, multi-session
decomposition, nonmutating diagnosis-only investigation, the Review finding
loop, optional TDD versus declarative validation, and unavailable `/to-spec` and
`/implement` fallback. After correcting lifecycle and fixture ambiguities, the
reviewers found no material remaining contract defect. They independently reran
the verifier with 23 passed groups and zero failures. This is semantic contract
review, not a live client-routing claim for all 70 catalog cases.

| Representative case | Confirmed route and boundary |
|---|---|
| Typo-only documentation | Direct parent edit and sanity check; no durable state or formal Review |
| Meaningful coherent behavior change | Implementation -> Verification -> Review; no Decomposition |
| Approved multi-session migration | IMP coordination -> Decomposition -> one frontier TKT through Implementation, Verification, and Review -> Decomposition frontier recomputation |
| Diagnosis-only cloud/intermittent failure | Debugging with existing evidence or read-only probes; no record, instrumentation write, fix, Verification, or Review |
| Confirmed independent-review finding | Review -> parent confirmation -> Implementation and/or Verification -> rerun -> Review |
| Application seam versus declarative infrastructure | Optional test-first loop only when strongest; otherwise configured declarative validation; both retain Verification and Review |
| Unavailable `/to-spec` and `/implement` | Disclose exclusion, install nothing, then use the already-authorized project-owned specification and local implementation route |

Live automatic routing may vary by client, model, configuration, and consuming
repository. Fresh-task manual evidence is still required before claiming
installed Codex or Copilot semantic activation for every prompt.

## Context and residual limitations

Normal Codex loads the compact root contract and discovers eight skill names and
descriptions. Full skill bodies, Hermes documentation, schemas, profile, and
adapter remain conditional. There is one canonical `.agents/skills` tree and no
framework `.github/skills` mirror. No live Codex token diagnostic was available,
so the report gives measured bytes and discovery structure rather than an
invented token count. Hermes prompt size was not measured because Hermes is not
installed.

Not verified in this environment:

- a live Hermes v0.20.0 turn, real OAuth/token freshness, model eligibility,
  quota or billing semantics, actual provider identity, response quality, and
  runtime private memory/skill/curator behavior;
- end-to-end Hermes `repo-read`, a negative Hermes `apply_patch` canary, or a
  safe approval bridge—the adapter reports the mode unavailable instead;
- live Codex implicit routing for every catalog prompt;
- live installed upstream skill invocation, native tracker/course/review artifact
  creation, and return behavior—the audit inspected source but did not install or
  execute any upstream skill;
- Copilot diagnostics, slash-menu discovery, or semantic routing in a signed-in
  current client;
- extended metadata mutation such as repository ACLs and xattrs; and
- behavior on clients and IDEs beyond the documented portable formats.

Local authentication inspection proves that expected credential structures are
present without exposing them; only a live authorized turn can prove token
freshness. The adapter's tool boundary and repository guard are defense in depth,
not an operating-system sandbox against a malicious same-user process.

If deterministic verification later fails, begin with the named failed check.
For a live Codex routing difference, inspect the loaded root `AGENTS.md`, skill
metadata, and state fixture. For Hermes, run adapter `status` and use its
classified reason; do not auto-install, update, reauthenticate, switch providers,
or enable `repo-read`. For Copilot discovery, inspect Chat Diagnostics, workspace
root, trust, frontmatter, and customization settings before changing policy.
