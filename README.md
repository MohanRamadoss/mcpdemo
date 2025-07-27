# 🤖 Model Context Protocol (MCP) Agent Collection

A comprehensive collection of AI agents and servers built with the Model Context Protocol (MCP) and powered by Google's Gemini 2.5 Flash AI model.

## 🎯 What This Repository Contains

This repository showcases three different MCP server architectures and provides complete documentation for building AI agents with tool-calling capabilities.

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

## 🚀 Quick Start

### Prerequisites
- Python 3.8+ (Python 3.11+ recommended)
- Google AI API key (already configured)
- Linux/macOS/Windows (WSL2 recommended for Windows)

### One-Command Setup
```bash
# Clone and set up the entire MCP collection
git clone <your-repo-url>
cd MCP

# Create shared virtual environment
python3 -m venv venv
source venv/bin/activate  # Linux/macOS
# venv\Scripts\activate   # Windows

# Install all dependencies
pip install --upgrade pip
pip install mcp fastmcp google-generativeai python-dotenv httpx psutil aiohttp
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

## 📊 Architecture Comparison

| Feature | Weather MCP | Calculator MCP | Linux MCP |
|---------|-------------|----------------|-----------|
| **Architecture** | Single-file | Single-file | Modular |
| **Complexity** | Medium | Low | High |
| **Tool Count** | 5 tools | 13 functions | 25+ tools |
| **External APIs** | ✅ Weather API | ❌ None | ✅ System APIs |
| **Async Support** | ✅ Yes | ❌ No | ✅ Yes |
| **Deployment** | Docker + Local | Local only | Docker + SSH + K8s |
| **Use Case** | API learning | MCP basics | Production systems |

## 🏗️ Project Structure

```
MCP/
├── 📖 docs/                           # Comprehensive documentation
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

### 1. **Start with Foundations** (`docs/part1-foundations.md`)
- Understand AI agents and tool calling
- Learn MCP protocol basics
- Compare architecture patterns

### 2. **Learn Tool Calling** (`docs/part2-tool-calling.md`)
- See real examples from our implementations
- Understand best practices
- Learn error handling patterns

### 3. **Explore MCP Servers** (`docs/part3-mcp-intro.md`)
- Compare single-file vs modular patterns
- Understand transport options
- See production deployment strategies

### 4. **Set Up Your Environment** (`docs/part4-setup.md`)
- Complete development setup
- IDE configuration
- Testing and validation

### 5. **Deploy MCP Servers** (`docs/part5-mcp-setup.md`)
- Server installation and configuration
- Multi-server management
- Production considerations

### 6. **Try the Implementations**
- **Weather MCP**: Learn API integration
- **Calculator MCP**: Understand MCP basics  
- **Linux MCP**: Explore modular architecture

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

## 🌟 Key Features

### Powered by Gemini 2.5 Flash
- 🚀 **Enhanced Performance**: Faster processing and response times
- 🧠 **Advanced Reasoning**: Better understanding of complex queries
- 🎯 **Smart Tool Selection**: Automatically chooses appropriate tools
- 📊 **Superior Formatting**: Well-structured, readable responses
- 🔧 **Improved Tool Usage**: More accurate parameter handling

### Production-Ready Architecture
- 🏗️ **Multiple Patterns**: Single-file and modular architectures
- 🚀 **Deployment Options**: Local, Docker, SSH, Kubernetes
- 🔒 **Security**: Authentication, validation, error handling
- 📊 **Monitoring**: Logging, health checks, status monitoring
- ⚡ **Performance**: Async operations, caching, optimization

### Comprehensive Documentation
- 📚 **Step-by-step guides** for every component
- 🎯 **Real-world examples** from working implementations
- 🛠️ **Best practices** for production deployment
- 🔧 **Troubleshooting guides** for common issues
- 📊 **Architecture diagrams** with Mermaid visualizations

## 🚀 Deployment Options

### Local Development
```bash
# Run any server locally
python3 weather_server.py    # Weather
python3 mcp_server.py        # Calculator  
python3 main.py              # Linux
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
```

### Remote SSH Deployment
```bash
# Deploy Linux MCP to remote server
cd mcp-for-linux/deployment/ssh
./ssh_deploy.sh deploy 192.168.1.100 ~/.ssh/key.pem ubuntu "your-api-key"
```

### Kubernetes Deployment
```bash
# Deploy to Kubernetes cluster
cd mcp-for-linux/deployment/kubernetes
kubectl apply -f deployment.yaml
```

### Cloud Deployment (AWS)
```bash
# Deploy with Terraform
cd mcp-for-linux/deployment/terraform
terraform init
terraform apply
```

## 🎯 Use Cases

### Educational
- **Learn MCP protocol** with Calculator agent
- **Understand API integration** with Weather agent
- **Explore system administration** with Linux agent

### Development
- **Prototype AI agents** using our templates
- **Test tool calling patterns** with real examples
- **Build custom MCP servers** following our patterns

### Production
- **Deploy weather services** for applications
- **System monitoring** with Linux agent
- **Mathematical computations** with Calculator agent

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
```

### Creating New Servers
```bash
# Use our templates
cp templates/simple_mcp_server.py my_custom_server.py
cp templates/simple_mcp_client.py my_custom_client.py

# Follow our architecture patterns
# See docs/part3-mcp-intro.md for guidance
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
```

### Manual Testing
```bash
# Start all servers for testing
./scripts/start_servers.sh

# Test with clients
python3 advanced_client.py weather_server.py
python3 advanced_calculator_client.py mcp_server.py
python3 advanced_linux_client.py main.py
```

## 🤝 Contributing

We welcome contributions to improve the MCP agent collection:

1. **Fork the repository**
2. **Create a feature branch**: `git checkout -b feature/new-tool`
3. **Add your implementation** following our patterns
4. **Test thoroughly** with our testing scripts
5. **Update documentation** as needed
6. **Submit a pull request**

### Contribution Areas
- 🔧 **New MCP tools** for existing servers
- 🏗️ **New MCP servers** for different domains
- 📚 **Documentation improvements**
- 🐛 **Bug fixes** and performance improvements
- 🧪 **Testing** and validation enhancements

## 🛡️ Security Considerations

### API Keys and Secrets
- Store in environment variables
- Never commit to version control
- Use proper access controls in production

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

## 📈 Performance Optimization

### Client-Side
- Connection pooling for multiple servers
- Caching of frequently used results
- Async operations for concurrent requests
- Error recovery and retry logic

### Server-Side  
- Efficient tool implementation
- Proper resource cleanup
- Monitoring and logging
- Horizontal scaling for high load

## 🔮 Future Roadmap

### Planned Enhancements
- 🔌 **Additional MCP servers**: Database, File System, Communication
- 🤖 **Multi-agent coordination**: Orchestrated agent workflows
- 🎨 **Web interface**: Browser-based MCP clients
- 📊 **Monitoring dashboard**: Real-time server monitoring
- 🔄 **CI/CD pipelines**: Automated testing and deployment

### Community Goals
- 📚 **Expanded documentation**: Video tutorials, workshops
- 🎓 **Educational content**: University course materials
- 🏆 **Best practices**: Production deployment guides
- 🌐 **Ecosystem growth**: Community-contributed servers

## 📞 Support and Community

### Getting Help
- 📖 **Documentation**: Start with `docs/` directory
- 🐛 **Issues**: GitHub Issues for bug reports
- 💡 **Discussions**: GitHub Discussions for questions
- 📧 **Contact**: Maintainers for direct support

### Resources
- **MCP Specification**: [https://modelcontextprotocol.io/](https://modelcontextprotocol.io/)
- **Google AI Documentation**: [https://ai.google.dev/docs](https://ai.google.dev/docs)
- **FastMCP Framework**: [https://github.com/jlowin/fastmcp](https://github.com/jlowin/fastmcp)

## 📜 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- **Model Context Protocol** team for the excellent specification
- **Google AI** team for Gemini 2.5 Flash
- **FastMCP** contributors for the framework
- **National Weather Service** for weather data API
- **Open source community** for tools and libraries

---

## 🎉 Get Started Now!

Ready to build AI agents with real-world capabilities?

1. **📖 Read the documentation** starting with `docs/part1-foundations.md`
2. **🚀 Set up your environment** following `docs/part4-setup.md`
3. **🧪 Try the examples** - Weather, Calculator, and Linux agents
4. **🛠️ Build your own** using our templates and patterns
5. **🚀 Deploy to production** with our deployment guides

**Happy building! 🤖✨**

---

*This MCP agent collection demonstrates the power of standardized AI tool calling with real-world implementations. From simple calculations to complex system administration, these agents showcase how AI can interact meaningfully with external systems and data sources.*
