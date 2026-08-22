# Current platform architecture

The accepted architecture supersedes the old combined control-service model.

- The **Policy control plane** owns policy definition and evaluation.
- The **Execution data plane** executes approved intents but does not evaluate policy.
- The **Audit boundary** receives results from both planes and owns compliance evidence.
- Execution depends on an approved intent from the Policy control plane.

The existing Wayfinder map must be revised in place. This evidence does not
authorize a new effort, a parallel territory, or an implementation decision.
