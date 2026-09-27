# Credential storage choice

The service must choose between a managed secrets vault and encrypted environment files.

Evidence discovered during inspection:

- The security review board owns the choice and meets next week; no one in this conversation can commit it.
- Deployment scripts, rotation runbooks, and onboarding documentation all depend on the answer and will be written in later sessions after the board decides.
- Inventory of current secrets can proceed now and its results must be available to whoever resumes after the decision.
