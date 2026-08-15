variable "cluster_name" {
  description = "Name of the existing EKS cluster."
  type        = string
}

variable "private_subnet_ids" {
  description = "Private subnet IDs supplied by the existing platform."
  type        = list(string)
}
