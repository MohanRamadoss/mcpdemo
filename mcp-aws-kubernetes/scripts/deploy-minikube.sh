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

# Check if running as ubuntu user
if [ "$USER" != "ubuntu" ]; then
    print_error "This script should be run as the ubuntu user"
    exit 1
fi

print_status "🚀 Starting Kubernetes MCP Server Deployment on Minikube"

# Check if Gemini API key is provided
if [ -z "$GEMINI_API_KEY" ]; then
    print_warning "GEMINI_API_KEY environment variable not set"
    read -p "Please enter your Gemini API key: " GEMINI_API_KEY
    if [ -z "$GEMINI_API_KEY" ]; then
        print_error "Gemini API key is required"
        exit 1
    fi
fi

# Export the API key
export GEMINI_API_KEY
echo "export GEMINI_API_KEY=$GEMINI_API_KEY" >> ~/.bashrc

# Check if minikube is running
print_status "📋 Checking Minikube status..."
if ! minikube status >/dev/null 2>&1; then
    print_status "🚀 Starting Minikube with Docker driver..."
    minikube start --driver=docker --memory=4096 --cpus=2
    print_success "Minikube started successfully"
else
    print_success "Minikube is already running"
fi

# Wait for minikube to be ready
print_status "⏳ Waiting for Minikube to be ready..."
kubectl wait --for=condition=Ready nodes --all --timeout=300s

# Create namespace if it doesn't exist
print_status "📁 Creating namespace (if needed)..."
kubectl create namespace default --dry-run=client -o yaml | kubectl apply -f -

# Create Gemini API key secret
print_status "🔑 Creating Gemini API key secret..."
kubectl delete secret gemini-api-key --ignore-not-found=true
kubectl create secret generic gemini-api-key \
  --from-literal=GEMINI_API_KEY="$GEMINI_API_KEY"

# Apply RBAC first
print_status "🔐 Applying RBAC configuration..."
kubectl apply -f ../rbac.yaml

# Deploy the mock application
print_status "🚀 Deploying mock application..."
kubectl apply -f ../mock-app.yaml

# Deploy MCP server
print_status "🤖 Deploying MCP server..."
kubectl apply -f ../mcp-deployment.yaml

# Deploy MCP service
print_status "🌐 Deploying MCP service..."
kubectl apply -f ../mcp-service.yaml

# Wait for deployments to be ready
print_status "⏳ Waiting for deployments to be ready..."
kubectl wait --for=condition=available --timeout=300s deployment/my-website-app
kubectl wait --for=condition=available --timeout=300s deployment/mcp-server

# Get service information
print_status "📊 Getting service information..."
MINIKUBE_IP=$(minikube ip)
MCP_NODEPORT=$(kubectl get svc mcp-service -o jsonpath='{.spec.ports[0].nodePort}')

print_success "🎉 Deployment completed successfully!"

echo
echo "=" * 60
print_status "📋 DEPLOYMENT SUMMARY"
echo "=" * 60
echo "🌐 Minikube IP: $MINIKUBE_IP"
echo "🚪 MCP Service NodePort: $MCP_NODEPORT"
echo "🔗 MCP Endpoint: http://$MINIKUBE_IP:$MCP_NODEPORT/mcp-schema.json"
echo

# Test MCP endpoint
print_status "🧪 Testing MCP endpoint..."
if curl -s "http://$MINIKUBE_IP:$MCP_NODEPORT/mcp-schema.json" >/dev/null; then
    print_success "MCP endpoint is accessible!"
else
    print_warning "MCP endpoint test failed - this is normal if the container is still starting"
fi

# Configure kubectl-ai
print_status "⚙️ Configuring kubectl-ai..."
mkdir -p ~/.kube/kubectl-ai

cat > ~/.kube/kubectl-ai/config.yaml << EOF
mcp:
  endpoint: http://$MINIKUBE_IP:$MCP_NODEPORT/mcp-schema.json
  name: mcp-server

llm:
  provider: gemini
  model: gemini-1.5-flash
EOF

print_success "kubectl-ai configured successfully!"

echo
echo "=" * 60
print_status "🚀 NEXT STEPS"
echo "=" * 60
echo "1. Test the MCP endpoint:"
echo "   curl http://$MINIKUBE_IP:$MCP_NODEPORT/mcp-schema.json"
echo
echo "2. Use kubectl-ai (free version):"
echo "   kubectl ai --model gemini-1.5-flash"
echo
echo "3. Example commands to try:"
echo "   • 'List all pods in the default namespace'"
echo "   • 'Scale my-website-app to 8 pods'"
echo "   • 'Get logs from my-website-app pods'"
echo "   • 'Restart the my-website-app deployment'"
echo
echo "4. Monitor deployments:"
echo "   kubectl get pods -w"
echo
echo "5. Check MCP server logs:"
echo "   kubectl logs -f deployment/mcp-server"
echo

print_status "📱 Useful commands:"
echo "• minikube dashboard  # Open Kubernetes dashboard"
echo "• minikube ip         # Get Minikube IP"
echo "• kubectl get all     # List all resources"
echo "• kubectl describe pod <pod-name>  # Debug pods"

print_success "✅ Kubernetes MCP Server is ready to use!"
        sudo mv kubectl-ai /usr/local/bin/
        cd ..
        
        print_success "kubectl-ai installed successfully!"
    else
        print_status "kubectl-ai is already installed."
    fi
}

# Main execution
main() {
    print_status "Starting Minikube MCP deployment..."
    
    check_prerequisites
    start_minikube
    deploy_mcp
    wait_for_deployment
    get_endpoint
    install_kubectl_ai
    configure_kubectl_ai
    
    print_success "Minikube MCP deployment completed successfully!"
    print_status "Test with: kubectl ai --model gemini-2.5-flash 'List all pods in default namespace'"
}

# Handle script arguments
case "${1:-deploy}" in
    "deploy")
        main
        ;;
    "cleanup")
        print_status "Cleaning up Minikube resources..."
        kubectl delete -f k8s-manifests/ || true
        minikube delete
        print_success "Cleanup completed!"
        ;;
    "status")
        kubectl get all
        minikube ip
        kubectl get svc mcp-service-nodeport
        ;;
    *)
        echo "Usage: $0 [deploy|cleanup|status]"
        exit 1
        ;;
esac
