# Migration architecture

The objective is a zero-downtime cutover of the existing platform. Changes to
unrelated product behavior are outside this effort.

The major areas are Consumer inventory, Cutover orchestration, Rollback, and
Ownership. Cutover orchestration depends on a complete Consumer inventory;
Rollback constrains every cutover step; Ownership establishes who may approve
the final transition and operate the result.
