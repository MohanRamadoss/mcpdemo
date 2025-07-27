# Part 2: Tool Calling Basics

## What is Tool Calling?

Tool calling is the mechanism that allows AI agents to execute specific functions or actions beyond just generating text. Instead of just responding with words, agents can:

- Make HTTP requests to APIs
- Execute database queries
- Send emails or messages
- Create or modify files
- Perform calculations
- Interact with external services

## How Tool Calling Works

### 1. **Tool Definition**
First, you define what tools your agent can use:

```python
tools = [
    {
        "name": "get_weather",
        "description": "Get current weather for a location",
        "parameters": {
            "type": "object",
            "properties": {
                "location": {
                    "type": "string",
                    "description": "City name or coordinates"
                }
            },
            "required": ["location"]
        }
    }
]
```

### 2. **Agent Decision**
The agent analyzes the user's request and decides which tool to call:

```
User: "What's the weather like in New York?"
Agent: I need to call the get_weather tool with location="New York"
```

### 3. **Tool Execution**
The system executes the tool and gets the result:

```python
def get_weather(location):
    # Make API call to weather service
    response = weather_api.get_current(location)
    return {
        "temperature": "72°F",
        "condition": "Partly cloudy",
        "humidity": "65%"
    }
```

### 4. **Response Generation**
The agent uses the tool result to generate a helpful response:

```
Agent: "The weather in New York is currently 72°F and partly cloudy with 65% humidity."
```

## MCP Tool Calling vs Traditional Tool Calling

### Traditional Tool Calling (OpenAI Functions)
```python
# Traditional approach - tools defined as JSON schemas
tools = [
    {
        "type": "function",
        "function": {
            "name": "calculate",
            "description": "Perform calculations",
            "parameters": {
                "type": "object",
                "properties": {"expression": {"type": "string"}},
                "required": ["expression"]
            }
        }
    }
]

response = openai.chat.completions.create(
    model="gpt-4",
    messages=messages,
    tools=tools
)
```

### MCP Tool Calling (Our Implementation)
```python
# MCP approach - tools as Python functions with decorators
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("Calculator Server")

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

# Tools automatically registered with type safety and documentation
```

## Real Examples from Our MCP Implementations

### 1. Weather Tools (External API Integration)

From `mcp-weather-client-tutorial/weather_server.py`:

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
    # First get the forecast grid endpoint
    points_url = f"{NWS_API_BASE}/points/{latitude},{longitude}"
    points_data = await make_nws_request(points_url)

    if not points_data:
        return f"Unable to fetch forecast data for coordinates {latitude}, {longitude}. Make sure coordinates are within the US."

    # Get location info
    location_name = points_data["properties"].get("relativeLocation", {}).get("properties", {}).get("city", "Unknown Location")
    state = points_data["properties"].get("relativeLocation", {}).get("properties", {}).get("state", "")
    
    # Get the forecast URL from the points response
    forecast_url = points_data["properties"]["forecast"]
    forecast_data = await make_nws_request(forecast_url)

    if not forecast_data:
        return f"Unable to fetch detailed forecast for {location_name}."

    # Format the periods into a readable forecast
    periods = forecast_data["properties"]["periods"]
    forecasts = []
    for period in periods[:5]:  # Only show next 5 periods
        forecast = f"""
📅 {period['name']}:
🌡️ Temperature: {period['temperature']}°{period['temperatureUnit']}
💨 Wind: {period['windSpeed']} {period['windDirection']}
🌤️ Conditions: {period['shortForecast']}
📋 Details: {period['detailedForecast']}
"""
        forecasts.append(forecast)

    return f"🌤️ Weather Forecast for {location_name}, {state}:\n" + "\n---\n".join(forecasts)
```

**Key Features:**
- ✅ **Async support** for external API calls
- ✅ **Error handling** for invalid coordinates
- ✅ **Rich documentation** with examples
- ✅ **Type hints** for parameter validation
- ✅ **Formatted responses** for better user experience

### 2. Calculator Tools (Pure Computation)

From `mcp-calculator/mcp_server.py`:

```python
@mcp.tool()
def power(a: float, b: float) -> float:
    """Power of two numbers"""
    try:
        return float(a ** b)
    except OverflowError:
        raise ValueError("Result too large")

@mcp.tool()
def factorial(a: int) -> int:
    """factorial of a number"""
    if not isinstance(a, int) or a < 0:
        raise ValueError("Factorial requires a non-negative integer")
    return int(math.factorial(a))
```

**Key Features:**
- ✅ **Input validation** preventing invalid operations
- ✅ **Custom error messages** for user feedback
- ✅ **Type enforcement** (int vs float)
- ✅ **Mathematical safety** (overflow protection)

### 3. System Administration Tools (Modular Architecture)

From `mcp-for-linux/tools/process_management.py`:

```python
def register(mcp):
    @mcp.tool()
    def kill_process(pid: int) -> dict:
        """Kill a process by PID"""
        try:
            process = psutil.Process(pid)
            process_name = process.name()
            process.terminate()
            
            # Wait for termination
            try:
                process.wait(timeout=5)
                return {"status": f"Process {pid} ({process_name}) terminated successfully"}
            except psutil.TimeoutExpired:
                # Force kill if termination timeout
                process.kill()
                return {"status": f"Process {pid} ({process_name}) forcefully killed"}
                
        except psutil.NoSuchProcess:
            return {"error": f"Process {pid} not found"}
        except psutil.AccessDenied:
            return {"error": f"Access denied to kill process {pid}"}
        except Exception as e:
            return {"error": f"Failed to kill process {pid}: {str(e)}"}
```

**Key Features:**
- ✅ **Graceful degradation** (try terminate, then force kill)
- ✅ **Comprehensive error handling** for different failure modes
- ✅ **Structured responses** with success/error status
- ✅ **System integration** with psutil library

## Tool Calling Patterns

### 1. **Single Tool Call**
Simple cases where one tool is sufficient:

```python
# User asks for weather
user_input = "What's the weather in London?"
# Agent calls weather tool
weather_data = get_weather("London")
# Agent responds with weather info
```

### 2. **Sequential Tool Calls**
Multiple tools called in order:

```python
# User asks for flight info and weather
user_input = "I'm flying to Tokyo tomorrow. What's the weather like there?"

# Step 1: Get flight info
flight_data = get_flight_info("Tokyo", "tomorrow")

# Step 2: Get weather for destination
weather_data = get_weather("Tokyo")

# Step 3: Combine and respond
response = f"Your flight to Tokyo is at {flight_data['time']}. The weather there will be {weather_data['condition']}."
```

### 3. **Conditional Tool Calls**
Tools called based on conditions - implemented in our Gemini client:

```python
# From advanced_client.py - intelligent tool selection
system_prompt = f"""You are an advanced weather assistant powered by Gemini 2.5 Flash with access to these weather tools:

{tools_description}

🔍 TOOL USAGE INSTRUCTIONS:
When you need to use a tool, respond with ONLY a clean JSON object in this format:
{{"tool_call": {{"name": "tool_name", "arguments": {{"param1": "value1", "param2": "value2"}}}}}}

🌍 IMPORTANT RULES:
- For international locations (non-US), use get_coordinates or get_international_weather_info
- Weather forecasts only work for US locations
- Always explain limitations for international requests
"""

# Gemini intelligently chooses appropriate tools based on context
response = self.model.generate_content(full_prompt)
```

## Implementing Tool Calling with MCP

### Step 1: Define Your Tools (MCP Style)

```python
from mcp.server.fastmcp import FastMCP
import asyncio
import httpx

mcp = FastMCP("My Agent Server")

@mcp.tool()
async def search_web(query: str, limit: int = 5) -> dict:
    """Search the web for information"""
    try:
        # Implement web search logic
        results = await web_search_api(query, limit)
        return {"results": results, "query": query}
    except Exception as e:
        return {"error": f"Search failed: {str(e)}"}

@mcp.tool()
def calculate_tip(bill_amount: float, tip_percentage: float = 15.0) -> dict:
    """Calculate tip amount and total bill"""
    if bill_amount <= 0:
        return {"error": "Bill amount must be positive"}
    
    tip_amount = bill_amount * (tip_percentage / 100)
    total = bill_amount + tip_amount
    
    return {
        "bill_amount": bill_amount,
        "tip_percentage": tip_percentage,
        "tip_amount": round(tip_amount, 2),
        "total": round(total, 2)
    }
```

### Step 2: Create Dynamic Tool Loading (Advanced Pattern)

From our Linux MCP implementation:

```python
# mcp-for-linux/main.py
def load_modules_from_folder(folder_path: str):
    """Dynamically load MCP tools and resources from a folder."""
    logger.info(f"Loading modules from: {folder_path}")
    for file_path in glob.glob(os.path.join(folder_path, "*.py")):
        if file_path.endswith("__init__.py"):
            continue
        
        module_name = os.path.splitext(os.path.basename(file_path))[0]
        spec = importlib.util.spec_from_file_location(module_name, file_path)
        if spec and spec.loader:
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            if hasattr(module, "register"):
                logger.info(f"Registering module: {module_name}")
                module.register(mcp)
            else:
                logger.warning(f"Module {module_name} has no register function.")

if __name__ == "__main__":
    # Load all tools and resources
    load_modules_from_folder("tools")
    load_modules_from_folder("resources")
    mcp.run(transport="stdio")
```

### Step 3: Build an Intelligent Client (Gemini Integration)

```python
# From advanced_client.py - our Gemini-powered MCP client
class MCPClient:
    def __init__(self):
        # ...existing code...
        # Configure Gemini 2.5 Flash
        self.model = genai.GenerativeModel('gemini-2.5-flash')
    
    async def process_query(self, query: str) -> str:
        """Process a query using Gemini 2.5 Flash and available tools"""
        response = await self.session.list_tools()
        available_tools = response.tools
        
        # Format tools for Gemini
        tools_description = "\n".join([
            f"🛠️ Tool: {tool.name}\n📝 Description: {tool.description}\n⚙️ Parameters: {tool.inputSchema}\n"
            for tool in available_tools
        ])
        
        # Enhanced system prompt optimized for Gemini 2.5 Flash
        system_prompt = f"""You are an advanced assistant powered by Gemini 2.5 Flash with access to these tools:

{tools_description}

When you need to use a tool, respond with a clean JSON object:
{{"tool_call": {{"name": "tool_name", "arguments": {{"param1": "value1"}}}}}}"""

        full_prompt = f"{system_prompt}\n\nUser query: {query}"
        
        # Generate response with Gemini
        response = self.model.generate_content(full_prompt)
        response_text = response.text.strip()
        
        # Parse and execute tool calls
        if '"tool_call"' in response_text:
            # Extract and execute tool call
            # ...existing code...
```

## Advanced Tool Calling Patterns

### 1. **Tool Chaining** (Weather Example)

```python
# From weather_server.py - tools that work together
@mcp.tool()
async def get_coordinates(city: str) -> str:
    """Get coordinates for a city"""
    # Returns coordinates that can be used by get_forecast

@mcp.tool() 
async def get_forecast(latitude: float, longitude: float) -> str:
    """Get forecast using coordinates from get_coordinates"""
    # Uses coordinates from previous tool

# User workflow:
# 1. "Get coordinates for Tokyo" → lat/lng
# 2. "Get forecast for coordinates 35.6762, 139.6503" → weather data
```

### 2. **Resource + Tool Pattern** (Linux Example)

```python
# From mcp-for-linux - resources provide data, tools perform actions
@mcp.resource("system://metrics/cpu")
def get_cpu_stats() -> dict:
    """Get current CPU usage statistics."""
    return {
        "cpu_percent": psutil.cpu_percent(interval=1),
        "cpu_cores": psutil.cpu_count()
    }

@mcp.tool()
def restart_service(service_name: str) -> dict:
    """Restart a system service"""
    # Can use CPU resource data to make decisions
    # ...existing code...
```

### 3. **Error Recovery Pattern**

```python
@mcp.tool()
async def get_weather_with_fallback(location: str) -> str:
    """Get weather with multiple fallback strategies"""
    try:
        # Try primary weather API
        return await get_weather_primary(location)
    except APIError:
        try:
            # Fallback to secondary API
            return await get_weather_secondary(location)
        except APIError:
            try:
                # Final fallback to cached data
                return get_cached_weather(location)
            except:
                return "Weather data temporarily unavailable"
```

## Best Practices for Tool Calling

### 1. **Tool Design** (From Our Examples)

```python
# ✅ Good - Clear, focused tool with validation
@mcp.tool()
def divide(a: float, b: float) -> float:
    """Divide two numbers"""
    if b == 0:
        raise ValueError("Cannot divide by zero")
    return float(a / b)

# ❌ Bad - Unclear, multiple responsibilities
@mcp.tool()
def do_math_stuff(operation: str, numbers: list) -> any:
    """Does various math things"""
    # Unclear what operations are supported
    # No validation
    # Generic return type
```

### 2. **Security** (From Linux Tools)

```python
@mcp.tool()
def kill_process(pid: int) -> dict:
    """Kill a process by PID"""
    try:
        # ✅ Validate PID is integer
        if not isinstance(pid, int) or pid <= 0:
            return {"error": "Invalid PID"}
        
        # ✅ Check permissions before action
        process = psutil.Process(pid)
        process_name = process.name()
        
        # ✅ Graceful termination first
        process.terminate()
        # ...existing code...
    except psutil.AccessDenied:
        # ✅ Handle permission errors gracefully
        return {"error": f"Access denied to kill process {pid}"}
```

### 3. **Error Handling** (From Weather Tools)

```python
@mcp.tool()
async def get_forecast(latitude: float, longitude: float) -> str:
    """Get weather forecast with comprehensive error handling"""
    try:
        points_data = await make_nws_request(points_url)
        
        # ✅ Validate API response
        if not points_data:
            return f"Unable to fetch forecast data for coordinates {latitude}, {longitude}. Make sure coordinates are within the US."
        
        # ✅ Handle missing data gracefully
        location_name = points_data["properties"].get("relativeLocation", {}).get("properties", {}).get("city", "Unknown Location")
        
    except Exception as e:
        # ✅ Log error for debugging
        logger.error(f"Error in get_forecast: {str(e)}")
        return f"Weather service temporarily unavailable: {str(e)}"
```

### 4. **Performance** (Async Pattern)

```python
# ✅ Async for I/O operations
@mcp.tool()
async def get_multiple_forecasts(locations: list) -> dict:
    """Get forecasts for multiple locations efficiently"""
    tasks = []
    for location in locations:
        task = get_forecast(location['lat'], location['lng'])
        tasks.append(task)
    
    # Execute all requests concurrently
    results = await asyncio.gather(*tasks, return_exceptions=True)
    return {"forecasts": results}
```

## Tool Types in Our MCP Implementations

### 1. **Information Retrieval** (Weather)
- External API integration
- Data transformation
- Caching strategies

### 2. **Computation** (Calculator)
- Pure functions
- Mathematical operations
- Input validation

### 3. **System Operations** (Linux)
- System monitoring
- Process management
- Service control

### 4. **Data Processing** (All)
- Format conversion
- Validation
- Error handling

## Architecture Comparison

| Pattern | Weather MCP | Calculator MCP | Linux MCP |
|---------|-------------|----------------|-----------|
| **Tool Definition** | `@mcp.tool()` decorator | `@mcp.tool()` decorator | Dynamic loading |
| **Error Handling** | Comprehensive | Basic | Production-grade |
| **Async Support** | ✅ Yes | ❌ No | ✅ Yes |
| **Type Safety** | ✅ Strong | ✅ Strong | ✅ Strong |
| **Documentation** | Rich examples | Mathematical focus | System admin focus |
| **Validation** | API response validation | Math safety checks | Permission checks |

## Next Steps

Now that you understand tool calling basics and have seen real implementations, let's explore [Part 3: MCP Server Introduction](./part3-mcp-intro.md) to learn how to build and deploy your own MCP servers.

## Key Takeaways

- ✅ **MCP simplifies tool calling** with decorators and automatic registration
- ✅ **Our three examples** demonstrate different tool patterns:
  - Weather: External API integration with async operations
  - Calculator: Pure computation with safety validation
  - Linux: System operations with comprehensive error handling
- ✅ **Best practices include**: Clear documentation, input validation, error handling, and security considerations
- ✅ **Gemini 2.5 Flash integration** provides intelligent tool selection
- ✅ **Modular architecture** (Linux MCP) enables scalable tool management

---

**Ready to build your own MCP server?** Continue to [Part 3: MCP Server Introduction](./part3-mcp-intro.md) to learn server architecture and deployment patterns! 🚀

## Resources and Examples

- **Weather Tools**: `mcp-weather-client-tutorial/weather_server.py`
- **Calculator Tools**: `mcp-calculator/mcp_server.py`  
- **Linux Tools**: `mcp-for-linux/tools/` directory
- **Client Implementation**: `advanced_client.py` files
- **Architecture Documentation**: `mcp-for-linux/arch.md`