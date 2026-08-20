# ARC platform delivery

The destination is to replace the current EC2 Auto Scaling Group GitHub Actions
runners with Actions Runner Controller on AWS EKS, validate a non-production
pilot, and agree the migration and decommission path.

The accepted delivery backlog has 24 items across authority, networking,
identity and secrets, Terraform delivery, runner runtime, and validation. Its
recorded critical path is 2 → 7 → 10 → 11 → 13 → 20 → 21 → 23 across several
of those areas. The custom runner image is a parallel track that does not depend
on the Terraform sequence.

The architecture decision record is still Proposed. Its owner describes it as
mostly confirmed, but the repository has no evidence that the required
full-team review happened. Work sourced from that record remains provisional
until the project authority confirms the review outcome.

The network will move to default-deny egress soon. ARC destinations need
firewall approval from the network team, current approval coverage is unknown,
and firewall approval has the longest external lead time even though it is off
the critical path.

The proposed two-region hot-hot topology is not confirmed. It governs CIDR
allocation, Terraform workspace naming, capacity layout, and parts of the
validation plan.

The precise cost model is not yet specified. It is useful planning context, but
no current decision, approval, or downstream work is blocked on it.
