# Part 4: Setting Up Your Development Environment

## Prerequisites

Before we start building MCP-powered AI agents, let's set up a proper development environment based on the working implementations we have.

### System Requirements

- **Python 3.8+** (Python 3.11+ recommended)
- **Git** for version control
- **Virtual environment** support
- **Terminal/Command Line** access
- **Text Editor/IDE** (VS Code, PyCharm, etc.)

### Platform Support

Our MCP implementations work on:
- ✅ **Linux** (Ubuntu, Debian, CentOS, etc.)
- ✅ **macOS** (Intel and Apple Silicon)
- ✅ **Windows** (with WSL2 recommended)

## Step 1: Python Environment Setup

### Check Python Version

```bash
# Check your Python version
python3 --version
# Should show Python 3.8.0 or higher

# Alternative check
python --version
```

### Install Python (if needed)

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install python3 python3-pip python3-venv
```

**macOS:**
```bash
# Using Homebrew
brew install python@3.11

# Or download from python.org
```

**Windows:**
```bash
# Download from python.org or use Microsoft Store
# Recommended: Install Python from python.org with "Add to PATH" checked
```

## Step 2: Create Project Structure

Based on our working MCP implementations, here's the recommended project structure:

```bash
# Create main MCP workspace
mkdir -p /home/mohan/terraform/MCP
cd /home/mohan/terraform/MCP

# Create project structure
mkdir -p {docs,examples,tools,templates}

# Your project structure will look like:
# MCP/
# ├── docs/                    # Documentation (this guide)
# ├── examples/                # Example implementations
# ├── tools/                   # Utility scripts
# ├── templates/               # Project templates
# ├── mcp-weather-client-tutorial/     # Weather MCP (existing)
# ├── mcp-calculator/          # Calculator MCP (existing)
# └── mcp-for-linux/           # Linux MCP (existing)
```

## Step 3: Virtual Environment Setup

### Create and Activate Virtual Environment

From our Weather MCP example:

```bash
# Navigate to your MCP workspace
cd /home/mohan/terraform/MCP

# Create virtual environment (do this once)
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate  # Linux/macOS
# venv\Scripts\activate   # Windows

# Verify activation (you should see (venv) in your prompt)
which python
# Should show: /home/mohan/terraform/MCP/venv/bin/python
```

### Deactivate Virtual Environment

```bash
# When you're done working
deactivate
```

## Step 4: Install Core Dependencies

Based on our working implementations, install the essential packages:

```bash
# Make sure virtual environment is activated
source venv/bin/activate

# Core MCP dependencies
pip install --upgrade pip
pip install mcp fastmcp

# AI and language models
pip install google-generativeai

# Environment and configuration
pip install python-dotenv

# HTTP and async support
pip install httpx aiohttp

# System monitoring (for Linux MCP)
pip install psutil

# Development tools
pip install pytest black flake8 mypy

# Optional but recommended
pip install jupyter ipython
```

### Create Requirements File

```bash
# Generate requirements file
pip freeze > requirements.txt

# Your requirements.txt should include:
# mcp>=1.0.0
# fastmcp>=0.9.0
# google-generativeai>=0.3.0
# python-dotenv>=1.0.0
# httpx>=0.25.0
# psutil>=5.9.0
```

## Step 5: Environment Configuration

### Create Environment File

Based on our implementations:

```bash
# Create .env file in your workspace
cat > .env << EOF
# Google AI API Key (for Gemini 2.5 Flash)
GOOGLE_API_KEY=AIzaSyC2YmGx9-_yx9QzW3D0qCEgvV03U9zik9E

# Development settings
PYTHONPATH=/home/mohan/terraform/MCP
PYTHONUNBUFFERED=1
LOG_LEVEL=INFO

# Optional: OpenAI API Key (if you want to use OpenAI models)
# OPENAI_API_KEY=your_openai_key_here

# Optional: Slack integration (for communication MCPs)
# SLACK_BOT_TOKEN=xoxb-your-token
# SLACK_APP_TOKEN=xapp-your-token

# Optional: GitHub integration (for development MCPs)
# GITHUB_TOKEN=ghp-your-token

# Optional: Database connection (for data MCPs)
# DATABASE_URL=postgresql://user:pass@host/db
EOF
```

### Set Up Git (if not already done)

```bash
# Configure Git
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"

# Initialize repository (if creating new project)
git init
git add .
git commit -m "Initial commit"
```

### Create .gitignore

```bash
cat > .gitignore << EOF
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Virtual Environment
venv/
env/
ENV/

# Environment Variables
.env
.env.local
.env.production

# IDE
.vscode/
.idea/
*.swp
*.swo

# Logs
*.log
logs/

# OS
.DS_Store
Thumbs.db

# MCP specific
*.mcp
.mcp/
EOF
```

## Step 6: Validate Installation

Let's test your setup with our existing MCP examples:

### Test 1: Basic Python Setup

```bash
# Test Python and packages
python3 -c "
import sys
print(f'Python version: {sys.version}')

try:
    import mcp
    print('✅ MCP installed successfully')
except ImportError:
    print('❌ MCP not installed')

try:
    import google.generativeai as genai
    print('✅ Google Generative AI installed successfully')
except ImportError:
    print('❌ Google Generative AI not installed')

try:
    import httpx
    print('✅ HTTPX installed successfully')
except ImportError:
    print('❌ HTTPX not installed')
"
```

### Test 2: Weather MCP Server

```bash
# Test Weather MCP server
cd mcp-weather-client-tutorial

# Start server (should start without errors)
timeout 5s python3 weather_server.py || echo "✅ Weather server starts correctly"

# Test client connection
echo "Testing weather client connection..."
# This should show available tools
timeout 10s python3 -c "
import asyncio
from advanced_client import MCPClient

async def test():
    client = MCPClient()
    try:
        await client.connect_to_server('weather_server.py')
        print('✅ Weather MCP client connects successfully')
    except Exception as e:
        print(f'❌ Weather MCP connection failed: {e}')
    finally:
        await client.cleanup()

asyncio.run(test())
" || echo "⚠️ Check weather client setup"
```

### Test 3: Calculator MCP Server

```bash
# Test Calculator MCP server
cd ../mcp-calculator

# Start server (should start without errors)
timeout 5s python3 mcp_server.py || echo "✅ Calculator server starts correctly"

# Basic calculation test
python3 -c "
import math
print('✅ Calculator tools working:')
print(f'  Add: {5 + 3}')
print(f'  Factorial: {math.factorial(5)}')
print(f'  Sin 30°: {math.sin(math.radians(30))}')
"
```

### Test 4: Linux MCP Server

```bash
# Test Linux MCP server
cd ../mcp-for-linux

# Test module loading
python3 -c "
import glob
import os

tools = glob.glob('tools/*.py')
resources = glob.glob('resources/*.py')

print(f'✅ Found {len(tools)} tool modules')
print(f'✅ Found {len(resources)} resource modules')

if tools and resources:
    print('✅ Linux MCP structure is correct')
else:
    print('⚠️ Create tools/ and resources/ directories')
"

# Test server startup (should load modules)
timeout 5s python3 main.py || echo "✅ Linux server starts correctly"
```

## Step 7: IDE/Editor Setup

### VS Code Configuration

If using VS Code, create workspace settings:

```bash
mkdir -p .vscode

cat > .vscode/settings.json << EOF
{
    "python.defaultInterpreterPath": "./venv/bin/python",
    "python.terminal.activateEnvironment": true,
    "python.linting.enabled": true,
    "python.linting.flake8Enabled": true,
    "python.formatting.provider": "black",
    "python.formatting.blackArgs": ["--line-length", "88"],
    "files.exclude": {
        "**/__pycache__": true,
        "**/*.pyc": true,
        "**/venv": true
    },
    "python.envFile": "${workspaceFolder}/.env"
}
EOF

cat > .vscode/launch.json << EOF
{
    "version": "0.2.0",
    "configurations": [
        {
            "name": "Weather MCP Server",
            "type": "python",
            "request": "launch",
            "program": "${workspaceFolder}/mcp-weather-client-tutorial/weather_server.py",
            "cwd": "${workspaceFolder}/mcp-weather-client-tutorial",
            "envFile": "${workspaceFolder}/.env"
        },
        {
            "name": "Calculator MCP Server",
            "type": "python",
            "request": "launch",
            "program": "${workspaceFolder}/mcp-calculator/mcp_server.py",
            "cwd": "${workspaceFolder}/mcp-calculator",
            "envFile": "${workspaceFolder}/.env"
        },
        {
            "name": "Linux MCP Server",
            "type": "python",
            "request": "launch",
            "program": "${workspaceFolder}/mcp-for-linux/main.py",
            "cwd": "${workspaceFolder}/mcp-for-linux",
            "envFile": "${workspaceFolder}/.env"
        }
    ]
}
EOF
```

### PyCharm Configuration

1. Open PyCharm
2. Open the `/home/mohan/terraform/MCP` directory
3. Go to **File → Settings → Project → Python Interpreter**
4. Select **Add Interpreter → Existing Environment**
5. Point to `/home/mohan/terraform/MCP/venv/bin/python`
6. Go to **File → Settings → Project → Environment Variables**
7. Add environment variables from your `.env` file

## Step 8: Development Scripts

Create helpful development scripts:

### Start Script

```bash
cat > start_servers.sh << 'EOF'
#!/bin/bash
# Start all MCP servers for development

echo "🚀 Starting MCP Development Servers..."

# Weather MCP
echo "🌤️ Starting Weather MCP..."
cd mcp-weather-client-tutorial
python3 weather_server.py &
WEATHER_PID=$!

# Calculator MCP  
echo "🧮 Starting Calculator MCP..."
cd ../mcp-calculator
python3 mcp_server.py &
CALC_PID=$!

# Linux MCP
echo "🐧 Starting Linux MCP..."
cd ../mcp-for-linux  
python3 main.py &
LINUX_PID=$!

echo "✅ All servers started!"
echo "Weather PID: $WEATHER_PID"
echo "Calculator PID: $CALC_PID" 
echo "Linux PID: $LINUX_PID"

# Wait for user input to stop
read -p "Press Enter to stop all servers..."

echo "🛑 Stopping servers..."
kill $WEATHER_PID $CALC_PID $LINUX_PID
echo "✅ All servers stopped!"
EOF

chmod +x start_servers.sh
```

### Test Script

```bash
cat > test_setup.sh << 'EOF'
#!/bin/bash
# Test MCP development environment

echo "🧪 Testing MCP Development Environment..."

# Test virtual environment
if [[ "$VIRTUAL_ENV" != "" ]]; then
    echo "✅ Virtual environment active: $VIRTUAL_ENV"
else
    echo "❌ Virtual environment not active"
    echo "Run: source venv/bin/activate"
    exit 1
fi

# Test Python packages
python3 -c "
packages = ['mcp', 'google.generativeai', 'httpx', 'psutil']
for pkg in packages:
    try:
        __import__(pkg)
        print(f'✅ {pkg} installed')
    except ImportError:
        print(f'❌ {pkg} not installed')
"

# Test environment variables
python3 -c "
import os
api_key = os.getenv('GOOGLE_API_KEY')
if api_key:
    print(f'✅ GOOGLE_API_KEY configured ({api_key[:8]}...)')
else:
    print('❌ GOOGLE_API_KEY not set')
"

# Test MCP servers
echo "🔍 Testing MCP servers..."
for server in "mcp-weather-client-tutorial/weather_server.py" "mcp-calculator/mcp_server.py" "mcp-for-linux/main.py"; do
    if [[ -f "$server" ]]; then
        echo "✅ Found $server"
    else
        echo "❌ Missing $server"
    fi
done

echo "✅ Environment test complete!"
EOF

chmod +x test_setup.sh
```

## Step 9: Quick Start Templates

Create templates for new MCP projects:

### Simple MCP Server Template

```bash
mkdir -p templates

cat > templates/simple_mcp_server.py << 'EOF'
#!/usr/bin/env python3
"""
Simple MCP Server Template
Usage: python3 simple_mcp_server.py
"""

from mcp.server.fastmcp import FastMCP
import sys
import os

# Initialize FastMCP server
mcp = FastMCP(
    "My MCP Server",
    description="A simple MCP server template",
    version="1.0.0"
)

@mcp.tool()
def hello_world(name: str = "World") -> str:
    """Say hello to someone"""
    return f"Hello, {name}!"

@mcp.tool()
def add_numbers(a: float, b: float) -> float:
    """Add two numbers together"""
    return a + b

@mcp.resource("greeting://{name}")
def get_greeting(name: str) -> str:
    """Get a personalized greeting resource"""
    return f"Greetings, {name}! Welcome to MCP."

if __name__ == "__main__":
    print("Starting Simple MCP Server...")
    
    try:
        mcp.run(transport="stdio")
    except Exception as e:
        print(f"Error starting server: {e}")
        sys.exit(1)
EOF
```

### MCP Client Template

```bash
cat > templates/simple_mcp_client.py << 'EOF'
#!/usr/bin/env python3
"""
Simple MCP Client Template
Usage: python3 simple_mcp_client.py server_script.py
"""

import sys
import asyncio
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

async def main():
    if len(sys.argv) < 2:
        print("Usage: python3 simple_mcp_client.py <server_script>")
        sys.exit(1)
    
    server_script = sys.argv[1]
    
    # Set up server parameters
    server_params = StdioServerParameters(
        command="python3",
        args=[server_script]
    )
    
    # Connect to server
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            
            # List available tools
            tools_response = await session.list_tools()
            print("Available tools:")
            for tool in tools_response.tools:
                print(f"  - {tool.name}: {tool.description}")
            
            # Example tool call
            if tools_response.tools:
                tool_name = tools_response.tools[0].name
                print(f"\nCalling tool: {tool_name}")
                
                # Call the first tool with example parameters
                if tool_name == "hello_world":
                    result = await session.call_tool(tool_name, {"name": "MCP User"})
                elif tool_name == "add_numbers":
                    result = await session.call_tool(tool_name, {"a": 5, "b": 3})
                else:
                    result = await session.call_tool(tool_name, {})
                
                print(f"Result: {result.content}")

if __name__ == "__main__":
    asyncio.run(main())
EOF
```

## Common Issues and Solutions

### Issue 1: Import Errors

```bash
# Problem: ModuleNotFoundError: No module named 'mcp'
# Solution: Make sure virtual environment is active and packages installed
source venv/bin/activate
pip install mcp fastmcp
```

### Issue 2: Permission Errors

```bash
# Problem: Permission denied accessing system resources (Linux MCP)
# Solution: Run with appropriate permissions or modify tools
sudo python3 main.py  # For system-level operations
# Or modify tools to handle permission errors gracefully
```

### Issue 3: API Key Issues

```bash
# Problem: Google AI API errors
# Solution: Verify API key is set correctly
echo $GOOGLE_API_KEY
# Check if key has proper permissions in Google AI Studio
```

### Issue 4: Port Conflicts

```bash
# Problem: Port already in use (HTTP servers)
# Solution: Change port or kill existing processes
lsof -i :8080  # Check what's using port 8080
kill -9 <PID>  # Kill the process
# Or use different port: python3 server.py --http --port 8081
```

## Next Steps

Now that your development environment is set up, you can:

1. **Explore existing implementations**: 
   - Weather MCP (`mcp-weather-client-tutorial/`)
   - Calculator MCP (`mcp-calculator/`)
   - Linux MCP (`mcp-for-linux/`)

2. **Create your first MCP server**:
   ```bash
   cp templates/simple_mcp_server.py my_first_server.py
   python3 templates/simple_mcp_client.py my_first_server.py
   ```

3. **Continue to Part 5**: [Installing and Configuring MCP Servers](./part5-mcp-setup.md)

## Key Takeaways

- ✅ **Virtual environment** isolates dependencies
- ✅ **Environment variables** manage configuration securely
- ✅ **Project structure** based on working implementations
- ✅ **Testing scripts** validate your setup
- ✅ **Templates** provide starting points for new projects
- ✅ **IDE configuration** improves development experience

---

**Environment ready?** Continue to [Part 5: Installing and Configuring MCP Servers](./part5-mcp-setup.md) to start working with specific MCP servers! 🚀

## Resources

- **MCP Documentation**: [https://modelcontextprotocol.io/](https://modelcontextprotocol.io/)
- **FastMCP Framework**: [https://github.com/jlowin/fastmcp](https://github.com/jlowin/fastmcp)
- **Google AI Studio**: [https://aistudio.google.com/](https://aistudio.google.com/)
- **Python Virtual Environments**: [https://docs.python.org/3/tutorial/venv.html](https://docs.python.org/3/tutorial/venv.html)
