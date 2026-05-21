variable "vpc_cidr" {
  description = "CIDR block for the NimbusKart VPC."
  type        = string
}

variable "public_subnet_cidrs" {
  description = "CIDR blocks for public subnets."
  type        = list(string)
}

variable "availability_zones" {
  description = "Availability zones for public subnets."
  type        = list(string)
}

variable "common_tags" {
  description = "Common tags applied to all supported resources."
  type        = map(string)
}