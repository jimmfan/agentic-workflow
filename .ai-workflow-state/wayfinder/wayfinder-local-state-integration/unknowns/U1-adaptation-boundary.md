# U1: How should the pinned Wayfinder method be adapted to local state?

- Status: resolved
- Resolution mode: direct
- Blocked by: none
- Related: D1, T1

## Question

What is the smallest mechanism that makes the full Wayfinder instruction set seen by a fresh Codex agent coherent without forking the upstream method or silently rewriting unknown provider content?

## Evidence

- The installed root and routing contracts make `.ai-workflow-state/wayfinder/<effort>/` canonical and define U# as uncertainty, D# as durable decision, and T# as executable work.
- The projected pinned `wayfinder/SKILL.md` still makes tracker issues canonical, treats its tickets as decision questions, requires tracker setup, and mandates tracker assignment/comment/close mechanics.
- The current lifecycle overlay changes only activation metadata and leaves that conflicting body unchanged.
- Current official Codex documentation says activation begins from skill metadata, but selection loads the full `SKILL.md`; it also says same-named skills are not merged.

## Resolution

Use [D1 — Use a fingerprinted local-mode provider overlay](../decisions/D1-fingerprinted-local-mode-overlay.md). A local-mode block in the selected `SKILL.md` has direct precedence over incompatible tracker mechanics while retaining the untouched upstream method below it. Validate the pinned upstream body before insertion and preserve unknown or modified bodies without writing.
