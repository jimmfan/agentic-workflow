# Current platform facts

These facts were exported from the platform inventory on 2026-08-14. This file
is a transient import and may be replaced after the migration has started.

- The EKS cluster already exists and is externally managed. This repository
  receives its name as an input and must not create the cluster.
- The approved runner AMI is published through the SSM parameter
  `/platform/arc/runner-ami`.
- Runner subnets are private and are supplied to this module as input.
- IAM roles created for runners require the supplied permissions boundary.

The inventory does not approve an EC2 instance family, a shared or dedicated
compute model, or Karpenter versus EKS managed node groups.

