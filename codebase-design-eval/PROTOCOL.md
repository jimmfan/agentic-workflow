# Evaluation protocol

This experiment compares observable architecture-review recommendations under
three instruction conditions:

- `direct`: general architecture reasoning with an explicit prohibition on
  reading or using Codebase Design instructions;
- `vanilla`: the current unmodified Codebase Design `SKILL.md`, `DEEPENING.md`,
  and `DESIGN-IT-TWICE.md`;
- `guarded`: a candidate variant created only after the direct and vanilla
  outputs have been reviewed.

The common task prompt and scenario prompts are held constant. Only the
condition instructions change. Synthetic runs use fresh ephemeral Codex
sessions, the same explicitly selected model and reasoning effort, and
read-only permissions. Each temporary workspace contains only one constructed
fixture plus the instructions required by its condition. It contains no root
`AGENTS.md`, Agentic Workflow source, documentation, or Scenario D material.

Scenario D uses the frozen worktree at baseline commit
`b722b0b1eba1bcdf52a818e06279082edbcb978d`. It remains qualitative and
non-controlled because approval to send the real repository to separate hosted
sessions was not granted.

Each final response and compact metric record is retained under
`runs/<condition>/`. Raw JSONL event streams, model commentary, temporary
workspaces, and session state are not retained. The outputs are evaluated only
for observable recommendations and cited evidence; hidden reasoning is not
used.

## Material limitations

- The conditions differ in instruction context by design, so this is a paired
  prompt comparison rather than a blinded experiment.
- A hosted model can vary nondeterministically even with fixed settings.
- Synthetic sessions omit project-level `AGENTS.md`, user config, and repository
  source. The hosted Codex system/tool instructions still apply to all
  conditions and are not a neutral laboratory system prompt.
- The synthetic fixtures are intentionally small and cannot establish behavior
  across all languages, team structures, or repository scales.
- Grading is against a fixed rubric but is not blinded.
- The real-repository scenario is qualitative, not a live condition comparison,
  and has no known-answer oracle.
- The common prompt prohibits sub-agent use, so the runs do not exercise the
  Design It Twice fan-out itself.
