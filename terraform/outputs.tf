# SmartMail AI — Terraform Outputs
# Core Infrastructure Endpoints and Resource Identifiers

output "alb_dns_name" {
  description = "Public DNS name of the Application Load Balancer"
  value       = aws_lb.main.dns_name
}

output "cloudfront_domain_name" {
  description = "Public domain name of the CloudFront distribution for the frontend"
  value       = aws_cloudfront_distribution.frontend.domain_name
}

output "ecr_repository_url" {
  description = "URL of the Amazon ECR repository for backend container images"
  value       = aws_ecr_repository.backend.repository_url
}

output "rds_endpoint" {
  description = "Private endpoint of the PostgreSQL RDS instance (accessible only within VPC)"
  value       = aws_db_instance.postgres.endpoint
}

output "redis_endpoint" {
  description = "Private primary endpoint address of the ElastiCache Redis replication group"
  value       = aws_elasticache_replication_group.redis.primary_endpoint_address
}

output "secrets_manager_arn" {
  description = "ARN of the AWS Secrets Manager secret storing application credentials"
  value       = aws_secretsmanager_secret.app_secrets.arn
}

output "ecs_cluster_name" {
  description = "Name of the ECS Fargate cluster"
  value       = aws_ecs_cluster.main.name
}

output "ecs_service_name" {
  description = "Name of the ECS Fargate service"
  value       = aws_ecs_service.backend.name
}

output "cloudwatch_log_group" {
  description = "CloudWatch log group for container logs"
  value       = aws_cloudwatch_log_group.ecs.name
}

output "github_oidc_role_arn" {
  description = "ARN of the IAM role for GitHub Actions OIDC deployment"
  value       = aws_iam_role.github_actions.arn
}

