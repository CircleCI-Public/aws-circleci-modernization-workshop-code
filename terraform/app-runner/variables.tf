variable "image_name" {
  type        = string
  description = "Name of the docker image being deployed"
  default     = "public.ecr.aws/k8z4c6u3/aws-circleci"
}

variable "image_tag" {
  type        = string
  description = "The docker image TAG being deployed"
  default     = "latest"
}