# SmartMail AI — Amazon RDS PostgreSQL Configuration
# Private, Encrypted, Automated-Backup Database for Production Telemetry & Users

resource "aws_db_parameter_group" "postgres16" {
  name        = "${var.app_name}-${var.environment}-pg16-params"
  family      = "postgres16"
  description = "Custom parameter group for SmartMail AI PostgreSQL 16"

  parameter {
    name  = "rds.force_ssl"
    value = "1"
  }

  tags = {
    Name = "${var.app_name}-${var.environment}-pg16-params"
  }
}

resource "aws_db_instance" "postgres" {
  identifier            = "${var.app_name}-${var.environment}-db"
  engine                = "postgres"
  engine_version        = "16"
  instance_class        = var.db_instance_class
  allocated_storage     = 20
  max_allocated_storage = 100
  storage_type          = "gp3"
  storage_encrypted     = true

  db_name  = var.db_name
  username = var.db_username
  password = random_password.db_password.result
  port     = 5432

  db_subnet_group_name   = aws_db_subnet_group.rds.name
  vpc_security_group_ids = [aws_security_group.rds.id]
  parameter_group_name   = aws_db_parameter_group.postgres16.name
  publicly_accessible    = false

  backup_retention_period    = 7
  backup_window              = "03:00-04:00"
  maintenance_window         = "Sun:04:30-Sun:05:30"
  auto_minor_version_upgrade = true
  copy_tags_to_snapshot      = true
  deletion_protection        = var.enable_deletion_protection
  skip_final_snapshot        = !var.enable_deletion_protection
  final_snapshot_identifier  = "${var.app_name}-${var.environment}-db-final-${formatdate("YYYYMMDDhhmmss", timestamp())}"

  lifecycle {
    ignore_changes = [
      final_snapshot_identifier,
      password
    ]
  }

  tags = {
    Name = "${var.app_name}-${var.environment}-db"
  }
}
