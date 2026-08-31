---
description: Investigate substantive questions against high-trust primary sources and return cited findings in chat. Create a repository artifact only when the user explicitly requests durable research output.
name: research
---
# Research

Spin up a **background agent** to do substantive research while you continue
independent work.

Its job:

1. Investigate the question against **primary sources** — official docs, source
   code, specifications, and first-party APIs — rather than secondary summaries.
   Follow each material claim back to the source that establishes it for the
   applicable scope.
2. Return concise, cited findings to the caller so the default user-facing
   result can be delivered in chat. Return sourced research findings in chat by
   default.
3. Do not create a standalone research file unless the user explicitly requests
   a durable research artifact.
4. When cited findings are adopted into a lasting project result and repository
   writes have action authorization, write the necessary evidence directly into
   the ADR or product documentation designated to maintain that result instead
   of creating a parallel research report.
5. Do not create raw or temporary research files inside the repository.
