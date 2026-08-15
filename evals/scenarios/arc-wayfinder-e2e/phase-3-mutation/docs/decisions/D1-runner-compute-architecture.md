# D1: Runner compute architecture

Status: approved

The initial ARC rollout will use:

- dedicated runner capacity;
- EKS managed node groups;
- the `m7i` instance family;
- no Karpenter; and
- an initial warm capacity of 2 nodes.

This decision resolves the earlier instance-family, shared-versus-dedicated, and
Karpenter-versus-managed-node-group questions. It does not establish ownership
of any existing legacy ARC resource.

