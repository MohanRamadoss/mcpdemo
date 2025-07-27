#!/bin/bash

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
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

print_header() {
    echo -e "${PURPLE}=================================${NC}"
    echo -e "${PURPLE}$1${NC}"
    echo -e "${PURPLE}=================================${NC}"
}

# Configuration
CLUSTER_NAME="mcp-k8s-cluster"
REGION="us-east-1"
CLUSTER_CONFIG="../eks-cluster-simple.yaml"

print_header "🚀 AWS EKS Kubernetes MCP Server Deployment"

# Check prerequisites
check_prerequisites() {
    print_status "🔍 Checking prerequisites..."
    
    # Check AWS CLI
    if ! command -v aws &> /dev/null; then
        print_error "AWS CLI is not installed. Please install it first."
        echo "Installation: https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html"
        exit 1
    fi
    
    # Check eksctl
    if ! command -v eksctl &> /dev/null; then
        print_error "eksctl is not installed. Please install it first."
        echo "Installation: https://eksctl.io/installation/"
        exit 1
    fi
    
    # Check kubectl
    if ! command -v kubectl &> /dev/null; then
        print_error "kubectl is not installed. Please install it first."
        echo "Installation: https://kubernetes.io/docs/tasks/tools/"
        exit 1
    fi
    
    # Check helm
    if ! command -v helm &> /dev/null; then
        print_warning "Helm is not installed. Installing..."
        curl https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3 | bash
    fi
    
    # Check AWS credentials
    if ! aws sts get-caller-identity &> /dev/null; then
        print_error "AWS credentials not configured. Run 'aws configure' first."
        exit 1
    fi
    
    # Check cluster config file
    if [ ! -f "$CLUSTER_CONFIG" ]; then
        print_error "Cluster configuration file not found: $CLUSTER_CONFIG"
        print_status "Expected path: $(pwd)/$CLUSTER_CONFIG"
        exit 1
    fi
    
    # Validate YAML syntax
    print_status "Validating YAML syntax..."
    if command -v yq &> /dev/null; then
        if ! yq eval '.' "$CLUSTER_CONFIG" >/dev/null 2>&1; then
            print_error "YAML syntax validation failed"
            print_status "Checking YAML with cat -n:"
            cat -n "$CLUSTER_CONFIG"
            exit 1
        fi
        print_success "YAML syntax is valid"
    else
        print_warning "yq not installed, skipping YAML validation"
    fi
    
    # Check for Gemini API key
    if [ -z "$GEMINI_API_KEY" ]; then
        print_warning "GEMINI_API_KEY environment variable not set"
        read -p "Please enter your Gemini API key: " GEMINI_API_KEY
        if [ -z "$GEMINI_API_KEY" ]; then
            print_error "Gemini API key is required"
            exit 1
        fi
    fi
    
    print_success "All prerequisites satisfied!"
}

# Create a minimal EKS cluster if config fails
create_minimal_cluster() {
    print_header "🔧 Creating Minimal EKS Cluster"
    
    print_status "Creating cluster without config file..."
    
    eksctl create cluster \
        --name "$CLUSTER_NAME" \
        --region "$REGION" \
        --version 1.28 \
        --node-type t3.medium \
        --nodes 2 \
        --nodes-min 1 \
        --nodes-max 3 \
        --with-oidc \
        --enable-ssm \
        --managed \
        --asg-access \
        --external-dns-access \
        --full-ecr-access \
        --alb-ingress-access
    
    if [ $? -eq 0 ]; then
        print_success "Minimal EKS cluster created successfully!"
        return 0
    else
        print_error "Failed to create minimal cluster"
        return 1
    fi
}

# Function to add nodes to existing cluster
add_nodes_to_cluster() {
    print_header "🔧 Adding Worker Nodes to Existing Cluster"
    
    # Check if node group already exists
    if eksctl get nodegroup --cluster="$CLUSTER_NAME" --region="$REGION" --name=mcp-workers &>/dev/null; then
        print_warning "Node group 'mcp-workers' already exists. Skipping creation."
        return 0
    fi
    
    print_status "Creating managed node group for existing cluster..."
    
    eksctl create nodegroup \
        --cluster="$CLUSTER_NAME" \
        --region="$REGION" \
        --name=mcp-workers \
        --node-type=t3.medium \
        --nodes=2 \
        --nodes-min=1 \
        --nodes-max=3 \
        --ssh-access \
        --ssh-public-key=~/.ssh/id_rsa.pub \
        --managed \
        --asg-access \
        --external-dns-access \
        --full-ecr-access \
        --alb-ingress-access
    
    if [ $? -eq 0 ]; then
        print_success "Node group created successfully!"
        return 0
    else
        print_error "Failed to create node group"
        return 1
    fi
}

# Create EKS cluster
create_eks_cluster() {
    print_header "📦 Creating EKS Cluster"
    
    print_status "Creating cluster: $CLUSTER_NAME in region: $REGION"
    print_status "This may take 15-20 minutes..."
    
    if eksctl get cluster --name "$CLUSTER_NAME" --region "$REGION" &>/dev/null; then
        print_warning "Cluster $CLUSTER_NAME already exists."
        
        # Check if cluster has nodes
        print_status "Checking for worker nodes..."
        if kubectl get nodes &>/dev/null && [ $(kubectl get nodes --no-headers | wc -l) -gt 0 ]; then
            print_success "Cluster has worker nodes. Skipping creation."
            return 0
        else
            print_warning "Cluster exists but has no worker nodes. Adding nodes..."
            add_nodes_to_cluster
            return $?
        fi
    fi
    
    # Validate YAML first
    if command -v yq &> /dev/null; then
        print_status "Validating YAML syntax with yq..."
        if ! yq eval '.' "$CLUSTER_CONFIG" >/dev/null 2>&1; then
            print_error "YAML syntax validation failed"
            print_status "Attempting to create minimal cluster instead..."
            create_minimal_cluster
            return $?
        fi
    fi
    
    print_status "Starting cluster creation with config file: $CLUSTER_CONFIG"
    
    # Try with config file first
    if eksctl create cluster --config-file="$CLUSTER_CONFIG"; then
        print_success "EKS cluster created successfully!"
    else
        print_error "Failed to create EKS cluster with config file"
        print_warning "Attempting to create minimal cluster instead..."
        
        if create_minimal_cluster; then
            print_success "Minimal cluster created as fallback"
        else
            print_error "All cluster creation attempts failed"
            print_status "Cleaning up any partial resources..."
            eksctl delete cluster --name "$CLUSTER_NAME" --region "$REGION" --wait || true
            exit 1
        fi
    fi
}

# Update kubeconfig
update_kubeconfig() {
    print_header "⚙️ Updating Kubeconfig"
    
    print_status "Updating kubeconfig for cluster: $CLUSTER_NAME"
    
    if aws eks update-kubeconfig --region "$REGION" --name "$CLUSTER_NAME"; then
        print_success "Kubeconfig updated successfully!"
    else
        print_error "Failed to update kubeconfig"
        exit 1
    fi
    
    # Verify connection
    print_status "Verifying cluster connection..."
    if kubectl cluster-info &>/dev/null; then
        print_success "Successfully connected to cluster!"
        kubectl get nodes
    else
        print_error "Failed to connect to cluster"
        exit 1
    fi
}

# Install AWS Load Balancer Controller
install_alb_controller() {
    print_header "🔄 Installing AWS Load Balancer Controller"
    
    # Check if already installed
    if kubectl get deployment -n kube-system aws-load-balancer-controller &>/dev/null; then
        print_warning "AWS Load Balancer Controller already installed. Skipping..."
        return 0
    fi
    
    # Create service account
    print_status "Creating service account for AWS Load Balancer Controller..."
    
    # Get AWS account ID
    AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query "Account" --output text)
    
    # Download IAM policy
    curl -o iam_policy.json https://raw.githubusercontent.com/kubernetes-sigs/aws-load-balancer-controller/v2.7.2/docs/install/iam_policy.json
    
    # Create IAM policy (ignore error if already exists)
    POLICY_ARN="arn:aws:iam::${AWS_ACCOUNT_ID}:policy/AWSLoadBalancerControllerIAMPolicy"
    aws iam create-policy \
        --policy-name AWSLoadBalancerControllerIAMPolicy \
        --policy-document file://iam_policy.json &>/dev/null || true
    
    rm iam_policy.json
    
    # Associate IAM OIDC provider
    eksctl utils associate-iam-oidc-provider \
        --region="$REGION" \
        --cluster="$CLUSTER_NAME" \
        --approve
    
    # Create service account
    eksctl create iamserviceaccount \
        --cluster="$CLUSTER_NAME" \
        --namespace=kube-system \
        --name=aws-load-balancer-controller \
        --role-name "AmazonEKSLoadBalancerControllerRole" \
        --attach-policy-arn="$POLICY_ARN" \
        --approve \
        --override-existing-serviceaccounts
    
    # Add helm repo if not already added
    if ! helm repo list | grep -q eks; then
        helm repo add eks https://aws.github.io/eks-charts
    fi
    helm repo update
    
    # Install controller
    print_status "Installing AWS Load Balancer Controller..."
    
    VPC_ID=$(aws eks describe-cluster --name "$CLUSTER_NAME" --query "cluster.resourcesVpcConfig.vpcId" --output text)
    
    helm install aws-load-balancer-controller eks/aws-load-balancer-controller \
        -n kube-system \
        --set clusterName="$CLUSTER_NAME" \
        --set serviceAccount.create=false \
        --set serviceAccount.name=aws-load-balancer-controller \
        --set region="$REGION" \
        --set vpcId="$VPC_ID"
    
    print_success "AWS Load Balancer Controller installed!"
    
    # Wait for controller to be ready
    print_status "Waiting for Load Balancer Controller to be ready..."
    kubectl wait --for=condition=available --timeout=300s deployment/aws-load-balancer-controller -n kube-system
}

# Create secrets
create_secrets() {
    print_header "🔐 Creating Kubernetes Secrets"
    
    print_status "Creating Gemini API key secret..."
    
    # Delete existing secret if it exists
    kubectl delete secret gemini-api-key --ignore-not-found=true
    
    # Create new secret
    kubectl create secret generic gemini-api-key \
        --from-literal=GEMINI_API_KEY="$GEMINI_API_KEY"
    
    print_success "Secrets created successfully!"
}

# Deploy MCP server
deploy_mcp_server() {
    print_header "🤖 Deploying MCP Server"
    
    print_status "Applying Kubernetes manifests..."
    
    # Apply manifests in order
    kubectl apply -f ../rbac.yaml || kubectl apply -f ../k8s-manifests/rbac.yaml || true
    kubectl apply -f ../mock-app.yaml || kubectl apply -f ../k8s-manifests/demo-app.yaml || true
    kubectl apply -f ../mcp-deployment.yaml || kubectl apply -f ../k8s-manifests/mcp-deployment.yaml || true
    kubectl apply -f ../mcp-service.yaml || kubectl apply -f ../k8s-manifests/mcp-service.yaml || true
    
    print_status "Waiting for deployments to be ready..."
    kubectl wait --for=condition=available --timeout=300s deployment/my-website-app || true
    kubectl wait --for=condition=available --timeout=300s deployment/mcp-server || true
    
    print_success "MCP server deployed successfully!"
}

# Configure kubectl-ai
configure_kubectl_ai() {
    print_header "🧠 Configuring kubectl-ai"
    
    # Install kubectl-ai if not present
    if ! command -v kubectl-ai &> /dev/null; then
        print_status "Installing kubectl-ai from pre-built binary..."
        
        # Download and install kubectl-ai binary
        cd /tmp
        wget https://github.com/GoogleCloudPlatform/kubectl-ai/releases/download/v0.0.18/kubectl-ai_Linux_x86_64.tar.gz
        tar -zxvf kubectl-ai_Linux_x86_64.tar.gz
        chmod +x kubectl-ai
        sudo mv kubectl-ai /usr/local/bin/
        rm -f kubectl-ai_Linux_x86_64.tar.gz
        cd - >/dev/null
        
        print_success "kubectl-ai installed!"
    fi
    
    # Wait for LoadBalancer to get external IP
    print_status "Waiting for LoadBalancer to get external IP..."
    
    local timeout=600 # 10 minutes
    local elapsed=0
    
    while [ $elapsed -lt $timeout ]; do
        EXTERNAL_IP=$(kubectl get svc mcp-service -o jsonpath='{.status.loadBalancer.ingress[0].hostname}' 2>/dev/null || echo "")
        if [ -n "$EXTERNAL_IP" ] && [ "$EXTERNAL_IP" != "<pending>" ] && [ "$EXTERNAL_IP" != "null" ]; then
            break
        fi
        print_status "Waiting for external IP... (${elapsed}s/${timeout}s)"
        sleep 30
        elapsed=$((elapsed + 30))
    done
    
    if [ -z "$EXTERNAL_IP" ] || [ "$EXTERNAL_IP" == "<pending>" ] || [ "$EXTERNAL_IP" == "null" ]; then
        print_warning "Failed to get LoadBalancer external IP after ${timeout}s"
        print_status "You can check manually later with: kubectl get svc mcp-service"
        return 1
    fi
    
    print_success "External endpoint: $EXTERNAL_IP"
    
    # Create kubectl-ai configuration
    mkdir -p ~/.kube/kubectl-ai
    
    cat > ~/.kube/kubectl-ai/config.yaml << EOF
mcp:
  endpoint: http://$EXTERNAL_IP/mcp-schema.json
  name: eks-mcp-server

llm:
  provider: gemini
  model: gemini-2.5-flash
EOF
    
    # Export Gemini API key
    echo "export GEMINI_API_KEY=$GEMINI_API_KEY" >> ~/.bashrc
    export GEMINI_API_KEY
    
    print_success "kubectl-ai configured successfully!"
    
    # Test the endpoint
    print_status "Testing MCP endpoint..."
    sleep 60  # Wait for service to be fully ready
    
    if curl -s --max-time 10 "http://$EXTERNAL_IP/mcp-schema.json" >/dev/null; then
        print_success "MCP endpoint is accessible!"
    else
        print_warning "MCP endpoint test failed - the service may still be starting"
        print_status "You can test manually with: curl http://$EXTERNAL_IP/mcp-schema.json"
    fi
}

# Cleanup function
cleanup() {
    print_header "🧹 Cleanup EKS Resources"
    
    read -p "Are you sure you want to delete the EKS cluster? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        print_status "Deleting MCP resources..."
        kubectl delete -f ../k8s-manifests/ || true
        kubectl delete -f ../ || true
        kubectl delete secret gemini-api-key || true
        
        print_status "Deleting EKS cluster... (this may take 10-15 minutes)"
        eksctl delete cluster --name "$CLUSTER_NAME" --region "$REGION"
        
        print_success "EKS cluster deleted successfully!"
    else
        print_status "Cleanup cancelled."
    fi
}

# Display summary
show_summary() {
    print_header "📋 Deployment Summary"
    
    EXTERNAL_IP=$(kubectl get svc mcp-service -o jsonpath='{.status.loadBalancer.ingress[0].hostname}' 2>/dev/null || echo "pending")
    
    echo
    echo "🎉 EKS Kubernetes MCP Server deployed successfully!"
    echo
    echo "📊 Cluster Information:"
    echo "• Cluster Name: $CLUSTER_NAME"
    echo "• Region: $REGION"
    echo "• LoadBalancer URL: http://$EXTERNAL_IP"
    echo "• MCP Schema: http://$EXTERNAL_IP/mcp-schema.json"
    echo
    echo "🎯 Next Steps:"
    echo "1. Test kubectl-ai:"
    echo "   kubectl ai --model gemini-2.5-flash \"List all pods in default namespace\""
    echo
    echo "2. Example AI commands:"
    echo "   • 'Scale my-website-app to 6 replicas'"
    echo "   • 'Get logs from my-website-app pods'"
    echo "   • 'Show cluster nodes'"
    echo "   • 'List all deployments'"
    echo
    echo "3. Monitor resources:"
    echo "   kubectl get all"
    echo "   kubectl logs -f deployment/mcp-server"
    echo
    echo "4. Access cluster:"
    echo "   kubectl cluster-info"
    echo "   kubectl get nodes"
    echo
    echo "💡 Useful Commands:"
    echo "• kubectl get svc mcp-service    # Check service status"
    echo "• kubectl describe pod <pod>     # Debug pods"
    echo "• kubectl logs -f deployment/mcp-server  # View MCP logs"
    echo "• eksctl get cluster             # List clusters"
    echo
    print_success "✅ Setup complete! Happy Kubernetes AI management! 🚀"
}

# Main execution
main() {
    case "${1:-deploy}" in
        "deploy")
            check_prerequisites
            create_eks_cluster
            update_kubeconfig
            install_alb_controller
            create_secrets
            deploy_mcp_server
            configure_kubectl_ai
            show_summary
            ;;
        "cleanup")
            cleanup
            ;;
        "help"|"-h"|"--help")
            echo "Usage: $0 [deploy|cleanup|help]"
            echo
            echo "Commands:"
            echo "  deploy   - Deploy EKS cluster and MCP server (default)"
            echo "  cleanup  - Delete EKS cluster and resources"
            echo "  help     - Show this help message"
            ;;
        *)
            print_error "Unknown command: $1"
            echo "Use '$0 help' for usage information"
            exit 1
            ;;
    esac
}

# Execute main function
main "$@"
            update_kubeconfig
            install_alb_controller
            create_secrets
            deploy_mcp_server
            configure_kubectl_ai
            show_summary
            ;;
        "cleanup")
            cleanup
            ;;
        "help"|"-h"|"--help")
            echo "Usage: $0 [deploy|cleanup|help]"
            echo
            echo "Commands:"
            echo "  deploy   - Deploy EKS cluster and MCP server (default)"
            echo "  cleanup  - Delete EKS cluster and resources"
            echo "  help     - Show this help message"
            ;;
        *)
            print_error "Unknown command: $1"
            echo "Use '$0 help' for usage information"
            exit 1
            ;;
    esac
}

# Execute main function
main "$@"
