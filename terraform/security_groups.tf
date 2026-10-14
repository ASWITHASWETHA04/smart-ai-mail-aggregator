# SmartMail AI — Security Groups & Network Firewall Rules
# Enforces Least-Privilege Network Boundaries Between Tiers

# 1. ALB Security Group (Internet Ingress -> Port 5000 Forwarding)
resource "aws_security_group" "alb" {
  name        = "${var.app_name}-${var.environment}-alb-sg"
  description = "Controls HTTP/HTTPS ingress traffic to Application Load Balancer"
  vpc_id      = aws_vpc.main.id

  ingress {
    description = "Allow inbound HTTP from internet"
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    description = "Allow inbound HTTPS from internet"
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    description     = "Forward traffic to ECS Fargate tasks on application port"
    from_port       = var.container_port
    to_port         = var.container_port
    protocol        = "tcp"
    security_groups = [aws_security_group.ecs.id]
  }

  tags = {
    Name = "${var.app_name}-${var.environment}-alb-sg"
  }
}

# 2. ECS Fargate Security Group (Private Ingress from ALB, Egress for APIs & DB)
resource "aws_security_group" "ecs" {
  name        = "${var.app_name}-${var.environment}-ecs-sg"
  description = "Controls ingress to ECS backend tasks strictly from ALB"
  vpc_id      = aws_vpc.main.id

  # Ingress rule defined via aws_security_group_rule to avoid circular dependency
  egress {
    description = "Allow outbound HTTPS for OpenAI API, ECR, CloudWatch, and AWS Secrets Manager"
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    description = "Allow outbound to PostgreSQL RDS"
    from_port   = 5432
    to_port     = 5432
    protocol    = "tcp"
    cidr_blocks = [var.vpc_cidr]
  }

  egress {
    description = "Allow outbound to ElastiCache Redis"
    from_port   = 6379
    to_port     = 6379
    protocol    = "tcp"
    cidr_blocks = [var.vpc_cidr]
  }

  tags = {
    Name = "${var.app_name}-${var.environment}-ecs-sg"
  }
}

resource "aws_security_group_rule" "ecs_ingress_from_alb" {
  type                     = "ingress"
  description              = "Allow traffic on container port strictly from ALB"
  from_port                = var.container_port
  to_port                  = var.container_port
  protocol                 = "tcp"
  security_group_id        = aws_security_group.ecs.id
  source_security_group_id = aws_security_group.alb.id
}

# 3. RDS PostgreSQL Security Group (Private Ingress Strictly from ECS Tasks)
resource "aws_security_group" "rds" {
  name        = "${var.app_name}-${var.environment}-rds-sg"
  description = "Restricts PostgreSQL access strictly to backend ECS tasks"
  vpc_id      = aws_vpc.main.id

  ingress {
    description     = "PostgreSQL port 5432 from ECS tasks"
    from_port       = 5432
    to_port         = 5432
    protocol        = "tcp"
    security_groups = [aws_security_group.ecs.id]
  }

  tags = {
    Name = "${var.app_name}-${var.environment}-rds-sg"
  }
}

# 4. ElastiCache Redis Security Group (Private Ingress Strictly from ECS Tasks)
resource "aws_security_group" "redis" {
  name        = "${var.app_name}-${var.environment}-redis-sg"
  description = "Restricts Redis access strictly to backend ECS tasks"
  vpc_id      = aws_vpc.main.id

  ingress {
    description     = "Redis port 6379 from ECS tasks"
    from_port       = 6379
    to_port         = 6379
    protocol        = "tcp"
    security_groups = [aws_security_group.ecs.id]
  }

  tags = {
    Name = "${var.app_name}-${var.environment}-redis-sg"
  }
}
