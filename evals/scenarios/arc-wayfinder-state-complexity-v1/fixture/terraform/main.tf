terraform {
  required_version = ">= 1.5"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = ">= 5.0"
    }
  }
}

# The cluster is owned by the platform repository. This module reads it only.
data "aws_eks_cluster" "existing" {
  name = var.cluster_name
}

