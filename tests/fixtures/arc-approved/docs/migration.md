# Approved ARC workload identity migration

Status: accepted by the Platform owner for `part-03-arc-runners`.
The objective is managed-identity access to Azure resources from runner jobs without downtime.
GitHub runner registration authentication is unchanged.

## Accepted approach

Use Azure workload identity federation with the runner job service account and a user-assigned managed identity.
Roll out a parallel canary scale set, validate a representative job, then drain jobs from the old scale set before switching the remaining job targets.
For rollback, redirect new jobs to the retained old scale set and drain the canary; retain the old credentials until the migration has been validated.
The Platform owner has approved this identity mechanism, rollout order, and rollback boundary.

## Security input

Security owns the workload-permission review and must approve the permission list before the canary can use the identity.
That approval is expected next week and has not arrived.
It does not reopen the accepted identity mechanism, rollout, or rollback approach.

## Preparation

Inventory runner jobs and their Azure permission references from local configuration now.
Draft the canary validation checklist against the accepted approach while waiting for Security.
Production changes and contacting Security require separate action authorization.
