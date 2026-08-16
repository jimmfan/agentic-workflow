# Generated evaluation artifacts

This directory is the repository-local home for raw, regenerable evaluation
output. Everything below it except this README is ignored by Git.

Harnesses should place full Codex JSONL, raw stdout/stderr, copied workspaces,
temporary Codex homes, grader transcripts, and similar execution exhaust under:

```text
evals/artifacts/<suite-or-campaign>/<run>/...
```

Durable source and reproducibility inputs stay in their suite directories.
Compact run results, token-forensics summaries, adjudication, and final reports
also stay outside this directory so they can be reviewed and committed.

Some harnesses use guarded host-temporary job/workspace directories instead of
copying those jobs here. Harbor, for example, keeps its external work/jobs/cache
paths ignored by its suite-local `.gitignore`. Do not duplicate those artifacts
under `evals/artifacts/` unless a local copy is needed for short-term analysis.

Raw artifacts may be deleted after the compact result and any important
adjudication or forensic summary have been preserved. They are not required to
render tracked reports.
