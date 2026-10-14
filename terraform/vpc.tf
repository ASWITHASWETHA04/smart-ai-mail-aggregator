# SmartMail AI — VPC & Networking Infrastructure
# Multi-AZ Architecture with Public, Private, and Isolated Database Subnets

resource "aws_vpc" "main" {
  cidr_block           = var.vpc_cidr
  enable_dns_hostnames = true
  enable_dns_support   = true

  tags = {
    Name = "${var.app_name}-${var.environment}-vpc"
  }
}

# Internet Gateway for public ingress
resource "aws_internet_gateway" "igw" {
  vpc_id = aws_vpc.main.id

  tags = {
    Name = "${var.app_name}-${var.environment}-igw"
  }
}

# 1. Public Subnets (ALB & NAT Gateway)
resource "aws_subnet" "public" {
  count                   = length(var.public_subnet_cidrs)
  vpc_id                  = aws_vpc.main.id
  cidr_block              = var.public_subnet_cidrs[count.index]
  availability_zone       = var.availability_zones[count.index]
  map_public_ip_on_launch = true

  tags = {
    Name = "${var.app_name}-${var.environment}-public-${count.index + 1}"
    Tier = "Public"
  }
}

# 2. Private Subnets (ECS Fargate Application Tasks)
resource "aws_subnet" "private" {
  count             = length(var.private_subnet_cidrs)
  vpc_id            = aws_vpc.main.id
  cidr_block        = var.private_subnet_cidrs[count.index]
  availability_zone = var.availability_zones[count.index]

  tags = {
    Name = "${var.app_name}-${var.environment}-private-${count.index + 1}"
    Tier = "Private"
  }
}

# 3. Database Subnets (Isolated RDS PostgreSQL & ElastiCache Redis)
resource "aws_subnet" "database" {
  count             = length(var.database_subnet_cidrs)
  vpc_id            = aws_vpc.main.id
  cidr_block        = var.database_subnet_cidrs[count.index]
  availability_zone = var.availability_zones[count.index]

  tags = {
    Name = "${var.app_name}-${var.environment}-database-${count.index + 1}"
    Tier = "Database"
  }
}

# Database Subnet Group for RDS
resource "aws_db_subnet_group" "rds" {
  name        = "${var.app_name}-${var.environment}-db-subnet-group"
  description = "Subnet group for private RDS PostgreSQL instance"
  subnet_ids  = aws_subnet.database[*].id

  tags = {
    Name = "${var.app_name}-${var.environment}-db-subnet-group"
  }
}

# Subnet Group for ElastiCache Redis
resource "aws_elasticache_subnet_group" "redis" {
  name        = "${var.app_name}-${var.environment}-redis-subnet-group"
  description = "Subnet group for private ElastiCache Redis cluster"
  subnet_ids  = aws_subnet.database[*].id

  tags = {
    Name = "${var.app_name}-${var.environment}-redis-subnet-group"
  }
}

# Cost-Optimized Single NAT Gateway in Public Subnet 1 for Private Egress
resource "aws_eip" "nat" {
  domain     = "vpc"
  depends_on = [aws_internet_gateway.igw]

  tags = {
    Name = "${var.app_name}-${var.environment}-nat-eip"
  }
}

resource "aws_nat_gateway" "nat" {
  allocation_id = aws_eip.nat.id
  subnet_id     = aws_subnet.public[0].id

  tags = {
    Name = "${var.app_name}-${var.environment}-nat"
  }

  depends_on = [aws_internet_gateway.igw]
}

# Route Tables
# Public Route Table -> Internet Gateway
resource "aws_route_table" "public" {
  vpc_id = aws_vpc.main.id

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.igw.id
  }

  tags = {
    Name = "${var.app_name}-${var.environment}-public-rt"
  }
}

resource "aws_route_table_association" "public" {
  count          = length(var.public_subnet_cidrs)
  subnet_id      = aws_subnet.public[count.index].id
  route_table_id = aws_route_table.public.id
}

# Private Route Table -> NAT Gateway (Allows ECS tasks to pull images & reach OpenAI API)
resource "aws_route_table" "private" {
  vpc_id = aws_vpc.main.id

  route {
    cidr_block     = "0.0.0.0/0"
    nat_gateway_id = aws_nat_gateway.nat.id
  }

  tags = {
    Name = "${var.app_name}-${var.environment}-private-rt"
  }
}

resource "aws_route_table_association" "private" {
  count          = length(var.private_subnet_cidrs)
  subnet_id      = aws_subnet.private[count.index].id
  route_table_id = aws_route_table.private.id
}

# Database Route Table (Isolated; No External Egress)
resource "aws_route_table" "database" {
  vpc_id = aws_vpc.main.id

  tags = {
    Name = "${var.app_name}-${var.environment}-database-rt"
  }
}

resource "aws_route_table_association" "database" {
  count          = length(var.database_subnet_cidrs)
  subnet_id      = aws_subnet.database[count.index].id
  route_table_id = aws_route_table.database.id
}
