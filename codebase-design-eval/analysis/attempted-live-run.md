# Approval and live-run record

- Attempted condition: `direct`
- Attempted repetition: `1`
- Runner: `run_condition.sh`
- Intended model/settings: `gpt-5.4`, high reasoning, ephemeral session,
  read-only sandbox
- Result: no scenario review was produced

The first runner combined synthetic Scenarios A/B/C with the real-repository
Scenario D. Its sandboxed attempt could not initialize the local Codex state
database or in-process app-server client. Escalated execution was rejected
because D would transmit the repository to a separate hosted session without
explicit payload approval.

The runner was then narrowed so hosted synthetic sessions receive only one
constructed fixture plus exact condition instructions. The user explicitly
authorized that isolated payload. Eighteen A/B/C runs completed successfully;
see `live-synthetic-findings.md` and `../runs/`.

A separate D-only runner was prepared and a narrow approval was requested for
three read-only repository sessions. That request was rejected because the user
had not explicitly authorized the exact repository payload and destination. No
workaround was used. D remains qualitative and non-controlled.
