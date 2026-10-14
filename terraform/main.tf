# SmartMail AI — AWS Infrastructure as Code (Terraform)
# Main Provider & Version Constraints

terraform {
  required_version = ">= 1.5.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.50"
    }
    random = {
      source  = "hashicorp/random"
      version = "~> 3.6"
    }
  }

  # NOTE: For remote state, configure an encrypted S3 backend with environment-isolated state keys.
  # Starting with Terraform v1.10+ (active: v1.16.5), native S3 locking via 'use_lockfile = true'
  # supersedes the legacy DynamoDB lock table requirement via S3 atomic conditional writes:
  # backend "s3" {
  #   bucket       = "smartmail-ai-staging-terraform-state" # Parameterized per environment
  #   key          = "staging/terraform.tfstate"            # Dedicated staging state key (never share with production)
  #   region       = "us-east-1"
  #   encrypt      = true
  #   use_lockfile = true                                  # Native S3 state locking (eliminates DynamoDB table)
  # }
}

provider "aws" {
  region              = var.aws_region
  allowed_account_ids = var.allowed_account_id != "" ? [var.allowed_account_id] : null

  default_tags {
    tags = {
      Project     = "SmartMail AI"
      ManagedBy   = "Terraform"
      Environment = var.environment
      UseCategory = "Academic-Professional-Email-Generator"
    }
  }
}

# Staging Safety Guardrail: Assert that allowed_account_id is explicitly set for staging
check "staging_account_guardrail" {
  assert {
    condition     = var.environment != "staging" || (var.allowed_account_id != "" && can(regex("^[0-9]{12}$", var.allowed_account_id)))
    error_message = "CRITICAL: 'allowed_account_id' must be configured with a valid 12-digit AWS Account ID when environment is 'staging' to prevent accidental execution against an unauthorized account."
  }
}

