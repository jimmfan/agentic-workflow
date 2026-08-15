variable "cluster_name" {
  description = "Name of the externally managed EKS cluster."
  type        = string
}

variable "private_subnet_ids" {
  description = "Private subnet IDs supplied by the platform."
  type        = list(string)
}

variable "permissions_boundary_arn" {
  description = "Required IAM permissions boundary for roles created here."
  type        = string
}

