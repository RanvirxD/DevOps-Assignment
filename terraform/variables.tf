variable "aws_region" {
  description = "AWS region used by LocalStack."
  type        = string
  default     = "us-east-1"
}

variable "environment" {
  description = "Deployment environment."
  type        = string
  default     = "staging"
}

variable "project" {
  description = "Project name used for tagging."
  type        = string
  default     = "NimbusKart"
}

variable "owner" {
  description = "Owner of the resources."
  type        = string
  default     = "devops-team"
}

variable "ssh_ingress_cidr" {
  description = "CIDR allowed for SSH access. Default is intentionally broad only to match assignment spec."
  type        = string
  default     = "0.0.0.0/0"
}

variable "vpc_cidr" {
  description = "CIDR block for the VPC."
  type        = string
  default     = "10.20.0.0/16"
}

variable "public_subnet_cidrs" {
  description = "CIDR blocks for public subnets."
  type        = list(string)
  default     = ["10.20.1.0/24", "10.20.2.0/24"]
}

variable "availability_zones" {
  description = "Availability zones for public subnets."
  type        = list(string)
  default     = ["us-east-1a", "us-east-1b"]
}