# Context-isolation audit review

Reviewed: 2026-08-15

The corrected automatic audit passed and its raw JSONL was manually inspected
before any evaluated phase began.

- Conditions A, B, and C used distinct disposable Git roots and distinct fresh
  Codex execution IDs.
- Condition A contained no Agentic Workflow policy, state, or Wayfinder skill.
- Conditions B and C had byte-identical Agentic Workflow installations
  (`c5527e63b68a5f25cc70202c68a246dc8b0e61afcb798c90a83699a6052b70f8`),
  framework version `0.11.1`, and Wayfinder provider pin `v1.2.3`.
- Every probe returned `controller_conversation_excerpt: null`; no parent or
  sibling canary was reported.
- The processes inherited neither controller variables nor cloud credentials,
  used auth-only temporary `CODEX_HOME` directories, and made no repository
  changes.
- The grader and expected results remained outside every evaluated workspace.

The audit supports enabling the registered automatic run. It remains behavioral
evidence rather than a proof of undocumented Codex context channels; the frozen
audit records that limitation explicitly.
