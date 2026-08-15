# D1: Runner compute architecture

Status: approved

The initial ARC rollout will use:

- dedicated runner capacity;
- EKS managed node groups;
- `m7i.large` from the approved `m7i` instance family;
- no Karpenter; and
- an initial warm capacity of 2 nodes.

The frozen scaling contract for this bounded slice is:

- minimum size: 2;
- desired size: 2; and
- maximum size: 6.

This decision resolves the earlier instance-family, shared-versus-dedicated, and
Karpenter-versus-managed-node-group questions. It does not establish ownership
of any existing legacy ARC resource.

The new managed node group and its new supporting IAM and launch-template
resources are explicitly authorized repository work. No external apply is
authorized. The implementation boundary and exact inputs are recorded in
`docs/implementation-readiness.md`.
