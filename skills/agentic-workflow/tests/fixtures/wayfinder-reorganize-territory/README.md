# Policy execution migration

The destination and scope are clear enough to map, but the current description
is a flat list that conflates three responsibilities:

- policy requests enter through an API;
- policy rules are evaluated and produce an approved execution intent; and
- a runtime performs that intent and reports the outcome.

The API, evaluator, and runtime are all currently called “the policy service,”
which hides their ownership boundaries and the fact that execution depends on
evaluation. Reorganizing these concepts would make the Wayfinder map materially
more useful even though work is not blocked.

Repository-local Wayfinder writes are authorized. No external mutation or
authority-owned product choice is authorized.
