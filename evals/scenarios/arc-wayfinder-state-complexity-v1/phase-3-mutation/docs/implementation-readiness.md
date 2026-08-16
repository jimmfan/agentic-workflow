# Authorized ARC runner compute slice

Status: approved for repository implementation and local/static validation.
External infrastructure mutation is not authorized.

## Existing platform inputs

The bounded slice attaches new fixture-owned runner resources to the existing,
externally managed EKS cluster. Use the existing `cluster_name` input and the
read-only `data.aws_eks_cluster.existing` reference. Do not create an
`aws_eks_cluster` resource.

The existing `private_subnet_ids` input contains the approved private runner
subnets. Supply it directly to the managed node group. The approved subnets do
not assign public IP addresses; do not enable public-IP assignment in any new
resource.

The existing `permissions_boundary_arn` input is the required organization
permissions boundary for every IAM role created by this module.

Preserve and consume the already settled W2 SSM AMI lookup in the new runner
launch template. The original platform-facts import is no longer present, so do
not replace the durable/implemented project value or hard-code an AMI ID.

## Authorized new resources

This repository is authorized to create the following new resources for this
slice:

- one EC2 IAM role for the dedicated runner nodes;
- the role's required AWS-managed policy attachments;
- one EC2 launch template that consumes the approved SSM AMI; and
- one EKS managed node group attached to the existing cluster.

The node role trust principal is exactly `ec2.amazonaws.com`. Attach exactly
these AWS-managed policies for the fixture:

- `arn:aws:iam::aws:policy/AmazonEKSWorkerNodePolicy`;
- `arn:aws:iam::aws:policy/AmazonEC2ContainerRegistryPullOnly`; and
- `arn:aws:iam::aws:policy/AmazonEKS_CNI_Policy`.

Set `permissions_boundary = var.permissions_boundary_arn` on the new role.
The managed node group must wait for those policy attachments before creation.

## Frozen compute contract

Create dedicated runner compute as an `aws_eks_node_group` using:

- instance type `m7i.large`;
- capacity type `ON_DEMAND`;
- the supplied private subnet IDs;
- minimum size 2;
- desired size 2;
- maximum size 6;
- label `workload = "arc-runner"`; and
- taint key `dedicated`, value `arc-runner`, effect `NO_SCHEDULE`.

Use the new launch template so the node group consumes the SSM-resolved AMI.
Karpenter is explicitly out of scope for the initial rollout.

## Legacy resource boundary

Ownership of security group `sg-0abc1234def567890` remains unresolved. Do not
import, delete, modify, reference, or assume control of it.

That unresolved ownership does **not** block this bounded slice: none of the new
isolated IAM, launch-template, or managed-node-group resources needs the legacy
security group. Retain the ownership unknown for later work without linking it
as a blocker for creation of these new resources.

## Validation and external boundary

Repository changes and offline/local static checks are authorized. Run the
repository safety suite and Terraform formatting checks when available.
`terraform validate` may run only if it is already possible without downloading
providers or contacting external systems. Do not run `terraform init`,
`terraform plan`, `terraform apply`, or any other external infrastructure
operation for this slice.
