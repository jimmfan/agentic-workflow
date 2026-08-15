# D1 — Runner Architecture

Status: approved

The runner platform will use:

- EC2 instance family: `m7i`
- runner nodes in a dedicated EKS managed node group
- one runner pod per node
- private subnets only
- no public IP assignment

The runner node group must use the already-approved runner AMI mechanism identified during platform investigation.

This decision intentionally does not duplicate the AMI parameter value. Existing validated platform findings should be reused.
