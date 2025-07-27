# 🐧 Linux Debug Agent with Gemini 2.5 Flash

A powerful Linux system administration and debugging agent that combines MCP (Model Context Protocol) with Google's Gemini 2.5 Flash AI for natural language system queries.

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Linux system (tested on Ubuntu/Debian/CentOS)
- Google AI API key (already configured)

### Setup with Existing Virtual Environment
```bash
# Activate the existing weather venv
cd /home/mohan/terraform/MCP/mcp-weather-client-tutorial
source venv/bin/activate

# Navigate to Linux MCP directory
cd ../mcp-for-linux

# Install additional requirements
pip install -r requirements.txt
```

### Usage
```bash
# Start the interactive Linux debug agent (CORRECT COMMAND)
python3 advanced_linux_client.py main.py
```

## 🔧 Key Differences from Other MCP Servers

### Linux MCP vs Calculator MCP vs Weather MCP

| Feature | Linux MCP | Calculator MCP | Weather MCP |
|---------|-----------|----------------|-------------|
| **Server File** | `main.py` (modular) | `mcp_server.py` (single) | `weather_server.py` (single) |
| **Architecture** | Modular (`tools/` + `resources/`) | Single file | Single file |
| **Tool Count** | 25+ tools | 13 math functions | 5 weather tools |
| **Complexity** | System administration | Mathematical operations | Weather data API |
| **Structure** | Dynamic loading | Direct definitions | Direct definitions |
| **Transport** | STDIO/HTTP | STDIO/SSE | STDIO/Docker |

### Why `main.py` vs `mcp_server.py`?

**Linux MCP (`main.py`):**
- **Modular Design**: Dynamically loads tools from `tools/` and resources from `resources/`
- **Scalable**: Easy to add new functionality by creating new files
- **Enterprise-Ready**: Separation of concerns, better maintainability
- **Complex Operations**: System administration requires many specialized tools

**Calculator/Weather MCP (`mcp_server.py`):**
- **Simple Design**: All tools defined in one file
- **Educational**: Easy to understand and modify
- **Focused**: Single-purpose servers with limited scope

## 📁 Tools vs Resources Structure

### Tools Directory (`/tools/`)
**Purpose**: Executable functions that perform system operations

**Current Tools:**
- `system_monitoring.py` - CPU, memory, disk, network stats
- `process_management.py` - List, manage, kill processes  
- `log_analysis.py` - System logs, error logs
- `service_management.py` - Start, stop, check services
- `user_management.py` - Add, delete, list users
- `firewall_management.py` - UFW firewall control
- `file_content.py` - View file contents
- `help_tool.py` - Help and documentation

### Resources Directory (`/resources/`)
**Purpose**: Data providers and configuration access

**Current Resources:**
- `system_metrics.py` - CPU/memory/log resources
- `cron_jobs.py` - Scheduled task information
- `config_files.py` - System configuration access

### Adding New Tools/Resources

**To add a new tool:**
```python
# /tools/new_tool.py
def register(mcp):
    @mcp.tool()
    def my_new_tool(param: str) -> dict:
        """Description of what this tool does"""
        # Implementation here
        return {"result": "success"}
```

**To add a new resource:**
```python
# /resources/new_resource.py  
def register(mcp):
    @mcp.resource("my_resource://{param}")
    def get_my_resource(param: str) -> str:
        """Get resource data"""
        return f"Resource data for {param}"
```

## 🐧 Available System Operations

### System Monitoring
- **CPU Usage**: "Check CPU usage" → Real-time CPU statistics and load
- **Memory Info**: "Show memory usage" → RAM and swap details
- **Disk Usage**: "Check disk space" → Filesystem usage across all mounts
- **Network Stats**: "Show network statistics" → Interface statistics
- **System Info**: "Get system information" → OS, kernel, hardware details
- **Hardware Info**: "Show hardware specs" → CPU, memory specifications

### Security & User Management
- **Failed Logins**: "Check failed login attempts" → Security audit
- **Active Users**: "Who is logged in?" → Current user sessions
- **Sudo Access**: "Check sudo privileges for user" → Permission audit
- **Open Ports**: "Show open ports" → Network security analysis
- **List Users**: "List all system users" → User account management
- **Add User**: "Add user newuser" → Create new accounts
- **Delete User**: "Delete user olduser" → Remove accounts

### Process Management
- **List Processes**: "Show running processes" → Process list with details
- **Top Processes**: "What's using the most resources?" → Resource-heavy processes
- **Kill Process**: "Kill process 1234" → Terminate specific PID
- **Network Connections**: "Show active connections" → Network activity

### Log Analysis
- **System Logs**: "Show recent system logs" → Latest log entries
- **Error Logs**: "Are there any errors?" → Error log analysis
- **Security Logs**: "Check for security issues" → Authentication failures

### Service Management
- **Service Status**: "Check status of apache2" → Service health check
- **Restart Service**: "Restart nginx" → Service management

### Firewall Management
- **Firewall Status**: "Get firewall status" → UFW status
- **Allow Port**: "Allow port 8080" → Open firewall ports
- **Deny Port**: "Deny port 22" → Block firewall ports

### File System Operations
- **View File**: "View file /etc/hosts" → Display file contents
- **Find Large Files**: "Find large files" → Disk space analysis
- **Check Disk Health**: "Check disk health" → SMART status

## 💡 Example Queries

```
🐧 Linux Query: What's using the most CPU and memory right now?
🐧 Linux Query: Are there any failed login attempts today?
🐧 Linux Query: Show me all open ports and what's using them
🐧 Linux Query: Find files larger than 500MB in /var directory
🐧 Linux Query: Check if my system needs any security updates
🐧 Linux Query: Are there any Docker containers running?
🐧 Linux Query: Test connectivity to google.com
🐧 Linux Query: Show me recent error logs
🐧 Linux Query: Who is currently logged into the system?
🐧 Linux Query: Check disk health status
🐧 Linux Query: Show me disk space on all drives
🐧 Linux Query: Kill process 1234
🐧 Linux Query: List all running processes
🐧 Linux Query: Add a new user named 'testuser'
🐧 Linux Query: What is the status of the firewall?
🐧 Linux Query: Show me the first 10 lines of /var/log/syslog
```

## 🛠️ Complete Available Tools

| Function | Description |
|----------|-------------|
| `get_cpu_usage` | CPU statistics and load average |
| `get_memory_usage` | Memory and swap information |
| `get_system_info` | OS, kernel, hardware details |
| `get_hardware_info` | CPU, memory specifications |
| `list_processes` | Running processes with details |
| `get_top_processes` | Resource-heavy processes |
| `kill_process` | Terminate process by PID |
| `check_failed_logins` | Failed authentication attempts |
| `get_active_users` | Currently logged in users |
| `check_sudo_access` | User privilege verification |
| `get_open_ports` | Listening services and ports |
| `check_network_connections` | Active network sessions |
| `ping_host` | Network connectivity test |
| `get_network_stats` | Interface statistics |
| `get_system_logs` | Recent system log entries |
| `get_error_logs` | Error log analysis |
| `restart_service` | Service management |
| `get_service_status` | Service health check |
| `get_disk_usage` | Filesystem usage |
| `find_large_files` | Large file detection |
| `check_disk_health` | SMART disk status |
| `get_docker_status` | Docker container monitoring |
| `check_package_updates` | Available system updates |
| `search_package` | Package repository search |
| `list_users` | List all system users |
| `add_user` | Add a new system user |
| `delete_user` | Delete a system user |
| `get_firewall_status` | Get UFW firewall status |
| `allow_port` | Allow traffic on a port |
| `deny_port` | Deny traffic on a port |
| `view_file` | View content of a file |

## 🎯 Features

✅ **Natural Language Processing**: Ask system questions conversationally  
✅ **Modular Architecture**: Tools and resources in separate, organized files  
✅ **Dynamic Loading**: Automatically discovers and loads all tools/resources  
✅ **Comprehensive Security Monitoring** - Failed logins, user sessions, privilege auditing  
✅ **Network Security Analysis** - Open ports, active connections, connectivity tests  
✅ **Storage Management** - Disk health, large file detection, usage analysis  
✅ **Container Orchestration** - Docker monitoring and management  
✅ **Package Management** - Update checking and package search  
✅ **Real-time Monitoring** - Live system statistics and resource tracking  
✅ **Multi-format Logging** - System logs, error logs, security events  
✅ **Hardware Diagnostics** - CPU, memory, disk health monitoring  
✅ **Interactive Interface**: Real-time system administration  
✅ **Highly Extensible**: Add new capabilities by simply creating new files  

## 🔧 Running Different Modes

### Interactive Client (Default)
```bash
python3 advanced_linux_client.py main.py
```

### HTTP Server Mode (Optional)
```bash
python3 main.py --http
# Then access via HTTP at http://localhost:8080
```

## 📊 System Requirements

- **Linux Distribution**: Ubuntu, Debian, CentOS, RHEL, etc.
- **Python**: 3.8 or higher
- **Permissions**: Some operations require sudo privileges
- **Memory**: 512MB+ available RAM
- **Disk**: 100MB+ free space

## ⚠️ Security Notes

- Process termination requires appropriate permissions
- Service management may require sudo privileges
- Log access depends on file permissions
- Always review operations before confirming destructive actions

## 🚀 Integration with Other MCP Servers

This Linux agent can run alongside other MCP servers using the same virtual environment:

```bash
# Terminal 1: Weather MCP
cd /home/mohan/terraform/MCP/mcp-weather-client-tutorial
source venv/bin/activate
python3 advanced_client.py weather_server.py

# Terminal 2: Calculator MCP (same venv)
cd ../mcp-calculator
python3 advanced_calculator_client.py mcp_server.py

# Terminal 3: Linux MCP (same venv)
cd ../mcp-for-linux
python3 advanced_linux_client.py main.py
```

## 🌟 Powered by Gemini 2.5 Flash

This Linux agent leverages Google's most advanced AI model for:
- Natural language system query understanding
- Intelligent operation selection
- System data interpretation
- Clear result formatting and recommendations

## 🔄 Development Workflow

### Adding New Functionality

1. **Create Tool File**: Add new `.py` file in `tools/` directory
2. **Implement Register Function**: Use `@mcp.tool()` decorator
3. **Test**: Restart server, new tool automatically loads
4. **No Code Changes**: No need to modify `main.py`

### Example: Adding a New Tool
```bash
# Create new tool
echo 'def register(mcp):
    @mcp.tool()
    def my_tool() -> str:
        return "Hello from my tool!"
' > tools/my_new_tool.py

# Restart server - tool automatically available
python3 advanced_linux_client.py main.py
```

---

**Happy system administration! 🐧⚡**

## 📈 Comparison Summary

The Linux MCP represents the **enterprise-grade, modular approach** to MCP servers, while Calculator and Weather MCPs demonstrate **educational, single-file approaches**. Choose the architecture that fits your needs:

- **Learning MCP**: Use Calculator/Weather pattern
- **Production Systems**: Use Linux modular pattern
- **Complex Domains**: Use modular architecture
- **Simple Tools**: Use single-file approach
