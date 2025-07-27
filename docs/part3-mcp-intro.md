# Part 3: MCP Server Introduction

## What is MCP (Model Context Protocol)?

The Model Context Protocol (MCP) is an open standard that enables AI models and applications to connect to external data sources and tools through a standardized interface. Think of it as a "plug-and-play" system for AI capabilities.

## Why MCP Matters

### Before MCP
- Each AI application had to implement its own integrations
- Limited to what the application developer built
- No standardization across different tools
- Difficult to extend functionality

### With MCP
- Standardized way to connect AI to any service
- Plug-and-play tool integration
- Rich ecosystem of pre-built servers
- Easy to extend with custom servers

## MCP Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   AI Agent      │    │   MCP Client    │    │   MCP Server    │
│                 │◄──►│                 │◄──►│                 │
│ - LLM Model     │    │ - Protocol      │    │ - Tool Logic    │
│ - Reasoning     │    │ - Connection    │    │ - API Calls     │
│ - Response Gen  │    │ - Tool Registry │    │ - Data Sources  │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## Our MCP Server Examples

Based on the three MCP servers we've built, let's explore different server architectures:

### 1. **Weather MCP Server** (API Integration Pattern)

From `mcp-weather-client-tutorial/weather_server.py`:

```python
# Initialize FastMCP server
mcp = FastMCP("weather")

@mcp.tool()
async def get_forecast(latitude: float, longitude: float) -> str:
    """Get detailed weather forecast for any location using coordinates."""
    # ...existing code...

@mcp.tool()
async def get_alerts(state: str) -> str:
    """Get active weather alerts for any US state."""
    # ...existing code...

@mcp.tool()
async def get_coordinates(city: str, country: str = "") -> str:
    """Get latitude and longitude coordinates for major world cities."""
    # ...existing code...
```

**Characteristics:**
- 🌐 **External API Integration**: Connects to National Weather Service API
- ⚡ **Async Operations**: Handles HTTP requests efficiently
- 🔍 **Smart Tool Selection**: Different tools for different queries
- 📍 **International Support**: Coordinates for global cities

### 2. **Calculator MCP Server** (Computation Pattern)

From `mcp-calculator/mcp_server.py`:

```python
# Initialize FastMCP server
mcp = FastMCP("Scientific Calculator")

@mcp.tool()
def add(a: float, b: float) -> float:
    """Add two numbers"""
    return float(a + b)

@mcp.tool()
def divide(a: float, b: float) -> float:
    """Divide two numbers"""
    if b == 0:
        raise ValueError("Cannot divide by zero")
    return float(a / b)

@mcp.tool()
def factorial(a: int) -> int:
    """factorial of a number"""
    if not isinstance(a, int) or a < 0:
        raise ValueError("Factorial requires a non-negative integer")
    return int(math.factorial(a))

# DEFINE RESOURCES
@mcp.resource("greeting://{name}")
def get_greeting(name: str) -> str:
    """Get a personalized greeting"""
    return f"Hello, {name}!"
```

**Characteristics:**
- 🧮 **Pure Computation**: Mathematical operations without external dependencies
- 🔒 **Input Validation**: Strong type checking and error handling
- 📚 **Educational Focus**: Perfect for learning MCP basics
- 📊 **Resources**: Demonstrates both tools and resources

### 3. **Linux MCP Server** (Modular System Pattern)

From `mcp-for-linux/main.py`:

```python
# Initialize FastMCP server
mcp = FastMCP("Linux Debug Agent")

def load_modules_from_folder(folder_path: str):
    """Dynamically load MCP tools and resources from a folder."""
    # ...existing code...
    for file_path in glob.glob(os.path.join(folder_path, "*.py")):
        # ...existing code...
        if hasattr(module, "register"):
            module.register(mcp)

if __name__ == "__main__":
    # Load all tools and resources
    load_modules_from_folder("tools")
    load_modules_from_folder("resources")
    mcp.run(transport="stdio")
```

**Characteristics:**
- 🏗️ **Modular Architecture**: Dynamic loading from multiple files
- 🐧 **System Integration**: Deep Linux system access
- 🛡️ **Production Ready**: Enterprise-grade error handling
- 📦 **Scalable Design**: Easy to add new tools

## Key Components

### 1. **MCP Client** (Our Implementation)

From `advanced_client.py`:

```python
class MCPClient:
    def __init__(self):
        # Initialize session and client objects
        self.session: Optional[ClientSession] = None
        self.exit_stack = AsyncExitStack()
        
        # Configure Google AI with your API key
        api_key = os.getenv("GOOGLE_API_KEY")
        genai.configure(api_key=api_key)
        
        # Use Gemini 2.5 Flash model
        self.model = genai.GenerativeModel('gemini-2.5-flash')
    
    async def connect_to_server(self, server_script_path: str):
        """Connect to an MCP server"""
        # ...existing code...
        
    async def process_query(self, query: str) -> str:
        """Process a query using Gemini 2.5 Flash and available tools"""
        # ...existing code...
```

### 2. **MCP Server** (FastMCP Framework)

Our servers use the FastMCP framework for simplicity:

```python
from mcp.server.fastmcp import FastMCP

# Single-file pattern (Weather & Calculator)
mcp = FastMCP("Server Name")

@mcp.tool()
def my_tool(param: str) -> str:
    """Tool description"""
    return "result"

# Modular pattern (Linux)
def register(mcp):
    @mcp.tool()
    def my_tool(param: str) -> str:
        """Tool description"""
        return "result"
```

### 3. **Protocol** (Transport Layers)

Our servers support different transport mechanisms:

```python
# STDIO (for local development and MCP clients)
mcp.run(transport="stdio")

# HTTP (for remote access and web integration)
mcp.run(transport="http", port=8080)

# SSE (for web streaming)
mcp.run(transport="sse", port=3001)
```

## MCP Server Architecture Patterns

### Pattern 1: Single-File Server (Weather & Calculator)

```
weather_server.py
├── FastMCP initialization
├── @mcp.tool() decorators
├── Async API functions
└── Transport selection
```

**When to use:**
- ✅ Focused domain (weather, math, etc.)
- ✅ Limited to what the application developer built
- ✅ No standardization across different tools
- ✅ Difficult to extend functionality

### Pattern 2: Modular Server (Linux)

```
main.py
├── FastMCP initialization
├── Dynamic module loader
└── Transport selection

tools/
├── system_monitoring.py
├── process_management.py
├── service_management.py
└── user_management.py

resources/
├── system_metrics.py
└── config_files.py
```

**When to use:**
- ✅ Large number of tools (25+)
- ✅ Multiple developers
- ✅ Production systems
- ✅ Extensible architecture

## Real-World Server Examples

### 1. **Communication Servers**

Based on our Weather server pattern, here's how to build a Slack server:

```python
from mcp.server.fastmcp import FastMCP
import slack_sdk

mcp = FastMCP("Slack Integration")

@mcp.tool()
async def send_message(channel: str, message: str) -> dict:
    """Send a message to a Slack channel"""
    try:
        client = slack_sdk.WebClient(token=os.getenv("SLACK_TOKEN"))
        result = client.chat_postMessage(channel=channel, text=message)
        return {"success": True, "ts": result["ts"]}
    except Exception as e:
        return {"error": str(e)}

@mcp.tool()
async def get_channels() -> dict:
    """List all available channels"""
    # ...existing code...
```

### 2. **Productivity Servers**

Based on our Calculator pattern, here's a Google Sheets server:

```python
from mcp.server.fastmcp import FastMCP
import gspread

mcp = FastMCP("Google Sheets")

@mcp.tool()
def read_sheet(sheet_id: str, range_name: str) -> dict:
    """Read data from a Google Sheet"""
    try:
        gc = gspread.service_account()
        sheet = gc.open_by_key(sheet_id)
        worksheet = sheet.sheet1
        values = worksheet.get(range_name)
        return {"data": values}
    except Exception as e:
        return {"error": str(e)}

@mcp.tool()
def write_sheet(sheet_id: str, range_name: str, values: list) -> dict:
    """Write data to a Google Sheet"""
    # ...existing code...
```

### 3. **Development Servers**

Based on our Linux pattern, here's a GitHub server structure:

```python
# tools/repository_management.py
def register(mcp):
    @mcp.tool()
    def create_issue(repo: str, title: str, body: str) -> dict:
        """Create a new GitHub issue"""
        # ...existing code...
    
    @mcp.tool()
    def get_pull_requests(repo: str, state: str = "open") -> dict:
        """List pull requests for a repository"""
        # ...existing code...

# tools/code_analysis.py
def register(mcp):
    @mcp.tool()
    def analyze_code(repo: str, file_path: str) -> dict:
        """Analyze code quality and complexity"""
        # ...existing code...
```

## MCP vs Traditional Tool Calling

### Traditional Approach (Hard-coded)
```python
# Weather agent - hard-coded integration
class WeatherAgent:
    def __init__(self):
        self.weather_api = WeatherAPI(api_key)
        self.calculator = Calculator()
        self.system_monitor = SystemMonitor()
    
    def process_query(self, query):
        if "weather" in query:
            return self.weather_api.get_forecast()
        elif "calculate" in query:
            return self.calculator.compute()
        # Need to add each integration manually
```

### MCP Approach (Our Implementation)
```python
# Generic MCP client
class MCPClient:
    async def connect_to_server(self, server_script_path: str):
        # Connect to any MCP server
        # ...existing code...
    
    async def process_query(self, query: str) -> str:
        # Gemini 2.5 Flash automatically selects appropriate tools
        # ...existing code...

# Usage - plug and play
client = MCPClient()
await client.connect_to_server("weather_server.py")
await client.connect_to_server("mcp_server.py")  # Calculator
await client.connect_to_server("main.py")        # Linux
```

## Benefits of MCP (From Our Experience)

### 1. **Standardization**
```python
# All our servers use the same pattern
@mcp.tool()
def tool_name(param: type) -> return_type:
    """Clear description"""
    # Implementation
```

### 2. **Modularity**
```python
# Easy to add new capabilities
# Linux server: just add a new file in tools/
# Weather server: just add a new @mcp.tool()
# Calculator: just add a new mathematical function
```

### 3. **AI Integration**
```python
# Gemini 2.5 Flash understands all tools automatically
system_prompt = f"""You have access to these tools: {tools_description}"""
response = self.model.generate_content(full_prompt)
```

### 4. **Transport Flexibility**
```python
# Same server, different access methods
mcp.run(transport="stdio")  # For MCP clients
mcp.run(transport="http")   # For web apps
mcp.run(transport="sse")    # For streaming
```

## Server Configuration Examples

### Environment Variables (From Our Servers)
```bash
# Weather server
# (Uses public APIs, no auth needed)

# Calculator server  
# (Pure computation, no external dependencies)

# Linux server
GOOGLE_API_KEY=your_gemini_api_key
LOG_LEVEL=INFO
MCP_ENVIRONMENT=production

# Custom servers might need:
SLACK_BOT_TOKEN=xoxb-your-token
GITHUB_TOKEN=ghp-your-token
DATABASE_URL=postgresql://user:pass@host/db
```

### Server Selection
```python
# Choose the right server for your needs
servers = {
    "weather": "weather_server.py",      # API integration
    "calculator": "mcp_server.py",       # Pure computation  
    "linux": "main.py",                  # System administration
    "custom": "my_custom_server.py"      # Your specific needs
}

# Connect to multiple servers
for name, script in servers.items():
    await client.connect_to_server(script)
```

## Building Your Own MCP Server

### Step 1: Choose Your Pattern

**Single-File Pattern** (like Weather/Calculator):
```python
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("My Server")

@mcp.tool()
def my_tool(param: str) -> str:
    """Tool description"""
    return f"Processed: {param}"

if __name__ == "__main__":
    mcp.run(transport="stdio")
```

**Modular Pattern** (like Linux):
```python
# main.py
from mcp.server.fastmcp import FastMCP
# ...existing code...

# tools/my_tools.py
def register(mcp):
    @mcp.tool()
    def my_tool(param: str) -> str:
        """Tool description"""
        return f"Processed: {param}"
```

### Step 2: Define Your Domain

**API Integration** (like Weather):
```python
@mcp.tool()
async def api_call(param: str) -> dict:
    """Call external API"""
    async with httpx.AsyncClient() as client:
        response = await client.get(f"https://api.example.com/{param}")
        return response.json()
```

**System Operations** (like Linux):
```python
@mcp.tool()
def system_operation(param: str) -> dict:
    """Perform system operation"""
    import subprocess
    result = subprocess.run(["command", param], capture_output=True, text=True)
    return {"output": result.stdout, "error": result.stderr}
```

**Pure Computation** (like Calculator):
```python
@mcp.tool()
def compute(a: float, b: float) -> float:
    """Perform computation"""
    return a * b
```

### Step 3: Add Error Handling (Learn from Our Examples)

```python
@mcp.tool()
def robust_tool(param: str) -> dict:
    """A tool with proper error handling"""
    try:
        # Validate input
        if not param:
            return {"error": "Parameter cannot be empty"}
        
        # Perform operation
        result = perform_operation(param)
        
        # Validate output
        if not result:
            return {"error": "Operation failed"}
        
        return {"success": True, "data": result}
        
    except Exception as e:
        return {"error": f"Tool execution failed: {str(e)}"}
```

## Best Practices (From Our Implementations)

### 1. **Tool Design** (Weather Example)
```python
@mcp.tool()
async def get_forecast(latitude: float, longitude: float) -> str:
    """Get detailed weather forecast for any location using coordinates.

    Args:
        latitude: Latitude of the location (-90 to 90)
        longitude: Longitude of the location (-180 to 180)
        
    Examples:
        - get_forecast(40.7128, -74.0060) - New York City
        - get_forecast(37.7749, -122.4194) - San Francisco
    """
    # ...existing code...
```

### 2. **Input Validation** (Calculator Example)
```python
@mcp.tool()
def factorial(a: int) -> int:
    """factorial of a number"""
    if not isinstance(a, int) or a < 0:
        raise ValueError("Factorial requires a non-negative integer")
    return int(math.factorial(a))
```

### 3. **Modular Architecture** (Linux Example)
```python
def load_modules_from_folder(folder_path: str):
    """Dynamically load MCP tools and resources from a folder."""
    # ...existing code...
    for file_path in glob.glob(os.path.join(folder_path, "*.py")):
        # ...existing code...
        if hasattr(module, "register"):
            module.register(mcp)
```

### 4. **Security** (All Examples)
```python
# Environment variables for sensitive data
api_key = os.getenv("API_KEY")

# Input validation
if not isinstance(param, expected_type):
    raise ValueError("Invalid parameter type")

# Error handling without exposing internals
except Exception as e:
    logger.error(f"Internal error: {e}")
    return {"error": "Operation failed"}
```