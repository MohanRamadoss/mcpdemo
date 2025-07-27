# 🚀 SSH Deployment Guide for MCP Linux Agent

This guide shows you how to deploy and run the MCP Linux Agent on remote Linux servers via SSH.

## 🎯 Deployment Options

### 1. Direct SSH Deployment
Deploy the MCP server directly on a remote Linux server.

### 2. SSH Tunnel Access  
Create an SSH tunnel to securely access a remote MCP server.

### 3. HTTP Client Access
Use an HTTP-based client to connect to remote MCP servers.

## 📋 Prerequisites

- **SSH Access**: SSH key-based authentication to remote server
- **Remote Server**: Ubuntu/Debian Linux server with Python 3.8+
- **Network Access**: Port 8080 open for HTTP API (or SSH tunnel)
- **Google AI API Key**: For Gemini 2.5 Flash integration

## 🚀 Quick Start

### Step 1: Prepare SSH Key
```bash
# Ensure proper SSH key permissions
chmod 600 ~/.ssh/your-key.pem

# Test SSH connection
ssh -i ~/.ssh/your-key.pem ubuntu@your-server-ip "echo 'SSH working'"
```

### Step 2: Deploy to Remote Server
```bash
# Navigate to deployment directory
cd /home/mohan/terraform/MCP/mcp-for-linux/deployment/ssh

# Make script executable
chmod +x ssh_deploy.sh

# Deploy to remote server
./ssh_deploy.sh deploy 192.168.1.100 ~/.ssh/your-key.pem ubuntu "your-google-api-key"
```

### Step 3: Access Remote MCP Server

**Option A: SSH Tunnel + Native Client**
```bash
# Create SSH tunnel (recommended for full MCP features)
./ssh_deploy.sh tunnel 192.168.1.100 ~/.ssh/your-key.pem ubuntu 8081

# In another terminal, use native MCP client via tunnel
# (Requires modification for HTTP transport)
```

**Option B: HTTP Client** 
```bash
# Use HTTP client for remote access
python3 http_client.py http://192.168.1.100:8080

# Or via SSH tunnel
python3 http_client.py http://localhost:8081
```

**Option C: Direct HTTP API**
```bash
# Test remote API directly
curl http://192.168.1.100:8080/health

# Check available tools
curl http://192.168.1.100:8080/tools
```

## 📖 Detailed Usage

### Deploy to Remote Server

```bash
# Full deployment with all options
./ssh_deploy.sh deploy <HOST> <SSH_KEY> [USER] [GOOGLE_API_KEY]

# Examples:
./ssh_deploy.sh deploy 192.168.1.100 ~/.ssh/id_rsa
./ssh_deploy.sh deploy ec2-user@aws-instance.com ~/.ssh/aws-key.pem ec2-user "your-api-key"
./ssh_deploy.sh deploy my-server.com ~/.ssh/key.pem root
```

**What it does:**
- ✅ Installs system dependencies (Python, pip, etc.)
- ✅ Creates `/opt/mcp-linux` directory structure
- ✅ Sets up Python virtual environment
- ✅ Installs MCP Linux Agent and dependencies
- ✅ Creates systemd service for automatic startup
- ✅ Configures firewall (SSH + port 8080)
- ✅ Starts the MCP service in HTTP mode

### Create SSH Tunnel

```bash
# Create secure tunnel for MCP access
./ssh_deploy.sh tunnel <HOST> <SSH_KEY> [USER] [LOCAL_PORT]

# Examples:
./ssh_deploy.sh tunnel 192.168.1.100 ~/.ssh/id_rsa ubuntu 8081
./ssh_deploy.sh tunnel my-server.com ~/.ssh/key.pem admin 9999
```

**SSH Tunnel Benefits:**
- 🔒 Secure encrypted connection
- 🌐 Access remote server as if local
- 🔧 Full MCP protocol support
- 🛡️ No need to expose ports publicly

### Check Remote Status

```bash
# Check deployment status
./ssh_deploy.sh status 192.168.1.100 ~/.ssh/id_rsa

# Example output:
# 🖥️ System Information:
# Hostname: my-linux-server
# OS: Ubuntu 22.04.3 LTS  
# Uptime: up 2 days, 14 hours, 23 minutes
# 
# 📦 MCP Service Status:
# ● mcp-linux.service - MCP Linux Debug Agent
#    Loaded: loaded (/etc/systemd/system/mcp-linux.service; enabled; vendor preset: enabled)
#    Active: active (running) since...
```

### Update Remote Installation

```bash
# Update remote MCP installation
./ssh_deploy.sh update 192.168.1.100 ~/.ssh/id_rsa

# Updates:
# - Downloads latest code
# - Updates Python dependencies  
# - Restarts service with zero downtime
# - Preserves configuration and logs
```

### Execute Remote Commands

```bash
# Execute arbitrary commands on remote server
./ssh_deploy.sh exec 192.168.1.100 ~/.ssh/id_rsa "command"

# Examples:
./ssh_deploy.sh exec 192.168.1.100 ~/.ssh/id_rsa "sudo systemctl status mcp-linux"
./ssh_deploy.sh exec 192.168.1.100 ~/.ssh/id_rsa "curl http://localhost:8080/health"
./ssh_deploy.sh exec 192.168.1.100 ~/.ssh/id_rsa "tail -f /opt/mcp-linux/current/logs/app.log"
```

## 🔧 Advanced Configuration

### Custom Remote Directory
```bash
# Modify REMOTE_DIR in ssh_deploy.sh
REMOTE_DIR="/custom/path/mcp-linux"
```

### Custom Service Name
```bash
# Modify SERVICE_NAME in ssh_deploy.sh  
SERVICE_NAME="my-mcp-service"
```

### Firewall Configuration
```bash
# SSH into server and configure firewall
ssh -i ~/.ssh/key.pem ubuntu@server

# Allow additional ports
sudo ufw allow 443  # HTTPS
sudo ufw allow from 192.168.1.0/24 to any port 8080  # Restrict access

# Check firewall status
sudo ufw status verbose
```

### SSL/HTTPS Setup
```bash
# SSH into server
ssh -i ~/.ssh/key.pem ubuntu@server

# Install nginx for SSL termination
sudo apt install nginx certbot python3-certbot-nginx

# Get SSL certificate
sudo certbot --nginx -d your-domain.com

# Configure nginx proxy (manual step)
```

## 🛠️ Troubleshooting

### Common Issues

**1. SSH Connection Failed**
```bash
# Check SSH key permissions
chmod 600 ~/.ssh/your-key.pem

# Test SSH connection
ssh -i ~/.ssh/your-key.pem -v ubuntu@host

# Check if key is correct for server
```

**2. Service Won't Start**
```bash
# Check service status
./ssh_deploy.sh exec host key "sudo systemctl status mcp-linux"

# Check logs  
./ssh_deploy.sh exec host key "sudo journalctl -u mcp-linux -f"

# Check Python environment
./ssh_deploy.sh exec host key "cd /opt/mcp-linux/current && source venv/bin/activate && python --version"
```

**3. HTTP API Not Responding**
```bash
# Check if service is listening
./ssh_deploy.sh exec host key "sudo netstat -tlnp | grep 8080"

# Check firewall
./ssh_deploy.sh exec host key "sudo ufw status"

# Test local connection
./ssh_deploy.sh exec host key "curl http://localhost:8080/health"
```

**4. Permission Errors**
```bash
# Fix ownership
./ssh_deploy.sh exec host key "sudo chown -R ubuntu:ubuntu /opt/mcp-linux"

# Check systemd service permissions
./ssh_deploy.sh exec host key "sudo systemctl edit mcp-linux"
```

### Debug Mode

Enable debug logging:
```bash
# SSH into server
ssh -i ~/.ssh/key.pem ubuntu@server

# Edit environment file
cd /opt/mcp-linux/current
echo "LOG_LEVEL=DEBUG" >> .env

# Restart service
sudo systemctl restart mcp-linux

# Watch debug logs
sudo journalctl -u mcp-linux -f
```

## 🔄 Comparison: SSH vs Docker vs Kubernetes

| Feature | SSH Deployment | Docker | Kubernetes |
|---------|----------------|---------|------------|
| **Complexity** | Low | Medium | High |
| **Setup Time** | ~5 minutes | ~10 minutes | ~30 minutes |
| **Resource Usage** | Low | Medium | High |
| **Scalability** | Manual | Medium | High |
| **Management** | systemd | Docker commands | kubectl |
| **Best For** | Simple servers | Development | Production clusters |

## 🎯 Use Cases

### Development & Testing
```bash
# Quick deployment for testing
./ssh_deploy.sh deploy test-server.local ~/.ssh/test-key.pem
```

### Production Single Server
```bash
# Production deployment with monitoring
./ssh_deploy.sh deploy prod-server.com ~/.ssh/prod-key.pem ubuntu "prod-api-key"

# Set up monitoring
./ssh_deploy.sh exec prod-server.com ~/.ssh/prod-key.pem "sudo apt install prometheus-node-exporter"
```

### Multiple Servers
```bash
# Deploy to multiple servers
for server in server1 server2 server3; do
    ./ssh_deploy.sh deploy $server.domain.com ~/.ssh/key.pem ubuntu "api-key"
done
```

### Edge Computing
```bash
# Deploy to Raspberry Pi or edge devices
./ssh_deploy.sh deploy pi@192.168.1.50 ~/.ssh/pi-key.pem pi "api-key"
```

---

## 🎉 Success!

Your MCP Linux Agent is now running on a remote server via SSH deployment. You can:

- 🌐 Access via HTTP API at `http://your-server:8080`
- 🔒 Create secure SSH tunnels for MCP client access  
- 📊 Monitor system status remotely
- 🔄 Update and manage the installation remotely
- 🛡️ Maintain security with SSH key authentication

**Next Steps:**
- Set up monitoring and alerting
- Configure SSL/HTTPS for production
- Implement backup strategies
- Scale to multiple servers as needed
