# Session migration planning context

The immediate request is to recommend the next planning step without modifying files.

Evidence discovered during inspection:

- Token rotation timing and session invalidation semantics are unresolved, interact with each other, and materially change the migration plan.
- The security owner must decide the rotation policy; other migration planning can continue while that answer is pending.
- The work will be handed to a fresh agent session tomorrow, so the distinctions and current blocker must survive this session.
- An old design note conflicts with the currently deployed configuration, and the provenance of each claim must remain explicit.
