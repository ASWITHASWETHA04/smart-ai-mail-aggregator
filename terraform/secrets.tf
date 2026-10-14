# SmartMail AI — AWS Secrets Manager Configuration
# Stores Database Credentials, JWT Keys, and OpenAI API Key Securely
# Secrets are injected directly into ECS Fargate containers via task execution role

resource "random_password" "jwt_secret" {
  length  = 64
  special = false
}

resource "random_password" "flask_secret" {
  length  = 64
  special = false
}

resource "random_password" "db_password" {
  length  = 32
  special = false
}

# Master Application Secret in AWS Secrets Manager
resource "aws_secretsmanager_secret" "app_secrets" {
  name                    = "${var.app_name}/${var.environment}/credentials"
  description             = "Production runtime secrets for SmartMail AI backend"
  recovery_window_in_days = 7

  tags = {
    Name = "${var.app_name}-${var.environment}-secrets"
  }
}

resource "aws_secretsmanager_secret_version" "app_secrets" {
  secret_id = aws_secretsmanager_secret.app_secrets.id
  secret_string = jsonencode({
    SECRET_KEY     = random_password.flask_secret.result
    JWT_SECRET_KEY = random_password.jwt_secret.result
    DB_PASSWORD    = random_password.db_password.result
    OPENAI_API_KEY = "REPLACE_WITH_ACTUAL_OPENAI_API_KEY_IN_CONSOLE"
    OPENAI_MODEL   = "gpt-4o-mini"
  })

  lifecycle {
    ignore_changes = [
      secret_string
    ]
  }
}
