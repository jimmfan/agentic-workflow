---
description: Investigate substantive questions against high-trust primary sources and return cited findings in chat. Create a repository artifact only when the user explicitly requests durable research output.
name: research
---
# Research

Investigate synchronously when that satisfies the evidence need, or use a background agent when delegation is available and independent work can proceed usefully.
Evidence requirements remain the same in either mode.
If the invoking method requires independent or parallel work, preserve that requirement and report unavailable capability honestly instead of presenting one agent's work as independent review.
Research establishes externally sourced facts and evidence.
It does not select the project's preferred alternative.
Return evidence to the caller; evidence concerning a consequential choice does not automatically require a Discovery transition.
The caller uses Direct or Discovery according to whether alternative and tradeoff analysis materially helps.

Its job:

1. Investigate the question against **primary sources** — official docs, source code, specifications, and first-party APIs — rather than secondary summaries.
   Follow each material claim back to the source that establishes it for the applicable scope.
   Use a secondary source only when no primary source exists, and label it as secondary.
2. Split a broad question into independent sub-questions; when delegation is available, investigate independent sub-questions in parallel under the same evidence requirements.
3. For evolving external systems, prefer current sources over remembered knowledge and record the version, revision, or retrieval date that establishes each claim.
4. When sources conflict, cite each side and state the conflict instead of silently choosing one.
5. Stop when each material claim is established or further searching stops producing new relevant evidence; report what remains unestablished instead of continuing indefinitely.
6. Return concise findings to the caller so the default user-facing result can be delivered in chat, separating cited findings, labeled inferences, and gaps.
   A claim without a source is a gap, not a finding.
7. Do not create a standalone research file unless the user explicitly requests a durable research artifact.
8. When cited findings are adopted into a lasting project result and repository writes have action authorization, write the necessary evidence directly into the ADR or product documentation designated to maintain that result instead of creating a parallel research report.
9. Do not create raw or temporary research files inside the repository.
