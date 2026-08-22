# U1: Do supported hosts preserve provider explicit-only invocation?

- Status: resolved
- Resolution mode: research
- Blocked by: none
- Related: none

## Question

Do Codex, GitHub Copilot, and Claude Code preserve the upstream distinction between model-selectable and explicit-only skills, and do Agent Workflow's current provider projection and host-support claims accurately reflect verified behavior?

## Evidence

- [Host invocation portability research](../../../../docs/host-invocation-portability-research.md) establishes from current primary sources that the Agent Skills specification does not standardize invocation policy; Codex uses machine/harness-owned `agents/openai.yaml`; and GitHub Copilot VS Code/CLI plus Claude Code document `SKILL.md:disable-model-invocation`.
- Repository inspection confirmed that user-only provider skills carry both host controls and that installation preserves whole provider directories except for the declared, fingerprinted Wayfinder adapter.
- `providers.py status .` reported all 14 provider skills present and the Wayfinder adapter ready.
- Two deterministic lifecycle regressions now reject a staged user-only skill if either the Copilot or Codex control is missing.
- `python3 skills/agent-workflow/scripts/verify_package.py --tests` passed all 65 tests.
- No live Codex, Copilot, Claude Code, cloud-agent, or cross-model matrix was run. Copilot cloud-agent/code-review enforcement remains unverified.

## Resolution

Agent Workflow has no confirmed invocation-policy defect for its documented Codex and GitHub Copilot VS Code/CLI paths. The existing dual metadata is behaviorally necessary and correctly validated. The appropriate change is limited to durable documentation, a manual live-host procedure, and deterministic regression coverage. No new D# is needed because the evidence confirms the existing provider contract rather than adopting a new design.
