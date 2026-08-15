terraform {
  required_version = ">= 1.5"
}

# The cluster is owned by the existing platform and is read as external data.
data "aws_eks_cluster" "existing" {
  name = var.cluster_name
}
