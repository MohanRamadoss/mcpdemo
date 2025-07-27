#!/bin/bash

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd "$SCRIPT_DIR/../.." && pwd)"

print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to deploy with Docker
deploy_docker() {
    print_status "Deploying MCP Linux Agent with Docker..."
    
    cd "$PROJECT_DIR"
    
    # Build the Docker image
    print_status "Building Docker image..."
    docker build -f deployment/docker/Dockerfile -t mcp-linux-agent:latest .
    
    # Create .env file if it doesn't exist
    if [ ! -f deployment/docker/.env ]; then
        print_warning "Creating .env file. Please update with your API key."
        cat > deployment/docker/.env << EOF
GOOGLE_API_KEY=your_google_api_key_here
EOF
    fi
    
    # Deploy with Docker Compose
    print_status "Starting services with Docker Compose..."
    cd deployment/docker
    docker-compose up -d
    
    print_success "Docker deployment completed!"
    print_status "HTTP API available at: http://localhost:8080"
}

# Function to deploy to AWS with Terraform
deploy_aws() {
    print_status "Deploying MCP Linux Agent to AWS with Terraform..."
    
    cd "$PROJECT_DIR/deployment/terraform"
    
    # Check if terraform is installed
    if ! command -v terraform &> /dev/null; then
        print_error "Terraform is not installed. Please install it first."
        exit 1
    fi
    
    # Initialize Terraform
    print_status "Initializing Terraform..."
    terraform init
    
    # Plan deployment
    print_status "Planning Terraform deployment..."
    terraform plan
    
    # Ask for confirmation
    read -p "Do you want to proceed with the deployment? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        print_status "Applying Terraform configuration..."
        terraform apply -auto-approve
        
        print_success "AWS deployment completed!"
        
        # Show outputs
        print_status "Deployment information:"
        terraform output
    else
        print_status "Deployment cancelled."
    fi
}

# Function to deploy to Kubernetes
deploy_k8s() {
    print_status "Deploying MCP Linux Agent to Kubernetes..."
    
    # Check if kubectl is installed
    if ! command -v kubectl &> /dev/null; then
        print_error "kubectl is not installed. Please install it first."
        exit 1
    fi
    
    cd "$PROJECT_DIR"
    
    # Build and tag image for registry
    print_status "Building Docker image for Kubernetes..."
    docker build -f deployment/docker/Dockerfile -t mcp-linux-agent:latest .
    
    # Create namespace
    print_status "Creating Kubernetes namespace..."
    kubectl create namespace mcp-system --dry-run=client -o yaml | kubectl apply -f -
    
    # Apply Kubernetes manifests
    print_status "Applying Kubernetes manifests..."
    kubectl apply -f deployment/kubernetes/
    
    # Wait for deployment
    print_status "Waiting for deployment to be ready..."
    kubectl wait --for=condition=available --timeout=300s deployment/mcp-linux-agent -n mcp-system
    
    print_success "Kubernetes deployment completed!"
    
    # Show service information
    print_status "Service information:"
    kubectl get svc -n mcp-system
}

# Function to deploy to remote server via SSH
deploy_remote() {
    local server_ip=$1
    local ssh_key=$2
    
    if [ -z "$server_ip" ] || [ -z "$ssh_key" ]; then
        print_error "Usage: deploy_remote <server_ip> <ssh_key_path>"
        exit 1
    fi
    
    print_status "Deploying MCP Linux Agent to remote server: $server_ip"
    
    # Create deployment package
    print_status "Creating deployment package..."
    cd "$PROJECT_DIR"
    tar -czf mcp-linux-deploy.tar.gz \
        --exclude='.git' \
        --exclude='venv' \
        --exclude='__pycache__' \
        --exclude='*.pyc' \
        .
    
    # Copy to remote server
    print_status "Copying files to remote server..."
    scp -i "$ssh_key" mcp-linux-deploy.tar.gz ubuntu@"$server_ip":/tmp/
    
    # Deploy on remote server
    print_status "Installing on remote server..."
    ssh -i "$ssh_key" ubuntu@"$server_ip" << 'EOF'
        set -e
        
        # Extract files
        cd /opt
        sudo rm -rf mcp-linux-old
        sudo mv mcp-linux mcp-linux-old 2>/dev/null || true
        sudo mkdir -p mcp-linux
        sudo tar -xzf /tmp/mcp-linux-deploy.tar.gz -C mcp-linux
        sudo chown -R ubuntu:ubuntu mcp-linux
        
        # Set up environment
        cd mcp-linux
        python3 -m venv venv
        source venv/bin/activate
        pip install --upgrade pip
        pip install -r requirements.txt
        
        # Create systemd service
        sudo tee /etc/systemd/system/mcp-linux.service > /dev/null << 'UNIT'
[Unit]
Description=MCP Linux Debug Agent
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/opt/mcp-linux
Environment=PATH=/opt/mcp-linux/venv/bin
ExecStart=/opt/mcp-linux/venv/bin/python main.py --http
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
UNIT
        
        # Restart service
        sudo systemctl daemon-reload
        sudo systemctl enable mcp-linux
        sudo systemctl restart mcp-linux
        
        echo "Deployment completed!"
EOF
    
    # Clean up
    rm mcp-linux-deploy.tar.gz
    
    print_success "Remote deployment completed!"
    print_status "HTTP API available at: http://$server_ip:8080"
}

# Function to show status of deployments
show_status() {
    print_status "Checking deployment status..."
    
    # Check Docker
    if docker ps | grep -q mcp-linux; then
        print_success "Docker containers are running"
        docker ps | grep mcp-linux
    else
        print_warning "No Docker containers found"
    fi
    
    # Check Kubernetes
    if kubectl get deployment mcp-linux-agent -n mcp-system &> /dev/null; then
        print_success "Kubernetes deployment found"
        kubectl get deployment mcp-linux-agent -n mcp-system
    else
        print_warning "No Kubernetes deployment found"
    fi
}

# Main script logic
main() {
    case "${1:-help}" in
        "docker")
            deploy_docker
            ;;
        "aws")
            deploy_aws
            ;;
        "k8s"|"kubernetes")
            deploy_k8s
            ;;
        "remote")
            deploy_remote "$2" "$3"
            ;;
        "status")
            show_status
            ;;
        "help"|*)
            cat << EOF
MCP Linux Agent Deployment Script

Usage: $0 [COMMAND] [OPTIONS]

Commands:
  docker              Deploy with Docker Compose
  aws                 Deploy to AWS with Terraform
  k8s|kubernetes      Deploy to Kubernetes
  remote <ip> <key>   Deploy to remote server via SSH
  status              Check deployment status
  help                Show this help message

Examples:
  $0 docker                                    # Local Docker deployment
  $0 aws                                       # AWS deployment
  $0 k8s                                       # Kubernetes deployment
  $0 remote 1.2.3.4 ~/.ssh/my-key.pem        # Remote server deployment
  $0 status                                    # Check status

Prerequisites:
- Docker & Docker Compose (for docker deployment)
- Terraform (for AWS deployment)
- kubectl (for Kubernetes deployment)
- SSH access (for remote deployment)
EOF
            ;;
    esac
}

main "$@"
