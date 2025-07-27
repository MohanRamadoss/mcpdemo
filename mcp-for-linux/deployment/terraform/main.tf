terraform {
  required_version = ">= 1.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = var.aws_region
}

# Variables
variable "aws_region" {
  description = "AWS region"
  type        = string
  default     = "us-west-2"
}

variable "instance_type" {
  description = "EC2 instance type"
  type        = string
  default     = "t3.medium"
}

variable "key_name" {
  description = "AWS Key Pair name"
  type        = string
}

variable "google_api_key" {
  description = "Google AI API Key"
  type        = string
  sensitive   = true
}

# VPC and Security Groups
resource "aws_vpc" "mcp_vpc" {
  cidr_block           = "10.0.0.0/16"
  enable_dns_hostnames = true
  enable_dns_support   = true

  tags = {
    Name = "mcp-linux-vpc"
  }
}

resource "aws_internet_gateway" "mcp_igw" {
  vpc_id = aws_vpc.mcp_vpc.id

  tags = {
    Name = "mcp-linux-igw"
  }
}

resource "aws_subnet" "mcp_subnet" {
  vpc_id                  = aws_vpc.mcp_vpc.id
  cidr_block              = "10.0.1.0/24"
  availability_zone       = data.aws_availability_zones.available.names[0]
  map_public_ip_on_launch = true

  tags = {
    Name = "mcp-linux-subnet"
  }
}

resource "aws_route_table" "mcp_rt" {
  vpc_id = aws_vpc.mcp_vpc.id

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.mcp_igw.id
  }

  tags = {
    Name = "mcp-linux-rt"
  }
}

resource "aws_route_table_association" "mcp_rta" {
  subnet_id      = aws_subnet.mcp_subnet.id
  route_table_id = aws_route_table.mcp_rt.id
}

resource "aws_security_group" "mcp_sg" {
  name_prefix = "mcp-linux-sg"
  vpc_id      = aws_vpc.mcp_vpc.id

  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    from_port   = 8080
    to_port     = 8080
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    from_port   = 80
    to_port     = 80
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
    Name = "mcp-linux-sg"
  }
}

# Data sources
data "aws_availability_zones" "available" {
  state = "available"
}

data "aws_ami" "ubuntu" {
  most_recent = true
  owners      = ["099720109477"] # Canonical

  filter {
    name   = "name"
    values = ["ubuntu/images/hvm-ssd/ubuntu-22.04-amd64-server-*"]
  }
}

# EC2 Instance
resource "aws_instance" "mcp_server" {
  ami                    = data.aws_ami.ubuntu.id
  instance_type          = var.instance_type
  key_name               = var.key_name
  vpc_security_group_ids = [aws_security_group.mcp_sg.id]
  subnet_id              = aws_subnet.mcp_subnet.id

  user_data = base64encode(templatefile("${path.module}/user_data.sh", {
    google_api_key = var.google_api_key
  }))

  tags = {
    Name = "mcp-linux-server"
    Type = "production"
  }
}

# Outputs
output "instance_ip" {
  description = "Public IP of the MCP server"
  value       = aws_instance.mcp_server.public_ip
}

output "instance_dns" {
  description = "Public DNS of the MCP server"
  value       = aws_instance.mcp_server.public_dns
}

output "ssh_command" {
  description = "SSH command to connect to the server"
  value       = "ssh -i ${var.key_name}.pem ubuntu@${aws_instance.mcp_server.public_ip}"
}

output "http_endpoint" {
  description = "HTTP endpoint for MCP API"
  value       = "http://${aws_instance.mcp_server.public_ip}:8080"
}
