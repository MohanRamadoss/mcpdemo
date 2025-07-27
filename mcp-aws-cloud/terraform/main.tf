# Configure the AWS Provider
terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
  required_version = ">= 1.0"
}

provider "aws" {
  region = var.aws_region
  
  default_tags {
    tags = {
      Project     = "MCP-AWS-Demo"
      Environment = var.environment
      ManagedBy   = "Terraform"
    }
  }
}

# Variables
variable "aws_region" {
  description = "AWS region"
  type        = string
  default     = "us-east-1"
}

variable "environment" {
  description = "Environment name"
  type        = string
  default     = "mcp-demo"
}

variable "vpc_cidr" {
  description = "CIDR block for VPC"
  type        = string
  default     = "10.0.0.0/16"
}

variable "key_name" {
  description = "EC2 Key Pair name"
  type        = string
  default     = "mcp-demo-key"
}

# Data sources
data "aws_availability_zones" "available" {
  state = "available"
}

data "aws_caller_identity" "current" {}

data "aws_ami" "amazon_linux" {
  most_recent = true
  owners      = ["amazon"]
  
  filter {
    name   = "name"
    values = ["amzn2-ami-hvm-*-x86_64-gp2"]
  }
}

# VPC and Networking
resource "aws_vpc" "mcp_demo_vpc" {
  cidr_block           = var.vpc_cidr
  enable_dns_hostnames = true
  enable_dns_support   = true

  tags = {
    Name        = "${var.environment}-vpc"
    Environment = var.environment
    Project     = "MCP-Demo"
  }
}

resource "aws_internet_gateway" "mcp_demo_igw" {
  vpc_id = aws_vpc.mcp_demo_vpc.id

  tags = {
    Name        = "${var.environment}-igw"
    Environment = var.environment
  }
}

# Public Subnets
resource "aws_subnet" "mcp_demo_public_subnet" {
  count = 2
  
  vpc_id                  = aws_vpc.mcp_demo_vpc.id
  cidr_block              = "10.0.${count.index + 1}.0/24"
  availability_zone       = data.aws_availability_zones.available.names[count.index]
  map_public_ip_on_launch = true

  tags = {
    Name        = "${var.environment}-public-subnet-${count.index + 1}"
    Environment = var.environment
    Type        = "Public"
  }
}

# Private Subnets
resource "aws_subnet" "mcp_demo_private_subnet" {
  count = 2
  
  vpc_id            = aws_vpc.mcp_demo_vpc.id
  cidr_block        = "10.0.${count.index + 10}.0/24"
  availability_zone = data.aws_availability_zones.available.names[count.index]

  tags = {
    Name        = "${var.environment}-private-subnet-${count.index + 1}"
    Environment = var.environment
    Type        = "Private"
  }
}

# Route Table for Public Subnets
resource "aws_route_table" "mcp_demo_public_rt" {
  vpc_id = aws_vpc.mcp_demo_vpc.id

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.mcp_demo_igw.id
  }

  tags = {
    Name        = "${var.environment}-public-rt"
    Environment = var.environment
  }
}

# Route Table Associations for Public Subnets
resource "aws_route_table_association" "mcp_demo_public_rta" {
  count = length(aws_subnet.mcp_demo_public_subnet)
  
  subnet_id      = aws_subnet.mcp_demo_public_subnet[count.index].id
  route_table_id = aws_route_table.mcp_demo_public_rt.id
}

# Security Groups
resource "aws_security_group" "mcp_demo_web_sg" {
  name_prefix = "${var.environment}-web-sg"
  vpc_id      = aws_vpc.mcp_demo_vpc.id
  description = "Security group for web servers and MCP server"

  ingress {
    description = "SSH"
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    description = "HTTP"
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    description = "HTTPS"
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    description = "MCP HTTP"
    from_port   = 8080
    to_port     = 8080
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name        = "${var.environment}-web-sg"
    Environment = var.environment
  }
}

resource "aws_security_group" "mcp_demo_db_sg" {
  name_prefix = "${var.environment}-mcp-demo-db-sg"
  description = "Security group for MCP demo database"
  vpc_id      = aws_vpc.mcp_demo_vpc.id

  ingress {
    description     = "MySQL from web security group"
    from_port       = 3306
    to_port         = 3306
    protocol        = "tcp"
    security_groups = [aws_security_group.mcp_demo_web_sg.id]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name        = "${var.environment}-mcp-demo-db-sg"
    Environment = var.environment
  }
}

# IAM Roles and Policies
resource "aws_iam_role" "lambda_execution_role" {
  name = "${var.environment}-lambda-execution-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "lambda.amazonaws.com"
        }
      }
    ]
  })

  tags = {
    Environment = var.environment
  }
}

resource "aws_iam_role_policy_attachment" "lambda_basic_execution" {
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
  role       = aws_iam_role.lambda_execution_role.name
}

resource "aws_iam_role_policy" "lambda_comprehensive_policy" {
  name = "${var.environment}-lambda-comprehensive-policy"
  role = aws_iam_role.lambda_execution_role.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "s3:GetObject",
          "s3:PutObject",
          "s3:DeleteObject",
          "s3:ListBucket",
          "s3:ListAllMyBuckets"
        ]
        Resource = [
          "arn:aws:s3:::*",
          "arn:aws:s3:::*/*"
        ]
      },
      {
        Effect = "Allow"
        Action = [
          "rds:DescribeDBInstances",
          "rds:DescribeDBClusters",
          "rds:DescribeDBSnapshots",
          "rds:ListTagsForResource"
        ]
        Resource = "*"
      },
      {
        Effect = "Allow"
        Action = [
          "cloudwatch:GetMetricStatistics",
          "cloudwatch:ListMetrics",
          "cloudwatch:DescribeAlarms"
        ]
        Resource = "*"
      },
      {
        Effect = "Allow"
        Action = [
          "ce:GetCostAndUsage",
          "ce:GetUsageReport",
          "ce:GetDimensionValues"
        ]
        Resource = "*"
      }
    ]
  })
}

# IAM role for MCP server EC2 instance
resource "aws_iam_role" "mcp_server_role" {
  name = "${var.environment}-mcp-server-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "ec2.amazonaws.com"
        }
      }
    ]
  })

  tags = {
    Name        = "${var.environment}-mcp-server-role"
    Environment = var.environment
  }
}

# Comprehensive policy for MCP server to manage AWS resources
resource "aws_iam_role_policy" "mcp_server_policy" {
  name = "${var.environment}-mcp-server-policy"
  role = aws_iam_role.mcp_server_role.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      # EC2 permissions
      {
        Effect = "Allow"
        Action = [
          "ec2:DescribeInstances",
          "ec2:DescribeInstanceStatus",
          "ec2:StartInstances",
          "ec2:StopInstances",
          "ec2:RebootInstances",
          "ec2:DescribeRegions",
          "ec2:DescribeAvailabilityZones",
          "ec2:DescribeTags"
        ]
        Resource = "*"
      },
      # S3 permissions
      {
        Effect = "Allow"
        Action = [
          "s3:ListAllMyBuckets",
          "s3:ListBucket",
          "s3:GetBucketLocation",
          "s3:GetObject",
          "s3:PutObject",
          "s3:DeleteObject",
          "s3:GetBucketAcl",
          "s3:GetBucketPolicy"
        ]
        Resource = [
          "arn:aws:s3:::*",
          "arn:aws:s3:::*/*"
        ]
      },
      # Lambda permissions
      {
        Effect = "Allow"
        Action = [
          "lambda:ListFunctions",
          "lambda:GetFunction",
          "lambda:InvokeFunction",
          "lambda:GetFunctionConfiguration",
          "lambda:ListTags"
        ]
        Resource = "*"
      },
      # RDS permissions
      {
        Effect = "Allow"
        Action = [
          "rds:DescribeDBInstances",
          "rds:DescribeDBClusters",
          "rds:DescribeDBSnapshots",
          "rds:ListTagsForResource",
          "rds:StartDBInstance",
          "rds:StopDBInstance"
        ]
        Resource = "*"
      },
      # CloudWatch permissions
      {
        Effect = "Allow"
        Action = [
          "cloudwatch:GetMetricStatistics",
          "cloudwatch:ListMetrics",
          "cloudwatch:DescribeAlarms",
          "logs:DescribeLogGroups",
          "logs:DescribeLogStreams",
          "logs:GetLogEvents"
        ]
        Resource = "*"
      },
      # Cost and billing permissions
      {
        Effect = "Allow"
        Action = [
          "ce:GetCostAndUsage",
          "ce:GetUsageReport",
          "ce:GetDimensionValues",
          "ce:GetReservationCoverage",
          "ce:GetReservationPurchaseRecommendation",
          "ce:GetReservationUtilization"
        ]
        Resource = "*"
      },
      # STS permissions for identity
      {
        Effect = "Allow"
        Action = [
          "sts:GetCallerIdentity"
        ]
        Resource = "*"
      }
    ]
  })
}

# Instance profile for EC2
resource "aws_iam_instance_profile" "mcp_server_profile" {
  name = "${var.environment}-mcp-server-profile"
  role = aws_iam_role.mcp_server_role.name

  tags = {
    Environment = var.environment
  }
}

# EC2 Key Pair
resource "aws_key_pair" "mcp_demo_key" {
  key_name   = var.key_name
  public_key = file("~/.ssh/id_rsa.pub")

  tags = {
    Environment = var.environment
  }
}

# EC2 Instances
resource "aws_instance" "mcp_demo_web" {
  count = 2
  
  ami                    = data.aws_ami.amazon_linux.id
  instance_type          = "t3.micro"
  key_name               = aws_key_pair.mcp_demo_key.key_name
  vpc_security_group_ids = [aws_security_group.mcp_demo_web_sg.id]
  subnet_id              = aws_subnet.mcp_demo_public_subnet[count.index].id

  user_data = base64encode(<<-EOF
    #!/bin/bash
    yum update -y
    yum install -y httpd
    systemctl start httpd
    systemctl enable httpd
    echo "<h1>MCP Demo Web Server ${count.index + 1}</h1>" > /var/www/html/index.html
    echo "<p>Instance ID: $(curl -s http://169.254.169.254/latest/meta-data/instance-id)</p>" >> /var/www/html/index.html
    echo "<p>Availability Zone: $(curl -s http://169.254.169.254/latest/meta-data/placement/availability-zone)</p>" >> /var/www/html/index.html
  EOF
  )

  tags = {
    Name        = "${var.environment}-web-server-${count.index + 1}"
    Environment = var.environment
    Role        = "WebServer"
  }
}

resource "aws_instance" "mcp_demo_app" {
  ami                    = data.aws_ami.amazon_linux.id
  instance_type          = "t3.small"
  key_name               = aws_key_pair.mcp_demo_key.key_name
  vpc_security_group_ids = [aws_security_group.mcp_demo_web_sg.id]
  subnet_id              = aws_subnet.mcp_demo_public_subnet[0].id

  user_data = base64encode(<<-EOF
    #!/bin/bash
    yum update -y
    yum install -y python3 python3-pip git
    pip3 install boto3 fastapi uvicorn
    echo "MCP Application Server Ready" > /home/ec2-user/status.txt
  EOF
  )

  tags = {
    Name        = "${var.environment}-app-server"
    Environment = var.environment
    Role        = "ApplicationServer"
  }
}

# Enhanced EC2 instance for MCP server
resource "aws_instance" "mcp_server" {
  ami                    = data.aws_ami.amazon_linux.id
  instance_type          = "t3.medium"
  key_name               = aws_key_pair.mcp_demo_key.key_name
  vpc_security_group_ids = [aws_security_group.mcp_demo_web_sg.id]
  subnet_id              = aws_subnet.mcp_demo_public_subnet[0].id
  iam_instance_profile   = aws_iam_instance_profile.mcp_server_profile.name

  user_data = base64encode(<<-EOF
    #!/bin/bash
    yum update -y
    yum install -y python3 python3-pip git htop
    
    # Install Python dependencies for MCP server
    pip3 install --upgrade pip
    pip3 install boto3 mcp fastmcp google-generativeai python-dotenv httpx
    
    # Create MCP directory
    mkdir -p /opt/mcp-aws
    cd /opt/mcp-aws
    
    # Create systemd service for MCP server
    cat > /etc/systemd/system/mcp-aws.service << 'UNIT'
[Unit]
Description=AWS MCP Server
After=network.target

[Service]
Type=simple
User=ec2-user
WorkingDirectory=/opt/mcp-aws
Environment=PATH=/usr/local/bin:/usr/bin:/bin
Environment=PYTHONPATH=/opt/mcp-aws
ExecStart=/usr/local/bin/python3 aws_server.py --http
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
UNIT

    # Set permissions
    chown -R ec2-user:ec2-user /opt/mcp-aws
    
    # Enable service (will start when aws_server.py is deployed)
    systemctl daemon-reload
    systemctl enable mcp-aws
    
    # Status file
    echo "MCP AWS Server Ready - Deploy aws_server.py to /opt/mcp-aws/" > /home/ec2-user/mcp-status.txt
    echo "Instance ready at: $(date)" >> /home/ec2-user/mcp-status.txt
  EOF
  )

  tags = {
    Name        = "${var.environment}-mcp-server"
    Environment = var.environment
    Role        = "MCPServer"
    Purpose     = "AWS MCP Management Server"
  }
}

# S3 Buckets
resource "random_id" "bucket_suffix" {
  byte_length = 4
}

resource "aws_s3_bucket" "mcp_demo_data" {
  bucket = "${var.environment}-data-bucket-${random_id.bucket_suffix.hex}"

  tags = {
    Name        = "${var.environment}-data-bucket"
    Environment = var.environment
    Purpose     = "Data Storage"
  }
}

resource "aws_s3_bucket" "mcp_demo_logs" {
  bucket = "${var.environment}-logs-bucket-${random_id.bucket_suffix.hex}"

  tags = {
    Name        = "${var.environment}-logs-bucket"
    Environment = var.environment
    Purpose     = "Log Storage"
  }
}

resource "aws_s3_bucket" "mcp_demo_backups" {
  bucket = "${var.environment}-backups-bucket-${random_id.bucket_suffix.hex}"

  tags = {
    Name        = "${var.environment}-backups-bucket"
    Environment = var.environment
    Purpose     = "Backup Storage"
  }
}

# S3 Bucket Configurations
resource "aws_s3_bucket_versioning" "mcp_demo_data_versioning" {
  bucket = aws_s3_bucket.mcp_demo_data.id
  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "mcp_demo_data_encryption" {
  bucket = aws_s3_bucket.mcp_demo_data.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

# Sample S3 Objects
resource "aws_s3_object" "sample_data" {
  bucket = aws_s3_bucket.mcp_demo_data.bucket
  key    = "sample-data/config.json"
  content = jsonencode({
    application = "mcp-demo"
    environment = var.environment
    created_at  = timestamp()
  })
  content_type = "application/json"

  tags = {
    Environment = var.environment
  }
}

resource "aws_s3_object" "sample_log" {
  bucket = aws_s3_bucket.mcp_demo_logs.bucket
  key    = "application-logs/app.log"
  content = "2024-01-01 12:00:00 INFO Application started\n2024-01-01 12:00:01 INFO MCP Demo environment initialized\n"

  tags = {
    Environment = var.environment
  }
}

# Lambda Functions
data "archive_file" "lambda_zip" {
  type        = "zip"
  output_path = "${path.module}/lambda_function.zip"
  source {
    content = <<EOF
import json
import boto3
import os
from datetime import datetime

def lambda_handler(event, context):
    """Simple Lambda function for MCP testing"""
    
    # Get environment info
    environment = os.environ.get('ENVIRONMENT', 'unknown')
    
    # Create response
    response = {
        'statusCode': 200,
        'body': json.dumps({
            'message': 'Hello from AWS Lambda!',
            'environment': environment,
            'timestamp': datetime.utcnow().isoformat(),
            'event': event,
            'function_name': context.function_name if context else 'unknown',
            'aws_request_id': context.aws_request_id if context else 'unknown'
        })
    }
    
    return response
EOF
    filename = "lambda_function.py"
  }
}

resource "aws_lambda_function" "mcp_test_function" {
  filename         = data.archive_file.lambda_zip.output_path
  function_name    = "${var.environment}-mcp-test"
  role            = aws_iam_role.lambda_execution_role.arn
  handler         = "lambda_function.lambda_handler"
  source_code_hash = data.archive_file.lambda_zip.output_base64sha256
  runtime         = "python3.9"
  timeout         = 60
  memory_size     = 256

  environment {
    variables = {
      ENVIRONMENT = var.environment
    }
  }

  tags = {
    Name        = "${var.environment}-mcp-test"
    Environment = var.environment
    Purpose     = "MCP Test Function"
  }
}

resource "aws_lambda_function" "mcp_demo_function" {
  filename         = data.archive_file.lambda_zip.output_path
  function_name    = "${var.environment}-mcp-demo"
  role            = aws_iam_role.lambda_execution_role.arn
  handler         = "lambda_function.lambda_handler"
  source_code_hash = data.archive_file.lambda_zip.output_base64sha256
  runtime         = "python3.9"
  timeout         = 30
  memory_size     = 128

  environment {
    variables = {
      ENVIRONMENT = var.environment
    }
  }

  tags = {
    Name        = "${var.environment}-mcp-demo"
    Environment = var.environment
    Purpose     = "MCP Demo Function"
  }
}

resource "aws_lambda_function" "mcp_data_processor" {
  filename         = data.archive_file.lambda_zip.output_path
  function_name    = "${var.environment}-mcp-data-processor"
  role            = aws_iam_role.lambda_execution_role.arn
  handler         = "lambda_function.lambda_handler"
  source_code_hash = data.archive_file.lambda_zip.output_base64sha256
  runtime         = "python3.9"
  timeout         = 60
  memory_size     = 256

  environment {
    variables = {
      ENVIRONMENT = var.environment
      PURPOSE     = "data-processing"
    }
  }

  tags = {
    Name        = "${var.environment}-mcp-data-processor"
    Environment = var.environment
    Purpose     = "MCP Data Processing"
  }
}

# RDS Database
resource "aws_db_subnet_group" "mcp_demo_db_subnet_group" {
  name       = "${var.environment}-mcp-demo-db-subnet-group"
  subnet_ids = aws_subnet.mcp_demo_private_subnet[*].id

  tags = {
    Name        = "${var.environment}-mcp-demo-db-subnet-group"
    Environment = var.environment
  }
}

resource "random_password" "db_password" {
  length  = 16
  special = true
}

resource "aws_db_instance" "mcp_demo_db" {
  identifier             = "${var.environment}-mcp-demo-db"
  engine                 = "mysql"
  engine_version         = "8.0"
  instance_class         = "db.t3.micro"
  allocated_storage      = 20
  storage_type           = "gp2"
  storage_encrypted      = true

  db_name  = "mcpdemo"
  username = "admin"
  password = random_password.db_password.result

  vpc_security_group_ids = [aws_security_group.mcp_demo_db_sg.id]
  db_subnet_group_name   = aws_db_subnet_group.mcp_demo_db_subnet_group.name

  backup_retention_period = 1
  backup_window          = "03:00-04:00"
  maintenance_window     = "sun:04:00-sun:05:00"

  skip_final_snapshot = true
  deletion_protection = false

  tags = {
    Name        = "${var.environment}-mcp-demo-db"
    Environment = var.environment
    Purpose     = "MCP Demo Database"
  }
}

# CloudWatch Dashboard
resource "aws_cloudwatch_dashboard" "mcp_demo_dashboard" {
  dashboard_name = "${var.environment}-mcp-dashboard"

  dashboard_body = jsonencode({
    widgets = [
      {
        type   = "metric"
        x      = 0
        y      = 0
        width  = 12
        height = 6

        properties = {
          metrics = [
            ["AWS/EC2", "CPUUtilization", "InstanceId", aws_instance.mcp_server.id],
            ["AWS/EC2", "NetworkIn", "InstanceId", aws_instance.mcp_server.id],
            ["AWS/EC2", "NetworkOut", "InstanceId", aws_instance.mcp_server.id]
          ]
          view    = "timeSeries"
          stacked = false
          region  = var.aws_region
          title   = "MCP Server Performance"
          period  = 300
        }
      },
      {
        type   = "metric"
        x      = 0
        y      = 6
        width  = 12
        height = 6

        properties = {
          metrics = [
            ["AWS/Lambda", "Invocations", "FunctionName", aws_lambda_function.mcp_demo_function.function_name],
            ["AWS/Lambda", "Duration", "FunctionName", aws_lambda_function.mcp_demo_function.function_name],
            ["AWS/Lambda", "Errors", "FunctionName", aws_lambda_function.mcp_demo_function.function_name]
          ]
          view    = "timeSeries"
          stacked = false
          region  = var.aws_region
          title   = "Lambda Function Metrics"
          period  = 300
        }
      }
    ]
  })
}

# Outputs
output "vpc_info" {
  description = "VPC information"
  value = {
    vpc_id     = aws_vpc.mcp_demo_vpc.id
    vpc_cidr   = aws_vpc.mcp_demo_vpc.cidr_block
    igw_id     = aws_internet_gateway.mcp_demo_igw.id
  }
}

output "subnet_info" {
  description = "Subnet information"
  value = {
    public_subnets  = aws_subnet.mcp_demo_public_subnet[*].id
    private_subnets = aws_subnet.mcp_demo_private_subnet[*].id
  }
}

output "security_groups" {
  description = "Security group information"
  value = {
    web_sg_id = aws_security_group.mcp_demo_web_sg.id
    db_sg_id  = aws_security_group.mcp_demo_db_sg.id
  }
}

output "ec2_instance_ids" {
  description = "EC2 Instance IDs"
  value = {
    web_servers = aws_instance.mcp_demo_web[*].id
    app_server  = aws_instance.mcp_demo_app.id
    mcp_server  = aws_instance.mcp_server.id
  }
}

output "ec2_public_ips" {
  description = "EC2 Public IP Addresses"
  value = {
    web_servers = aws_instance.mcp_demo_web[*].public_ip
    app_server  = aws_instance.mcp_demo_app.public_ip
    mcp_server  = aws_instance.mcp_server.public_ip
  }
}

output "s3_buckets" {
  description = "S3 Bucket Names"
  value = {
    data_bucket    = aws_s3_bucket.mcp_demo_data.bucket
    logs_bucket    = aws_s3_bucket.mcp_demo_logs.bucket
    backups_bucket = aws_s3_bucket.mcp_demo_backups.bucket
  }
}

output "lambda_functions" {
  description = "Lambda function information"
  value = {
    demo_function     = aws_lambda_function.mcp_demo_function.function_name
    data_processor    = aws_lambda_function.mcp_data_processor.function_name
    test_function     = aws_lambda_function.mcp_test_function.function_name
  }
}

output "rds_info" {
  description = "RDS database information"
  value = {
    endpoint = aws_db_instance.mcp_demo_db.endpoint
    port     = aws_db_instance.mcp_demo_db.port
    database = aws_db_instance.mcp_demo_db.db_name
    username = aws_db_instance.mcp_demo_db.username
  }
  sensitive = false
}

output "mcp_server_info" {
  description = "MCP Server Information"
  value = {
    instance_id  = aws_instance.mcp_server.id
    public_ip    = aws_instance.mcp_server.public_ip
    private_ip   = aws_instance.mcp_server.private_ip
    ssh_command  = "ssh -i ~/.ssh/${var.key_name}.pem ec2-user@${aws_instance.mcp_server.public_ip}"
    http_url     = "http://${aws_instance.mcp_server.public_ip}:8080"
    status_check = "curl http://${aws_instance.mcp_server.public_ip}:8080/health"
  }
}

output "deployment_instructions" {
  description = "Instructions for deploying MCP server"
  value = [
    "1. SSH to MCP server: ssh -i ~/.ssh/${var.key_name}.pem ec2-user@${aws_instance.mcp_server.public_ip}",
    "2. Upload aws_server.py to /opt/mcp-aws/",
    "3. Start service: sudo systemctl start mcp-aws",
    "4. Check status: sudo systemctl status mcp-aws",
    "5. Test MCP server: curl http://${aws_instance.mcp_server.public_ip}:8080/health",
    "6. View logs: sudo journalctl -u mcp-aws -f"
  ]
}

output "sample_mcp_queries" {
  description = "Sample queries to test with your MCP server"
  value = [
    "List all EC2 instances in ${var.aws_region}",
    "Show me all S3 buckets",
    "Get Lambda functions",
    "Start instance ${aws_instance.mcp_demo_web[0].id}",
    "Stop instance ${aws_instance.mcp_demo_web[1].id}",
    "List objects in bucket ${aws_s3_bucket.mcp_demo_data.bucket}",
    "Invoke Lambda function ${aws_lambda_function.mcp_test_function.function_name}",
    "Get CPU metrics for EC2 in the last hour",
    "Show AWS costs for the last 7 days"
  ]
}

output "aws_account_info" {
  description = "AWS account information"
  value = {
    account_id = data.aws_caller_identity.current.account_id
    user_id    = data.aws_caller_identity.current.user_id
    arn        = data.aws_caller_identity.current.arn
  }
}