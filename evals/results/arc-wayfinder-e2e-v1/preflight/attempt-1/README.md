# Preflight attempt 1 — preserved failure

This pre-live, non-evaluated isolation probe failed before contacting a model.
The source checkout's sandbox prevented the Codex subprocess from writing its
normal state database. The first scanner also matched the generic lowercase
phrase “agentic workflows” in the system `openai-docs` skill, and inspection of
the controller environment exposed inherited `CODEX_THREAD_ID` and related
`CODEX_*` variables that the initial sanitizer had not removed.

No A/B fixture was prepared and no evaluated agent ran. The original freeze,
failed audit JSON, raw empty JSONL, and stderr are preserved here. Before the
successful audit, the harness was corrected to remove controller `CODEX_*`
variables and to distinguish the exact project name from the generic API phrase;
all deterministic eval tests passed again and a new final pre-live freeze was
created.

