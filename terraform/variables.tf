# SmartMail AI — Terraform Variables

variable "aws_region" {
  type        = string
  description = "Target AWS region for resources."
  default     = "us-east-1"
}

variable "environment" {
  type        = string
  description = "Deployment environment tier (production, staging, dev). Explicit selection is required to prevent accidental deployment to production."
  # NOTE: Default 'production' removed as a safety guardrail. Callers must explicitly specify
  # environment via -var-file="terraform.staging.tfvars" or -var="environment=..."

  validation {
    condition     = contains(["production", "staging", "dev"], var.environment)
    error_message = "The environment variable must be one of: 'production', 'staging', 'dev'."
  }
}

variable "allowed_account_id" {
  type        = string
  description = "Target AWS Account ID guardrail. When configured, Terraform will strictly refuse execution against any other account."
  default     = ""

  validation {
    condition = (
      var.environment != "staging" ||
      (var.allowed_account_id != "" && can(regex("^[0-9]{12}$", var.allowed_account_id)))
    )
    error_message = "CRITICAL: When environment is 'staging', 'allowed_account_id' must be explicitly configured with a valid 12-digit AWS Account ID (e.g. '123456789012') to prevent accidental execution against an unauthorized account."
  }
}

variable "app_name" {
  type        = string
  description = "Application identifier used for resource naming."
  default     = "smartmail-ai"
}

variable "vpc_cidr" {
  type        = string
  description = "CIDR block for the dedicated VPC."
  default     = "10.0.0.0/16"
}

variable "availability_zones" {
  type        = list(string)
  description = "AWS availability zones for multi-AZ high availability."
  default     = ["us-east-1a", "us-east-1b"]
}

variable "public_subnet_cidrs" {
  type        = list(string)
  description = "CIDR blocks for public subnets (ALB & NAT Gateway)."
  default     = ["10.0.1.0/24", "10.0.2.0/24"]
}

variable "private_subnet_cidrs" {
  type        = list(string)
  description = "CIDR blocks for private application subnets (ECS Fargate)."
  default     = ["10.0.10.0/24", "10.0.11.0/24"]
}

variable "database_subnet_cidrs" {
  type        = list(string)
  description = "CIDR blocks for isolated database subnets (RDS PostgreSQL & ElastiCache Redis)."
  default     = ["10.0.20.0/24", "10.0.21.0/24"]
}

variable "container_image" {
  type        = string
  description = "Container image URI in ECR (e.g. 123456789012.dkr.ecr.us-east-1.amazonaws.com/smartmail-ai-backend:v1.0.0)."
  default     = ""
}

variable "container_port" {
  type        = number
  description = "Internal port exposed by backend container."
  default     = 5000
}

variable "container_cpu" {
  type        = number
  description = "CPU units allocated for each Fargate task (256 = 0.25 vCPU)."
  default     = 256
}

variable "container_memory" {
  type        = number
  description = "Memory (MB) allocated for each Fargate task (512 = 0.5 GB)."
  default     = 512
}

variable "desired_count" {
  type        = number
  description = "Number of ECS task replicas to run."
  default     = 2
}

variable "min_capacity" {
  type        = number
  description = "Minimum ECS task instances for autoscaling."
  default     = 1
}

variable "max_capacity" {
  type        = number
  description = "Maximum ECS task instances for autoscaling."
  default     = 4
}

variable "db_instance_class" {
  type        = string
  description = "Instance type for Amazon RDS PostgreSQL."
  default     = "db.t4g.micro"
}

variable "db_name" {
  type        = string
  description = "Database name inside RDS PostgreSQL."
  default     = "smartmail_db"
}

variable "db_username" {
  type        = string
  description = "Master username for RDS PostgreSQL."
  default     = "smartmail_admin"
}

variable "redis_node_type" {
  type        = string
  description = "Node type for Amazon ElastiCache Redis cluster."
  default     = "cache.t4g.micro"
}

variable "certificate_arn" {
  type        = string
  description = "Optional AWS Certificate Manager (ACM) ARN for HTTPS listener on ALB."
  default     = ""
}

variable "enable_deletion_protection" {
  type        = bool
  description = "Enable deletion protection on RDS database."
  default     = true
}

variable "log_retention_days" {
  type        = number
  description = "Retention period for CloudWatch logs in days."
  default     = 30
}

variable "github_repo" {
  type        = string
  description = "GitHub repository (owner/repo) permitted to deploy via OIDC (e.g. wipro-org/smartmail-ai)."
  default     = "wipro-org/smartmail-ai"
}

