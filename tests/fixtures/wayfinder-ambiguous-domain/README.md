# Ambiguous migration domain language

The migration spans several sessions, but the repository uses Consumer, Cutover owner, and Operating owner inconsistently across business contexts.
No authoritative domain artifact yet establishes whether Consumer means a customer organization, an integrating application, or both, or how approval responsibility crosses those context boundaries.

The objective and current migration boundary are established: move the existing platform to a zero-downtime cutover without changing unrelated product behavior.
The inconsistent domain language affects how consumer inventory and ownership relationships can be represented.

Repository-local Wayfinder writes are authorized. No human-authority choice has
been accepted, and no external-system mutation is authorized.
