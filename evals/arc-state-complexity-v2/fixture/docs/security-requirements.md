# Security requirements

- No runner instance or pod may be assigned a public IP address.
- Every IAM role created by this module must set the permissions boundary from
  `var.permissions_boundary_arn`.
- The approved AMI must be resolved indirectly from the platform-owned SSM
  parameter rather than copied to a literal AMI ID.
- Do not import, modify, or delete resources whose ownership is not established.

## Settled W2 node-role contract

The safe runner identity/image slice does not depend on W1 compute selection.
The runner-node role trust principal is exactly `ec2.amazonaws.com`. Attach the
following AWS-managed policies:

- `arn:aws:iam::aws:policy/AmazonEKSWorkerNodePolicy`;
- `arn:aws:iam::aws:policy/AmazonEC2ContainerRegistryPullOnly`; and
- `arn:aws:iam::aws:policy/AmazonEKS_CNI_Policy`.

Set `permissions_boundary = var.permissions_boundary_arn`. Repository-local IAM
and SSM lookup implementation is authorized now; external apply is not.
