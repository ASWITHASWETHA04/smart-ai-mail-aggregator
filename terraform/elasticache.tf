# SmartMail AI — Amazon ElastiCache Redis Configuration
# Provides High-Performance Shared Storage for Flask-Limiter Across ECS Tasks

resource "aws_elasticache_parameter_group" "redis7" {
  name        = "${var.app_name}-${var.environment}-redis7-params"
  family      = "redis7"
  description = "Custom parameter group for SmartMail AI ElastiCache Redis 7"

  parameter {
    name  = "maxmemory-policy"
    value = "volatile-lru"
  }

  tags = {
    Name = "${var.app_name}-${var.environment}-redis7-params"
  }
}

resource "aws_elasticache_replication_group" "redis" {
  replication_group_id = "${var.app_name}-${var.environment}-redis"
  description          = "Shared Redis cluster for SmartMail AI rate limiting"
  node_type            = var.redis_node_type
  num_cache_clusters   = 1
  port                 = 6379
  engine_version       = "7.0"
  parameter_group_name = aws_elasticache_parameter_group.redis7.name
  subnet_group_name    = aws_elasticache_subnet_group.redis.name
  security_group_ids   = [aws_security_group.redis.id]

  at_rest_encryption_enabled = true
  transit_encryption_enabled = false
  auto_minor_version_upgrade = true
  apply_immediately          = true

  tags = {
    Name = "${var.app_name}-${var.environment}-redis"
  }
}
