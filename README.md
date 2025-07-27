# 🤖 Model Context Protocol (MCP) Agent Collection

A comprehensive collection of AI agents and servers built with the Model Context Protocol (MCP) and powered by Google's Gemini 2.5 Flash AI model.

## 🎯 What This Repository Contains

This repository showcases five different MCP server architectures and provides complete documentation for building AI agents with tool-calling capabilities, including cloud infrastructure management and Kubernetes operations.

### 🌤️ Weather MCP Agent
- **Location**: `mcp-weather-client-tutorial/`
- **Type**: External API Integration
- **Tools**: 5 weather-focused tools
- **Features**: US weather forecasts, alerts, international city coordinates
- **Best For**: Learning API integration with MCP

### 🧮 Calculator MCP Agent  
- **Location**: `mcp-calculator/`
- **Type**: Pure Computation
- **Tools**: 13 mathematical functions
- **Features**: Scientific calculations, trigonometry, error handling
- **Best For**: Understanding MCP basics and mathematical operations

### 🐧 Linux MCP Agent
- **Location**: `mcp-for-linux/`
- **Type**: System Administration
- **Tools**: 25+ system tools across 8 categories
- **Features**: Modular architecture, comprehensive Linux system management
- **Best For**: Production-ready system administration

### ☸️ Kubernetes MCP Agent ⭐ **NEW!**
- **Location**: `mcp-aws-kubernetes/`
- **Type**: Cloud Infrastructure + AI
- **Tools**: kubectl-ai + Gemini 2.5 Flash integration
- **Features**: Natural language Kubernetes operations, EKS + Minikube deployment
- **Best For**: AI-powered Kubernetes management

### ☁️ AWS Cloud MCP Agent 🚧 **IN DEVELOPMENT**
- **Location**: `mcp-aws-cloud/`
- **Type**: Cloud Services Management
- **Tools**: AWS SDK + AI integration (planned)
- **Features**: EC2, S3, Lambda, VPC management through natural language
- **Best For**: Comprehensive AWS cloud operations

## 🚀 Quick Start

### Prerequisites
- Python 3.8+ (Python 3.11+ recommended)
- Google AI API key (already configured)
- Linux/macOS/Windows (WSL2 recommended for Windows)
- **NEW**: AWS CLI and kubectl for cloud projects

### One-Command Setup
```bash
# Clone and set up the entire MCP collection
git clone <your-repo-url>
cd MCP

# Create shared virtual environment
python3 -m venv venv
source venv/bin/activate  # Linux/macOS
# venv\Scripts\activate   # Windows

# Install all dependencies (including new cloud tools)
pip install --upgrade pip
pip install mcp fastmcp google-generativeai python-dotenv httpx psutil aiohttp
pip install kubernetes boto3 fastapi uvicorn  # For cloud projects
```

### Try Each Agent

**Weather Agent:**
```bash
cd mcp-weather-client-tutorial
python3 advanced_client.py weather_server.py
# Ask: "What are the weather alerts in California?"
```

**Calculator Agent:**
```bash
cd ../mcp-calculator  
python3 advanced_calculator_client.py mcp_server.py
# Ask: "What is the square root of 144?"
```

**Linux Agent:**
```bash
cd ../mcp-for-linux
python3 advanced_linux_client.py main.py
# Ask: "What's using the most CPU?"
```

**Kubernetes Agent:** ⭐ **NEW!**
```bash
cd ../mcp-aws-kubernetes

# Option 1: EKS Production Deployment
export GEMINI_API_KEY="your-api-key"
./scripts/deploy-eks.sh

# Option 2: Minikube Development
./scripts/deploy-minikube.sh

# Use kubectl-ai for natural language K8s operations
kubectl ai --model gemini-2.5-flash "List all pods in default namespace"
kubectl ai --model gemini-2.5-flash "Scale my-website-app to 6 replicas"
```

**AWS Cloud Agent:** 🚧 **COMING SOON**
```bash
cd ../mcp-aws-cloud
# Full AWS integration in development
```

## 📊 Architecture Comparison

| Feature | Weather MCP | Calculator MCP | Linux MCP | **Kubernetes MCP** ⭐ | **AWS Cloud MCP** 🚧 |
|---------|-------------|----------------|-----------|------------------------|----------------------|
| **Architecture** | Single-file | Single-file | Modular | **Cloud-native** | **Multi-service** |
| **Complexity** | Medium | Low | High | **High** | **Very High** |
| **Tool Count** | 5 tools | 13 functions | 25+ tools | **kubectl-ai integration** | **50+ AWS services** |
| **External APIs** | ✅ Weather API | ❌ None | ✅ System APIs | **✅ Kubernetes API** | **✅ AWS APIs** |
| **Async Support** | ✅ Yes | ❌ No | ✅ Yes | **✅ Yes** | **✅ Yes** |
| **Deployment** | Docker + Local | Local only | Docker + SSH + K8s | **EKS + Minikube** | **Multi-cloud** |
| **Use Case** | API learning | MCP basics | Production systems | **K8s management** | **Cloud operations** |
| **AI Integration** | Basic | Basic | Advanced | **kubectl-ai + Gemini** | **Planned** |

## 🏗️ Project Structure

```
MCP/
├── 📖 docs/                           # Comprehensive documentation
│   ├── intro.md                       # AI/ML/LLM fundamentals ⭐ NEW
│   ├── part1-foundations.md           # AI agents fundamentals
│   ├── part2-tool-calling.md          # Tool calling patterns
│   ├── part3-mcp-intro.md             # MCP server introduction
│   ├── part4-setup.md                 # Development environment
│   └── part5-mcp-setup.md             # Server installation guide
│
├── 🌤️ mcp-weather-client-tutorial/    # Weather MCP implementation
│   ├── weather_server.py              # FastMCP weather server
│   ├── advanced_client.py             # Gemini 2.5 Flash client
│   └── README.md                      # Weather-specific guide
│
├── 🧮 mcp-calculator/                  # Calculator MCP implementation
│   ├── mcp_server.py                  # Scientific calculator server
│   └── README.md                      # Calculator-specific guide
│
├── 🐧 mcp-for-linux/                   # Linux MCP implementation
│   ├── main.py                        # Modular server loader
│   ├── tools/                         # Tool modules (8 categories)
│   ├── resources/                     # Resource modules
│   ├── deployment/                    # Production deployment
│   ├── arch.md                        # Architecture documentation
│   └── README.md                      # Linux-specific guide
│
├── ☸️ mcp-aws-kubernetes/              # ⭐ NEW: Kubernetes MCP server
│   ├── 📁 scripts/                    # Deployment automation
│   │   ├── deploy-eks.sh              # ✅ EKS automated deployment
│   │   ├── deploy-minikube.sh         # ✅ Minikube deployment
│   │   └── eks-setup.sh               # ✅ Prerequisites setup
│   ├── 📁 k8s-manifests/              # Kubernetes YAML files
│   │   ├── rbac.yaml                  # ✅ Security configuration
│   │   ├── mcp-deployment.yaml        # ✅ MCP server deployment
│   │   ├── mcp-service.yaml           # ✅ LoadBalancer/NodePort
│   │   └── demo-app.yaml              # ✅ Demo application
│   ├── 📁 terraform/                  # Infrastructure as Code
│   │   └── main.tf                    # ✅ EC2 + Minikube setup
│   ├── 📄 eks-cluster.yaml            # ✅ EKS cluster configuration
│   ├── 📄 mcp-schema.json             # ✅ Tool definitions
│   └── 📖 README.md                   # ✅ Comprehensive guide
│
├── ☁️ mcp-aws-cloud/                   # 🚧 AWS Cloud MCP server
│   └── 🚧 (In Development)            # Comprehensive AWS integration
│
├── 🛠️ templates/                       # Project templates
│   ├── simple_mcp_server.py          # Basic server template
│   └── simple_mcp_client.py          # Basic client template
│
├── 📜 scripts/                         # Utility scripts
│   ├── start_servers.sh               # Start all servers
│   ├── test_setup.sh                  # Validate installation
│   └── manage_servers.sh              # Server management
│
├── .env                               # Environment configuration
├── requirements.txt                   # Python dependencies
└── README.md                          # This master guide
```

## 🎓 Learning Path

### 1. **Start with Foundations** (`docs/intro.md`) ⭐ **UPDATED**
- **NEW**: Complete AI/ML/LLM background
- Understanding of modern language models (GPT, Gemini, Claude)
- Transformer architecture and attention mechanisms
- Multi-agent LLM systems and reasoning capabilities

### 2. **Learn Tool Calling** (`docs/part2-tool-calling.md`)
- See real examples from our implementations
- Understand best practices
- Learn error handling patterns
- **NEW**: Advanced kubectl-ai integration patterns

### 3. **Explore MCP Servers** (`docs/part3-mcp-intro.md`)
- Compare single-file vs modular patterns
- Understand transport options
- See production deployment strategies
- **NEW**: Cloud-native MCP architectures

### 4. **Set Up Your Environment** (`docs/part4-setup.md`)
- Complete development setup
- IDE configuration
- Testing and validation
- **NEW**: AWS and Kubernetes prerequisites

### 5. **Deploy MCP Servers** (`docs/part5-mcp-setup.md`)
- Server installation and configuration
- Multi-server management
- Production considerations
- **NEW**: Cloud deployment strategies

### 6. **Try the Implementations**
- **Weather MCP**: Learn API integration
- **Calculator MCP**: Understand MCP basics  
- **Linux MCP**: Explore modular architecture
- **Kubernetes MCP**: ⭐ **NEW** - Master AI-powered K8s operations
- **AWS Cloud MCP**: 🚧 **COMING SOON** - Comprehensive cloud management

## 🛠️ Available Tools by Category

### Weather Tools (5 tools)
- `get_forecast` - US weather forecasts by coordinates
- `get_alerts` - Weather alerts by US state
- `get_coordinates` - Coordinates for major world cities
- `get_international_weather_info` - International weather guidance
- `get_help` - Weather assistant help

### Calculator Tools (13 functions)
- **Basic**: `add`, `subtract`, `multiply`, `divide`
- **Advanced**: `power`, `sqrt`, `cbrt`, `factorial`, `log`, `remainder`
- **Trigonometry**: `sin`, `cos`, `tan`

### Linux Tools (25+ tools across 8 categories)
- **System Monitoring**: CPU, memory, disk, network stats
- **Process Management**: List, manage, kill processes
- **Log Analysis**: System logs, error logs
- **Service Management**: Systemd service control
- **User Management**: User operations (add, delete, list)
- **Firewall Management**: UFW firewall control
- **File Operations**: File viewing and content inspection
- **Security**: Failed logins, sudo access, open ports

### Kubernetes Tools ⭐ **NEW** (kubectl-ai integration)
- **Pod Management**: "List all pods", "Delete pod xyz", "Get pod logs"
- **Deployments**: "Scale app to 5 replicas", "Restart deployment", "Update image"
- **Cluster Info**: "Show nodes", "List namespaces", "Get cluster events"
- **Services**: "Expose pod as LoadBalancer", "Show all services"
- **Troubleshooting**: "Why is pod failing?", "Show recent errors", "Check resource usage"
- **Interactive**: Approval prompts for destructive operations
- **Namespaces**: Automatic namespace creation when needed

### AWS Cloud Tools 🚧 **PLANNED**
- **EC2 Management**: Instance lifecycle, security groups, key pairs
- **S3 Operations**: Bucket management, file operations, permissions
- **Lambda Functions**: Deployment, monitoring, log analysis
- **VPC Networking**: Subnet creation, routing, security
- **IAM Management**: Users, roles, policies, access control
- **CloudFormation**: Infrastructure as Code deployment
- **CloudWatch**: Monitoring, alerting, log analysis
- **RDS**: Database management and operations

## 🌟 Key Features

### Powered by Gemini 2.5 Flash
- 🚀 **Enhanced Performance**: Faster processing and response times
- 🧠 **Advanced Reasoning**: Better understanding of complex queries
- 🎯 **Smart Tool Selection**: Automatically chooses appropriate tools
- 📊 **Superior Formatting**: Well-structured, readable responses
- 🔧 **Improved Tool Usage**: More accurate parameter handling
- ⭐ **NEW**: kubectl-ai integration for natural language Kubernetes operations

### Production-Ready Architecture
- 🏗️ **Multiple Patterns**: Single-file and modular architectures
- 🚀 **Deployment Options**: Local, Docker, SSH, Kubernetes, **EKS**, **Minikube**
- 🔒 **Security**: Authentication, validation, error handling, **RBAC**, **IAM**
- 📊 **Monitoring**: Logging, health checks, status monitoring
- ⚡ **Performance**: Async operations, caching, optimization
- ☁️ **Cloud-Native**: **NEW** - EKS, LoadBalancer, Auto-scaling support

### Comprehensive Documentation
- 📚 **Step-by-step guides** for every component
- 🎯 **Real-world examples** from working implementations
- 🛠️ **Best practices** for production deployment
- 🔧 **Troubleshooting guides** for common issues
- 📊 **Architecture diagrams** with Mermaid visualizations
- 🧠 **NEW**: Complete AI/ML background in `docs/intro.md`

## 🚀 Deployment Options

### Local Development
```bash
# Run any server locally
python3 weather_server.py    # Weather
python3 mcp_server.py        # Calculator  
python3 main.py              # Linux

# NEW: Minikube Kubernetes development
cd mcp-aws-kubernetes
./scripts/deploy-minikube.sh
```

### Docker Deployment
```bash
# Weather server in Docker
cd mcp-weather-client-tutorial
docker build -t weather-mcp .
docker run -p 8080:8080 weather-mcp

# Linux server with Docker Compose
cd mcp-for-linux/deployment/docker
docker-compose up -d

# NEW: Kubernetes MCP in Docker
cd mcp-aws-kubernetes
docker build -t k8s-mcp .
docker run -p 8080:8080 k8s-mcp
```

### Remote SSH Deployment
```bash
# Deploy Linux MCP to remote server
cd mcp-for-linux/deployment/ssh
./ssh_deploy.sh deploy 192.168.1.100 ~/.ssh/key.pem ubuntu "your-api-key"

# NEW: Deploy Kubernetes MCP to EC2
cd mcp-aws-kubernetes/terraform
terraform apply
```

### Kubernetes Deployment
```bash
# Deploy to Kubernetes cluster
cd mcp-for-linux/deployment/kubernetes
kubectl apply -f deployment.yaml

# NEW: Deploy MCP server on existing cluster
cd mcp-aws-kubernetes
kubectl apply -f k8s-manifests/
```

### Cloud Deployment (AWS)
```bash
# Deploy with Terraform
cd mcp-for-linux/deployment/terraform
terraform init
terraform apply

# NEW: EKS Production Deployment
cd mcp-aws-kubernetes/scripts
export GEMINI_API_KEY="your-api-key"
./deploy-eks.sh
```

### ⭐ **NEW**: AI-Powered Kubernetes Operations
```bash
# Natural language Kubernetes commands
kubectl ai --model gemini-2.5-flash "List all pods in default namespace"
kubectl ai --model gemini-2.5-flash "Scale my-website-app to 6 replicas"
kubectl ai --model gemini-2.5-flash "Deploy nginx pod in test namespace"
kubectl ai --model gemini-2.5-flash "Get logs from my-website-app pods"
kubectl ai --model gemini-2.5-flash "Show cluster nodes"

# Interactive operations with approval prompts
kubectl ai --model gemini-2.5-flash "Delete all failed pods"
# The following commands require your approval to run:
# • kubectl delete pod failing-pod-123
# Do you want to proceed? [1. Yes / 2. Yes, and don't ask me again / 3. No]
```

## 🎯 Use Cases

### Educational
- **Learn MCP protocol** with Calculator agent
- **Understand API integration** with Weather agent
- **Explore system administration** with Linux agent
- ⭐ **NEW**: **Master AI-powered DevOps** with Kubernetes agent
- 🚧 **PLANNED**: **Learn cloud architecture** with AWS agent

### Development
- **Prototype AI agents** using our templates
- **Test tool calling patterns** with real examples
- **Build custom MCP servers** following our patterns
- ⭐ **NEW**: **Develop cloud-native AI applications**
- ⭐ **NEW**: **Create Kubernetes automation workflows**

### Production
- **Deploy weather services** for applications
- **System monitoring** with Linux agent
- **Mathematical computations** with Calculator agent
- ⭐ **NEW**: **Kubernetes cluster management** with natural language
- ⭐ **NEW**: **Infrastructure as Code** with Terraform integration
- 🚧 **PLANNED**: **Multi-cloud operations** with AWS agent

## 🔧 Customization and Extension

### Adding New Tools
```python
# For single-file servers (Weather/Calculator pattern)
@mcp.tool()
def my_new_tool(param: str) -> str:
    """Description of the tool"""
    return f"Processed: {param}"

# For modular servers (Linux pattern)
# Create new file in tools/ directory
def register(mcp):
    @mcp.tool()
    def my_tool(param: str) -> str:
        return f"Result: {param}"

# NEW: For Kubernetes MCP
# Add to mcp-schema.json
{
  "name": "my_k8s_tool",
  "description": "Custom Kubernetes operation",
  "parameters": {
    "namespace": "string",
    "resource": "string"
  }
}
```

### Creating New Servers
```bash
# Use our templates
cp templates/simple_mcp_server.py my_custom_server.py
cp templates/simple_mcp_client.py my_custom_client.py

# Follow our architecture patterns
# See docs/part3-mcp-intro.md for guidance

# NEW: Cloud-native server template
cp mcp-aws-kubernetes/terraform/main.tf my_cloud_server.tf
```

## 🧪 Testing and Validation

### Automated Testing
```bash
# Test all servers
./scripts/test_setup.sh

# Test individual components
cd mcp-weather-client-tutorial && python3 -m pytest
cd mcp-calculator && python3 -m pytest  
cd mcp-for-linux && python3 -m pytest

# NEW: Test Kubernetes deployment
cd mcp-aws-kubernetes && ./scripts/test-deployment.sh
```

### Manual Testing
```bash
# Start all servers for testing
./scripts/start_servers.sh

# Test with clients
python3 advanced_client.py weather_server.py
python3 advanced_calculator_client.py mcp_server.py
python3 advanced_linux_client.py main.py

# NEW: Test kubectl-ai integration
kubectl ai --model gemini-2.5-flash "test connection"
```

## 🛡️ Security Considerations

### API Keys and Secrets
- Store in environment variables
- Never commit to version control
- Use proper access controls in production
- ⭐ **NEW**: Kubernetes secrets management
- ⭐ **NEW**: AWS IAM integration

### System Access (Linux MCP)
- Run with minimal required permissions
- Validate all inputs
- Implement proper error handling
- Monitor system access logs

### Network Security
- Use HTTPS for HTTP transport
- Implement rate limiting
- Validate all API requests
- Monitor for unusual activity
- ⭐ **NEW**: EKS security groups and NACLs
- ⭐ **NEW**: Kubernetes RBAC policies

### ⭐ **NEW**: Cloud Security
- **RBAC**: Kubernetes role-based access control
- **IAM**: AWS identity and access management
- **Secrets**: Secure API key storage in Kubernetes
- **Network**: VPC, security groups, load balancer security
- **Monitoring**: CloudWatch logs and audit trails

## 📈 Performance Optimization

### Client-Side
- Connection pooling for multiple servers
- Caching of frequently used results
- Async operations for concurrent requests
- Error recovery and retry logic
- ⭐ **NEW**: kubectl-ai response caching

### Server-Side  
- Efficient tool implementation
- Proper resource cleanup
- Monitoring and logging
- Horizontal scaling for high load
- ⭐ **NEW**: Kubernetes horizontal pod autoscaling
- ⭐ **NEW**: EKS node group auto-scaling

### ⭐ **NEW**: Cloud Performance
- **Auto-scaling**: EKS managed node groups
- **Load Balancing**: AWS Application Load Balancer
- **Caching**: CloudFront for static content
- **Monitoring**: CloudWatch metrics and alarms
- **Optimization**: Instance types and storage optimization

## 🔮 Future Roadmap

### Planned Enhancements
- 🔌 **Additional MCP servers**: Database, File System, Communication
- 🤖 **Multi-agent coordination**: Orchestrated agent workflows
- 🎨 **Web interface**: Browser-based MCP clients
- 📊 **Monitoring dashboard**: Real-time server monitoring
- 🔄 **CI/CD pipelines**: Automated testing and deployment
- ⭐ **NEW**: Complete AWS Cloud MCP server
- ⭐ **NEW**: Multi-cloud support (Azure, GCP)
- ⭐ **NEW**: ArgoCD GitOps integration
- ⭐ **NEW**: Prometheus/Grafana monitoring stack

### Community Goals
- 📚 **Expanded documentation**: Video tutorials, workshops
- 🎓 **Educational content**: University course materials
- 🏆 **Best practices**: Production deployment guides
- 🌐 **Ecosystem growth**: Community-contributed servers
- ⭐ **NEW**: Kubernetes operator development
- ⭐ **NEW**: Helm charts for easy deployment

## 📞 Support and Community

### Getting Help
- 📖 **Documentation**: Start with `docs/` directory
- 🐛 **Issues**: GitHub Issues for bug reports
- 💡 **Discussions**: GitHub Discussions for questions
- 📧 **Contact**: Maintainers for direct support
- ⭐ **NEW**: Kubernetes troubleshooting guide
- ⭐ **NEW**: kubectl-ai best practices

### Resources
- **MCP Specification**: [https://modelcontextprotocol.io/](https://modelcontextprotocol.io/)
- **Google AI Documentation**: [https://ai.google.dev/docs](https://ai.google.dev/docs)
- **FastMCP Framework**: [https://github.com/jlowin/fastmcp](https://github.com/jlowin/fastmcp)
- ⭐ **NEW**: **kubectl-ai**: [https://github.com/GoogleCloudPlatform/kubectl-ai](https://github.com/GoogleCloudPlatform/kubectl-ai)
- ⭐ **NEW**: **EKS Documentation**: [https://docs.aws.amazon.com/eks/](https://docs.aws.amazon.com/eks/)
- ⭐ **NEW**: **Kubernetes Documentation**: [https://kubernetes.io/docs/](https://kubernetes.io/docs/)

## 📜 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- **Model Context Protocol** team for the excellent specification
- **Google AI** team for Gemini 2.5 Flash
- **FastMCP** contributors for the framework
- **National Weather Service** for weather data API
- **Open source community** for tools and libraries
- ⭐ **NEW**: **Google kubectl-ai** team for AI-powered Kubernetes CLI
- ⭐ **NEW**: **Amazon EKS** team for managed Kubernetes service
- ⭐ **NEW**: **Kubernetes community** for the amazing orchestration platform

---

## 🎉 Get Started Now!

Ready to build AI agents with real-world capabilities including cloud infrastructure management?

1. **📖 Read the documentation** starting with `docs/intro.md` for complete AI/ML background
2. **🚀 Set up your environment** following `docs/part4-setup.md`
3. **🧪 Try the examples** - Weather, Calculator, Linux, **and NEW Kubernetes agents**
4. **☸️ Deploy to Kubernetes** with our EKS or Minikube guides
5. **🛠️ Build your own** using our templates and patterns
6. **🚀 Deploy to production** with our cloud deployment guides

### ⭐ **Quick Start for Kubernetes MCP:**
```bash
cd mcp-aws-kubernetes
export GEMINI_API_KEY="your-api-key"

# For production (EKS)
./scripts/deploy-eks.sh

# For development (Minikube)  
./scripts/deploy-minikube.sh

# Start using AI for Kubernetes!
kubectl ai --model gemini-2.5-flash "List all pods in default namespace"
```

**Happy building! 🤖✨**

---

*This MCP agent collection demonstrates the power of standardized AI tool calling with real-world implementations. From simple calculations to complex cloud infrastructure management, these agents showcase how AI can interact meaningfully with external systems, APIs, and cloud platforms.*
