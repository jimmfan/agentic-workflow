# Security requirements

- No runner instance or pod may be assigned a public IP address.
- Every IAM role created by this module must set the permissions boundary from
  `var.permissions_boundary_arn`.
- The approved AMI must be resolved indirectly from the platform-owned SSM
  parameter rather than copied to a literal AMI ID.
- Do not import, modify, or delete resources whose ownership is not established.

