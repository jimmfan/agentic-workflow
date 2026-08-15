# Preflight attempt 2 — preserved invalidation

This non-evaluated probe passed every static and behavioral isolation check, but
the initial auto gate invalidated it immediately afterward because one unrelated
globally cached skill disappeared (the scan changed from 42 files to 41). No
Agentic Workflow or Wayfinder marker appeared, and no A/B fixture or evaluated
agent existed.

The aggregate-only inventory could not name the vanished file, so refreshing the
hash would have been unjustified. The gate was refined before live execution to
hash global `AGENTS.md`/`CLAUDE.md` separately, retain the complete scanned
path/hash inventory for diagnostics, and rescan every skill for exact Agentic
Workflow or Wayfinder markers. Unrelated plugin-cache churn is recorded but no
longer conflated with controller-context contamination. The 27-test eval suite
then passed and the final pre-live evaluator was frozen again.

