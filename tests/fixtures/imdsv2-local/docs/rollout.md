# Application rollout policy

This guide describes the fictional application's rollout policy, not a universal AWS requirement.
An individual request may delegate only local implementation or planning.

When a ticket includes existing instances, the release operator publishes an updated launch-template version and launches a representative pilot in the next maintenance window.
The operator returns pilot evidence for review before the wider Auto Scaling instance refresh may proceed.
The accepted version is used for the refresh, and rollout and functional checks must finish before that ticket is complete.
Changing source configuration alone does not change existing instances or establish runtime acceptance.

## Acceptance details

- New instances require IMDSv2, the token-based Instance Metadata Service protocol.
- Requests with a valid token succeed, and requests without a token are rejected.
- The application remains healthy on the pilot.
- Runtime behavior is tested, rather than inferred from Terraform configuration.
- The pilot result is reviewed before the wider refresh.
- Existing instances receive the change through the established refresh process.
- Rollout and functional checks finish before the ticket is complete.

## Evidence to return

The release operator returns the tested launch-template version, pilot health observations, token and tokenless request results, and any failures.
After pilot acceptance, the operator performs the refresh and returns its completion and functional results.
No live results have been supplied yet.
