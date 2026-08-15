# Isolation audit attempt 1

This first preflight attempt ran inside the host command sandbox on
2026-08-15. All static isolation checks passed, including distinct disposable
roots, the absence of Agentic Workflow from condition A, and byte-identical
Agentic Workflow installations in conditions B and C.

No probe agent executed successfully. Each of the three fresh `codex exec`
processes exited before inference because the sandbox denied DNS/network access
to `chatgpt.com` (`failed to lookup address information`). The raw JSONL and
stderr evidence is retained under `isolation-audit/`.

The evaluator, manifest, scenario, and frozen criteria were not changed after
this attempt. A subsequent attempt may rerun the same frozen audit with network
access enabled.
