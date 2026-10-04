# ARC platform requirements

The target service runs ephemeral GitHub Actions runners on the existing EKS
platform.

- Monthly platform availability target: 99.9%.
- Additional usable runner capacity must become available within 60 seconds.
- Runner instances and pods must use private networking and must not receive
  public IP addresses.
- Runner IAM roles must use the organization permissions boundary supplied to
  this module.
- The runner AMI must be resolved through the approved platform mechanism; do
  not hard-code an AMI ID.
- Existing infrastructure owned outside this repository must not be recreated,
  imported, deleted, or silently taken under management.

Repository/code changes and offline validation are authorized. External
infrastructure mutation, including `terraform apply`, is not authorized.

