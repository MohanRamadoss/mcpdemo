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
  default     = "us-east-1"
}

variable "key_name" {
  description = "EC2 Key Pair name"
  type        = string
  default     = "k8-mcp-server"
}

variable "instance_type" {
  description = "EC2 instance type"
  type        = string
  default     = "t3.medium"
}

variable "environment" {
  description = "Environment name"
  type        = string
  default     = "k8s-mcp"
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
  
  filter {
    name   = "virtualization-type"
    values = ["hvm"]
  }
}

# Security Group for Kubernetes MCP Server
resource "aws_security_group" "mcp_server_sg" {
  name_prefix = "${var.environment}-mcp-server-sg"
  description = "Security group for Kubernetes MCP Server"

  # SSH access
  ingress {
    description = "SSH"
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  # Kubernetes NodePort range
  ingress {
    description = "Kubernetes NodePort Range"
    from_port   = 30000
    to_port     = 32767
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  # HTTP (optional)
  ingress {
    description = "HTTP"
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  # HTTPS (optional)
  ingress {
    description = "HTTPS"
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  # Minikube API Server (optional for external access)
  ingress {
    description = "Minikube API Server"
    from_port   = 8443
    to_port     = 8443
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
    Name        = "${var.environment}-mcp-server-sg"
    Environment = var.environment
    Project     = "Kubernetes-MCP"
  }
}

# Key Pair
resource "aws_key_pair" "k8_mcp_server" {
  key_name   = var.key_name
  public_key = file("~/.ssh/id_rsa.pub")  # Make sure this file exists

  tags = {
    Name        = var.key_name
    Environment = var.environment
  }
}

# EC2 Instance for Kubernetes MCP Server
resource "aws_instance" "k8s_mcp_server" {
  ami           = data.aws_ami.ubuntu.id
  instance_type = var.instance_type
  key_name      = aws_key_pair.k8_mcp_server.key_name
  
  vpc_security_group_ids = [aws_security_group.mcp_server_sg.id]
  
  root_block_device {
    volume_type = "gp3"
    volume_size = 30
    encrypted   = true
    
    tags = {
      Name = "${var.environment}-k8s-mcp-root"
    }
  }

  user_data = base64encode(<<-EOF
    #!/bin/bash
    set -e
    
    # Log everything
    exec > >(tee /var/log/user-data.log) 2>&1
    echo "Starting user-data script at $(date)"
    
    # Update system and install essentials
    apt-get update -y && apt-get upgrade -y
    apt-get install -y curl wget git ca-certificates gnupg lsb-release apt-transport-https software-properties-common htop unzip
    
    # ---- Python ----
    apt-get install -y python3 python3-pip python3-venv
    update-alternatives --install /usr/bin/python python /usr/bin/python3 1
    update-alternatives --install /usr/bin/pip pip /usr/bin/pip3 1
    
    # ---- Docker ----
    apt-get install -y docker.io
    systemctl enable docker
    systemctl start docker
    
    # Add ubuntu user to docker group
    usermod -aG docker ubuntu
    
    # ---- Install kubectl ----
    curl -LO "https://dl.k8s.io/release/v1.30.1/bin/linux/amd64/kubectl"
    chmod +x kubectl
    mv kubectl /usr/local/bin/
    
    # ---- Install minikube ----
    curl -LO https://storage.googleapis.com/minikube/releases/latest/minikube-linux-amd64
    chmod +x minikube-linux-amd64
    mv minikube-linux-amd64 /usr/local/bin/minikube
    
    # ---- Install Go ----
    cd /tmp
    wget https://go.dev/dl/go1.22.3.linux-amd64.tar.gz
    tar -C /usr/local -xzf go1.22.3.linux-amd64.tar.gz
    echo 'export PATH=$PATH:/usr/local/go/bin:$HOME/go/bin' >> /home/ubuntu/.bashrc
    echo 'export PATH=$PATH:/usr/local/go/bin:$HOME/go/bin' >> /root/.bashrc
    
    # ---- Setup directories and permissions ----
    mkdir -p /home/ubuntu/k8s-mcp
    chown -R ubuntu:ubuntu /home/ubuntu/k8s-mcp
    
    # Create a setup script for the ubuntu user
    cat > /home/ubuntu/setup-k8s-mcp.sh << 'SETUP_SCRIPT'
#!/bin/bash
set -e

echo "🚀 Setting up Kubernetes MCP Environment..."

# Source the PATH for Go
export PATH=$PATH:/usr/local/go/bin:$HOME/go/bin

# Clone kubectl-ai repo
cd $HOME
if [ ! -d "kubectl-ai" ]; then
    echo "📦 Cloning kubectl-ai repository..."
    git clone https://github.com/GoogleCloudPlatform/kubectl-ai.git
fi

# Build kubectl-ai
cd kubectl-ai
echo "🔨 Building kubectl-ai..."
go build -o kubectl-ai ./cmd/kubectl-ai
sudo mv kubectl-ai /usr/local/bin/

# Clone the MCP server repo (placeholder - replace with actual repo)
cd $HOME
if [ ! -d "k8s-mcp-server" ]; then
    echo "📦 Setting up MCP server directory..."
    mkdir -p k8s-mcp-server
fi

echo "✅ Setup complete! You can now:"
echo "1. Start minikube: minikube start --driver=docker"
echo "2. Create Gemini API secret: kubectl create secret generic gemini-api-key --from-literal=GEMINI_API_KEY=your-key"
echo "3. Deploy MCP server manifests"
echo "4. Configure kubectl-ai"
SETUP_SCRIPT

    chmod +x /home/ubuntu/setup-k8s-mcp.sh
    chown ubuntu:ubuntu /home/ubuntu/setup-k8s-mcp.sh
    
    echo "✅ User-data script completed at $(date)"
    echo "🎯 Instance ready for Kubernetes MCP setup!"
    
    # Create status file
    echo "EC2 instance ready for Kubernetes MCP setup at $(date)" > /home/ubuntu/instance-ready.txt
    chown ubuntu:ubuntu /home/ubuntu/instance-ready.txt
  EOF
  )

  tags = {
    Name        = "${var.environment}-k8s-mcp-server"
    Environment = var.environment
    Project     = "Kubernetes-MCP"
    Role        = "MCPServer"
  }
}

# Outputs
output "instance_id" {
  description = "EC2 Instance ID"
  value       = aws_instance.k8s_mcp_server.id
}

output "public_ip" {
  description = "Public IP address"
  value       = aws_instance.k8s_mcp_server.public_ip
}

output "public_dns" {
  description = "Public DNS name"
  value       = aws_instance.k8s_mcp_server.public_dns
}

output "security_group_id" {
  description = "Security Group ID"
  value       = aws_security_group.mcp_server_sg.id
}

output "ssh_command" {
  description = "SSH command to connect to the instance"
  value       = "ssh -i ~/.ssh/${var.key_name}.pem ubuntu@${aws_instance.k8s_mcp_server.public_ip}"
}

output "connection_info" {
  description = "Connection information and next steps"
  value = {
    ssh_command     = "ssh -i ~/.ssh/${var.key_name}.pem ubuntu@${aws_instance.k8s_mcp_server.public_ip}"
    instance_ip     = aws_instance.k8s_mcp_server.public_ip
    security_group  = aws_security_group.mcp_server_sg.id
    next_steps = [
      "1. SSH to the instance using the command above",
      "2. Run: ./setup-k8s-mcp.sh",
      "3. Start minikube: minikube start --driver=docker",
      "4. Deploy your MCP manifests",
      "5. Configure kubectl-ai with your Gemini API key"
    ]
  }
}
