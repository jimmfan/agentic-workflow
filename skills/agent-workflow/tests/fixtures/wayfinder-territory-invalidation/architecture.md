# Current platform architecture

The policy execution migration still separates policy concerns so the platform can move away from the combined control-service model.
Its current scope includes policy definition, evaluation, approved-intent execution, and result auditing.
Changes to product policy semantics and audit-retention policy are outside this migration.

- The **Policy control plane** owns policy definition and evaluation.
- The **Execution data plane** executes approved intents but does not evaluate policy.
- The **Audit boundary** receives results from both planes and owns compliance evidence.
- Execution depends on an approved intent from the Policy control plane.

The approved-intent handoff schema is not yet settled.
Inventorying call sites that combine evaluation and execution can proceed before that schema is chosen.
