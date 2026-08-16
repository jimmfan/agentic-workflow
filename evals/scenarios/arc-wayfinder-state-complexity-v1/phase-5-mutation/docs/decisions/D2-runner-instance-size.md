# D2: Supersede runner instance size only

Status: approved

Use `m7i.xlarge` for the ARC runner managed node group. This supersedes only the
`m7i.large` instance-size portion of D1.

The following D1 decisions remain active and unchanged:

- dedicated runner compute;
- EKS managed node groups;
- no Karpenter; and
- minimum/desired/maximum scaling of 2/2/6.

Existing W1/W2 implementation remains valid except for the instance-type
literal. Preserve it rather than rebuilding unrelated resources.
