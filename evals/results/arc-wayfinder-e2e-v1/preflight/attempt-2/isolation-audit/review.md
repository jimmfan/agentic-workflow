# Context-isolation audit review

- Status: **passed**
- Evaluated A/B agents launched: **none**
- Probe type: one non-evaluated, read-only, ephemeral `codex exec`
- Probe workspace: disposable Git root under `/private/tmp`, removed after the run
- Raw evidence: [`probe.jsonl`](probe.jsonl) and [`probe.stderr.txt`](probe.stderr.txt)
- Machine audit: [`../context-isolation-audit.json`](../context-isolation-audit.json)

All machine checks passed. The parent `AGENTS.md` canary was not inherited; the
probe reported no project instruction path, controller conversation, or router
requirement; global skills exposed to the probe did not include Wayfinder; all
controller `CODEX_*` variables were removed; and the probe changed no repository
file.

The CLI emitted warnings about pre-existing Codex state-database maintenance and
a stale model-cache field. It nevertheless completed successfully with the
pinned model/configuration. These warnings are retained in stderr and are not
evidence of parent-context transfer.

A read-only Codex app task listing immediately after the probe did not contain
the JSONL `thread.started` ID, which is additional evidence that `--ephemeral`
did not leave a visible persisted task. This app-level check is supporting
evidence only; the static workspace, environment, inventory, canary, and raw
probe checks remain the auto-mode gate.

