# 🤖 AI-Powered Kubernetes MCP Server

Deploy an AI-connected Kubernetes MCP (Model Context Protocol) server on AWS EKS or EC2+Minikube using **kubectl-ai**, **Google Gemini**, and **FastAPI**. This project demonstrates how to create a natural language interface for Kubernetes operations.

## 🏗️ Architecture Overview

### 🌟 Supported Environments

| Environment | Use Case | Deployment | Status |
|-------------|----------|------------|---------|
| **Amazon EKS** | Production, Enterprise | AWS Managed Kubernetes | ✅ Tested & Working |
| **EC2 + Minikube** | Development, Learning | Single-Node Cluster | ✅ Tested & Working |

### 🏗️ System Components

- **EKS Cluster** (Production) or **Minikube** (Development)
- **kubectl-ai** – Google's CLI for AI-driven Kubernetes commands
- **Gemini API (2.5 Flash)** – Natural language LLM
- **FastAPI MCP Server** – Hosts custom `mcp-schema.json` for command interpretation
- **LoadBalancer/NodePort Service** – Exposes MCP server endpoint
- **Demo App** – `my-website-app` deployed for live testing

---

## 🚀 Quick Start Options

### Option 1: Amazon EKS (Production) - Automated

```bash
# Clone the repository
git clone https://github.com/your-repo/mcp-aws-kubernetes.git
cd mcp-aws-kubernetes

# Set your Gemini API key
export GEMINI_API_KEY="your-gemini-api-key"

# Run automated EKS deployment
cd scripts
./deploy-eks.sh
```

### Option 2: EC2 + Minikube (Development) - Step by Step

Based on the comprehensive guide in our article, follow these steps for a development setup.

---

## 📦 Prerequisites

### Common Requirements
| Tool | Version | Required | Installation |
|------|---------|----------|--------------|
| Gemini API Key | Latest | ✅ | [Get API Key](https://aistudio.google.com/) |
| Docker | 20.10+ | ✅ | System dependent |

### EKS Specific
| Tool | Version | Required | Installation |
|------|---------|----------|--------------|
| AWS CLI | 2.0+ | ✅ | `scripts/eks-setup.sh` |
| eksctl | 0.150+ | ✅ | `scripts/eks-setup.sh` |
| kubectl | 1.28+ | ✅ | `scripts/eks-setup.sh` |
| AWS Credentials | - | ✅ | `aws configure` |

### EC2 + Minikube Specific
| Tool | Version | Required | Installation |
|------|---------|----------|--------------|
| Ubuntu EC2 | 22.04+ | ✅ | AWS Console |
| Minikube | 1.30+ | ✅ | Automated in setup |
| Go | 1.22+ | ✅ | Automated in setup |

---

## 🌩️ EKS Production Deployment

### 1. Prerequisites Setup (Automated)

```bash
# Install all EKS prerequisites
cd scripts
./eks-setup.sh

# Or install individually
./eks-setup.sh aws      # AWS CLI only
./eks-setup.sh kubectl  # kubectl only
./eks-setup.sh eksctl   # eksctl only
```

### 2. Deploy EKS Cluster (Automated)

```bash
# Set your Gemini API key
export GEMINI_API_KEY="your-gemini-api-key"

# Deploy everything automatically
./deploy-eks.sh

# Or for cleanup
./deploy-eks.sh cleanup
```

### 3. Manual EKS Deployment (If needed)

```bash
# Create simplified cluster
eksctl create cluster \
  --name mcp-k8s-cluster \
  --region us-east-1 \
  --version 1.28 \
  --node-type t3.medium \
  --nodes 2 \
  --with-oidc \
  --managed

# Deploy MCP components
kubectl create secret generic gemini-api-key \
  --from-literal=GEMINI_API_KEY=your-gemini-api-key

kubectl apply -f rbac.yaml
kubectl apply -f mock-app.yaml
kubectl apply -f mcp-deployment.yaml
kubectl apply -f mcp-service.yaml
```

---

## 🖥️ EC2 + Minikube Development Setup

### 1. Create AWS Infrastructure

#### Option A: Terraform (Recommended)

```bash
cd terraform
terraform init
terraform plan
terraform apply

# Get connection info
terraform output
```

#### Option B: Manual AWS Setup

**Create Security Group:**
- Name: `mcp-server-sg`
- Inbound Rules:
  - SSH (22) from your IP
  - Custom TCP (30000-32767) for Kubernetes NodePort
  - HTTP (80) for web access

**Launch EC2 Instance:**
- AMI: Ubuntu 22.04 LTS
- Type: t2.medium (minimum)
- Storage: 30 GiB
- Key Pair: Create or use existing
- Security Group: `mcp-server-sg`

**User Data Script:**
```bash
#!/bin/bash
set -e

# Update system
apt-get update -y && apt-get upgrade -y
apt-get install -y curl wget git ca-certificates gnupg lsb-release apt-transport-https software-properties-common

# Install Python
apt-get install -y python3 python3-pip
update-alternatives --install /usr/bin/python python /usr/bin/python3 1
update-alternatives --install /usr/bin/pip pip /usr/bin/pip3 1

# Install Docker
apt-get install -y docker.io
systemctl enable docker
systemctl start docker
usermod -aG docker ubuntu
```

### 2. Setup Development Environment

```bash
# SSH to your EC2 instance
ssh -i ~/.ssh/your-key.pem ubuntu@your-ec2-ip

# Add ubuntu user to docker group (if not done in user-data)
sudo usermod -aG docker ubuntu
sudo reboot

# After reboot, continue setup
```

### 3. Install Kubernetes Tools

```bash
# Install kubectl
curl -LO https://dl.k8s.io/release/v1.30.1/bin/linux/amd64/kubectl
chmod +x kubectl
sudo mv kubectl /usr/local/bin/
kubectl version --client

# Install minikube
curl -LO https://storage.googleapis.com/minikube/releases/latest/minikube-linux-amd64
chmod +x minikube-linux-amd64
sudo mv minikube-linux-amd64 /usr/local/bin/minikube
minikube version

# Install Go
wget https://go.dev/dl/go1.22.3.linux-amd64.tar.gz
sudo tar -C /usr/local -xzf go1.22.3.linux-amd64.tar.gz
echo 'export PATH=$PATH:/usr/local/go/bin:$HOME/go/bin' >> ~/.bashrc
source ~/.bashrc
go version
```

### 4. Install and Build kubectl-ai

```bash
# Method 1: Pre-built Binary (Recommended)
cd /tmp
wget https://github.com/GoogleCloudPlatform/kubectl-ai/releases/download/v0.0.18/kubectl-ai_Linux_x86_64.tar.gz
tar -zxvf kubectl-ai_Linux_x86_64.tar.gz
chmod +x kubectl-ai
sudo mv kubectl-ai /usr/local/bin/
rm -f kubectl-ai_Linux_x86_64.tar.gz

# Method 2: Build from Source (Alternative)
git clone https://github.com/GoogleCloudPlatform/kubectl-ai.git
cd kubectl-ai
go build -o kubectl-ai ./cmd/kubectl-ai
sudo mv kubectl-ai /usr/local/bin/

# Verify installation
kubectl-ai --help
```

### 5. Start Minikube and Deploy

```bash
# Start minikube
minikube start --driver=docker --memory=4096 --cpus=2

# Clone project repo
git clone https://github.com/samcolon/k8s_mcp_server_prod.git
cd k8s_mcp_server_prod

# Create Gemini API secret
kubectl create secret generic gemini-api-key \
  --from-literal=GEMINI_API_KEY=your-gemini-api-key

# Export API key for local use
export GEMINI_API_KEY=your-gemini-api-key
echo 'export GEMINI_API_KEY=your-gemini-api-key' >> ~/.bashrc

# Deploy all manifests
kubectl apply -f rbac.yaml
kubectl apply -f mock-app.yaml
kubectl apply -f mcp-deployment.yaml
kubectl apply -f mcp-service.yaml

# Wait for deployments
kubectl wait --for=condition=available --timeout=300s deployment/my-website-app
kubectl wait --for=condition=available --timeout=300s deployment/mcp-server
```

### 6. Configure kubectl-ai

```bash
# Get minikube IP and service port
MINIKUBE_IP=$(minikube ip)
NODEPORT=$(kubectl get svc mcp-service -o jsonpath='{.spec.ports[0].nodePort}')

echo "Minikube IP: $MINIKUBE_IP"
echo "NodePort: $NODEPORT"

# Create kubectl-ai config
mkdir -p ~/.kube/kubectl-ai
cat > ~/.kube/kubectl-ai/config.yaml << EOF
mcp:
  endpoint: http://$MINIKUBE_IP:$NODEPORT/mcp-schema.json
  name: mcp-server

llm:
  provider: gemini
  model: gemini-2.5-flash
EOF

# Test MCP endpoint
curl http://$MINIKUBE_IP:$NODEPORT/mcp-schema.json
```

---

## 🧪 Testing & Validation

### Install kubectl-ai (Both Environments)

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

### Configure kubectl-ai for Your Environment

#### For EKS (LoadBalancer):
```bash
# Get LoadBalancer endpoint
export EXTERNAL_IP=$(kubectl get svc mcp-service -o jsonpath='{.status.loadBalancer.ingress[0].hostname}')

# Create config
mkdir -p ~/.kube/kubectl-ai
cat > ~/.kube/kubectl-ai/config.yaml << EOF
mcp:
  endpoint: http://$EXTERNAL_IP/mcp-schema.json
  name: eks-mcp-server

llm:
  provider: gemini
  model: gemini-2.5-flash
EOF
```

#### For EKS (NodePort Fallback):
```bash
# Get node IP and service port
NODE_IP=$(kubectl get nodes -o jsonpath='{.items[0].status.addresses[?(@.type=="ExternalIP")].address}')
if [ -z "$NODE_IP" ]; then
    NODE_IP=$(kubectl get nodes -o jsonpath='{.items[0].status.addresses[?(@.type=="InternalIP")].address}')
fi
NODEPORT=$(kubectl get svc mcp-service -o jsonpath='{.spec.ports[0].nodePort}')

# Create config
mkdir -p ~/.kube/kubectl-ai
cat > ~/.kube/kubectl-ai/config.yaml << EOF
mcp:
  endpoint: http://$NODE_IP:$NODEPORT/mcp-schema.json
  name: eks-mcp-server

llm:
  provider: gemini
  model: gemini-2.5-flash
EOF
```

#### For Minikube:
```bash
# Get minikube IP and service port
MINIKUBE_IP=$(minikube ip)
NODEPORT=$(kubectl get svc mcp-service -o jsonpath='{.spec.ports[0].nodePort}')

# Create config
mkdir -p ~/.kube/kubectl-ai
cat > ~/.kube/kubectl-ai/config.yaml << EOF
mcp:
  endpoint: http://$MINIKUBE_IP:$NODEPORT/mcp-schema.json
  name: mcp-server

llm:
  provider: gemini
  model: gemini-2.5-flash
EOF
```

### Test kubectl-ai Commands

```bash
# Set Gemini API key
export GEMINI_API_KEY=your-gemini-api-key

# Test basic functionality (these work without MCP endpoint)
kubectl ai --model gemini-2.5-flash "List all pods in default namespace"
kubectl ai --model gemini-2.5-flash "List all namespaces"
kubectl ai --model gemini-2.5-flash "Scale my-website-app to 6 replicas"
kubectl ai --model gemini-2.5-flash "Deploy nginx pod in test namespace"
kubectl ai --model gemini-2.5-flash "Expose nginx-pod as LoadBalancer on port 80"
kubectl ai --model gemini-2.5-flash "Get logs from my-website-app pods"
```

---

## 💬 Working AI Commands Examples

Based on our successful testing:

| Category | Example Commands | Status |
|----------|------------------|---------|
| **Pod Management** | "List all pods", "Deploy nginx pod in test namespace" | ✅ Working |
| **Deployments** | "Scale my-website-app to 8 replicas", "Restart deployment" | ✅ Working |
| **Cluster Info** | "Show nodes", "List namespaces", "Get cluster events" | ✅ Working |
| **Services** | "Expose pod as LoadBalancer", "Show all services" | ✅ Working |
| **Troubleshooting** | "Get logs from pods", "Describe deployment" | ✅ Working |
| **Interactive** | Creates namespaces, asks for confirmation | ✅ Working |

### Example Session:

```bash
>>> kubectl ai --model gemini-2.5-flash "List all pods in default namespace"
The following pods are running in the default namespace:
• mcp-server-766d9577ff-t57pk
• my-website-app-6b975f7844-fgxmv
• my-website-app-6b975f7844-jxx9h
• my-website-app-6b975f7844-nq7ct
• my-website-app-6b975f7844-smszc

>>> kubectl ai --model gemini-2.5-flash "deploy nginx pod on test namespace"
It seems that the test namespace does not exist. I need to create it first.

The following commands require your approval to run:
• kubectl create namespace test

Do you want to proceed?
1. Yes
2. Yes, and don't ask me again
3. No

Enter your choice: 1
Running: kubectl create namespace test

I have created the test namespace. Now I will deploy the nginx pod...
```

---

## 🔧 Troubleshooting

### Common Issues

1. **MCP Endpoint Not Accessible**
   - kubectl-ai works without MCP endpoint
   - MCP server is optional for basic functionality
   - Check service status: `kubectl get svc mcp-service`

2. **LoadBalancer Pending (EKS)**
   - Use NodePort method instead
   - Check AWS Load Balancer Controller installation
   - Verify security groups allow traffic

3. **kubectl-ai Command Not Found**
   ```bash
   # Reinstall kubectl-ai
   cd /tmp
   wget https://github.com/GoogleCloudPlatform/kubectl-ai/releases/download/v0.0.18/kubectl-ai_Linux_x86_64.tar.gz
   tar -zxvf kubectl-ai_Linux_x86_64.tar.gz
   chmod +x kubectl-ai
   sudo mv kubectl-ai /usr/local/bin/
   ```

4. **Minikube Start Issues**
   ```bash
   # Check Docker status
   sudo systemctl status docker
   
   # Restart Docker if needed
   sudo systemctl restart docker
   
   # Delete and restart minikube
   minikube delete
   minikube start --driver=docker
   ```

5. **EC2 Connection Issues**
   ```bash
   # Check security group
   # Ensure port 22 (SSH) is open from your IP
   # Check key pair permissions
   chmod 400 ~/.ssh/your-key.pem
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

# Minikube specific
minikube status
minikube logs
minikube ip
```

---

## 🧹 Cleanup

### EKS Cleanup
```bash
# Automated cleanup
cd scripts
./deploy-eks.sh cleanup

# Manual cleanup
kubectl delete -f mcp-service.yaml
kubectl delete -f mcp-deployment.yaml
kubectl delete -f mock-app.yaml
kubectl delete -f rbac.yaml
kubectl delete secret gemini-api-key
eksctl delete cluster --name mcp-k8s-cluster --region us-east-1
```

### Minikube Cleanup
```bash
# Delete Kubernetes resources
kubectl delete -f mcp-service.yaml
kubectl delete -f mcp-deployment.yaml
kubectl delete -f mock-app.yaml
kubectl delete -f rbac.yaml
kubectl delete secret gemini-api-key

# Delete minikube cluster
minikube delete

# Terminate EC2 instance (if using)
```

---

## 🗂️ Project Structure

```
mcp-aws-kubernetes/
├── scripts/
│   ├── deploy-eks.sh          # Automated EKS deployment ✅
│   ├── deploy-minikube.sh     # Minikube deployment
│   └── eks-setup.sh           # Prerequisites setup ✅
├── terraform/
│   └── main.tf                # EC2 infrastructure ✅
├── k8s-manifests/
│   ├── rbac.yaml              # Service account & permissions ✅
│   ├── mcp-deployment.yaml    # MCP server deployment ✅
│   ├── mcp-service.yaml       # Load balancer service ✅
│   └── demo-app.yaml          # Demo application ✅
├── docs/
│   └── intro.md               # AI/ML background ✅
├── eks-cluster.yaml           # EKS cluster configuration ✅
├── mcp-schema.json           # MCP protocol schema ✅
├── requirements.txt          # Python dependencies ✅
└── README.md                 # This file ✅
```

---

## 🎯 Key Features

- ✅ **Natural Language Interface**: Talk to Kubernetes in plain English
- ✅ **Production Ready**: EKS with Load Balancer and Auto-scaling
- ✅ **Development Ready**: EC2 + Minikube for learning and testing
- ✅ **AI-Powered**: Google Gemini 2.5 Flash for intelligent responses
- ✅ **Secure**: RBAC configuration with least privilege
- ✅ **Scalable**: Multi-replica deployments with health checks
- ✅ **Interactive**: Approval prompts for destructive operations
- ✅ **Automated**: One-command deployment scripts
- ✅ **Flexible**: Multiple deployment options

---

## 📚 Next Steps

1. **Extend Functionality**: Add more custom MCP actions in `mcp-schema.json`
2. **Monitor**: Set up Prometheus and Grafana for cluster monitoring
3. **CI/CD**: Integrate with GitHub Actions for automated deployments
4. **Security**: Implement network policies and pod security standards
5. **Multi-cluster**: Extend to manage multiple Kubernetes clusters
6. **Custom Agents**: Build domain-specific AI agents
7. **GUI Interface**: Create a web interface for the AI assistant

---

## 🙌 Acknowledgements

- [Google kubectl-ai](https://github.com/GoogleCloudPlatform/kubectl-ai)
- [Amazon EKS](https://aws.amazon.com/eks/)
- [Gemini API](https://ai.google.dev/)
- [FastAPI](https://fastapi.tiangolo.com/)
- [Minikube](https://minikube.sigs.k8s.io/)
- Original MCP server implementation by samcolon

---

## 📖 Additional Resources

### Medium Article
📝 Check out the comprehensive Medium article walkthrough:  
👉 [**AI-Powered Kubernetes MCP Server**](https://medium.com/@samuel.colon.jr/ai-powered-kubernetes-mcp-server-4d6de6233f65)

### Learning Resources
- [AI/ML Background](./docs/intro.md) - Deep dive into AI, ML, and LLMs
- [Kubernetes Documentation](https://kubernetes.io/docs/)
- [AWS EKS Workshop](https://www.eksworkshop.com/)
- [Minikube Tutorial](https://minikube.sigs.k8s.io/docs/tutorials/)

---

**✅ Success Status**: kubectl-ai is working perfectly with Gemini 2.5 Flash for natural language Kubernetes operations on both EKS and Minikube! 🚀

**🎯 Ready to Deploy?** Choose your environment and follow the guide above!
