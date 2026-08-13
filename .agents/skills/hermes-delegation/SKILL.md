---
name: hermes-delegation
description: Optionally delegate a substantial, separable external research or general investigation from a parent Codex workflow to a compatible Hermes Agent. Use only when context isolation or verified Hermes tooling provides a concrete advantage; keep ordinary coding and repository exploration in Codex, and fail safely when Hermes is absent.
---

# Optional Hermes delegation

Codex remains the parent workflow owner. Hermes is a bounded evidence-gathering
adapter, not a mandatory stage or a second repository editor.

This adapter is Codex-parent only. If this shared skill is discovered or selected
from GitHub Copilot, do not invoke the adapter; report that the Codex-parent path
is unavailable in that host and continue with Copilot's native capabilities.

## Decide before invoking

Use Hermes only when the investigation is substantial, independently bounded,
mostly external/general rather than repository editing, and the expected benefit
exceeds handoff and context cost. Prefer the parent Codex task for small research
and a native Codex subagent for independent engineering analysis. Installation,
complexity, file count, or available parallelism are not sufficient reasons.

Read `docs/integrations/hermes.md` before first use or when status reports an
incompatibility. Apply these capability levels:

- `disabled`: the default; continue in Codex or report a genuinely unavailable
  optional investigation.
- `research`: supported only through the adapter's normal Hermes loop with the
  `openai-codex` provider and exact `web,memory,skills` allowlist. It permits
  authorized network reads plus profile-private memory and approval-staged
  learned-skill writes. It gives the model no local file, terminal, delegation,
  browser automation, code-execution, MCP, or plugin tool.
- `repo-read`: recognized but unavailable for Hermes v0.20.0. Its documented
  Codex app-server toggle cannot force `:read-only` end to end: its migration
  ignores `CODEX_HOME`, may target the normal Codex home when process `HOME` is
  not isolated, and otherwise diverges from the runtime's selected Codex home.
  Do not invoke or simulate success. Re-evaluate only after a pinned compatible release passes
  the negative write canaries in the integration guide.

Write-capable Hermes repository delegation is outside this MVP.

## Preflight and approval

1. Refuse delegation if `AI_ENGINEERING_WORKFLOW_CHAIN` is already set.
2. Run the adapter's `status` action. Do not install, update, authenticate,
   reconfigure, or switch providers during ordinary use.
3. Require explicit authorization for the external network reads, consistent
   with the project command contract. Never infer authorization for network
   writes or another external mutation.
4. Continue only for the exact compatible Hermes version, dedicated profile,
   and requested capability. Absence or failure leaves the core workflow intact.

## Build the handoff

Create a short JSON request from the schema in
`adapters/hermes/request.schema.json`. Include the objective, why Hermes is
justified, bounded scope, curated project context, known facts, constraints,
prohibited actions, state references, expected output, and evidence quality.
Repository modification and all external writes must be false. Pass only the
minimum project excerpts needed; do not pass credentials or raw private state.

Invoke `scripts/hermes_adapter.py research` only after approval. The adapter sets
an ephemeral `Codex -> Hermes` marker, prohibits Codex/delegation in the child
prompt, restricts Hermes to external research and profile-private learning,
validates the structured result, and compares repository snapshots before and
after. Never use `--yolo`, `-z`, `-w`, the Hermes `safe`, `file`, `terminal`,
`browser`, delegation, code-execution, MCP, or plugin tools. Memory and skill
tools are allowed only for private learning under the validated dedicated
profile; they must never target shared repository paths.

## Accept the result

Require the result schema to separate conclusions, evidence, sources,
assumptions, tools used, files inspected, uncertainty, recommendations, actions,
prohibited-action confirmation, and parent verification needs. A nonzero exit,
invalid result, missing evidence, detected repository change, recursion attempt,
or provider/version mismatch is failure—not partial success disguised as success.

The parent Codex task independently checks material claims, reconciles them with
accepted repository state, and owns every decision, edit, and final verification.
Persist only a concise accepted result when needed, never the raw transcript.

Hermes memory, learned skills, and curator artifacts remain within the dedicated
profile. Do not expose repository-owned `.agents/skills` as a writable Hermes
external skill directory. Promoting a private lesson into shared policy or state
is a separate reviewed Codex change with reusable evidence, duplication/staleness
checks, and the narrowest useful placement.
