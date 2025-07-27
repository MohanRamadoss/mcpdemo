# 🧠 AI-Powered Kubernetes MCP Server (Minikube + Gemini + kubectl-ai)

This project deploys an AI-connected Kubernetes MCP (Model-Controller-Prompt) server on an EC2 instance using **Minikube**, **Google Gemini**, and **kubectl-ai**. The MCP server allows natural-language interaction with Kubernetes — powered by a custom schema and FastAPI backend.

---

## 📖 Full Guide Available

📝 Check out the full Medium article walkthrough here:  
👉 [**Read on Medium**](https://medium.com/@samuel.colon.jr/ai-powered-kubernetes-mcp-server-4d6de6233f65)

---

## 🧱 Architecture Overview

- **EC2 Ubuntu Instance** (T2.Medium, 30 GiB EBS)
- **Minikube** (Docker driver)
- **kubectl-ai** – Google’s CLI for AI-driven Kubernetes commands
- **Gemini API (1.5 Flash)** – Natural language LLM
- **FastAPI MCP Server** – Hosts custom `mcp-schema.json` for command interpretation
- **NodePort Service** – Exposes MCP server endpoint
- **Demo App** – `my-website-app` deployed for live testing

---

## 📦 Prerequisites

| Tool        | Required |
|-------------|----------|
| Ubuntu 22.04 EC2       | ✅ |
| Docker (non-root)      | ✅ |
| Minikube               | ✅ |
| Go 1.22+               | ✅ |
| kubectl                | ✅ |
| Gemini API Key         | ✅ |

---

## ⚙️ Setup Steps

### 🔐 1. Create Security Group

- Allow SSH (22)
- Allow NodePort range: `30000–32767` (TCP)
- Allow HTTP (80)
---

### ☁️ 2. Launch EC2 Instance

- AMI: Ubuntu 22.04+
- Type: `t2.medium` or higher
- Disk: `30 GiB`
- User-data:
  ```bash
  #!/bin/bash

set -e

# Update system and install essentials
apt-get update -y && apt-get upgrade -y
apt-get install -y curl wget git ca-certificates gnupg lsb-release apt-transport-https software-properties-common

# ---- Python ----
apt-get install -y python3 python3-pip
update-alternatives --install /usr/bin/python python /usr/bin/python3 1
update-alternatives --install /usr/bin/pip pip /usr/bin/pip3 1

# ---- Docker ----
apt-get install -y docker.io
systemctl enable docker
systemctl start dockeru
  ```

---

### 🧑‍💻 3. Initial Setup After SSH

```bash
sudo usermod -aG docker ubuntu
sudo reboot
```

---

### 📦 4. Install Requirements

```bash
# kubectl

# Go
  ```

Follow official Minikube install guide:  
👉 https://minikube.sigs.k8s.io/docs/start/

---

### 📁 5. Clone Repos

```bash
git clone https://github.com/your-username/k8s-mcp-server-prod.git
cd k8s-mcp-server-prod

git clone https://github.com/GoogleCloudPlatform/kubectl-ai.git
cd kubectl-ai
go build -o kubectl-ai ./cmd/kubectl-ai
sudo mv kubectl-ai /usr/local/bin/
```

---

### ☸️ 6. Start Minikube

```bash
minikube start --driver=docker
```

---

### 🔌 7. Deploy MCP + App

```bash
kubectl apply -f rbac.yaml
kubectl apply -f my-website-app.yaml
kubectl apply -f mcp-deployment.yaml
kubectl apply -f mcp-service.yaml
```

---

### 🔍 8. Test MCP Server

```bash
minikube ip  # e.g. 192.168.49.2
kubectl get svc mcp-service  # Note NodePort, e.g. 31390

curl http://192.168.49.2:31390/mcp-schema.json
```

✅ Should return your schema in JSON.

---

### 📘 9. Configure `kubectl-ai`

```bash
mkdir -p ~/.kube/kubectl-ai
nano ~/.kube/kubectl-ai/config.yaml
```

Paste:

```yaml
mcp:
  endpoint: http://192.168.49.2:31390/mcp-schema.json
  name: mcp-server

llm:
  provider: gemini
  model: gemini-1.5-flash
```

---

### 🔑 10. Create Gemini Secret

```bash
kubectl create secret generic gemini-api-key   --from-literal=GEMINI_API_KEY=your-key

export GEMINI_API_KEY=your-key
echo 'export GEMINI_API_KEY=your-key' >> ~/.bashrc
source ~/.bashrc
```

---

### 🧠 11. Use `kubectl ai`

```bash
kubectl ai --model gemini-1.5-flash
```

---

## 💬 Demo Prompts

You can now ask `kubectl ai` things like:

| Prompt | Action |
|--------|--------|
| List all pods in the default namespace | `list_pods` |
| Restart the my-website-app deployment | `restart_deployment` |
| Scale the my-website-app to 5 replicas | `scale_deployment` |
| Delete pod `my-website-app-xyz` | `delete_pod` |
| Get logs from pod in default namespace | `get_pod_logs` |
| List all nodes | `get_nodes` |
| Get cluster namespaces | `get_namespaces` |
| Get events in default namespace | `get_events` |

---

## 🧹 Cleanup

```bash
kubectl delete -f mcp-service.yaml
kubectl delete -f mcp-deployment.yaml
kubectl delete -f my-website-app.yaml
kubectl delete -f rbac.yaml
kubectl delete secret gemini-api-key
```

---

## 🙌 Acknowledgements

- [Google kubectl-ai](https://github.com/GoogleCloudPlatform/kubectl-ai)
- [Minikube](https://minikube.sigs.k8s.io/)
- [Gemini API](https://ai.google.dev/)
- [FastAPI](https://fastapi.tiangolo.com/)

---

## 📌 Next Steps

- Add HTTPS ingress controller with TLS
- Package MCP as a Helm chart
- Add multi-model support for OpenAI or Anthropic