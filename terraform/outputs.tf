output "vpc_id" {
  description = "Created VPC ID."
  value       = module.network.vpc_id
}

output "public_subnet_ids" {
  description = "Created public subnet IDs."
  value       = module.network.public_subnet_ids
}

output "bucket_name" {
  description = "Application logs bucket name."
  value       = aws_s3_bucket.logs.bucket
}