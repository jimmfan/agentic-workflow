---
name: workflow-verification
description: Verify implemented behavior or a causal fix against explicit acceptance criteria using configured safe checks. Use after meaningful changes or when auditing completion; classify every criterion from observed evidence and report missing, unsafe, or unavailable checks without inventing commands.
---

# Verification workflow

Verification gathers evidence; it never converts missing evidence into success.

When resuming from `ai-workflow/state/active.md`, require
`Active workflow: verification`, validate the referenced acceptance criteria and
work record, and continue at the exact stored check.

## Select checks

1. Read the acceptance criteria, changed scope, and relevant risks.
2. Read command definitions in `ai-workflow/project-profile.md` using the contract
   in `ai-workflow/contracts/project-profile.md`.
3. Select the smallest executable set covering behavior, regression risk, and
   safety. Qualitative specification, standards, and maintainability assessment
   belongs to Review. Do not run every configured command by default.
4. If configuration is missing, report the gap and use only an explicitly
   documented manual check; do not guess technology-specific commands.

## Apply the safety gate

- Any entry with `Approval required: yes` waits for explicit approval, regardless
  of safety class.
- Any command with `Scope: external` waits for explicit approval, including a
  read-only network or cloud inspection.
- `read-only` and `locally-mutating` commands may run automatically when
  relevant, local in scope, and not marked approval-required; disclose durable
  local artifacts.
- `externally-mutating` commands require explicit approval.
- `destructive` commands require explicit approval, an exact target, and a
  reversal or recovery plan where possible.
- A command with an unknown or malformed safety class or scope does not run.
- Respect the command's working directory, prerequisites, environment notes,
  timeout, and unavailable behavior. Never store secret values in configuration.

## Report evidence

For every criterion, report `pass`, `fail`, `blocked`, or `not applicable`, with
the supporting command or observation. Separate:

- checks run and observed results;
- checks skipped as unsafe or awaiting approval;
- checks unavailable because a tool or environment is missing; and
- checks not applicable, with the reason.

Completion requires all required criteria to pass or an explicitly accepted
limitation to be recorded. If anything fails, return the most useful next
diagnostic step. Include side effects created by checks and cleanup or reversal
instructions.

For delegated findings, verify material claims independently and report the
delegate's success separately from the engineering criterion.

After meaningful work, apply the retrospective, IDP, and controlled-promotion
rules in `ai-workflow/state/README.md`. During read-only work, report candidates
without writing them.
