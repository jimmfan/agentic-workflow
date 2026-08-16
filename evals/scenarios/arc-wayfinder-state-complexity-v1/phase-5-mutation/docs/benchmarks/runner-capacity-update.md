# Runner workload capacity update

The approved production workload replay exceeds the usable CPU and memory
envelope of `m7i.large`. The same replay on `m7i.xlarge` meets the required
headroom while retaining the validated two-warm-node startup behavior.

This evidence changes only the node-group instance size. It does not change the
dedicated placement, EKS managed node group, no-Karpenter, or 2/2/6 scaling
decisions.
