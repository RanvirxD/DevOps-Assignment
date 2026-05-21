terraform {
  required_version = ">= 1.5.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region                      = var.aws_region
  access_key                  = "test"
  secret_key                  = "test"
  s3_use_path_style           = true
  skip_credentials_validation = true
  skip_metadata_api_check     = true
  skip_requesting_account_id  = true

  endpoints {
    ec2 = "http://localhost:4566"
    s3  = "http://localhost:4566"
  }
}

locals {
  common_tags = {
    Project     = var.project
    Environment = var.environment
    Owner       = var.owner
    ManagedBy   = "terraform"
  }
}

module "network" {
  source = "./modules/network"

  vpc_cidr            = var.vpc_cidr
  public_subnet_cidrs = var.public_subnet_cidrs
  availability_zones  = var.availability_zones
  common_tags         = local.common_tags
}

resource "aws_security_group" "web" {
  name        = "nimbuskart-${var.environment}-web-sg"
  description = "Security group for NimbusKart web tier."
  vpc_id      = module.network.vpc_id

  ingress {
    description = "Allow HTTP from anywhere."
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    description = "Allow HTTPS from anywhere."
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    description = "Allow SSH from configurable CIDR. Broad default is documented as unsafe."
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = [var.ssh_ingress_cidr]
  }

  egress {
    description = "Allow all outbound traffic."
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = merge(local.common_tags, {
    Name = "nimbuskart-${var.environment}-web-sg"
  })
}

resource "aws_instance" "web" {
  count = 2

  ami                    = "ami-12345678"
  instance_type          = "t3.micro"
  subnet_id              = module.network.public_subnet_ids[count.index]
  vpc_security_group_ids = [aws_security_group.web.id]

  tags = merge(local.common_tags, {
    Name = "nimbuskart-${var.environment}-web-${count.index + 1}"
    Tier = "web"
  })
}

resource "aws_s3_bucket" "logs" {
  bucket = "nimbuskart-${var.environment}-app-logs"

  tags = merge(local.common_tags, {
    Name = "nimbuskart-${var.environment}-app-logs"
  })
}

resource "aws_ebs_volume" "known_orphan" {
  availability_zone = var.availability_zones[0]
  size              = 10
  type              = "gp3"

  tags = merge(local.common_tags, {
    Name = "nimbuskart-${var.environment}-known-orphan-volume"
  })
}