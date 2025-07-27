#!/bin/bash

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

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

# Check prerequisites
check_prerequisites() {
    print_status "Checking prerequisites..."
    
    # Check if Terraform is installed
    if ! command -v terraform &> /dev/null; then
        print_error "Terraform is not installed. Please install it first."
        exit 1
    fi
    
    # Check if AWS CLI is installed and configured
    if ! command -v aws &> /dev/null; then
        print_error "AWS CLI is not installed. Please install it first."
        exit 1
    fi
    
    # Check AWS credentials
    if ! aws sts get-caller-identity &> /dev/null; then
        print_error "AWS credentials not configured. Run 'aws configure' first."
        exit 1
    fi
    
    # Check for SSH key
    if [ ! -f ~/.ssh/id_rsa.pub ]; then
        print_warning "SSH public key not found at ~/.ssh/id_rsa.pub"
        print_status "Generating SSH key pair..."
        ssh-keygen -t rsa -b 4096 -f ~/.ssh/id_rsa -N ""
    fi
    
    print_success "Prerequisites check passed!"
}

# Deploy infrastructure
deploy() {
    print_status "Deploying AWS infrastructure for MCP..."
    
    # Initialize Terraform
    print_status "Initializing Terraform..."
    terraform init
    
    # Plan deployment
    print_status "Planning Terraform deployment..."
    terraform plan -out=tfplan
    
    # Ask for confirmation
    read -p "Do you want to proceed with the deployment? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        print_status "Applying Terraform configuration..."
        terraform apply tfplan
        
        print_success "Infrastructure deployed successfully!"
        
        # Show deployment information
        print_status "Deployment Information:"
        terraform output
        
        print_status "Next steps:"
        echo "1. Deploy the MCP server code to the EC2 instance"
        echo "2. Test the MCP server functionality"
        echo "3. Use the provided sample queries"
        
    else
        print_status "Deployment cancelled."
        rm -f tfplan
    fi
}

# Destroy infrastructure
destroy() {
    print_warning "This will destroy ALL AWS resources created by this Terraform configuration!"
    read -p "Are you sure you want to continue? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        print_status "Destroying infrastructure..."
        terraform destroy -auto-approve
        print_success "Infrastructure destroyed successfully!"
    else
        print_status "Destroy cancelled."
    fi
}

# Show outputs
show_outputs() {
    print_status "Current deployment outputs:"
    terraform output
}

# Deploy MCP server code
deploy_mcp_server() {
    print_status "Deploying MCP server code..."
    
    # Get MCP server IP
    MCP_SERVER_IP=$(terraform output -raw mcp_server_info | jq -r '.public_ip')
    
    if [ "$MCP_SERVER_IP" == "null" ] || [ -z "$MCP_SERVER_IP" ]; then
        print_error "Could not get MCP server IP. Make sure infrastructure is deployed."
        exit 1
    fi
    
    print_status "MCP Server IP: $MCP_SERVER_IP"
    
    # Copy MCP server code
    print_status "Copying MCP server code..."
    scp -o StrictHostKeyChecking=no -i ~/.ssh/id_rsa ../aws_server.py ec2-user@$MCP_SERVER_IP:/opt/mcp-aws/
    
    # Start MCP service
    print_status "Starting MCP service..."
    ssh -o StrictHostKeyChecking=no -i ~/.ssh/id_rsa ec2-user@$MCP_SERVER_IP << 'EOF'
        sudo systemctl start mcp-aws
        sudo systemctl status mcp-aws --no-pager
        echo "MCP Server deployed and started!"
EOF
    
    print_success "MCP server deployed successfully!"
    print_status "Test the server: curl http://$MCP_SERVER_IP:8080/health"
}

# Test MCP server
test_mcp_server() {
    MCP_SERVER_IP=$(terraform output -raw mcp_server_info | jq -r '.public_ip')
    
    if [ "$MCP_SERVER_IP" == "null" ] || [ -z "$MCP_SERVER_IP" ]; then
        print_error "Could not get MCP server IP."
        exit 1
    fi
    
    print_status "Testing MCP server at $MCP_SERVER_IP:8080..."
    
    # Test health endpoint
    if curl -f -s http://$MCP_SERVER_IP:8080/health > /dev/null; then
        print_success "MCP server is responding!"
    else
        print_error "MCP server is not responding. Check the service status."
        exit 1
    fi
    
    # Show sample queries
    print_status "Sample MCP queries you can try:"
    terraform output sample_mcp_queries
}

# Main script logic
case "${1:-help}" in
    "deploy")
        check_prerequisites
        deploy
        ;;
    "destroy")
        destroy
        ;;
    "outputs")
        show_outputs
        ;;
    "deploy-mcp")
        deploy_mcp_server
        ;;
    "test")
        test_mcp_server
        ;;
    "help"|*)
        cat << EOF
AWS MCP Infrastructure Deployment Script

Usage: $0 [COMMAND]

Commands:
  deploy      Deploy AWS infrastructure with Terraform
  destroy     Destroy all AWS infrastructure
  outputs     Show Terraform outputs
  deploy-mcp  Deploy MCP server code to EC2 instance
  test        Test MCP server functionality
  help        Show this help message

Examples:
  $0 deploy      # Deploy infrastructure
  $0 deploy-mcp  # Deploy MCP server code
  $0 test        # Test MCP server
  $0 destroy     # Destroy everything

Prerequisites:
- Terraform installed
- AWS CLI installed and configured
- SSH key pair (generated automatically if not found)
EOF
        ;;
esac
