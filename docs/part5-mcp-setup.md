# Part 5: Installing and Configuring MCP Servers

## Overview

Now that your development environment is ready, let's install and configure MCP servers. We'll use our three working implementations as examples and show you how to set up additional servers.

## Our MCP Server Portfolio

Based on the implementations we have, here's what we'll cover:

1. **Weather MCP Server** - External API integration
2. **Calculator MCP Server** - Pure computation
3. **Linux MCP Server** - System administration
4. **Custom MCP Servers** - Building your own

## Part 1: Weather MCP Server Setup

### Overview
The Weather MCP server provides real-time weather data using the National Weather Service API.

### Installation

```bash
# Navigate to weather MCP directory
cd /home/mohan/terraform/MCP/mcp-weather-client-tutorial

# Activate virtual environment
source ../venv/bin/activate

# Install weather-specific dependencies (if not already installed)
pip install httpx fastmcp mcp
```

### Configuration

The Weather MCP server is ready to use without additional configuration since it uses public APIs:

```python
# filepath: /home/mohan/terraform/MCP/mcp-weather-client-tutorial/weather_server.py
# ...existing code...

# Constants
NWS_API_BASE = "https://api.weather.gov"
USER_AGENT = "weather-app/1.0"

# ...existing code...
```

### Available Tools

| Tool | Description | Parameters |
|------|-------------|------------|
| `get_forecast` | Get weather forecast for US coordinates | `latitude`, `longitude` |
| `get_alerts` | Get weather alerts for US states | `state` |
| `get_coordinates` | Get coordinates for major cities | `city`, `country` (optional) |
| `get_international_weather_info` | Info about international weather | `location` |
| `get_help` | Help and usage examples | None |

### Testing Weather MCP

```bash
# Test server startup
python3 weather_server.py &
SERVER_PID=$!

# Test with client
python3 advanced_client.py weather_server.py

# Example queries to test:
# "What are the weather alerts in California?"
# "Get the forecast for New York City coordinates 40.7128, -74.0060"
# "What are the coordinates for Singapore?"

# Stop server
kill $SERVER_PID
```

### Weather MCP for Different Deployments

**Local Development:**
```bash
python3 weather_server.py  # STDIO transport
```

**Docker Deployment:**
```bash
# Already configured for Docker in weather_server.py
# ...existing code...
if is_docker:
    logger.info("Running in Docker environment")
    mcp.run(transport='stdio')
```

## Part 2: Calculator MCP Server Setup

### Overview
The Calculator MCP server provides mathematical operations and demonstrates pure computation patterns.

### Installation

```bash
# Navigate to calculator MCP directory
cd /home/mohan/terraform/MCP/mcp-calculator

# Virtual environment should already be active
# Dependencies already installed (mcp, fastmcp, math is built-in)
```

### Configuration

The Calculator MCP server requires no external dependencies:

```python
# filepath: /home/mohan/terraform/MCP/mcp-calculator/mcp_server.py
# ...existing code...

# instantiate an MCP server client
mcp = FastMCP(
    "Scientific Calculator",
    description="A scientific calculator providing mathematical operations",
    version="1.0.0"
)

# ...existing code...
```

### Available Tools

| Tool | Description | Parameters | Example |
|------|-------------|------------|---------|
| `add` | Add two numbers | `a`, `b` | `add(5, 3)` → `8` |
| `subtract` | Subtract two numbers | `a`, `b` | `subtract(10, 4)` → `6` |
| `multiply` | Multiply two numbers | `a`, `b` | `multiply(7, 8)` → `56` |
| `divide` | Divide two numbers | `a`, `b` | `divide(15, 3)` → `5` |
| `power` | Power of two numbers | `a`, `b` | `power(2, 3)` → `8` |
| `sqrt` | Square root | `a` | `sqrt(16)` → `4` |
| `cbrt` | Cube root | `a` | `cbrt(27)` → `3` |
| `factorial` | Factorial | `a` (int) | `factorial(5)` → `120` |
| `log` | Natural logarithm | `a` | `log(10)` → `2.302...` |
| `remainder` | Modulo operation | `a`, `b` | `remainder(17, 5)` → `2` |
| `sin` | Sine (degrees) | `a` | `sin(30)` → `0.5` |
| `cos` | Cosine (degrees) | `a` | `cos(60)` → `0.5` |
| `tan` | Tangent (degrees) | `a` | `tan(45)` → `1` |

### Available Resources

```python
# ...existing code...
@mcp.resource("greeting://{name}")
def get_greeting(name: str) -> str:
    """Get a personalized greeting"""
    return f"Hello, {name}!"
```

### Testing Calculator MCP

```bash
# Test server startup
python3 mcp_server.py &
SERVER_PID=$!

# Test with client
python3 advanced_calculator_client.py mcp_server.py

# Example queries to test:
# "What is 15 + 27?"
# "Calculate the square root of 144"
# "What is 5 factorial?"
# "Find the sine of 30 degrees"

# Stop server
kill $SERVER_PID
```

### Calculator MCP Transport Options

**STDIO (default):**
```bash
python3 mcp_server.py
```

**SSE for web applications:**
```bash
python3 mcp_server.py --sse
# Server available at http://localhost:3001
```

## Part 3: Linux MCP Server Setup

### Overview
The Linux MCP server provides comprehensive system administration tools with a modular architecture.

### Installation

```bash
# Navigate to Linux MCP directory
cd /home/mohan/terraform/MCP/mcp-for-linux

# Install Linux-specific dependencies
pip install psutil  # For system monitoring

# Optional: Install Docker-related dependencies
pip install docker  # If you want Docker tool support
```

### Configuration

The Linux MCP server uses dynamic module loading:

```python
# filepath: /home/mohan/terraform/MCP/mcp-for-linux/main.py
# ...existing code...

def load_modules_from_folder(folder_path: str):
    """Dynamically load MCP tools and resources from a folder."""
    # ...existing code...

if __name__ == "__main__":
    # Load all tools and resources
    load_modules_from_folder("tools")
    load_modules_from_folder("resources")
    # ...existing code...
```

### Module Structure

**Tools Directory:**
```
tools/
├── system_monitoring.py    # CPU, memory, disk, network
├── process_management.py   # List, manage, kill processes
├── log_analysis.py        # System and error logs
├── service_management.py  # Systemd service control
├── user_management.py     # User operations (add, delete, list)
├── firewall_management.py # UFW firewall control
├── file_content.py        # File viewing
└── help_tool.py          # Help and documentation
```

**Resources Directory:**
```
resources/
├── system_metrics.py      # CPU, memory, log resources
├── cron_jobs.py          # Scheduled task information
└── config_files.py       # System configuration access
```

### Available Tools (25+ tools)

| Category | Tools | Description |
|----------|-------|-------------|
| **System Monitoring** | `get_cpu_usage`, `get_memory_usage`, `get_disk_usage`, `get_network_stats` | System resource monitoring |
| **Process Management** | `list_processes`, `get_top_processes`, `kill_process` | Process operations |
| **Log Analysis** | `get_system_logs`, `get_error_logs` | Log file analysis |
| **Service Management** | `restart_service`, `get_service_status` | Systemd service control |
| **User Management** | `list_users`, `add_user`, `delete_user` | User account management |
| **Firewall** | `get_firewall_status`, `allow_port`, `deny_port` | UFW firewall control |
| **File Operations** | `view_file` | File content viewing |

### Testing Linux MCP

```bash
# Test server startup
python3 main.py &
SERVER_PID=$!

# Test with client
python3 advanced_linux_client.py main.py

# Example queries to test:
# "What's using the most CPU?"
# "Check memory usage"
# "List all users"
# "Show recent system logs"
# "Get firewall status"

# Stop server
kill $SERVER_PID
```

### Linux MCP Transport Options

**STDIO (default):**
```bash
python3 main.py
```

**HTTP for remote access:**
```bash
python3 main.py --http
# Server available at http://localhost:8080
```

### Security Considerations

The Linux MCP server requires careful permission management:

```bash
# Some operations require sudo privileges
sudo python3 main.py

# Or configure sudoers for specific operations
# For production, consider running with limited privileges
```

## Part 4: Custom MCP Server Configuration

### Creating Your Own MCP Server

Based on our patterns, here's how to create custom servers:

#### Pattern 1: Simple Single-File Server (Weather/Calculator Style)

```python
# your_custom_server.py
from mcp.server.fastmcp import FastMCP
import sys

mcp = FastMCP(
    "Your Custom Server",
    description="Description of your server",
    version="1.0.0"
)

@mcp.tool()
def your_custom_tool(param: str) -> str:
    """Description of your tool"""
    # Your implementation here
    return f"Processed: {param}"

@mcp.resource("your_resource://{id}")
def get_your_resource(id: str) -> str:
    """Get a custom resource"""
    return f"Resource data for {id}"

if __name__ == "__main__":
    print("Starting Your Custom MCP Server...")
    try:
        mcp.run(transport="stdio")
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
```

#### Pattern 2: Modular Server (Linux Style)

```python
# main.py
from mcp.server.fastmcp import FastMCP
# ...existing code... (use Linux MCP main.py as template)

# tools/your_custom_tools.py
def register(mcp):
    @mcp.tool()
    def your_tool(param: str) -> str:
        """Your custom tool"""
        return f"Result: {param}"
```

## Part 5: Multi-Server Configuration

### Running Multiple Servers

You can run multiple MCP servers simultaneously:

```bash
# Terminal 1: Weather MCP
cd mcp-weather-client-tutorial
python3 weather_server.py

# Terminal 2: Calculator MCP
cd ../mcp-calculator
python3 mcp_server.py

# Terminal 3: Linux MCP
cd ../mcp-for-linux
python3 main.py

# Terminal 4: Client (connect to any server)
python3 advanced_client.py weather_server.py
```

### Server Orchestration Script

```bash
# Create server manager script
cat > manage_servers.sh << 'EOF'
#!/bin/bash

case "$1" in
    start)
        echo "🚀 Starting all MCP servers..."
        
        # Weather server
        cd mcp-weather-client-tutorial
        python3 weather_server.py &
        echo $! > ../weather.pid
        
        # Calculator server  
        cd ../mcp-calculator
        python3 mcp_server.py &
        echo $! > ../calculator.pid
        
        # Linux server
        cd ../mcp-for-linux
        python3 main.py &
        echo $! > ../linux.pid
        
        echo "✅ All servers started"
        ;;
        
    stop)
        echo "🛑 Stopping all MCP servers..."
        
        for pidfile in weather.pid calculator.pid linux.pid; do
            if [[ -f "$pidfile" ]]; then
                kill $(cat $pidfile) 2>/dev/null
                rm $pidfile
            fi
        done
        
        echo "✅ All servers stopped"
        ;;
        
    status)
        echo "📊 Server status:"
        
        for pidfile in weather.pid calculator.pid linux.pid; do
            server=$(basename $pidfile .pid)
            if [[ -f "$pidfile" ]] && kill -0 $(cat $pidfile) 2>/dev/null; then
                echo "  ✅ $server: running (PID: $(cat $pidfile))"
            else
                echo "  ❌ $server: stopped"
            fi
        done
        ;;
        
    *)
        echo "Usage: $0 {start|stop|status}"
        ;;
esac
EOF

chmod +x manage_servers.sh

# Usage
./manage_servers.sh start   # Start all servers
./manage_servers.sh status  # Check status
./manage_servers.sh stop    # Stop all servers
```

## Part 6: Configuration Best Practices

### Environment Variables

Create server-specific environment configurations:

```bash
# .env.weather
GOOGLE_API_KEY=your_key_here
WEATHER_API_TIMEOUT=30
WEATHER_CACHE_TTL=300

# .env.calculator  
GOOGLE_API_KEY=your_key_here
CALCULATOR_PRECISION=10
MATH_SAFETY_CHECKS=true

# .env.linux
GOOGLE_API_KEY=your_key_here
LINUX_LOG_LEVEL=INFO
LINUX_REQUIRE_SUDO=false
LINUX_MAX_PROCESSES=1000
```

### Server Configuration Files

```yaml
# config/servers.yaml
servers:
  weather:
    name: "Weather MCP Server"
    script: "mcp-weather-client-tutorial/weather_server.py"
    transport: "stdio"
    description: "Real-time weather data and forecasts"
    
  calculator:
    name: "Scientific Calculator"
    script: "mcp-calculator/mcp_server.py"
    transport: "stdio"
    description: "Mathematical operations and calculations"
    
  linux:
    name: "Linux Debug Agent"
    script: "mcp-for-linux/main.py"
    transport: "stdio"
    description: "System administration and monitoring"
    requires_sudo: true
```

### Logging Configuration

```python
# shared/logging_config.py
import logging
import sys
import os

def setup_logging(server_name: str, level: str = "INFO"):
    """Set up consistent logging across all MCP servers"""
    
    # Create logs directory if it doesn't exist
    log_dir = "logs"
    os.makedirs(log_dir, exist_ok=True)
    
    # Configure logging
    logging.basicConfig(
        level=getattr(logging, level.upper()),
        format=f'%(asctime)s - {server_name} - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler(f"{log_dir}/{server_name.lower()}.log")
        ]
    )
    
    return logging.getLogger(server_name)
```

## Part 7: Testing and Validation

### Automated Testing Script

```bash
cat > test_all_servers.sh << 'EOF'
#!/bin/bash

echo "🧪 Testing All MCP Servers..."

FAILED=0

# Test Weather MCP
echo "🌤️ Testing Weather MCP..."
cd mcp-weather-client-tutorial
timeout 10s python3 -c "
import asyncio
from advanced_client import MCPClient

async def test():
    client = MCPClient()
    try:
        await client.connect_to_server('weather_server.py')
        print('✅ Weather MCP: Connection successful')
        
        # Test a simple query
        result = await client.process_query('help')
        if 'weather' in result.lower():
            print('✅ Weather MCP: Tool execution successful')
        else:
            print('❌ Weather MCP: Tool execution failed')
            return False
    except Exception as e:
        print(f'❌ Weather MCP: {e}')
        return False
    finally:
        await client.cleanup()
    return True

success = asyncio.run(test())
exit(0 if success else 1)
"
if [[ $? -ne 0 ]]; then FAILED=$((FAILED + 1)); fi

# Test Calculator MCP
echo "🧮 Testing Calculator MCP..."
cd ../mcp-calculator
timeout 10s python3 -c "
import asyncio
from advanced_calculator_client import MCPCalculatorClient

async def test():
    client = MCPCalculatorClient()
    try:
        await client.connect_to_server('mcp_server.py')
        print('✅ Calculator MCP: Connection successful')
        
        # Test a simple calculation
        result = await client.process_query('What is 2 + 2?')
        if '4' in result:
            print('✅ Calculator MCP: Calculation successful')
        else:
            print('❌ Calculator MCP: Calculation failed')
            return False
    except Exception as e:
        print(f'❌ Calculator MCP: {e}')
        return False
    finally:
        await client.cleanup()
    return True

success = asyncio.run(test())
exit(0 if success else 1)
"
if [[ $? -ne 0 ]]; then FAILED=$((FAILED + 1)); fi

# Test Linux MCP
echo "🐧 Testing Linux MCP..."
cd ../mcp-for-linux
timeout 10s python3 -c "
import asyncio
from advanced_linux_client import MCPLinuxClient

async def test():
    client = MCPLinuxClient()
    try:
        await client.connect_to_server('main.py')
        print('✅ Linux MCP: Connection successful')
        
        # Test a simple system query
        result = await client.process_query('help')
        if 'linux' in result.lower():
            print('✅ Linux MCP: Tool execution successful')
        else:
            print('❌ Linux MCP: Tool execution failed')
            return False
    except Exception as e:
        print(f'❌ Linux MCP: {e}')
        return False
    finally:
        await client.cleanup()
    return True

success = asyncio.run(test())
exit(0 if success else 1)
"
if [[ $? -ne 0 ]]; then FAILED=$((FAILED + 1)); fi

# Summary
echo ""
if [[ $FAILED -eq 0 ]]; then
    echo "✅ All MCP servers tested successfully!"
else
    echo "❌ $FAILED server(s) failed testing"
    exit 1
fi
EOF

chmod +x test_all_servers.sh
```

## Troubleshooting Common Issues

### Issue 1: Server Won't Start

```bash
# Check Python path and imports
python3 -c "import mcp; print('MCP imported successfully')"

# Check file permissions
ls -la weather_server.py
chmod +x weather_server.py

# Check for syntax errors
python3 -m py_compile weather_server.py
```

### Issue 2: Client Connection Fails

```bash
# Verify server is running
ps aux | grep python
netstat -tlnp | grep 8080  # For HTTP servers

# Check transport compatibility
# STDIO client → STDIO server ✅
# HTTP client → HTTP server ✅  
# STDIO client → HTTP server ❌
```

### Issue 3: Tool Execution Errors

```bash
# Check tool registration
python3 -c "
from weather_server import mcp
print('Registered tools:', [tool for tool in dir(mcp) if not tool.startswith('_')])
"

# Test individual tools
python3 -c "
import asyncio
from weather_server import get_help
result = asyncio.run(get_help())
print(result)
"
```

## Next Steps

With your MCP servers configured, you're ready to:

1. **Build custom agents** using the configured servers
2. **Deploy servers** to production environments  
3. **Integrate with AI models** beyond Gemini
4. **Scale your MCP architecture** with multiple servers

## Key Takeaways

- ✅ **Three server patterns**: Weather (API), Calculator (computation), Linux (system)
- ✅ **Transport flexibility**: STDIO for clients, HTTP for web apps
- ✅ **Modular architecture**: Linux MCP demonstrates scalable design
- ✅ **Security considerations**: Permissions and access control
- ✅ **Testing strategies**: Automated validation and monitoring
- ✅ **Configuration management**: Environment variables and config files

---

**Servers configured and tested?** You're now ready to build sophisticated AI agents that can interact with the real world through your MCP servers! 🎉

## Resources

- **Weather Data**: [National Weather Service API](https://weather.gov/documentation/services-web-api)
- **System Monitoring**: [psutil Documentation](https://psutil.readthedocs.io/)
- **MCP Specification**: [Model Context Protocol](https://modelcontextprotocol.io/)
- **FastMCP Framework**: [FastMCP Repository](https://github.com/jlowin/fastmcp)