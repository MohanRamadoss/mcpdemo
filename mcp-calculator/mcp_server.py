from mcp.server.fastmcp import FastMCP
import sys
import math

# instantiate an MCP server client
mcp = FastMCP(
    "Scientific Calculator",
    description="A scientific calculator providing mathematical operations",
    version="1.0.0"
)

#addition tool
@mcp.tool()
def add(a: float, b: float) -> float:
    """Add two numbers"""
    return float(a + b)

# subtraction tool
@mcp.tool()
def subtract(a: float, b: float) -> float:
    """Subtract two numbers"""
    return float(a - b)

# multiplication tool
@mcp.tool()
def multiply(a: float, b: float) -> float:
    """Multiply two numbers"""
    return float(a * b)

#  division tool
@mcp.tool() 
def divide(a: float, b: float) -> float:
    """Divide two numbers"""
    if b == 0:
        raise ValueError("Cannot divide by zero")
    return float(a / b)

# power tool
@mcp.tool()
def power(a: float, b: float) -> float:
    """Power of two numbers"""
    try:
        return float(a ** b)
    except OverflowError:
        raise ValueError("Result too large")

# square root tool
@mcp.tool()
def sqrt(a: float) -> float:
    """Square root of a number"""
    if a < 0:
        raise ValueError("Cannot calculate square root of negative number")
    return float(a ** 0.5)

# cube root tool
@mcp.tool()
def cbrt(a: float) -> float:
    """Cube root of a number"""
    return float(abs(a) ** (1/3)) * (-1 if a < 0 else 1)

# factorial tool
@mcp.tool()
def factorial(a: int) -> int:
    """factorial of a number"""
    if not isinstance(a, int) or a < 0:
        raise ValueError("Factorial requires a non-negative integer")
    return int(math.factorial(a))

# log tool
@mcp.tool()
def log(a: float) -> float:
    """log of a number"""
    if a <= 0:
        raise ValueError("Cannot calculate logarithm of non-positive number")
    return float(math.log(a))

# remainder tool
@mcp.tool()
def remainder(a: float, b: float) -> float:
    """remainder of two numbers division"""
    if b == 0:
        raise ValueError("Cannot calculate remainder with zero divisor")
    return float(a % b)

# sin tool
@mcp.tool()
def sin(a: float) -> float:
    """sin of a number"""
    return float(math.sin(math.radians(a)))

# cos tool
@mcp.tool()
def cos(a: float) -> float:
    """cos of a number"""
    return float(math.cos(math.radians(a)))

# tan tool
@mcp.tool()
def tan(a: float) -> float:
    """tan of a number"""
    angle = math.radians(a)
    if math.cos(angle) == 0:
        raise ValueError("Tangent undefined at this angle")
    return float(math.tan(angle))

# DEFINE RESOURCES

# Add a dynamic greeting resource
@mcp.resource("greeting://{name}")
def get_greeting(name: str) -> str:
    """Get a personalized greeting"""
    return f"Hello, {name}!"
    
# execute and return the output
if __name__ == "__main__":
    print("Scientific Calculator MCP Server is starting up...")
    
    # Check if we should run with STDIO (for MCP client) or SSE (for web)
    transport = "stdio"  # Default to STDIO for MCP client compatibility
    port = None
    
    if len(sys.argv) > 1 and sys.argv[1] == "--sse":
        transport = "sse"
        port = 3001
        print(f"Server will be available on port {port}")
    else:
        print("Server will use STDIO transport for MCP client")
    
    try:
        if transport == "sse":
            mcp.run(transport="sse", port=port)
        else:
            mcp.run(transport="stdio")
    except Exception as e:
        print(f"Error starting server: {e}")
        sys.exit(1)