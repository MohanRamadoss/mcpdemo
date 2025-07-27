# 🤖 AI-Powered Kubernetes MCP Server

Deploy an AI-connected Kubernetes MCP (Model Context Protocol) server on AWS EKS using **kubectl-ai**, **Google Gemini**, and **FastAPI**. This project demonstrates how to create a natural language interface for Kubernetes operations.

## 🏗️ Architecture Overview

### 🌟 Supported Environments

| Environment | Use Case | Deployment |
|-------------|----------|------------|
| **Amazon EKS** | Production, Enterprise | AWS Managed Kubernetes |
| **Minikube** | Development, Learning | Local Single-Node Cluster |

### 🏗️ System Components

- **EKS Cluster** (Production) or **Minikube** (Development)
- **kubectl-ai** – Google's CLI for AI-driven Kubernetes commands
- **Gemini API (2.5 Flash)** – Natural language LLM
- **FastAPI MCP Server** – Optional: Hosts custom `mcp-schema.json` for command interpretation
- **LoadBalancer/NodePort Service** – Exposes MCP server endpoint
- **Demo App** – `my-website-app` deployed for live testing

---

## 🚀 Quick Start - EKS Deployment

### Option 1: Automated Deployment (Recommended)
```bash
# Clone the repository
git clone https://github.com/your-repo/mcp-aws-kubernetes.git
cd mcp-aws-kubernetes

# Set your Gemini API key
export GEMINI_API_KEY="your-gemini-api-key"

# Run automated deployment
cd scripts
./deploy-eks.sh
```

### Option 2: Manual Step-by-Step Deployment

## 📦 Prerequisites

### Common Requirements
| Tool | Version | Required |
|------|---------|----------|
| kubectl | 1.28+ | ✅ |
| Gemini API Key | Latest | ✅ |
| Docker | 20.10+ | ✅ |

### EKS Specific
| Tool | Version | Required |
|------|---------|----------|
| eksctl | 0.150+ | ✅ |
| AWS CLI | 2.0+ | ✅ |
| AWS Credentials | - | ✅ |

---

## 🌩️ EKS Manual Deployment Guide

### 1. Prerequisites Setup

```bash
# Install eksctl
curl --silent --location "https://github.com/weaveworks/eksctl/releases/latest/download/eksctl_$(uname -s)_amd64.tar.gz" | tar xz -C /tmp
sudo mv /tmp/eksctl /usr/local/bin

# Install AWS CLI v2
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip awscliv2.zip
sudo ./aws/install

# Configure AWS credentials
aws configure
```

### 2. Create EKS Cluster

```bash
# Create cluster using eksctl (simplified)
eksctl create cluster \
  --name mcp-k8s-cluster \
  --region us-east-1 \
  --version 1.28 \
  --node-type t3.medium \
  --nodes 2 \
  --with-oidc \
  --managed

# Verify cluster
kubectl get nodes
```

### 3. Deploy MCP Server to EKS

```bash
# Create Gemini API secret
kubectl create secret generic gemini-api-key \
  --from-literal=GEMINI_API_KEY=your-gemini-api-key

# Deploy all manifests
kubectl apply -f rbac.yaml
kubectl apply -f mock-app.yaml
kubectl apply -f mcp-deployment.yaml
kubectl apply -f mcp-service.yaml

# Wait for deployments
kubectl wait --for=condition=available --timeout=300s deployment/mcp-server
kubectl wait --for=condition=available --timeout=300s deployment/my-website-app
```

### 4. Install and Configure kubectl-ai

```bash
# Install kubectl-ai from pre-built binary
cd /tmp
wget https://github.com/GoogleCloudPlatform/kubectl-ai/releases/download/v0.0.18/kubectl-ai_Linux_x86_64.tar.gz
tar -zxvf kubectl-ai_Linux_x86_64.tar.gz
chmod +x kubectl-ai
sudo mv kubectl-ai /usr/local/bin/
rm -f kubectl-ai_Linux_x86_64.tar.gz

# Verify installation
kubectl-ai --help
```

### 5. Configure kubectl-ai for EKS

```bash
# Method 1: LoadBalancer (if external IP is available)
export EXTERNAL_IP=$(kubectl get svc mcp-service -o jsonpath='{.status.loadBalancer.ingress[0].hostname}')

# Method 2: NodePort (fallback method that works reliably)
NODE_IP=$(kubectl get nodes -o jsonpath='{.items[0].status.addresses[?(@.type=="ExternalIP")].address}')
if [ -z "$NODE_IP" ]; then
    NODE_IP=$(kubectl get nodes -o jsonpath='{.items[0].status.addresses[?(@.type=="InternalIP")].address}')
fi
NODEPORT=$(kubectl get svc mcp-service -o jsonpath='{.spec.ports[0].nodePort}')

echo "Node IP: $NODE_IP"
echo "NodePort: $NODEPORT"

# Create kubectl-ai config (works without MCP server endpoint)
mkdir -p ~/.kube/kubectl-ai
cat > ~/.kube/kubectl-ai/config.yaml << EOF
mcp:
  endpoint: http://$NODE_IP:$NODEPORT/mcp-schema.json
  name: eks-mcp-server

llm:
  provider: gemini
  model: gemini-2.5-flash
EOF

# Export Gemini API key
export GEMINI_API_KEY="your-gemini-api-key"
echo 'export GEMINI_API_KEY="your-gemini-api-key"' >> ~/.bashrc
```

---

## 🧪 Testing & Validation

### Test kubectl-ai (Works without MCP endpoint)

```bash
# Set Gemini API key
export GEMINI_API_KEY=your-gemini-api-key

# Test basic functionality
kubectl ai --model gemini-2.5-flash "List all pods in default namespace"
kubectl ai --model gemini-2.5-flash "List all namespaces"
kubectl ai --model gemini-2.5-flash "Scale my-website-app to 6 replicas"
kubectl ai --model gemini-2.5-flash "Deploy nginx pod in test namespace"
kubectl ai --model gemini-2.5-flash "Expose nginx-pod as LoadBalancer on port 80"
```

### Advanced AI Commands

```bash
# Interactive prompts that work
kubectl ai --model gemini-2.5-flash "Create a namespace called production"
kubectl ai --model gemini-2.5-flash "Deploy a redis pod in production namespace"
kubectl ai --model gemini-2.5-flash "Show me all services across all namespaces"
kubectl ai --model gemini-2.5-flash "Get logs from my-website-app pods"
kubectl ai --model gemini-2.5-flash "Describe the mcp-server deployment"
```

---

## 💬 Working AI Commands Examples

| Category | Example Commands | Status |
|----------|------------------|---------|
| **Pod Management** | "List all pods", "Deploy nginx pod in test namespace" | ✅ Working |
| **Deployments** | "Scale app to 5 replicas", "Restart deployment" | ✅ Working |
| **Cluster Info** | "Show nodes", "List namespaces", "Get cluster events" | ✅ Working |
| **Services** | "Expose pod as LoadBalancer", "Show all services" | ✅ Working |
| **Troubleshooting** | "Get logs from pods", "Describe deployment" | ✅ Working |

---

## 🔧 Troubleshooting

### Common Issues

1. **MCP Endpoint Not Accessible**
   - kubectl-ai works without MCP endpoint
   - MCP server is optional for basic functionality
   - Check service status: `kubectl get svc mcp-service`

2. **LoadBalancer Pending**
   - Use NodePort method instead
   - Check AWS Load Balancer Controller installation

3. **kubectl-ai Command Not Found**
   ```bash
   # Reinstall kubectl-ai
   cd /tmp
   wget https://github.com/GoogleCloudPlatform/kubectl-ai/releases/download/v0.0.18/kubectl-ai_Linux_x86_64.tar.gz
   tar -zxvf kubectl-ai_Linux_x86_64.tar.gz
   chmod +x kubectl-ai
   sudo mv kubectl-ai /usr/local/bin/
   ```

### Debug Commands

```bash
# Check cluster status
kubectl get nodes
kubectl get all

# Check MCP server logs
kubectl logs -f deployment/mcp-server

# Check service endpoints
kubectl get svc
kubectl describe svc mcp-service

# Test Gemini API connectivity
kubectl ai --model gemini-2.5-flash "test connection"
```

---

## 🧹 Cleanup

```bash
# Delete MCP resources
kubectl delete -f mcp-service.yaml
kubectl delete -f mcp-deployment.yaml
kubectl delete -f mock-app.yaml
kubectl delete -f rbac.yaml
kubectl delete secret gemini-api-key

# Delete EKS cluster
eksctl delete cluster --name mcp-k8s-cluster --region us-east-1
```

---

## 🗂️ Project Structure

```
mcp-aws-kubernetes/
├── scripts/
│   ├── deploy-eks.sh          # Automated EKS deployment
│   ├── deploy-minikube.sh     # Minikube deployment
│   └── eks-setup.sh           # Prerequisites setup
├── k8s-manifests/
│   ├── rbac.yaml              # Service account & permissions
│   ├── mcp-deployment.yaml    # MCP server deployment
│   ├── mcp-service.yaml       # Load balancer service
│   └── demo-app.yaml          # Demo application
├── terraform/
│   └── main.tf                # Infrastructure as code
├── eks-cluster.yaml           # EKS cluster configuration
├── mcp-schema.json           # MCP protocol schema
└── README.md                 # This file
```

---

## 🎯 Key Features

- ✅ **Natural Language Interface**: Talk to Kubernetes in plain English
- ✅ **Production Ready**: EKS with Load Balancer and Auto-scaling
- ✅ **AI-Powered**: Google Gemini 2.5 Flash for intelligent responses
- ✅ **Secure**: RBAC configuration with least privilege
- ✅ **Scalable**: Multi-replica deployments with health checks
- ✅ **Interactive**: Approval prompts for destructive operations

---

## 📚 Next Steps

1. **Extend Functionality**: Add more custom MCP actions in `mcp-schema.json`
2. **Monitor**: Set up Prometheus and Grafana for cluster monitoring
3. **CI/CD**: Integrate with GitHub Actions for automated deployments
4. **Security**: Implement network policies and pod security standards
5. **Multi-cluster**: Extend to manage multiple Kubernetes clusters

---

## 🙌 Acknowledgements

- [Google kubectl-ai](https://github.com/GoogleCloudPlatform/kubectl-ai)
- [Amazon EKS](https://aws.amazon.com/eks/)
- [Gemini API](https://ai.google.dev/)
- [FastAPI](https://fastapi.tiangolo.com/)

---

**✅ Success Status**: kubectl-ai is working perfectly with Gemini 2.5 Flash for natural language Kubernetes operations!
